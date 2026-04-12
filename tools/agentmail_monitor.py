#!/usr/bin/env python3
"""
AgentMail Monitor - Persistent inbox monitoring for aether-aiciv@agentmail.to

Polls agentmail.to inbox every 30 seconds.
On new messages:
  - Injects notification into active tmux pane (Primary AI sees it immediately)
  - Sends alert to Telegram
  - Saves state to prevent re-processing
  - MAGIC LINK handler: watches for "MAGIC LINK" emails from Witness,
    stores link by session UUID, sends welcome email to customer, notifies Jared

State file: memories/agents/email-monitor/agentmail_state.json
Magic links: .magic-links.json (persistent, keyed by session UUID)

Usage:
  python3 tools/agentmail_monitor.py

Background:
  nohup python3 tools/agentmail_monitor.py >> logs/agentmail_monitor.log 2>&1 &

Author: human-liaison / dept-systems-technology
Date: 2026-03-13
Updated: 2026-03-13 (Magic Link pipeline: watch Witness emails, store by UUID, send welcome email)
"""

import json
import os
import re
import smtplib
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.parse
import urllib.error
import logging
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# ─── Config ─────────────────────────────────────────────────────────────────

CIV_ROOT = Path("/home/jared/projects/AI-CIV/aether")
STATE_FILE = CIV_ROOT / "memories/agents/email-monitor/agentmail_state.json"
LOG_FILE = CIV_ROOT / "logs/agentmail_monitor.log"
TG_SEND = CIV_ROOT / "tools/tg_send.sh"
POLL_INTERVAL = 30  # seconds

# Magic links store — persistent JSON, keyed by session UUID
MAGIC_LINKS_FILE = CIV_ROOT / ".magic-links.json"
_magic_links_lock = threading.Lock()

# Email template path -- prefer the newer welcome-email-template.html if present,
# fall back to magic-link-email-template.html for backwards compatibility
_WELCOME_TEMPLATE_PRIMARY  = Path("/tmp/welcome-email-template.html")
_WELCOME_TEMPLATE_FALLBACK = Path("/tmp/magic-link-email-template.html")
MAGIC_LINK_EMAIL_TEMPLATE = _WELCOME_TEMPLATE_PRIMARY if _WELCOME_TEMPLATE_PRIMARY.exists() else _WELCOME_TEMPLATE_FALLBACK

# Load credentials from .env
def load_env():
    env = {}
    env_path = CIV_ROOT / ".env"
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

ENV = load_env()
API_KEY = ENV.get("AGENTMAIL_API_KEY", "")
INBOX = ENV.get("AGENTMAIL_INBOX", "aether-aiciv@agentmail.to")

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [agentmail-monitor] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE),
    ]
)
log = logging.getLogger(__name__)

# ─── Magic Links Store ───────────────────────────────────────────────────────

def load_magic_links() -> dict:
    """Load the persistent magic links store."""
    with _magic_links_lock:
        if MAGIC_LINKS_FILE.exists():
            try:
                with open(MAGIC_LINKS_FILE) as f:
                    return json.load(f)
            except Exception as e:
                log.warning(f"Magic links file corrupted, starting fresh: {e}")
        return {}


def save_magic_links(links: dict):
    """Atomically write the magic links store."""
    with _magic_links_lock:
        tmp = MAGIC_LINKS_FILE.with_suffix(".tmp")
        with open(tmp, "w") as f:
            json.dump(links, f, indent=2)
        tmp.replace(MAGIC_LINKS_FILE)


def store_magic_link(uuid: str, entry: dict):
    """Store a magic link entry keyed by session UUID AND by email (fallback)."""
    links = load_magic_links()
    links[uuid] = entry
    # 2026-03-26 FIX: Also store by email for fallback lookup.
    # The page polls /api/magic-link/{uuid}?email=xxx — if UUID lookup fails
    # (due to UUID mismatch), the email fallback catches it.
    human_email = (entry.get('human_email') or '').strip().lower()
    if human_email:
        email_key = f"email:{human_email}"
        links[email_key] = entry
        log.info(f"Magic link also stored for email key={email_key}")
    save_magic_links(links)
    log.info(f"Magic link stored for UUID={uuid}: {entry.get('magic_link', '')}")


