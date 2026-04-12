#!/usr/bin/env python3
"""
AgentMail General Monitor - Persistent inbox monitoring for aethergottaeat@agentmail.to

Polls the general comms inbox every 30 seconds.
On new messages from whitelisted senders:
  - Injects notification into active tmux pane (Primary AI sees it immediately)
  - Sends alert to Telegram

For non-whitelisted senders:
  - Still notifies (tmux + Telegram) but does NOT auto-respond

State file: /home/jared/.aiciv/processed-agentmail-general.txt
            (flat list of processed message IDs, one per line)

Whitelisted senders (auto-notify + flagged for AI response):
  - parallax@agentmail.to
  - keel@agentmail.to
  - witness-support@agentmail.to
  - witness-aiciv@agentmail.to
  - true-bearing-aiciv@agentmail.to
  - acg-aiciv@agentmail.to

Usage:
  python3 tools/agentmail_general_monitor.py

Background (nohup):
  nohup python3 tools/agentmail_general_monitor.py >> logs/agentmail_general_monitor.log 2>&1 &

Managed by systemd:
  sudo systemctl start aether-agentmail-general
  sudo systemctl status aether-agentmail-general

Author: dept-systems-technology
Date: 2026-03-20
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import logging
from datetime import datetime, timezone
from pathlib import Path

# ─── Config ─────────────────────────────────────────────────────────────────

CIV_ROOT = Path("/home/jared/projects/AI-CIV/aether")
INBOX = "aethergottaeat@agentmail.to"
POLL_INTERVAL = 30  # seconds
LOG_FILE = CIV_ROOT / "logs/agentmail_general_monitor.log"
TG_SEND = CIV_ROOT / "tools/tg_send.sh"

# State: flat file of processed message IDs (one per line)
STATE_FILE = Path("/home/jared/.aiciv/processed-agentmail-general.txt")

# Whitelisted senders — messages from these get flagged for AI response
WHITELIST = {
    "meridian-pt@agentmail.to",  # Meridian - HR Intelligence, Pure Technology
    "donatobsms@gmail.com",  # DJ/Flint (Witness Civilization)
    "parallax@agentmail.to",
    "keel@agentmail.to",
    "witness-support@agentmail.to",
    "witness-aiciv@agentmail.to",
    "true-bearing-aiciv@agentmail.to",
    "acg-aiciv@agentmail.to",
    "metis.pa.mh@gmail.com",  # Metis - General Counsel AI (Michael Hancock)
    "mthancock@gmail.com",  # Michael Hancock - General Counsel (human)
}

# ─── Logging ─────────────────────────────────────────────────────────────────

def _setup_logging() -> logging.Logger:
    """Set up logging, creating the log file and directory if needed."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("agentmail-general")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [agentmail-general] %(levelname)s: %(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    try:
        fh = logging.FileHandler(str(LOG_FILE))
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except PermissionError as e:
        sh.stream.write(f"WARNING: Cannot write to log file {LOG_FILE}: {e}\n")
    return logger

log = _setup_logging()

# ─── Credentials ─────────────────────────────────────────────────────────────

def load_env() -> dict:
    env = {}
    env_path = CIV_ROOT / ".env"
    with open(str(env_path)) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

ENV = load_env()
API_KEY = ENV.get("AGENTMAIL_API_KEY", "")

if not API_KEY:
    log.error("AGENTMAIL_API_KEY not found in .env — cannot poll inbox")
    sys.exit(1)

# ─── State Management ─────────────────────────────────────────────────────────

def load_seen_ids() -> set:
    """Load the set of already-processed message IDs from the state file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            lines = STATE_FILE.read_text().splitlines()
            return set(line.strip() for line in lines if line.strip())
        except Exception as e:
            log.warning(f"State file read error, starting fresh: {e}")
    return set()


def save_seen_id(msg_id: str):
    """Append a single processed message ID to the state file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(str(STATE_FILE), "a") as f:
        f.write(msg_id + "\n")


# ─── AgentMail API ──────────────────────────────────────────────────────────

