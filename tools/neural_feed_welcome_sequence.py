#!/usr/bin/env python3
"""
Neural Feed Welcome Sequence Automation
=======================================

Sends the 7-email welcome sequence to new subscribers of Brevo List 3
(The Neural Feed - Blog Subscribers).

How it works:
  1. A background scheduler polls Brevo List 3 every hour for new contacts.
  2. When a new contact is found (not in state file), Email 1 fires immediately.
  3. Subsequent emails (2-7) are sent when the elapsed time since subscription
     meets each email's threshold day.
  4. State is persisted in config/welcome_sequence_state.json so sends survive
     server restarts. Each contact's entry is keyed by email address.

Email schedule (relative to subscription date / Email 1 send time):
  Email 1: Day 0  - immediate on subscribe
  Email 2: Day 2  - 2 days after Email 1
  Email 3: Day 4  - 4 days after Email 1
  Email 4: Day 7  - 7 days after Email 1
  Email 5: Day 10 - 10 days after Email 1
  Email 6: Day 14 - 14 days after Email 1
  Email 7: Day 21 - 21 days after Email 1

Brevo template IDs (already created, active):
  1: Neural Feed - Email 1 - Welcome (Aether)
  2: Neural Feed - Email 2 - Jared's Story
  3: Neural Feed - Email 3 - Aether Writes Directly
  4: Neural Feed - Email 4 - Partnership in Practice
  5: Neural Feed - Email 5 - The Context Tax
  6: Neural Feed - Email 6 - Social Proof & Results
  7: Neural Feed - Email 7 - The Invitation

Integration:
  - Import and call `start_welcome_sequence_scheduler()` from purebrain_log_server.py
    at app startup (once, in main()).
  - Or run standalone: `python3 tools/neural_feed_welcome_sequence.py`

Author: full-stack-developer
Date: 2026-02-21
"""

import json
import logging
import os
import threading
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

import requests as _requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load environment
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).parent.parent
load_dotenv(_ROOT / '.env')

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger('neural_feed_welcome')
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BREVO_API_KEY: str = os.getenv('BREVO_API_KEY', '')
BREVO_BASE_URL = 'https://api.brevo.com/v3'

# List 3 = The Neural Feed - Blog Subscribers
NEURAL_FEED_LIST_ID = 3

# Email schedule: (email_number, template_id, delay_days)
# Email 1 is sent immediately (delay_days=0).
EMAIL_SCHEDULE = [
    (1,  1,  0),   # Day 0  - Immediate Welcome (Aether)
    (2,  2,  2),   # Day 2  - Jared's Story
    (3,  3,  4),   # Day 4  - Aether Writes Directly
    (4,  4,  7),   # Day 7  - Partnership in Practice
    (5,  5, 10),   # Day 10 - The Context Tax
    (6,  6, 14),   # Day 14 - Social Proof & Results
    (7,  7, 21),   # Day 21 - The Invitation
]

# State persistence
STATE_FILE = _ROOT / 'config' / 'welcome_sequence_state.json'

# Brevo polling interval (seconds).  Default: every 3600 seconds (1 hour).
# In tests or dev you can set NEURAL_FEED_POLL_INTERVAL env var to a smaller value.
# INFO-001: Floor at 60s to prevent accidental Brevo API hammering in dev environments.
POLL_INTERVAL_SECONDS = max(60, int(os.getenv('NEURAL_FEED_POLL_INTERVAL', '3600')))

# Email log path (shared with post-purchase email logger)
EMAIL_LOG_FILE = _ROOT / 'logs' / 'purebrain_emails.jsonl'

# tg_send.sh helper
TG_SEND_SCRIPT = _ROOT / 'tools' / 'tg_send.sh'
TG_CONFIG_FILE = _ROOT / 'config' / 'telegram_config.json'

# INFO-002: Cache Telegram config at module load to avoid repeated file reads per call.
# Falls back gracefully if the file is missing or malformed.
try:
    with open(TG_CONFIG_FILE) as _f:
        _tg_config = json.load(_f)
    _TG_BOT_TOKEN: str = _tg_config.get('bot_token', '')
    _TG_CHAT_ID: str = str(_tg_config.get('default_chat_id', ''))
