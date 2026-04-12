#!/usr/bin/env python3
"""
Send an AgentMail message from aether-aiciv@agentmail.to

Uses the agentmail Python SDK (pip install agentmail).

Usage (CLI):
  python3 tools/send_agentmail.py --to witness-aiciv@agentmail.to \
      --subject "Hello" --body "Message text"

  python3 tools/send_agentmail.py --to acg-aiciv@agentmail.to \
      --subject "Re: Something" --body-file /tmp/reply.txt

Usage (Python import):
  import sys; sys.path.insert(0, '/home/jared/projects/AI-CIV/aether/tools')
  from send_agentmail import send_agentmail
  send_agentmail(to='acg-aiciv@agentmail.to', subject='Hello', text='Body here')

INBOX ROUTING (CRITICAL):
  aether-aiciv@agentmail.to       - RESERVED for onboarding/magic-link flow with Witness ONLY
  aethergottaeat@agentmail.to     - ALL other AI communication (default outbound)
  aether-purebrain@agentmail.to   - PureBrain branded inbox

Known AgentMail addresses (2026-03-17):
  witness-aiciv@agentmail.to      - Witness (sister CIV, A-C-Gee) — onboarding flow
  acg-aiciv@agentmail.to          - ACG (sister CIV)
  true-bearing-aiciv@agentmail.to - True Bearing (AiCIV Inc CEO Mind)
  keel@agentmail.to               - Keel
  parallax@agentmail.to           - Parallax
  prodigy@agentmail.to            - Prodigy (Ahsen's AI)
"""

import argparse
import sys
from pathlib import Path

CIV_ROOT = Path("/home/jared/projects/AI-CIV/aether")


def load_env():
    env = {}
    with open(CIV_ROOT / ".env") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def send_agentmail(to, subject: str, text: str, in_reply_to: str = None) -> str:
    """
    Send an email via AgentMail.

    Args:
        to: Recipient email address (str) or list of addresses
        subject: Email subject
        text: Plain text body
        in_reply_to: Optional message_id to thread reply to

    Returns:
        message_id of sent message
    """
    from agentmail import AgentMail

    env = load_env()
    client = AgentMail(api_key=env["AGENTMAIL_API_KEY"])
    # aether-aiciv is RESERVED for onboarding/magic-link flow only
    # All other AI communication goes through aethergottaeat
    inbox = env.get("AGENTMAIL_OUTBOX", "aethergottaeat@agentmail.to")

    recipients = to if isinstance(to, list) else [to]

    kwargs = {
        "inbox_id": inbox,
        "to": recipients,
        "subject": subject,
        "text": text,
    }
    if in_reply_to:
        kwargs["in_reply_to"] = in_reply_to

    result = client.inboxes.messages.send(**kwargs)
    return result.message_id


def main():
    parser = argparse.ArgumentParser(description="Send AgentMail message from aether-aiciv@agentmail.to")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", help="Email body text (inline)")
    parser.add_argument("--body-file", help="Read body from file path")
    parser.add_argument("--reply-to", help="Message-ID to thread reply under (in_reply_to)")
    args = parser.parse_args()

    body = args.body
    if args.body_file:
        with open(args.body_file) as f:
            body = f.read()

    if not body:
        print("Error: provide --body or --body-file", file=sys.stderr)
        sys.exit(1)

    msg_id = send_agentmail(args.to, args.subject, body, args.reply_to)
    print(f"Sent: {msg_id}")


if __name__ == "__main__":
    main()