# ─── State Management ────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception as e:
            log.warning(f"State file corrupted, starting fresh: {e}")
    return {
        "seen_ids": [],
        "processed_count": 0,
        "last_check": None,
        "daemon_started": datetime.now(timezone.utc).isoformat(),
    }


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    tmp.replace(STATE_FILE)


# ─── AgentMail API ──────────────────────────────────────────────────────────

def api_get(path: str) -> dict:
    url = f"https://api.agentmail.to/v0{path}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def api_patch(path: str, body: dict) -> dict:
    url = f"https://api.agentmail.to/v0{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="PATCH",
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


def send_message(to: str, subject: str, text: str, reply_to: str = None) -> dict:
    """Send an email via AgentMail."""
    url = f"https://api.agentmail.to/v0/inboxes/{INBOX}/messages"
    body = {"to": [to], "subject": subject, "text": text}
    if reply_to:
        body["in_reply_to"] = reply_to
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


# ─── Notification Delivery ──────────────────────────────────────────────────

def get_active_tmux_pane() -> str:
    """Get the pane ID of the active Claude Code pane."""
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
    """Inject a message notification into the active tmux pane."""
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
    """Send message to Jared via Telegram."""
    try:
        result = subprocess.run(
            [str(TG_SEND), message],
            capture_output=True, text=True, timeout=15,
            cwd=str(CIV_ROOT)
        )
        if result.returncode == 0:
            log.info("Telegram alert sent")
        else:
            log.warning(f"tg_send.sh failed: {result.stderr}")
    except Exception as e:
        log.warning(f"Telegram send failed: {e}")


# ─── Message Classification ─────────────────────────────────────────────────

def classify_sender(sender: str) -> str:
    """Classify the type of sender for routing decisions."""
    s = sender.lower()
    if "witness-aiciv" in s or "witness" in s:
        return "sister_civ_witness"
    if "acg-aiciv" in s or "acg" in s:
        return "sister_civ_acg"
    if "true-bearing" in s:
        return "partner_civ_true_bearing"
    if "parallax" in s:
        return "sister_civ_parallax"
    if "keel" in s:
        return "partner_civ_keel"
    if "jared" in s or "puretechnology" in s or "puremarketing" in s:
        return "human_jared"
    if "agentmail.to" in s:
        return "ai_collective_unknown"
    return "external_unknown"


def format_notification(msg: dict, full_body: str) -> str:
    """Format a message as a tmux-injectable notification."""
    sender = msg.get("from", "unknown")
    subject = msg.get("subject", "(no subject)")
    preview = full_body[:200] if full_body else msg.get("preview", "")[:200]
    classification = classify_sender(sender)

    return (
        f"\n[AGENTMAIL NEW MESSAGE] "
        f"from:{sender} | subject:{subject} | "
        f"type:{classification} | "
        f"preview:{preview}"
    )


def format_telegram_alert(msg: dict, full_body: str) -> str:
    """Format a Telegram alert for Jared."""
    sender = msg.get("from", "unknown")
    subject = msg.get("subject", "(no subject)")
    body = full_body[:500] if full_body else msg.get("preview", "")[:500]
    classification = classify_sender(sender)

    lines = [
        f"AgentMail: New message ({classification})",
        f"From: {sender}",
        f"Subject: {subject}",
        f"",
        body,
    ]
    if len(body) >= 500:
        lines.append("... (truncated)")
    return "\n".join(lines)


# ─── Magic Link Parser ───────────────────────────────────────────────────────

# Expected email format from Witness:
#   Subject: MAGIC LINK — [AI Name] for [Human Name]
#   Body:
#     AI Name: Aria
#     Human Name: Lucas Neuteufel
#     Email: lucas@example.com
#     UUID: 4d1a1ede-f188-4458-b816-d7781c1d649e
#     Container: aria-lucas-abc123
#     Magic Link: https://aria-lucas.ai-civ.com/portal?token=...

