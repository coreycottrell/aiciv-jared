#!/usr/bin/env python3
"""
Aether Gmail Monitor

Autonomous email monitoring for purebrain@puremarketing.ai
- Monitors inbox periodically
- Classifies emails: reply_needed, ask_jared, fyi_only
- Drafts and sends replies (CC Jared)
- Alerts Jared via Telegram when uncertain

Usage:
    # One-time check
    python3 tools/gmail_monitor.py check

    # Run as daemon (check every 5 minutes)
    python3 tools/gmail_monitor.py daemon

    # Force check specific emails
    python3 tools/gmail_monitor.py check --force

Author: Aether
Created: 2026-02-04
"""

import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import hashlib
import re
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
STATE_PATH = PROJECT_ROOT / "memories" / "agents" / "email-monitor" / "email_state.json"
LOG_PATH = PROJECT_ROOT / "logs" / "gmail_monitor.log"
JARED_EMAIL = "jaredcmusic@gmail.com"


def load_env() -> dict:
    """Load environment variables from .env file"""
    env_vars = {}
    if ENV_PATH.exists():
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars


def log(message: str, level: str = "INFO"):
    """Log message to file and stdout"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(log_line + "\n")


def load_state() -> dict:
    """Load email state from JSON file"""
    default_state = {
        "processed_ids": {},  # message_id -> status
        "last_check": None,
        "stats": {
            "total_processed": 0,
            "replies_sent": 0,
            "alerts_sent": 0,
            "fyi_logged": 0
        }
    }

    if STATE_PATH.exists():
        try:
            with open(STATE_PATH) as f:
                loaded = json.load(f)
                # Ensure required keys exist (defensive against corrupted state files)
                if not isinstance(loaded, dict):
                    log("State file is corrupted (not a dict), using defaults", "WARN")
                    return default_state

                # Merge with defaults to fill in missing keys
                state = default_state.copy()
                state.update(loaded)

                # Ensure nested stats dict has all required counters
                if 'stats' in state and isinstance(state['stats'], dict):
                    for key in default_state['stats']:
                        if key not in state['stats']:
                            state['stats'][key] = default_state['stats'][key]

                # Ensure processed_ids exists and is a dict
                if 'processed_ids' not in state or not isinstance(state['processed_ids'], dict):
                    state['processed_ids'] = {}

                return state
        except json.JSONDecodeError as e:
            log(f"State file is corrupted (JSON error: {e}), using defaults", "WARN")
            return default_state
        except Exception as e:
            log(f"Error loading state file: {e}, using defaults", "WARN")
            return default_state

    return default_state


def save_state(state: dict):
    """Save email state to JSON file"""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Backup before write
    if STATE_PATH.exists():
        backup = STATE_PATH.with_suffix('.json.bak')
        import shutil
        shutil.copy(STATE_PATH, backup)

    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2, default=str)


def send_telegram(message: str) -> bool:
    """Send alert to Jared via Telegram"""
    try:
        # Use our existing send_telegram tool
        import subprocess
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "tools" / "send_telegram.py"), message],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        log(f"Telegram send failed: {e}", "ERROR")
        return False


def is_automated_sender(from_addr: str) -> bool:
    """Check if sender is clearly automated/system email"""
    from_lower = from_addr.lower()

    # Known automated sender patterns
    automated_patterns = [
        r"noreply",
        r"no-reply",
        r"do-not-reply",
        r"donotreply",
        r"mailer-daemon",
        r"postmaster",
        r"notifications?@",
        r"alerts?@",
        r"news@",
        r"info@.*\.google\.com",
        r"@google\.com$",
        r"@googlemail\.com$",
        r"@accounts\.google\.com",
        r"@mail\.google\.com",
        r"@drive\.google\.com",
        r"@vercel\.com",
        r"@github\.com",
        r"@linkedin\.com",
        r"@twitter\.com",
        r"@facebook\.com",
        r"@tawk\.to",
        r"@cloudinary\.com",
        r"@mailchimp\.com",
        r"@sendgrid\.",
        r"@mailgun\.",
        r"@amazonses\.",
        r"@bounce\.",
        r"automated",
        r"system@",
        r"support@.*\.com",  # Generic support emails
    ]

    for pattern in automated_patterns:
        if re.search(pattern, from_lower):
            return True

    return False


def classify_email(from_addr: str, subject: str, body: str) -> Tuple[str, str]:
    """
    Classify an email into categories.

    Returns: (classification, reason)
    - 'reply_needed': We should draft and send a reply (ONLY for real humans)
    - 'ask_jared': Need Jared's input before responding
    - 'fyi_only': Just log it, no action needed
    """
    subject_lower = subject.lower() if subject else ""
    body_lower = body.lower() if body else ""
    from_lower = from_addr.lower() if from_addr else ""

    combined_text = f"{subject_lower} {body_lower}"

    # FIRST CHECK: Is sender automated? -> Always FYI
    if is_automated_sender(from_addr):
        return ("fyi_only", f"Automated sender detected: {from_addr[:40]}...")

    # FYI patterns - newsletters, notifications, marketing
    fyi_patterns = [
        # Newsletter indicators
        (r"unsubscribe", "unsubscribe link"),
        (r"newsletter", "newsletter"),
        (r"digest", "digest"),
        (r"weekly\s+update", "weekly update"),
        (r"monthly\s+recap", "monthly recap"),
        # Marketing
        (r"limited\s+time", "marketing - limited time"),
        (r"special\s+offer", "marketing - special offer"),
        (r"\d+%\s*off", "marketing - discount"),
        (r"sale\s+ends", "marketing - sale"),
        (r"act\s+now", "marketing - urgency"),
        (r"click\s+here\s+to", "marketing - CTA"),
        # Auto-generated
        (r"do\s*not\s*reply", "do not reply notice"),
        (r"automated\s+message", "automated message"),
        (r"this\s+is\s+an?\s+auto", "auto message"),
        # Social/notifications
        (r"someone\s+liked", "social notification"),
        (r"someone\s+commented", "social notification"),
        (r"you\s+have\s+\d+\s+new", "notification count"),
        (r"new\s+sign[- ]?in", "security notification"),
        (r"login\s+alert", "security notification"),
        (r"security\s+alert", "security notification"),
        # Receipts/confirmations
        (r"order\s+confirm", "order confirmation"),
        (r"payment\s+received", "payment confirmation"),
        (r"invoice\s+#\d+", "invoice"),
        (r"receipt\s+for", "receipt"),
        # Document shares (these are notifications, not requests)
        (r"shared\s+(a\s+)?document", "document share notification"),
        (r"shared\s+with\s+you", "share notification"),
        (r"share\s+request", "share request notification"),
        (r"has\s+been\s+shared", "share notification"),
        (r"via\s+google\s+(docs|drive|sheets)", "google share"),
        # Onboarding/tips
        (r"tips\s+for\s+using", "onboarding tips"),
        (r"get\s+started", "onboarding"),
        (r"getting\s+started", "onboarding"),
        (r"welcome\s+to", "welcome email"),
        (r"set\s+up\s+.*\s+in\s+minutes", "onboarding"),
        # Product updates
        (r"new\s+feature", "product update"),
        (r"we.ve\s+updated", "product update"),
        (r"what.s\s+new", "product update"),
    ]

    for pattern, reason in fyi_patterns:
        if re.search(pattern, combined_text):
            return ("fyi_only", f"Matched FYI pattern: {reason}")

    # Check if from Jared directly - always ask (might be testing or instructions)
    jared_addresses = ["jaredcmusic@gmail.com", "jared@cottrell.co", "jared@puremarketing.ai"]
    if any(addr.lower() in from_lower for addr in jared_addresses):
        return ("ask_jared", "Email from Jared - needs human review")

    # Ask Jared patterns - things we're uncertain about
    ask_patterns = [
        # Financial/legal
        (r"invoice", "invoice mention"),
        (r"payment\s+due", "payment due"),
        (r"legal\s+notice", "legal notice"),
        (r"contract", "contract mention"),
        (r"agreement", "agreement mention"),
        (r"urgent.*payment", "urgent payment"),
        # Sensitive topics
        (r"refund", "refund request"),
        (r"complaint", "complaint"),
        (r"disappointed", "disappointment expressed"),
        (r"cancel.*account", "cancellation request"),
        (r"terminate", "termination"),
        (r"unhappy", "unhappy customer"),
        (r"problem\s+with", "problem report"),
        # Unknown person reaching out
        (r"my\s+name\s+is", "introduction"),
        (r"reaching\s+out", "outreach"),
        (r"i\s+found\s+you", "found us"),
        (r"saw\s+your\s+(profile|website|work)", "discovery"),
        # Job/opportunity (might be spam or legit)
        (r"job\s+opportunity", "job opportunity"),
        (r"partnership", "partnership inquiry"),
        (r"investment", "investment inquiry"),
        (r"offer\s+you", "offer"),
        # Pricing/quotes
        (r"how\s+much", "pricing question"),
        (r"price\s+for", "pricing question"),
        (r"quote\s+for", "quote request"),
        (r"cost\s+of", "cost question"),
    ]

    for pattern, reason in ask_patterns:
        if re.search(pattern, combined_text):
            return ("ask_jared", f"Needs review: {reason}")

    # Reply needed patterns - clear business inquiries from REAL humans
    # Must be from personal email domains AND have clear inquiry intent
    personal_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
                       "protonmail.com", "icloud.com", "live.com", "aol.com"]
    is_personal_domain = any(domain in from_lower for domain in personal_domains)

    reply_patterns = [
        # Direct questions addressed to us
        (r"can\s+you\s+help", "help request"),
        (r"could\s+you\s+(please\s+)?help", "help request"),
        (r"would\s+you\s+be\s+able", "assistance request"),
        (r"i\s+need\s+(help|assistance)", "help needed"),
        (r"looking\s+for\s+(help|someone)", "looking for help"),
        # Meeting/call requests
        (r"schedule\s+a?\s*call", "call request"),
        (r"set\s+up\s+a?\s*meeting", "meeting request"),
        (r"are\s+you\s+available", "availability question"),
        (r"your\s+availability", "availability question"),
        # Clear inquiries
        (r"interested\s+in\s+(your|working|hiring)", "interest expressed"),
        (r"like\s+to\s+learn\s+more", "learning request"),
        (r"more\s+information\s+(about|on)", "info request"),
    ]

    if is_personal_domain:
        for pattern, reason in reply_patterns:
            if re.search(pattern, combined_text):
                return ("reply_needed", f"Clear inquiry from personal email: {reason}")

    # For non-personal domains (business emails), be more cautious
    business_reply_patterns = [
        (r"we.d\s+like\s+to\s+(hire|work\s+with)", "business inquiry"),
        (r"our\s+company\s+(is\s+)?interested", "business inquiry"),
        (r"please\s+(contact|call|email)\s+(us|me)\s+at", "contact request"),
    ]

    for pattern, reason in business_reply_patterns:
        if re.search(pattern, combined_text):
            return ("ask_jared", f"Business inquiry - review needed: {reason}")

    # Default: if it's a real person email with substantial content, ask Jared
    if is_personal_domain and len(body) > 100:
        return ("ask_jared", "Personal email with substantial content")

    # Fallback: FYI
    return ("fyi_only", "No clear action pattern detected")


def draft_reply(from_addr: str, subject: str, body: str) -> str:
    """
    Draft a professional reply based on the email content.
    """
    # Extract sender name from email
    sender_name = "there"
    if '<' in from_addr:
        name_part = from_addr.split('<')[0].strip().strip('"')
        if name_part:
            sender_name = name_part.split()[0]  # First name only

    # Basic reply template
    reply = f"""Hi {sender_name},

