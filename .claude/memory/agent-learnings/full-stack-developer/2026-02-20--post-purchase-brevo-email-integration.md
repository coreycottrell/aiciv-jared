# Post-Purchase Brevo Email Integration

**Date**: 2026-02-20
**Type**: teaching
**Agent**: full-stack-developer
**Topic**: Server-side post-purchase welcome email automation via Brevo transactional API

---

## What Was Built

Complete post-purchase email sequence triggered server-side when a customer completes the PureBrain pay-test flow.

---

## Brevo Infrastructure Created (Live)

| Resource | ID | Name |
|---|---|---|
| Contact List | 8 | PureBrain Customers |
| Contact Attribute | - | AI_NAME (text) |
| Contact Attribute | - | PRIMARY_GOAL (text) |
| Email Template | 11 | PureBrain - Welcome - Your AI partner is live |
| Email Template | 12 | PureBrain - Setup Complete - 40 minutes in |

Config persisted at: `/home/jared/projects/AI-CIV/aether/config/post_purchase_brevo_config.json`

DO NOT TOUCH Templates 1-10 (Neural Feed nurture sequence for blog subscribers / List 3).

---

## Architecture: What Triggers What

```
pay-test page JS
  → POST /api/log-pay-test  (when flow:complete fires with flowCompleted=true + email present)
  → log_pay_test() handler (Flask, purebrain_log_server.py)
  → background thread: _trigger_post_purchase_emails(data)
      → _upsert_brevo_contact(email, attrs, list_id=8)
      → _send_brevo_transactional(template_id=11, immediate)  ← Welcome email
      → threading.Timer(2400s, send_email_2)                  ← Setup-complete email (40 min later)
      → _send_telegram_notification(summary to Jared)
```

---

## Key Technical Details

### Brevo Transactional API Pattern

```python
resp = requests.post(
    'https://api.brevo.com/v3/smtp/email',
    headers={'api-key': BREVO_API_KEY, 'Content-Type': 'application/json'},
    json={
        'to': [{'email': to_email, 'name': to_name}],
        'templateId': template_id,
        'params': {
            'FIRSTNAME': '...',
            'AI_NAME': '...',    # Custom template variable
            'TIER': '...',
            'PRIMARY_GOAL': '...',
        },
    },
    timeout=15,
)
# 201 = success, messageId returned
```

### Brevo Contact Upsert Pattern

```python
resp = requests.post(
    'https://api.brevo.com/v3/contacts',
    headers={'api-key': BREVO_API_KEY, 'Content-Type': 'application/json'},
    json={
        'email': email,
        'attributes': {k: v for k, v in attrs.items() if v},  # strip empties
        'listIds': [8],
        'updateEnabled': True,  # CRITICAL: upsert, not create-only
    },
    timeout=15,
)
# 201 = new contact, 204 = updated existing
```

### Template Variable Substitution

Brevo templates use `{{params.VARNAME}}` syntax. Passed via `params` dict in API call.
Example: `{{params.AI_NAME}}` → substituted from `params.AI_NAME`.

### 40-Minute Delay (threading.Timer)

```python
timer = threading.Timer(2400, callback_fn)  # 40 * 60 seconds
timer.daemon = True   # Don't block process exit
timer.start()
```

**Known limitation**: State lost on server restart within 40 min window.
Upgrade path: Redis + Celery or Brevo's automation workflow for production scale.

---

## Guard Condition (Critical)

Email sequence only fires when BOTH:
1. `data.get('flowCompleted') == True`
2. `data.get('email')` is truthy (non-empty string)

Historical data shows `flowCompleted: false` on all past entries - the JS event may not have been firing. This guard ensures we only send when we have a real completed flow with a real email.

---

## Error Handling Pattern

- Brevo failures: log to `logs/purebrain_emails.jsonl` + logger.error, do NOT raise
- Missing API key: log error, return False immediately
- Email failure never blocks the HTTP response (runs in daemon thread)
- Empty attribute values are stripped before upsert (avoids overwriting good data with "")

---

## Email Log Format

```jsonl
{"event": "welcome_email_sent", "email": "...", "name": "...", "tier": "...", "ai_name": "...", "template_id": 11, "contact_upserted": true, "email_sent": true, "timestamp": "..."}
{"event": "setup_complete_email_sent", "email": "...", ..., "template_id": 12, "email_sent": true, "timestamp": "..."}
```

Log path: `logs/purebrain_emails.jsonl`

---

## Setup Script

One-time setup (already run, idempotent if run again):
```bash
python3 tools/setup_post_purchase_brevo.py         # live
python3 tools/setup_post_purchase_brevo.py --dry-run  # preview
```

---

## How to Restart the Server

After modifying purebrain_log_server.py, restart via systemd:
```bash
sudo systemctl restart purebrain-log-server
# or if running manually:
pkill -f purebrain_log_server.py
nohup python3 tools/purebrain_log_server.py >> logs/purebrain_log_server.log 2>&1 &
```

---

## Files Modified/Created

- **Created**: `/home/jared/projects/AI-CIV/aether/tools/setup_post_purchase_brevo.py`
- **Modified**: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`
  - Added: `import requests as _requests`, `from dotenv import load_dotenv`, `load_dotenv(...)`
  - Added: Brevo constants (BREVO_API_KEY, BREVO_BASE_URL, list/template IDs)
  - Added: `_log_email_sent()`, `_send_brevo_transactional()`, `_upsert_brevo_contact()`, `_parse_name()`, `_trigger_post_purchase_emails()`
  - Modified: `log_pay_test()` - added email thread trigger after flowCompleted check
- **Created**: `/home/jared/projects/AI-CIV/aether/config/post_purchase_brevo_config.json`
- **Created**: Email log file will appear at `logs/purebrain_emails.jsonl` on first purchase
