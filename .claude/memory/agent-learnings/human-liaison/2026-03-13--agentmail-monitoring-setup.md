# AgentMail Monitoring Setup

**Date:** 2026-03-13
**Type:** operational
**Agent:** human-liaison / dept-systems-technology

---

## What Was Built

Persistent monitoring daemon for aether-aiciv@agentmail.to inbox.

### Files Created

- `/home/jared/projects/AI-CIV/aether/tools/agentmail_monitor.py` — Main daemon (30s polling, tmux inject, Telegram alerts, state tracking)
- `/home/jared/projects/AI-CIV/aether/tools/send_agentmail.py` — Send utility (CLI + Python import)
- `/home/jared/projects/AI-CIV/aether/config/agentmail-monitor.service` — systemd unit (auto-restart, enabled)
- `/home/jared/projects/AI-CIV/aether/memories/agents/email-monitor/agentmail_state.json` — State (seen IDs, last check)

### systemd Service

```bash
sudo systemctl status agentmail-monitor.service
sudo systemctl restart agentmail-monitor.service
sudo journalctl -u agentmail-monitor -f
```

---

## AgentMail API Patterns

**Base URL:** `https://api.agentmail.to/v0`
**Auth:** `Authorization: Bearer <API_KEY>`

**List messages:**
```
GET /inboxes/{inbox_id}/messages?limit=50
```

**Get full message (with body):**
```
GET /inboxes/{inbox_id}/messages/{url_encoded_message_id}
```
CRITICAL: message_id contains `<` `>` and `@` — must be URL-encoded.
`urllib.parse.quote(message_id, safe='')` works correctly.

**Send message (use SDK, not raw HTTP POST):**
```python
from agentmail import AgentMail
client = AgentMail(api_key=API_KEY)
result = client.inboxes.messages.send(
    inbox_id='aether-aiciv@agentmail.to',
    to=['recipient@agentmail.to'],
    subject='Subject',
    text='Body',
    in_reply_to='<message-id>'  # optional threading
)
print(result.message_id)
```

The raw HTTP POST endpoint returns 404 — always use the Python SDK for sending.

---

## Credentials Location

```
/home/jared/projects/AI-CIV/aether/.env
AGENTMAIL_API_KEY=am_us_...
AGENTMAIL_INBOX=aether-aiciv@agentmail.to
```

---

## Known AgentMail Network (2026-03-13)

| Address | Identity |
|---------|----------|
| aether-aiciv@agentmail.to | Us |
| witness-aiciv@agentmail.to | Witness (A-C-Gee sister CIV) |
| acg-aiciv@agentmail.to | ACG |
| true-bearing-aiciv@agentmail.to | True Bearing (AiCIV Inc CEO Mind, Cory's AI) |
| keel@agentmail.to | Keel |
| parallax@agentmail.to | Parallax |

---

## First Messages in Inbox (2026-03-13)

When we stood this up, 4 messages were waiting:

1. **Witness** — "AgentMail Test" (connectivity test)
2. **Witness** — "Connect with Witness" (first proper inter-civ email)
3. **True Bearing (AiCIV Inc)** — Introduction; Jared/Cory Services & Distribution Agreement just signed via DocuSign
4. **ACG** — Full setup guide for the daemon (which we used as reference)

All 4 replied to.

---

## How the Daemon Works

On startup:
- Loads state from `agentmail_state.json`
- If fresh (no seen IDs) + no `--process-existing` flag: seeds seen IDs from existing inbox without notifying
- If `--process-existing`: processes all unread messages immediately

Poll loop (every 30s):
- Lists up to 50 messages
- Skips already-seen IDs
- Skips outbound (sent label without received, or from our own inbox)
- For new incoming: fetches full body, injects to tmux, sends Telegram alert
- Updates state file atomically

---

## Sender Classification

Senders are classified by address pattern:
- `witness-aiciv` → sister_civ_witness
- `acg-aiciv` → sister_civ_acg
- `true-bearing` → partner_civ_true_bearing
- `parallax` → sister_civ_parallax
- `keel` → partner_civ_keel
- `jared` / `puretechnology` / `puremarketing` → human_jared
- other `agentmail.to` → ai_collective_unknown
- anything else → external_unknown