except Exception as _e:
    _TG_BOT_TOKEN = ''
    _TG_CHAT_ID = ''
    logging.getLogger('neural_feed_welcome').warning(
        f'Could not load Telegram config at startup: {_e}'
    )

# Retry config for failed email sends
MAX_SEND_RETRIES = 3
RETRY_DELAY_SECONDS = 30

# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

_state_lock = threading.Lock()


def _load_state() -> dict:
    """
    Load subscriber state from disk.

    Returns a dict keyed by email address.  Each value is:
    {
        "email": "subscriber@example.com",
        "firstname": "Jane",                # optional
        "subscribed_at": "2026-02-21T...",  # ISO-8601 UTC
        "emails_sent": [1, 2, 3],           # email numbers already sent
        "sequence_complete": false,
        "last_checked": "2026-02-21T...",
        "errors": []                         # list of error strings (for debug)
    }
    """
    with _state_lock:
        if not STATE_FILE.exists():
            return {}
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f'Failed to load welcome sequence state: {e}')
            return {}


def _save_state(state: dict) -> None:
    """Persist subscriber state to disk (thread-safe)."""
    with _state_lock:
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            # Atomic write: write to .tmp then rename
            tmp = STATE_FILE.with_suffix('.tmp')
            with open(tmp, 'w') as f:
                json.dump(state, f, indent=2)
            tmp.rename(STATE_FILE)
        except OSError as e:
            logger.error(f'Failed to save welcome sequence state: {e}')


# ---------------------------------------------------------------------------
# Brevo API helpers
# ---------------------------------------------------------------------------

def _brevo_headers() -> dict:
    return {
        'api-key': BREVO_API_KEY,
        'Content-Type': 'application/json',
    }


def _get_list3_contacts() -> list[dict]:
    """
    Fetch all contacts currently in Brevo List 3.

    Handles Brevo pagination (limit=1000 per page).

    Returns a list of contact dicts:
      { id, email, emailBlacklisted, createdAt, attributes: {FIRSTNAME, ...}, ... }
    """
    if not BREVO_API_KEY:
        logger.error('BREVO_API_KEY not set - cannot fetch contacts')
        return []

    contacts = []
    offset = 0
    limit = 1000

    while True:
        try:
            resp = _requests.get(
                f'{BREVO_BASE_URL}/contacts',
                headers=_brevo_headers(),
                params={
                    'listId': NEURAL_FEED_LIST_ID,
                    'limit': limit,
                    'offset': offset,
                },
                timeout=20,
            )
            if resp.status_code != 200:
                logger.error(
                    f'Brevo contacts fetch failed: status={resp.status_code} '
                    f'body={resp.text[:200]}'
                )
                break

            data = resp.json()
            batch = data.get('contacts', [])
            contacts.extend(batch)

            if len(batch) < limit:
                break  # No more pages

            offset += limit

        except Exception as e:
            logger.error(f'Brevo contacts fetch exception: {e}')
            break

    logger.info(f'Fetched {len(contacts)} contacts from List {NEURAL_FEED_LIST_ID}')
    return contacts


def _send_template_email(
    to_email: str,
    to_name: str,
    template_id: int,
    params: dict,
) -> bool:
    """
    Send a transactional email via Brevo template.

    Args:
        to_email:    Recipient address.
        to_name:     Recipient display name (may be empty string).
        template_id: Brevo template ID (1-7 for Neural Feed sequence).
        params:      Template variables substituted as {{ params.VARNAME }}.

    Returns:
        True if the email was accepted by Brevo (HTTP 200 or 201).
    """
    if not BREVO_API_KEY:
        logger.error('BREVO_API_KEY not set - cannot send email')
        return False

    payload = {
        'to': [{'email': to_email, 'name': to_name or to_email}],
        'templateId': template_id,
        'params': params,
    }

    for attempt in range(1, MAX_SEND_RETRIES + 1):
        try:
            resp = _requests.post(
                f'{BREVO_BASE_URL}/smtp/email',
                headers=_brevo_headers(),
                json=payload,
                timeout=15,
            )
            if resp.status_code in (200, 201):
                msg_id = resp.json().get('messageId', '')
                logger.info(
                    f'Neural Feed email sent: template={template_id} '
                    f'to={to_email} messageId={msg_id} attempt={attempt}'
                )
                return True
            else:
                logger.warning(
                    f'Brevo send attempt {attempt}/{MAX_SEND_RETRIES} failed: '
                    f'template={template_id} to={to_email} '
                    f'status={resp.status_code} body={resp.text[:200]}'
                )
                if attempt < MAX_SEND_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS)

        except Exception as e:
            logger.warning(
                f'Brevo send exception attempt {attempt}/{MAX_SEND_RETRIES}: '
                f'template={template_id} to={to_email} error={e}'
            )
            if attempt < MAX_SEND_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)

    return False