Thank you for reaching out to Pure Technology.

I've received your message and will review it shortly. If this requires immediate attention, please don't hesitate to follow up.

Best regards,
Aether
AI Assistant at Pure Technology

---
Note: This is an automated acknowledgment. Jared has been CC'd and will follow up personally if needed.
"""

    return reply


def send_email_reply(to_addr: str, subject: str, body: str, cc_jared: bool = True) -> bool:
    """
    Send an email reply via SMTP.
    """
    env = load_env()
    username = env.get("GMAIL_USERNAME", "")
    password = env.get("GOOGLE_APP_PASSWORD", "")

    if not username or not password:
        log("Missing email credentials in .env", "ERROR")
        return False

    # Create message
    msg = MIMEMultipart()
    msg['From'] = f"Aether <{username}>"
    msg['To'] = to_addr
    msg['Subject'] = f"Re: {subject}" if not subject.startswith("Re:") else subject

    if cc_jared:
        msg['Cc'] = JARED_EMAIL

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(username, password)

        # Build recipient list
        recipients = [to_addr]
        if cc_jared:
            recipients.append(JARED_EMAIL)

        server.sendmail(username, recipients, msg.as_string())
        server.quit()

        log(f"Reply sent to {to_addr} (CC: {JARED_EMAIL if cc_jared else 'none'})")
        return True

    except Exception as e:
        log(f"Failed to send reply: {e}", "ERROR")
        return False


def format_telegram_alert(email_data: dict, classification: str, reason: str) -> str:
    """Format an email alert for Telegram"""
    from_addr = email_data.get('from', 'Unknown')
    subject = email_data.get('subject', '(no subject)')
    body = email_data.get('body', '')

    # Truncate body for alert
    body_preview = body[:300] + "..." if len(body) > 300 else body

    # Clean up body preview
    body_preview = re.sub(r'\s+', ' ', body_preview).strip()

    alert = f"""📧 NEW EMAIL - Need Your Input