def is_magic_link_email(msg: dict) -> bool:
    """Return True if this email is a Witness magic link notification."""
    subject = (msg.get("subject") or "").upper()
    sender = (msg.get("from") or "").lower()
    return "MAGIC LINK" in subject and (
        "witness" in sender or "agentmail.to" in sender
    )


def parse_magic_link_body(body: str) -> dict:
    """
    Parse structured fields from a Witness magic link email body.
    Returns dict with: ai_name, human_name, human_email, uuid,
    container, magic_link (original), magic_link_pb (.app.purebrain.ai).
    Returns empty dict if parsing fails completely.
    """
    if not body:
        return {}

    result = {}

    patterns = {
        "ai_name":     r"(?:AI Name|CIV Name|AiCIV Name)\s*[:=]\s*(.+)",
        "human_name":  r"Human Name\s*[:=]\s*(.+)",
        "human_email": r"Email\s*[:=]\s*([^\s@]+@[^\s@]+\.[^\s@]+)",
        "uuid":        r"UUID\s*[:=]\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        "container":   r"Container\s*[:=]\s*([^\s]+)",
        "magic_link":  r"Magic Link\s*[:=]\s*(https?://\S+)",
    }

    for key, pattern in patterns.items():
        m = re.search(pattern, body, re.IGNORECASE | re.MULTILINE)
        if m:
            result[key] = m.group(1).strip()

    # Fallback: scan for any bare https:// URL on .ai-civ.com domain
    if "magic_link" not in result:
        url_match = re.search(r"(https://[^\s]+\.ai-civ\.com[^\s]*)", body)
        if url_match:
            result["magic_link"] = url_match.group(1).strip()

    # Rewrite magic link domain: .ai-civ.com -> .app.purebrain.ai
    if "magic_link" in result:
        raw_link = result["magic_link"]
        rewritten = re.sub(
            r"(https?://)([^./]+)\.ai-civ\.com",
            r"\1\2.app.purebrain.ai",
            raw_link
        )
        result["magic_link_pb"] = rewritten
        log.info(f"Magic link rewritten: {raw_link} -> {rewritten}")

    return result


def _get_fallback_email_html(human_first: str, ai_name: str, magic_link: str) -> str:
    """Generate inline HTML email when template file is missing."""
    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Your PureBrain AI is Ready</title>"
        "<style>*{margin:0;padding:0;box-sizing:border-box}"
        "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;"
        "background:#080a12;color:#e0e0e0;line-height:1.6}"
        ".w{max-width:600px;margin:0 auto;padding:32px 16px}"
        "h1{font-size:28px;font-weight:700;color:#fff;margin:24px 0 12px}"
        ".ai{color:#f1420b}"
        ".btn{display:inline-block;background:linear-gradient(135deg,#2a93c1,#1d6e99);"
        "color:#fff;font-size:16px;font-weight:700;text-decoration:none;"
        "padding:16px 40px;border-radius:8px;margin:24px 0}"
        ".ft{font-size:13px;color:#6b7280;margin-top:32px;border-top:1px solid #1a1d2e;padding-top:16px}"
        ".ft a{color:#2a93c1;text-decoration:none}</style></head>"
        f"<body><div class='w'>"
        f"<h1>Welcome, {human_first}.<br><span class='ai'>{ai_name}</span> is ready.</h1>"
        f"<p>Your personal AI has been built and is waiting. Tap below to enter.</p>"
        f"<a href='{magic_link}' class='btn'>Enter {ai_name}'s Brain Stream &rarr;</a>"
        f"<p style='font-size:13px;color:#6b7280;'>This link is personal to you.</p>"
        f"<div class='ft'><a href='https://purebrain.ai'>purebrain.ai</a>"
        f" | <a href='mailto:support@puremarketing.ai'>support@puremarketing.ai</a></div>"
        f"</div></body></html>"
    )