# ---------------------------------------------------------------------------
# Email log
# ---------------------------------------------------------------------------

_email_log_lock = threading.Lock()


def _log_email_event(entry: dict) -> None:
    """Append an email event to purebrain_emails.jsonl (thread-safe)."""
    try:
        with _email_log_lock:
            with open(EMAIL_LOG_FILE, 'a') as f:
                f.write(json.dumps(entry) + '\n')
    except Exception as e:
        logger.warning(f'Failed to write email log: {e}')


# ---------------------------------------------------------------------------
# Telegram notification
# ---------------------------------------------------------------------------

def _send_telegram_notification(message: str) -> None:
    """Send a Telegram notification to Jared (best-effort, non-blocking).

    INFO-002: Uses module-level cached credentials (_TG_BOT_TOKEN, _TG_CHAT_ID)
    instead of reading telegram_config.json on every call.
    """
    try:
        if not _TG_BOT_TOKEN or not _TG_CHAT_ID:
            return
        url = f'https://api.telegram.org/bot{_TG_BOT_TOKEN}/sendMessage'
        data = json.dumps({'chat_id': _TG_CHAT_ID, 'text': message}).encode('utf-8')
        req = urllib.request.Request(
            url, data=data, headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=10)
        logger.info('Telegram notification sent')
    except Exception as e:
        logger.warning(f'Telegram notification failed: {e}')


# ---------------------------------------------------------------------------
# Core sequence logic
# ---------------------------------------------------------------------------

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_brevo_timestamp(ts_str: str) -> Optional[datetime]:
    """
    Parse a Brevo createdAt timestamp.

    Brevo returns timestamps in ISO-8601 with timezone offset, e.g.:
      '2026-02-21T10:30:00.000+01:00'

    Returns a timezone-aware datetime in UTC, or None on failure.
    """
    if not ts_str:
        return None
    try:
        # Python 3.7+ fromisoformat handles ±HH:MM offsets
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt.astimezone(timezone.utc)
    except (ValueError, AttributeError) as e:
        logger.warning(f'Failed to parse Brevo timestamp "{ts_str}": {e}')
        return None


def _emails_due(subscribed_at: datetime, emails_already_sent: list[int]) -> list[tuple]:
    """
    Determine which emails should be sent now.

    Args:
        subscribed_at:        When the contact subscribed (UTC datetime).
        emails_already_sent:  List of email numbers that have already been sent.

    Returns:
        List of (email_number, template_id, delay_days) tuples that are now due
        and have not yet been sent.  Ordered by delay_days ascending.
    """
    now = _now_utc()
    due = []
    for email_num, template_id, delay_days in EMAIL_SCHEDULE:
        if email_num in emails_already_sent:
            continue
        send_after = subscribed_at + timedelta(days=delay_days)
        if now >= send_after:
            due.append((email_num, template_id, delay_days))
    return due


