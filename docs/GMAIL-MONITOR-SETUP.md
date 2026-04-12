# Gmail Monitor Setup

Autonomous email monitoring for purebrain@puremarketing.ai.

## Overview

The Gmail monitor:
1. Checks inbox periodically (default: every 5 minutes)
2. Classifies emails into three categories:
   - **reply_needed**: Clear human inquiry - auto-reply with acknowledgment
   - **ask_jared**: Uncertain - alert Jared via Telegram for guidance
   - **fyi_only**: Newsletters, notifications - log but no action
3. Always CCs Jared on any automated replies
4. Tracks processed emails to avoid duplicates

## Quick Start

### One-time check
```bash
python3 tools/gmail_monitor.py check
```

### Start daemon (background)
```bash
./tools/launch_gmail_monitor.sh
```

### Stop daemon
```bash
./tools/launch_gmail_monitor.sh stop
```

### Check status
```bash
./tools/launch_gmail_monitor.sh status
```

### View stats
```bash
python3 tools/gmail_monitor.py stats
```

## Configuration

Credentials are in `.env`:
```
GMAIL_USERNAME=purebrain@puremarketing.ai
GOOGLE_APP_PASSWORD=mldvztmeligxhyaw
```

Jared's email for CC: `jaredcmusic@gmail.com`

## Classification Logic

### FYI Only (No Action)
- Automated senders (noreply, google.com, vercel.com, etc.)
- Newsletters (unsubscribe link detected)
- Notifications (security alerts, sign-in alerts)
- Document shares (Google Docs/Drive notifications)
- Onboarding/welcome emails
- Marketing emails

### Ask Jared (Telegram Alert)
- Financial matters (invoices, payments, contracts)
- Sensitive topics (complaints, refunds, cancellations)
- Unknown people reaching out
- Business inquiries from company emails
- Pricing questions
- Anything unclear

### Reply Needed (Auto-Acknowledge)
- Clear help requests from personal email domains
- Meeting/call requests
- Direct inquiries about services

## Files

| File | Purpose |
|------|---------|
| `tools/gmail_monitor.py` | Main monitoring script |
| `tools/email_state.py` | State tracking utilities |
| `tools/launch_gmail_monitor.sh` | Daemon launcher |
| `memories/agents/email-monitor/email_state.json` | Persistent state |
| `logs/gmail_monitor.log` | Activity log |

## Telegram Integration

Uses existing Telegram bridge to alert Jared:
- Config: `config/telegram_config.json`
- Jared's chat_id: `548906264`

Alert format:
```
📧 NEW EMAIL - Need Your Input

From: [sender]
Subject: [subject]

Preview:
[body preview]

Classification: ask_jared
Reason: [why it needs review]

Reply with your guidance or "handle it" if I should proceed with auto-reply.
```

## State Tracking

Email state persists in `memories/agents/email-monitor/email_state.json`:
- Processed message IDs
- Classification history
- Statistics

To reset state:
```bash
python3 tools/email_state.py reset
```

## Systemd Service (Optional)

For production use, install as systemd service:
```bash
sudo cp tools/gmail_monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gmail_monitor
sudo systemctl start gmail_monitor
```

## Troubleshooting

### Authentication Failed
Check `.env` has correct app password (must be app-specific password, not regular password).

### Not Detecting New Emails
Check IMAP is enabled in Gmail settings.

### Telegram Alerts Not Working
Verify `config/telegram_config.json` has correct bot token and chat_id.

## Future Improvements

- [ ] Smart reply drafting based on email content
- [ ] Calendar integration for meeting requests
- [ ] Learn from Jared's responses to improve classification
- [ ] Thread tracking for conversation context
