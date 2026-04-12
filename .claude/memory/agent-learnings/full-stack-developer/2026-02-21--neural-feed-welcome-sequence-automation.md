# Neural Feed Welcome Sequence Automation

**Date**: 2026-02-21
**Type**: teaching
**Agent**: full-stack-developer
**Topic**: Brevo List 3 polling automation for 7-email welcome sequence

---

## What Was Built

A standalone Python module that:
1. Polls Brevo List 3 (Neural Feed) every hour for new subscribers
2. Fires Email 1 immediately when a new subscriber is detected
3. Fires Emails 2-7 on schedule (days 2, 4, 7, 10, 14, 21) based on subscription timestamp
4. Persists state in `config/welcome_sequence_state.json` (survives server restarts)
5. Logs all sends to `logs/purebrain_emails.jsonl` (shared with post-purchase logger)
6. Sends Telegram notifications on new subscriber and sequence completion

---

## Architecture Decision: Polling (not webhook)

**Why polling instead of Brevo webhook?**
- Brevo's webhook approach requires a public endpoint + Brevo webhook config
- Our server is already running and has the Brevo API key
- Polling List 3 every hour is sufficient for a newsletter (new subscribers don't need email in seconds)
- Simpler to implement, test, and debug
- No Brevo UI changes required

**Why a separate module instead of inline in purebrain_log_server.py?**
- Separation of concerns: log server handles HTTP, welcome module handles CRM automation
- Easier to test the welcome module independently
- Can be run standalone from CLI for status checks and one-off cycles

---

## Files

| File | Role |
|---|---|
| `tools/neural_feed_welcome_sequence.py` | Core module + CLI |
| `tools/purebrain_log_server.py` | Calls `start_welcome_sequence_scheduler()` in `main()` |
| `config/welcome_sequence_state.json` | Per-subscriber state (created on first run) |
| `logs/purebrain_emails.jsonl` | Email send log (shared, append-only) |

---

## Brevo Templates Used

| Email | Template ID | Day |
|---|---|---|
| 1 - Welcome (Aether) | 1 | 0 (immediate) |
| 2 - Jared's Story | 2 | 2 |
| 3 - Aether Writes Directly | 3 | 4 |
| 4 - Partnership in Practice | 4 | 7 |
| 5 - The Context Tax | 5 | 10 |
| 6 - Social Proof & Results | 6 | 14 |
| 7 - The Invitation | 7 | 21 |

---

## Key Technical Patterns

### Polling + State Pattern
```python
# Run cycle
def run_one_cycle():
    state = _load_state()           # Load JSON state from disk
    contacts = _get_list3_contacts() # Fetch Brevo List 3
    for contact in contacts:
        state = _process_contact(contact, state)
    _save_state(state)              # Atomic write via .tmp rename
```

### Contact Eligibility Filtering
- Skip if `emailBlacklisted == True`
- Skip if contact's `listIds` does not include `3` (they may have been removed)
- Skip if no email address (Brevo can have ID-only contacts)

### Email Due Logic
```python
def _emails_due(subscribed_at, emails_already_sent):
    due = []
    for email_num, template_id, delay_days in EMAIL_SCHEDULE:
        if email_num in emails_already_sent:
            continue
        send_after = subscribed_at + timedelta(days=delay_days)
        if now >= send_after:
            due.append((email_num, template_id, delay_days))
    return due
```

### State File Atomic Write (prevents corruption)
```python
tmp = STATE_FILE.with_suffix('.tmp')
with open(tmp, 'w') as f:
    json.dump(state, f, indent=2)
tmp.rename(STATE_FILE)
```

### Retry on Send Failure
- MAX_SEND_RETRIES = 3, RETRY_DELAY_SECONDS = 30
- Only marks email as sent if Brevo returns 200/201
- Failed sends are logged to subscriber's `errors` list (retried on next cycle)
- This means if Email 2 fails, it will retry on the next hourly cycle

---

## Brevo API Gotchas Learned

- `createdAt` in List 3 contact is the contact creation date, NOT the list-join date
  - For most subscribers this is the same thing
  - Use `createdAt` as the subscription reference timestamp
- Contacts with no email address appear in the API response (id but no email field)
  - Must check `contact.get('email')` before processing
- `listIds` on a contact shows CURRENT list membership, not historical
  - If subscriber unsubscribes from List 3, `listIds` will not contain 3
  - The code correctly skips them

---

## Deployment Notes

- Module runs as daemon thread inside purebrain_log_server.py
- Scheduler starts automatically in `main()` before Flask starts serving
- To check status: `python3 tools/neural_feed_welcome_sequence.py --status`
- To run one cycle manually: `python3 tools/neural_feed_welcome_sequence.py`
- To run continuously standalone: `python3 tools/neural_feed_welcome_sequence.py --daemon`
- Poll interval can be overridden via env: `NEURAL_FEED_POLL_INTERVAL=60` (seconds)

---

## State File Structure

```json
{
  "subscriber@example.com": {
    "email": "subscriber@example.com",
    "firstname": "Jane",
    "subscribed_at": "2026-02-21T09:00:00+00:00",
    "emails_sent": [1, 2],
    "send_times": {"1": "2026-02-21T09:05:00+00:00", "2": "2026-02-23T09:05:00+00:00"},
    "sequence_complete": false,
    "last_checked": "2026-02-23T10:00:00+00:00",
    "errors": []
  }
}
```

---

## What NOT to Do

- Do NOT restart the server within the first hour of deployment to see Email 1 fire
  - The first cycle runs immediately on start, so Email 1 fires within seconds for existing List 3 contacts
  - Existing subscribers (purebrain@puremarketing.ai, jared@puretechnology.nyc, jaredsanborn@yahoo.com) will receive Emails 1 AND 2 on first production deployment (both are due as of 2026-02-21)
  - Jared should be aware of this and may want to pre-populate state with existing subscribers before first deploy

- Do NOT modify template IDs 1-7 in Brevo (they are used by this automation)
  - Post-purchase templates are 11 and 12 (separate, safe to modify)