def api_get(path: str) -> dict:
    url = f"https://api.agentmail.to/v0{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def list_messages(limit: int = 50) -> list:
    data = api_get(f"/inboxes/{INBOX}/messages?limit={limit}")
    return data.get("messages", [])


def get_message(message_id: str) -> dict:
    mid_enc = urllib.parse.quote(message_id, safe="")
    return api_get(f"/inboxes/{INBOX}/messages/{mid_enc}")


# ─── Sender Classification ───────────────────────────────────────────────────

def is_whitelisted(sender: str) -> bool:
    """Return True if this sender address matches the whitelist."""
    sender_lower = sender.lower().strip()
    # Exact match or contained within angle-bracket format <addr@domain>
    for addr in WHITELIST:
        if addr in sender_lower:
            return True
    return False


def sender_label(sender: str) -> str:
    """Return a short human-readable label for the sender."""
    s = sender.lower()
    if "parallax" in s:
        return "Parallax"
    if "keel" in s:
        return "Keel"
    if "witness-support" in s:
        return "Witness (support)"
    if "witness-aiciv" in s:
        return "Witness"
    if "true-bearing" in s:
        return "True Bearing"
    if "acg-aiciv" in s or "acgee" in s:
        return "ACG"
    return sender


# ─── Notification Delivery ──────────────────────────────────────────────────

def get_active_tmux_pane() -> str:
    """Get the pane ID of the currently active tmux pane."""
    try:
        result = subprocess.run(
            ["tmux", "display-message", "-p", "#{pane_id}"],
            capture_output=True, text=True, timeout=5
        )
        pane = result.stdout.strip()
        if pane:
            return pane
    except Exception:
        pass
    return "%1"  # fallback to known Primary pane


def inject_to_tmux(message: str):
    """Inject a notification into the active tmux pane."""
    pane = get_active_tmux_pane()
    try:
        subprocess.run(
            ["tmux", "send-keys", "-t", pane, message, ""],
            timeout=5
        )
        log.info(f"Injected to tmux pane {pane}")
    except Exception as e:
        log.warning(f"tmux inject failed: {e}")


def send_telegram(message: str):
    """Send a Telegram notification to Jared via tg_send.sh."""
    try:
        result = subprocess.run(
            [str(TG_SEND), message],
            capture_output=True, text=True, timeout=15,
            cwd=str(CIV_ROOT)
        )
        if result.returncode == 0:
            log.info("Telegram alert sent")
        else:
            log.warning(f"tg_send.sh failed: {result.stderr.strip()}")
    except Exception as e:
        log.warning(f"Telegram send failed: {e}")


# ─── Message Formatting ──────────────────────────────────────────────────────

def format_tmux_notification(msg: dict, body: str, whitelisted: bool) -> str:
    """Format a message for tmux injection."""
    sender = msg.get("from", "unknown")
    subject = msg.get("subject", "(no subject)")
    preview = (body or msg.get("preview", ""))[:300]
    label = sender_label(sender)
    flag = "[WHITELISTED — RESPOND]" if whitelisted else "[UNKNOWN SENDER]"

    return (
        f"\n[AGENTMAIL-GENERAL] {flag} "
        f"from:{label} ({sender}) | "
        f"subject:{subject} | "
        f"preview:{preview}"
    )


def format_telegram_notification(msg: dict, body: str, whitelisted: bool) -> str:
    """Format a message for Telegram delivery to Jared."""
    sender = msg.get("from", "unknown")
    subject = msg.get("subject", "(no subject)")
    preview = (body or msg.get("preview", ""))[:500]
    label = sender_label(sender)
    flag = "WHITELISTED — AI should respond" if whitelisted else "Unknown sender — review manually"

    lines = [
        f"GeneralInbox: New message",
        f"From: {label} ({sender})",
        f"Subject: {subject}",
        f"Status: {flag}",
        f"",
        preview,
    ]
    if len(preview) >= 500:
        lines.append("... (truncated)")
    return "\n".join(lines)


