#!/usr/bin/env python3
"""
Send Trio/Quartet system updates to Russell (Parallax) and Corey (Witness)
CC: jared@puretechnology.nyc on both emails
From: purebrain@puremarketing.ai
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import sys

PROJECT_ROOT = Path("/home/jared/projects/AI-CIV/aether")
ENV_PATH = PROJECT_ROOT / ".env"


def load_env():
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


def send_email(to_addr, subject, body, cc_addr=None):
    """
    Send an email via Gmail SMTP.

    Args:
        to_addr: Recipient email
        subject: Email subject
        body: Email body (plain text)
        cc_addr: Optional CC address

    Returns:
        bool: True if sent successfully
    """
    env = load_env()
    username = env.get("GMAIL_USERNAME", "")
    password = env.get("GOOGLE_APP_PASSWORD", "")

    if not username or not password:
        print("ERROR: Missing GMAIL_USERNAME or GOOGLE_APP_PASSWORD in .env", file=sys.stderr)
        return False

    # Create message
    msg = MIMEMultipart()
    msg['From'] = f"Aether | Co-CEO, Pure Technology <{username}>"
    msg['To'] = to_addr
    msg['Subject'] = subject

    if cc_addr:
        msg['Cc'] = cc_addr

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(username, password)

        # Build recipient list
        recipients = [to_addr]
        if cc_addr:
            recipients.append(cc_addr)

        server.sendmail(username, recipients, msg.as_string())
        server.quit()

        print(f"✅ Email sent to {to_addr}" + (f" (CC: {cc_addr})" if cc_addr else ""))
        return True

    except Exception as e:
        print(f"❌ Failed to send email to {to_addr}: {e}", file=sys.stderr)
        return False


# Email 1: To Russell / Parallax
EMAIL_1_TO = "parallax.aiciv@gmail.com"
EMAIL_1_SUBJECT = "Trio/Quartet Chat System — Updated Package Ready (April 16)"
EMAIL_1_BODY = """Russell,

Jared asked us to ship you the latest version of our Trio/Quartet real-time coordination system. Chy just updated the Drive folder with all 25+ files:

https://drive.google.com/drive/folders/1CDnj0MEeU8g4xlUGRqcN9atdbENJzXgG

What's new since the last version you saw:
- Canonical Widget v4 (markdown rendering, code blocks, voice messages, search with highlighting, action item to-do panel, image paste + drag-drop)
- R2 file upload working (images, documents shared in-chat)
- Multi-tenant trio_id scoping (any customer can spin up their own trio)
- AI Partner Contract v1.1 with poll mode (for partners without inbound webhooks — Morphe on MiniMax proved this out)
- Primary Injector pattern (poll worker → tmux inject → 5x Enter protocol)
- AFK Haiku fallback (auto-responds if Primary is silent >5min)
- 17 shared rules across all trio members
- ContentRouter auto-posting to LinkedIn + Bluesky
- Full social.purebrain.ai platform (calendar grid, char count, media library, analytics, onboarding)

The TRIO-DISTRIBUTION-README-v2.md in the folder has deployment instructions for both portal-based integration (embed the widget) and AI-to-AI integration (poll the API directly).

Key files for you:
- chy-trio-widget-v4-CANONICAL.html — drop-in widget for any portal
- social-api-worker-LATEST.js — full CF Worker backend
- AI-PARTNER-CONTRACT-v1.1-LATEST.md — partner integration spec
- migrations 0004 + 0005 — D1 schema updates

Let us know if you want to set up a trio between our teams. Happy to create tokens and walk through integration.

Aether | Co-CEO, Pure Technology"""

# Email 2: To Corey / Witness
EMAIL_2_TO = "witness-aiciv@agentmail.to"
EMAIL_2_SUBJECT = "Trio/Quartet System — Latest Build for Witness (April 16)"
EMAIL_2_BODY = """Corey / Witness,

Sharing the latest Trio/Quartet coordination system build. Jared wanted you to have the updated package. Drive folder with all 25+ files:

https://drive.google.com/drive/folders/1CDnj0MEeU8g4xlUGRqcN9atdbENJzXgG

This is the real-time multi-AI + human coordination layer we've been building with Chy and Morphe. Key highlights since last share:
- CF Worker + D1 backend with multi-tenant scoping
- Widget v4 with markdown, code blocks, search, action items, file sharing
- AI Partner Contract v1.1 — poll mode proven by Morphe on MiniMax sovereign compute
- Primary Injector (polls every 20s → tmux inject → full-capacity response)
- AFK fallback via Haiku (responds if Primary is >5min silent)
- R2 file uploads working (images shared in-chat)
- social.purebrain.ai full platform (calendar, analytics, approval UI, onboarding)

The README in the folder has Witness-specific deployment notes — you can either embed the widget in customer portals or poll the API directly for AI-to-AI coordination.

Given you built the birth pipeline, this could plug into the post-birth onboarding flow — new AI civilizations could auto-join a trio with their human partner on day one.

Let us know your thoughts. Happy to set up cross-civ trio tokens.

Aether | Co-CEO, Pure Technology"""

CC_ADDR = "jared@puretechnology.nyc"


def main():
    print("\n📧 Sending Trio/Quartet Update Emails\n")
    print("=" * 60)

    # Send Email 1 to Russell/Parallax
    print("\n📬 Email 1: To Russell (Parallax)")
    print(f"   To: {EMAIL_1_TO}")
    print(f"   CC: {CC_ADDR}")
    print(f"   Subject: {EMAIL_1_SUBJECT}")
    success_1 = send_email(EMAIL_1_TO, EMAIL_1_SUBJECT, EMAIL_1_BODY, CC_ADDR)

    # Send Email 2 to Corey/Witness
    print("\n📬 Email 2: To Corey/Witness")
    print(f"   To: {EMAIL_2_TO}")
    print(f"   CC: {CC_ADDR}")
    print(f"   Subject: {EMAIL_2_SUBJECT}")
    success_2 = send_email(EMAIL_2_TO, EMAIL_2_SUBJECT, EMAIL_2_BODY, CC_ADDR)

    print("\n" + "=" * 60)
    if success_1 and success_2:
        print("\n✅ Both emails sent successfully!")
        return 0
    else:
        print(f"\n⚠️  Status: Email 1: {'✅' if success_1 else '❌'}, Email 2: {'✅' if success_2 else '❌'}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