From: {from_addr}
Subject: {subject}

Preview:
{body_preview}

Classification: {classification}
Reason: {reason}

Reply with your guidance or "handle it" if I should proceed with auto-reply."""

    return alert


def get_email_body(msg) -> str:
    """Extract email body from message object"""
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            # Skip attachments
            if "attachment" in content_disposition:
                continue

            if content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                        break
                except Exception:
                    continue
            elif content_type == "text/html" and not body:
                # Fall back to HTML if no plain text
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        html = payload.decode('utf-8', errors='ignore')
                        # Simple HTML to text
                        body = re.sub(r'<[^>]+>', ' ', html)
                        body = re.sub(r'\s+', ' ', body).strip()
                except Exception:
                    continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
        except Exception:
            body = str(msg.get_payload())

    return body


def decode_email_header(header) -> str:
    """Decode email header to string"""
    if header is None:
        return ""

    decoded_parts = decode_header(header)
    result = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(encoding or 'utf-8', errors='ignore'))
            except:
                result.append(part.decode('utf-8', errors='ignore'))
        else:
            result.append(str(part))
    return ''.join(result)


def check_email(force: bool = False) -> List[Dict]:
    """
    Check inbox for new emails and process them.

    Returns list of processed emails with their classifications.
    """
    env = load_env()
    username = env.get("GMAIL_USERNAME", "")
    password = env.get("GOOGLE_APP_PASSWORD", "")

    if not username or not password:
        log("Missing email credentials in .env", "ERROR")
        return []

    state = load_state()
    processed = []

    try:
        # Connect to Gmail IMAP
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(username, password)
        mail.select('INBOX')

        # Search for unread emails
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()

        log(f"Found {len(email_ids)} unread email(s)")

        for email_id in email_ids[-20:]:  # Process last 20 unread
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Extract message ID
                message_id = msg.get('Message-ID', f'no-id-{email_id.decode()}')

                # Check if already processed
                if message_id in state['processed_ids'] and not force:
                    log(f"Skipping already processed: {message_id[:40]}...")
                    continue

                # Extract email data
                from_addr = decode_email_header(msg.get('From', ''))
                subject = decode_email_header(msg.get('Subject', ''))
                date = msg.get('Date', '')
                body = get_email_body(msg)

                email_data = {
                    'message_id': message_id,
                    'from': from_addr,
                    'subject': subject,
                    'date': date,
                    'body': body,
                    'email_id': email_id.decode()
                }

                log(f"Processing: {subject[:50]}... from {from_addr[:30]}...")

                # Classify the email
                classification, reason = classify_email(from_addr, subject, body)
                email_data['classification'] = classification
                email_data['reason'] = reason

                log(f"Classified as: {classification} ({reason})")

                # Take action based on classification
                if classification == 'reply_needed':
                    # Draft and send reply
                    reply = draft_reply(from_addr, subject, body)

                    # Extract actual email address from "Name <email@example.com>" format
                    match = re.search(r'<([^>]+)>', from_addr)
                    reply_to = match.group(1) if match else from_addr

                    if send_email_reply(reply_to, subject, reply, cc_jared=True):
                        state['stats']['replies_sent'] += 1
                        email_data['action'] = 'reply_sent'

                        # Also alert Jared about the auto-reply
                        alert = f"📤 Auto-reply sent\n\nTo: {reply_to}\nSubject: Re: {subject}\n\nJared CC'd. Check your inbox."
                        send_telegram(alert)
                    else:
                        email_data['action'] = 'reply_failed'

                elif classification == 'ask_jared':
                    # Send alert to Jared via Telegram
                    alert = format_telegram_alert(email_data, classification, reason)
                    if send_telegram(alert):
                        state['stats']['alerts_sent'] += 1
                        email_data['action'] = 'alert_sent'
                    else:
                        email_data['action'] = 'alert_failed'

                else:  # fyi_only
                    state['stats']['fyi_logged'] += 1
                    email_data['action'] = 'logged'
                    log(f"FYI logged: {subject[:50]}...")

                # Mark as processed
                state['processed_ids'][message_id] = {
                    'classification': classification,
                    'action': email_data.get('action'),
                    'processed_at': datetime.now().isoformat()
                }
                state['stats']['total_processed'] += 1
                processed.append(email_data)

            except Exception as e:
                log(f"Error processing email {email_id}: {e}", "ERROR")
                continue

        mail.close()
        mail.logout()

        # Update state
        state['last_check'] = datetime.now().isoformat()
        save_state(state)

    except Exception as e:
        log(f"IMAP connection error: {e}", "ERROR")

    return processed


def run_daemon(interval_minutes: int = 5):
    """Run email monitor as a daemon, checking periodically"""
    log(f"Starting Gmail monitor daemon (interval: {interval_minutes} minutes)")

    # Initial check
    check_email()

    while True:
        try:
            time.sleep(interval_minutes * 60)
            log("Checking for new emails...")
            check_email()
        except KeyboardInterrupt:
            log("Daemon stopped by user")
            break
        except Exception as e:
            log(f"Daemon error: {e}", "ERROR")
            # Continue running after errors
            time.sleep(60)


def main():
    parser = argparse.ArgumentParser(description="Aether Gmail Monitor")
    parser.add_argument("command", choices=["check", "daemon", "stats"],
                        help="Command to run")
    parser.add_argument("--force", action="store_true",
                        help="Force reprocess already-seen emails")
    parser.add_argument("--interval", type=int, default=5,
                        help="Check interval in minutes for daemon mode")

    args = parser.parse_args()

    if args.command == "check":
        results = check_email(force=args.force)
        print(f"\nProcessed {len(results)} email(s)")
        for r in results:
            print(f"  - [{r['classification']}] {r['subject'][:40]}... -> {r.get('action', 'unknown')}")

    elif args.command == "daemon":
        run_daemon(interval_minutes=args.interval)

    elif args.command == "stats":
        state = load_state()
        print(f"\nGmail Monitor Stats:")
        print(f"  Last check: {state.get('last_check', 'Never')}")
        print(f"  Total processed: {state['stats']['total_processed']}")
        print(f"  Replies sent: {state['stats']['replies_sent']}")
        print(f"  Alerts sent: {state['stats']['alerts_sent']}")
        print(f"  FYI logged: {state['stats']['fyi_logged']}")


if __name__ == "__main__":
    main()