def _process_contact(contact: dict, state: dict) -> dict:
    """
    Evaluate and send any due emails for a single contact.

    Modifies `state` in place with updated send records.
    Returns the updated state dict.
    """
    email = contact.get('email')
    if not email:
        logger.debug('Skipping contact with no email address')
        return state

    # Skip blacklisted contacts
    if contact.get('emailBlacklisted'):
        logger.debug(f'Skipping blacklisted contact: {email}')
        return state

    # Ensure contact is still in List 3 (they might have been removed)
    list_ids = contact.get('listIds', [])
    if NEURAL_FEED_LIST_ID not in list_ids:
        logger.debug(f'Contact {email} is no longer in List {NEURAL_FEED_LIST_ID} - skipping')
        return state

    # Initialise state entry for new subscriber
    if email not in state:
        created_at_str = contact.get('createdAt', '')
        subscribed_at = _parse_brevo_timestamp(created_at_str) or _now_utc()
        state[email] = {
            'email': email,
            'firstname': contact.get('attributes', {}).get('FIRSTNAME', ''),
            'subscribed_at': subscribed_at.isoformat(),
            'emails_sent': [],
            'sequence_complete': False,
            'last_checked': _now_utc().isoformat(),
            'errors': [],
        }
        logger.info(f'New Neural Feed subscriber: {email} (subscribed {subscribed_at.isoformat()})')

    subscriber = state[email]

    # Skip if sequence is already complete
    if subscriber.get('sequence_complete'):
        return state

    subscribed_at = _parse_brevo_timestamp(subscriber['subscribed_at'])
    if subscribed_at is None:
        logger.error(f'Cannot parse subscribed_at for {email} - skipping')
        return state

    emails_already_sent = subscriber.get('emails_sent', [])
    due_emails = _emails_due(subscribed_at, emails_already_sent)

    if not due_emails:
        logger.debug(f'No emails due for {email}')
        subscriber['last_checked'] = _now_utc().isoformat()
        return state

    # Build template params from contact attributes
    attrs = contact.get('attributes', {})
    firstname = attrs.get('FIRSTNAME', '') or subscriber.get('firstname', '')
    params = {
        'FIRSTNAME': firstname or email.split('@')[0],
    }

    for email_num, template_id, delay_days in due_emails:
        logger.info(
            f'Sending Neural Feed Email {email_num} (template {template_id}) '
            f'to {email} (Day {delay_days})'
        )

        sent_ok = _send_template_email(
            to_email=email,
            to_name=firstname or '',
            template_id=template_id,
            params=params,
        )

        # Log the event
        _log_email_event({
            'event': 'neural_feed_email_sent',
            'email': email,
            'email_number': email_num,
            'template_id': template_id,
            'delay_days': delay_days,
            'sent_ok': sent_ok,
            'timestamp': _now_utc().isoformat(),
        })

        if sent_ok:
            subscriber['emails_sent'].append(email_num)
            subscriber.setdefault('send_times', {})[str(email_num)] = _now_utc().isoformat()
        else:
            error_msg = (
                f'Email {email_num} (template {template_id}) send FAILED at '
                f'{_now_utc().isoformat()}'
            )
            subscriber.setdefault('errors', []).append(error_msg)
            logger.error(f'{error_msg} for {email}')

    # Mark sequence complete when all 7 emails have been sent
    if set(subscriber['emails_sent']) >= {num for num, _, _ in EMAIL_SCHEDULE}:
        subscriber['sequence_complete'] = True
        logger.info(f'Welcome sequence COMPLETE for {email}')

        # Telegram notification for sequence completion
        tg_msg = (
            f'Neural Feed sequence COMPLETE\n'
            f'Subscriber: {email}\n'
            f'Emails sent: {sorted(subscriber["emails_sent"])}\n'
            f'All 7 emails delivered successfully.'
        )
        threading.Thread(
            target=_send_telegram_notification,
            args=(tg_msg,),
            daemon=True
        ).start()

    subscriber['last_checked'] = _now_utc().isoformat()
    state[email] = subscriber
    return state


def _notify_new_subscriber(email: str, email_num: int, sent_ok: bool) -> None:
    """Send Telegram notification when Email 1 fires for a new subscriber."""
    status = 'SENT' if sent_ok else 'FAILED'
    tg_msg = (
        f'New Neural Feed subscriber!\n'
        f'Email: {email}\n'
        f'Email 1 (Welcome): {status}'
    )
    threading.Thread(
        target=_send_telegram_notification,
        args=(tg_msg,),
        daemon=True
    ).start()


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

_scheduler_thread: Optional[threading.Thread] = None
_scheduler_running = False