# ─── Main Poll Cycle ─────────────────────────────────────────────────────────

def seed_seen_ids_from_inbox(seen: set) -> set:
    """
    On first run, populate seen IDs with all existing messages so we don't
    replay the full inbox history.
    """
    log.info("Fresh start — seeding seen IDs from existing inbox...")
    try:
        messages = list_messages(limit=100)
        for msg in messages:
            mid = msg.get("message_id", "")
            if mid and mid not in seen:
                seen.add(mid)
                save_seen_id(mid)
        log.info(f"Seeded {len(seen)} existing message IDs")
    except Exception as e:
        log.error(f"Seeding failed: {e}")
    return seen


def process_new_messages(seen: set) -> tuple[set, int]:
    """
    Fetch inbox, process any unseen incoming messages.
    Returns (updated seen set, count of new messages processed).
    """
    new_count = 0

    try:
        messages = list_messages(limit=50)
    except Exception as e:
        log.error(f"Failed to list messages: {e}")
        return seen, 0

    for msg in messages:
        msg_id = msg.get("message_id", "")
        if not msg_id or msg_id in seen:
            continue

        # Skip our own outbound messages
        labels = msg.get("labels", [])
        if "sent" in labels and "received" not in labels:
            seen.add(msg_id)
            save_seen_id(msg_id)
            continue

        # Skip messages originating from this inbox (outbound)
        sender = msg.get("from", "")
        if INBOX in sender.lower():
            seen.add(msg_id)
            save_seen_id(msg_id)
            continue

        # New incoming message — fetch full body
        log.info(f"New message from {sender}: {msg.get('subject', '?')}")

        try:
            full_msg = get_message(msg_id)
            body = full_msg.get("text") or full_msg.get("extracted_text") or msg.get("preview", "")
        except Exception as e:
            log.warning(f"Could not fetch full message body: {e}")
            body = msg.get("preview", "")

        whitelisted = is_whitelisted(sender)

        # Inject tmux notification
        inject_to_tmux(format_tmux_notification(msg, body, whitelisted))

        # Telegram alert
        send_telegram(format_telegram_notification(msg, body, whitelisted))

        if whitelisted:
            log.info(f"Whitelisted sender processed: {sender}")
        else:
            log.info(f"Non-whitelisted sender notified: {sender}")

        seen.add(msg_id)
        save_seen_id(msg_id)
        new_count += 1

        # Brief pause between messages to avoid hammering tmux/TG
        if new_count > 1:
            time.sleep(1)

    return seen, new_count


# ─── Entry Point ─────────────────────────────────────────────────────────────

def run():
    log.info(f"AgentMail General Monitor starting")
    log.info(f"Inbox: {INBOX}")
    log.info(f"Poll interval: {POLL_INTERVAL}s")
    log.info(f"State file: {STATE_FILE}")
    log.info(f"Whitelisted senders: {sorted(WHITELIST)}")

    seen = load_seen_ids()
    is_fresh = len(seen) == 0
    process_existing = "--process-existing" in sys.argv

    if is_fresh and not process_existing:
        seen = seed_seen_ids_from_inbox(seen)
        send_telegram(
            f"AgentMail General Monitor LIVE\n"
            f"Inbox: {INBOX}\n"
            f"Poll: every {POLL_INTERVAL}s\n"
            f"Whitelisted: {len(WHITELIST)} senders\n"
            f"Watching for: Parallax, Keel, Witness, True Bearing, ACG"
        )
    elif is_fresh:
        log.info("Fresh start with --process-existing flag — will process all existing messages")
    else:
        log.info(f"Resuming — {len(seen)} message IDs already tracked")

    log.info("Entering poll loop...")

    while True:
        try:
            seen, new = process_new_messages(seen)
            if new > 0:
                log.info(f"Processed {new} new message(s)")
            else:
                log.debug("No new messages")
        except KeyboardInterrupt:
            log.info("Shutting down (KeyboardInterrupt)")
            break
        except Exception as e:
            log.error(f"Poll cycle error: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()