def send_welcome_email(human_email: str, human_first: str, ai_name: str, magic_link: str):
    """
    Send the welcome email to the customer via Google SMTP (purebrain@puremarketing.ai).
    Uses approved template at /tmp/magic-link-email-template.html with placeholder replacement.
    Falls back to inline HTML if template file is missing.
    """
    if not human_email or "@" not in human_email:
        log.warning(f"Cannot send welcome email: invalid address '{human_email}'")
        return

    # Load and render template
    if MAGIC_LINK_EMAIL_TEMPLATE.exists():
        html = MAGIC_LINK_EMAIL_TEMPLATE.read_text(encoding="utf-8")
        html = html.replace("{{HUMAN_FIRST_NAME}}", human_first)
        html = html.replace("{{CIV_NAME}}", ai_name)
        html = html.replace("{{MAGIC_LINK}}", magic_link)
    else:
        log.warning("Magic link email template not found at /tmp — using fallback HTML")
        html = _get_fallback_email_html(human_first, ai_name, magic_link)

    subject = f"Your AI {ai_name} is Ready — Enter Your Brain Stream"
    smtp_user = ENV.get("SMTP_USER", "purebrain@puremarketing.ai")
    smtp_pass = ENV.get("GOOGLE_APP_PASSWORD", ENV.get("SMTP_PASS", ""))

    if not smtp_pass:
        log.error("No GOOGLE_APP_PASSWORD in .env — cannot send welcome email")
        return

    try:
        msg_obj = MIMEMultipart("alternative")
        msg_obj["Subject"] = subject
        msg_obj["From"] = f"Aether | PureBrain <{smtp_user}>"
        msg_obj["To"] = human_email
        msg_obj["Bcc"] = "jared@puretechnology.nyc"
        msg_obj["Reply-To"] = "support@puremarketing.ai"

        plain = (
            f"Hi {human_first},\n\n{ai_name} is ready for you.\n\n"
            f"Enter your Brain Stream: {magic_link}\n\n"
            f"This link is personal to you — do not share it.\n\n"
            f"— Aether, Pure Technology\npurebrain.ai"
        )
        msg_obj.attach(MIMEText(plain, "plain"))
        msg_obj.attach(MIMEText(html, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [human_email, "jared@puretechnology.nyc"], msg_obj.as_string())

        log.info(f"Welcome email sent to {human_email} (AI={ai_name})")

    except Exception as e:
        log.error(f"Failed to send welcome email to {human_email}: {e}")


def handle_magic_link_email(msg: dict, full_body: str):
    """
    Full pipeline for a Witness MAGIC LINK email:
    1. Parse all fields from email body
    2. Rewrite domain .ai-civ.com -> .app.purebrain.ai
    3. Store in .magic-links.json keyed by session UUID
    4. Send welcome email to customer
    5. Notify Jared on Telegram
    """
    log.info(f"MAGIC LINK email detected: subject='{msg.get('subject')}'")

    parsed = parse_magic_link_body(full_body)

    if not parsed:
        log.error("Failed to parse any fields from magic link email body")
        send_telegram(
            f"MAGIC LINK email from Witness — PARSE FAILED\n"
            f"Subject: {msg.get('subject')}\n"
            f"Preview: {full_body[:400]}"
        )
        return

    uuid_val = parsed.get("uuid", "")
    ai_name = parsed.get("ai_name", "Your AI")
    human_name = parsed.get("human_name", "")
    human_email = parsed.get("human_email", "")
    container = parsed.get("container", "")
    magic_link_raw = parsed.get("magic_link", "")
    magic_link_pb = parsed.get("magic_link_pb", magic_link_raw)

    human_first = human_name.split()[0] if human_name else "there"

    if not uuid_val:
        log.warning("No UUID in magic link email — using email-based fallback key")
        uuid_val = f"email:{human_email}" if human_email else f"ts:{int(datetime.now().timestamp())}"

    # Store in .magic-links.json
    entry = {
        "status": "ready",
        "uuid": uuid_val,
        "ai_name": ai_name,
        "human_name": human_name,
        "human_email": human_email,
        "container": container,
        "magic_link": magic_link_pb,
        "original_magic_link": magic_link_raw,
        "received_at": datetime.now(timezone.utc).isoformat(),
    }
    store_magic_link(uuid_val, entry)

    # 2026-03-28: Dual-email welcome logic.
    # Look up the PayPal payer email (Email A) stored by purebrain_log_server at payment time.
    # If it differs from the chatbox email (Email B = human_email), send welcome to BOTH.
    paypal_email = ""
    _payer_emails_file = CIV_ROOT / "logs" / "payer_emails_by_uuid.json"
    try:
        if _payer_emails_file.exists():
            with open(_payer_emails_file) as _pef:
                _payer_lookup = json.load(_pef)
            _payer_entry = _payer_lookup.get(uuid_val, {})
            paypal_email = (_payer_entry.get("paypal_email") or "").strip()
    except Exception as _pe_err:
        log.warning(f"Failed to look up PayPal email for UUID={uuid_val}: {_pe_err}")

    # Determine which addresses to send the welcome email to
    emails_to_send = set()

    # ── Sandbox email bypass ─────────────────────────────────────────────
    # When the chatbox email or PayPal email is a sandbox address
    # (sb-*@*.example.com), redirect the welcome email to Jared so he can
    # verify the full E2E flow.  The original sandbox address is logged but
    # never mailed (it would bounce anyway).
    _SANDBOX_REDIRECT = "jared@puretechnology.nyc"
    _sandbox_redirected = False

    def _is_sandbox_email(addr: str) -> bool:
        if not addr:
            return False
        a = addr.lower().strip()
        return (
            a.startswith("sb-")
            or a.endswith("@personal.example.com")
            or a.endswith("@business.example.com")
            or "example.com" in a
            or a == "(sandbox-sub)"
        )

    if human_email and "@" in human_email:
        if _is_sandbox_email(human_email):
            log.info(f"[SANDBOX BYPASS] Redirecting welcome email from {human_email} to {_SANDBOX_REDIRECT}")
            emails_to_send.add(_SANDBOX_REDIRECT)
            _sandbox_redirected = True
        else:
            emails_to_send.add(human_email.lower().strip())

    if paypal_email and "@" in paypal_email:
        _pp_lower = paypal_email.lower().strip()
        if _is_sandbox_email(_pp_lower):
            # Already redirected above (or will be); don't add sandbox addr
            if not _sandbox_redirected:
                log.info(f"[SANDBOX BYPASS] Redirecting welcome email from PayPal {paypal_email} to {_SANDBOX_REDIRECT}")
                emails_to_send.add(_SANDBOX_REDIRECT)
                _sandbox_redirected = True
        elif _pp_lower != "(sandbox-sub)":
            emails_to_send.add(_pp_lower)

    # If sandbox redirect happened, also store magic link under Jared's email
    # so the thank-you page poller can find it via email fallback.
    if _sandbox_redirected:
        _jared_key = f"email:{_SANDBOX_REDIRECT}"
        store_magic_link(_jared_key, entry)
        log.info(f"[SANDBOX BYPASS] Magic link also stored under {_jared_key} for poller fallback")

    if emails_to_send:
        for _addr in emails_to_send:
            _first = human_first  # Use same first name for both
            send_welcome_email(_addr, _first, ai_name, magic_link_pb)
        _dual = len(emails_to_send) > 1
        log.info(
            f"Welcome email sent to {len(emails_to_send)} address(es): {emails_to_send}"
            + (" (dual-email: PayPal + chatbox differ)" if _dual else "")
        )
    else:
        log.warning(f"No valid email addresses for welcome email (UUID={uuid_val})")

    # Notify Jared
    _email_summary = f"{human_email}"
    if paypal_email and paypal_email.lower().strip() != (human_email or "").lower().strip():
        _email_summary += f" + PayPal: {paypal_email}"
    send_telegram(
        f"MAGIC LINK received from Witness\n"
        f"AI: {ai_name}\n"
        f"Human: {human_name} ({_email_summary})\n"
        f"UUID: {uuid_val}\n"
        f"Container: {container}\n"
        f"Link: {magic_link_pb}\n"
        f"Welcome email: {len(emails_to_send)} address(es)"
    )
    log.info(f"Magic link pipeline complete for UUID={uuid_val}")


# ─── Main Loop ──────────────────────────────────────────────────────────────

def process_new_messages(state: dict) -> int:
    """Check for new messages and process them. Returns count of new messages."""
    seen_ids = set(state.get("seen_ids", []))
    new_count = 0

    try:
        messages = list_messages(limit=50)
    except Exception as e:
        log.error(f"Failed to list messages: {e}")
        return 0

    for msg in messages:
        msg_id = msg.get("message_id", "")
        if not msg_id or msg_id in seen_ids:
            continue

        # Skip our own outbound messages
        labels = msg.get("labels", [])
        if "sent" in labels and "received" not in labels:
            seen_ids.add(msg_id)
            continue

        # Skip outbound by checking from address
        sender = msg.get("from", "")
        if INBOX in sender:
            seen_ids.add(msg_id)
            continue

        # New incoming message - fetch full body
        log.info(f"New message: {msg.get('subject', '?')} from {sender}")

        try:
            full_msg = get_message(msg_id)
            full_body = full_msg.get("text") or full_msg.get("extracted_text") or msg.get("preview", "")
        except Exception as e:
            log.warning(f"Could not fetch full message body: {e}")
            full_body = msg.get("preview", "")

        # ── Priority: Magic Link handler ──────────────────────────────────
        if is_magic_link_email(msg):
            try:
                handle_magic_link_email(msg, full_body)
            except Exception as e:
                log.error(f"Magic link handler error: {e}")
                send_telegram(f"MAGIC LINK handler error: {e}\nSubject: {msg.get('subject')}")
        else:
            # Generic notification path
            inject_to_tmux(format_notification(msg, full_body))
            send_telegram(format_telegram_alert(msg, full_body))

        seen_ids.add(msg_id)
        new_count += 1

        if new_count > 1:
            time.sleep(1)

    state["seen_ids"] = list(seen_ids)
    state["processed_count"] = state.get("processed_count", 0) + new_count
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    return new_count


def seed_seen_ids(state: dict):
    """On first run, seed seen_ids with existing messages so we don't replay history."""
    log.info("Seeding seen IDs from existing inbox (first run)...")
    try:
        messages = list_messages(limit=100)
        seen = set(state.get("seen_ids", []))
        for msg in messages:
            seen.add(msg.get("message_id", ""))
        state["seen_ids"] = list(seen)
        state["seeded_at"] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        log.info(f"Seeded {len(seen)} existing message IDs")
    except Exception as e:
        log.error(f"Seeding failed: {e}")


def run():
    log.info(f"AgentMail Monitor starting | inbox={INBOX} | poll_interval={POLL_INTERVAL}s")

    state = load_state()

    is_fresh = len(state.get("seen_ids", [])) == 0
    seed_mode = "--process-existing" not in sys.argv

    if is_fresh and seed_mode:
        log.info("Fresh start — seeding existing messages")
        seed_seen_ids(state)
        send_telegram(f"AgentMail monitor started. Inbox: {INBOX}. Watching for new messages every {POLL_INTERVAL}s. Magic Link pipeline active.")
    elif is_fresh:
        log.info("Fresh start with --process-existing flag")
        send_telegram(f"AgentMail monitor started (process-existing mode). Magic Link pipeline active.")
    else:
        log.info(f"Resuming — {len(state.get('seen_ids', []))} IDs already tracked")

    log.info("Entering poll loop...")

    while True:
        try:
            new = process_new_messages(state)
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