def run_one_cycle() -> dict:
    """
    Run a single check cycle: fetch List 3 contacts, process due emails.

    Returns the updated state dict.  Safe to call directly for testing.
    """
    logger.info('Neural Feed welcome sequence: starting check cycle')
    state = _load_state()
    contacts = _get_list3_contacts()

    new_subscribers_this_cycle = []
    for contact in contacts:
        email = contact.get('email')
        if not email or contact.get('emailBlacklisted'):
            continue

        was_new = email not in state
        state = _process_contact(contact, state)

        # Detect brand-new subscribers (Email 1 just fired)
        if was_new and email in state:
            subscriber = state[email]
            email1_sent = 1 in subscriber.get('emails_sent', [])
            new_subscribers_this_cycle.append((email, email1_sent))
            _notify_new_subscriber(email, 1, email1_sent)

    _save_state(state)
    logger.info(
        f'Neural Feed check cycle complete: '
        f'{len(contacts)} contacts checked, '
        f'{len(new_subscribers_this_cycle)} new subscribers found'
    )
    return state


def _scheduler_loop() -> None:
    """Background loop: run_one_cycle every POLL_INTERVAL_SECONDS."""
    global _scheduler_running
    logger.info(
        f'Neural Feed scheduler started (interval={POLL_INTERVAL_SECONDS}s)'
    )
    while _scheduler_running:
        try:
            run_one_cycle()
        except Exception as e:
            logger.error(f'Neural Feed scheduler cycle error: {e}')

        # Sleep in small increments so we can be stopped quickly
        slept = 0
        while _scheduler_running and slept < POLL_INTERVAL_SECONDS:
            time.sleep(min(10, POLL_INTERVAL_SECONDS - slept))
            slept += 10

    logger.info('Neural Feed scheduler stopped')


def start_welcome_sequence_scheduler() -> None:
    """
    Start the background scheduler thread.

    Call this ONCE from purebrain_log_server.py main() after the Flask app
    is created.  Idempotent: safe to call multiple times (won't start twice).
    """
    global _scheduler_thread, _scheduler_running

    if _scheduler_thread and _scheduler_thread.is_alive():
        logger.info('Neural Feed scheduler is already running - skipping start')
        return

    _scheduler_running = True
    _scheduler_thread = threading.Thread(
        target=_scheduler_loop,
        name='neural-feed-scheduler',
        daemon=True,
    )
    _scheduler_thread.start()
    logger.info('Neural Feed welcome sequence scheduler started')


def stop_welcome_sequence_scheduler() -> None:
    """
    Signal the scheduler to stop.  Used for clean shutdown / testing.
    The thread exits within ~10 seconds of being signalled.
    """
    global _scheduler_running
    _scheduler_running = False
    logger.info('Neural Feed scheduler stop requested')


# ---------------------------------------------------------------------------
# CLI / standalone mode
# ---------------------------------------------------------------------------

def _print_state_summary(state: dict) -> None:
    """Print a human-readable summary of the current state."""
    if not state:
        print('No subscribers in state file yet.')
        return
    print(f'\n{"="*60}')
    print(f'Neural Feed Welcome Sequence State ({len(state)} subscribers)')
    print(f'{"="*60}')
    for email, sub in state.items():
        sent = sorted(sub.get('emails_sent', []))
        complete = sub.get('sequence_complete', False)
        subscribed = sub.get('subscribed_at', 'unknown')
        errors = sub.get('errors', [])
        print(f'\nSubscriber: {email}')
        print(f'  Subscribed: {subscribed}')
        print(f'  Emails sent: {sent}')
        print(f'  Complete: {complete}')
        if errors:
            print(f'  Errors: {len(errors)}')
            for err in errors[-3:]:
                print(f'    - {err}')
    print(f'\n{"="*60}\n')


def main() -> None:
    """
    Standalone CLI mode.

    Usage:
      python3 tools/neural_feed_welcome_sequence.py          # Run one cycle
      python3 tools/neural_feed_welcome_sequence.py --daemon # Run continuously
      python3 tools/neural_feed_welcome_sequence.py --status # Show current state
    """
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
    )

    args = set(sys.argv[1:])

    if '--status' in args:
        state = _load_state()
        _print_state_summary(state)
        return

    if '--daemon' in args:
        print(f'Starting Neural Feed scheduler in daemon mode (interval={POLL_INTERVAL_SECONDS}s)')
        print('Press Ctrl+C to stop.')
        start_welcome_sequence_scheduler()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('\nStopping...')
            stop_welcome_sequence_scheduler()
        return

    # Default: run a single cycle and exit
    print('Running one Neural Feed check cycle...')
    state = run_one_cycle()
    _print_state_summary(state)


if __name__ == '__main__':
    main()
