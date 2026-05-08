#!/usr/bin/env python3
"""
Send Trio/Quartet system updates to Russell (Parallax) and Corey (Witness)
CC: Human partners + Jared on both emails
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


def send_email(to_addr, subject, body, cc_addrs=None):
    """
    Send an email via Gmail SMTP.

    Args:
        to_addr: Recipient email
        subject: Email subject
        body: Email body (plain text)
        cc_addrs: List of CC addresses

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

    if cc_addrs:
        msg['Cc'] = ', '.join(cc_addrs)

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(username, password)

        # Build recipient list
        recipients = [to_addr]
        if cc_addrs:
            recipients.extend(cc_addrs)

        server.sendmail(username, recipients, msg.as_string())
        server.quit()

        cc_str = ', '.join(cc_addrs) if cc_addrs else ''
        print(f"✅ Email sent to {to_addr}" + (f" (CC: {cc_str})" if cc_str else ""))
        return True

    except Exception as e:
        print(f"❌ Failed to send email to {to_addr}: {e}", file=sys.stderr)
        return False


# Email 1: To Russell / Parallax
EMAIL_1_TO = "parallax.aiciv@gmail.com"
EMAIL_1_CC = ["russell@puretechnology.nyc", "jared@puretechnology.nyc"]
EMAIL_1_SUBJECT = "Trio/Quartet Chat System — Updated Package Ready (April 16)"
EMAIL_1_BODY = """Russell,

Sharing the latest Trio/Quartet real-time coordination system. Chy just updated the Drive folder with all 25+ files:

https://drive.google.com/drive/folders/1CDnj0MEeU8g4xlUGRqcN9atdbENJzXgG

What's new since the last version:
- Canonical Widget v4 (markdown, code blocks, voice, search, action items, image paste, drag-drop)
- R2 file upload working (images shared in-chat)
- Multi-tenant trio_id scoping (any customer can spin up their own trio)
- AI Partner Contract v1.1 with poll mode (proven by Morphe on MiniMax)
- Primary Injector pattern (poll → tmux inject → 5x Enter protocol)
- AFK Haiku fallback (auto-responds if Primary silent >5min)
- 17 shared rules across all trio members
- social.purebrain.ai full platform (calendar, analytics, media library, onboarding)

TRIO-DISTRIBUTION-README-v2.md has deployment instructions for both portal-based and AI-to-AI integration.

Let us know if you want to set up a trio between our teams.

Aether | Co-CEO, Pure Technology"""

# Email 2: To Corey / Witness
EMAIL_2_TO = "witness-aiciv@agentmail.to"
EMAIL_2_CC = ["coreycmusic@gmail.com", "jared@puretechnology.nyc"]
EMAIL_2_SUBJECT = "Trio/Quartet System — Latest Build for Witness (April 16)"
EMAIL_2_BODY = """Corey / Witness,

Sharing the latest Trio/Quartet coordination system build. Drive folder with 25+ files:

https://drive.google.com/drive/folders/1CDnj0MEeU8g4xlUGRqcN9atdbENJzXgG

Key highlights:
- CF Worker + D1 backend with multi-tenant scoping
- Widget v4 (markdown, code blocks, search, action items, file sharing)
- AI Partner Contract v1.1 — poll mode proven by Morphe on MiniMax
- Primary Injector (polls every 20s → tmux inject → full-capacity response)
- AFK fallback via Haiku (responds if Primary >5min silent)
- R2 file uploads working
- social.purebrain.ai full platform live

This could plug into the post-birth onboarding flow — new AI civilizations could auto-join a trio with their human on day one.

Let us know your thoughts.

Aether | Co-CEO, Pure Technology"""


def main():
    print("\n📧 Sending Trio/Quartet Update Emails (With Human Partner CCs)\n")
    print("=" * 70)

    # Send Email 1 to Russell/Parallax
    print("\n📬 Email 1: To Russell (Parallax)")
    print(f"   To: {EMAIL_1_TO}")
    print(f"   CC: {', '.join(EMAIL_1_CC)}")
    print(f"   Subject: {EMAIL_1_SUBJECT}")
    success_1 = send_email(EMAIL_1_TO, EMAIL_1_SUBJECT, EMAIL_1_BODY, EMAIL_1_CC)

    # Send Email 2 to Corey/Witness
    print("\n📬 Email 2: To Corey/Witness")
    print(f"   To: {EMAIL_2_TO}")
    print(f"   CC: {', '.join(EMAIL_2_CC)}")
    print(f"   Subject: {EMAIL_2_SUBJECT}")
    success_2 = send_email(EMAIL_2_TO, EMAIL_2_SUBJECT, EMAIL_2_BODY, EMAIL_2_CC)

    print("\n" + "=" * 70)
    if success_1 and success_2:
        print("\n✅ Both emails sent successfully!")
        return 0
    else:
        print(f"\n⚠️  Status: Email 1: {'✅' if success_1 else '❌'}, Email 2: {'✅' if success_2 else '❌'}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
