# RSS-to-Email Daemon: PureBrain Neural Feed

**Date**: 2026-02-23
**Type**: operational
**Topic**: RSS polling daemon integrated into purebrain_log_server.py

## What Was Built

Three deliverables for the Neural Feed blog distribution system:

### Files Created/Modified
- **NEW**: `/home/jared/projects/AI-CIV/aether/tools/rss_to_email.py` — RSS polling daemon
- **NEW**: `/home/jared/projects/AI-CIV/aether/config/rss_email_state.json` — seeded with 10 existing post GUIDs
- **MODIFIED**: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` — RSS thread added at startup

## Architecture Decisions

### Sender Email Critical Fix
- `support@puremarketing.ai` is NOT verified in Brevo
- Used `purebrain@puremarketing.ai` instead (verified)
- This was a CRITICAL change from the spec — would have caused all campaigns to fail silently

### f-string Double/Quadruple Braces
- CSS braces in f-strings: `{{ }}` renders as `{ }` in output — CORRECT
- Brevo unsubscribe tag in f-string: `{{{{ unsubscribe }}}}` renders as `{{ unsubscribe }}` — REQUIRED
- Without quadruple braces, the unsubscribe tag would be consumed by Python's f-string parser

### State File Seeding
- Fetched live feed at 2026-02-23 to get all 10 existing post GUIDs
- Seeded state file so first daemon run doesn't blast emails for all existing posts
- Daemon will only fire for posts published AFTER the seed date

### Error Handling Pattern
- `fetch_rss()` returns empty list on ANY error (never raises) — daemon must not crash
- `send_rss_campaign()` returns `False` on failure, does NOT add GUID to seen list
- Failed posts will retry on next poll cycle automatically
- Outer `while True` has catch-all `except Exception` so a bug never kills the thread

### No Double-Send Protection
- GUID added to `seen_guids` ONLY after successful campaign send
- State file uses atomic write (`os.replace(tmp, dest)`) to prevent corruption
- If server restarts mid-send, the GUID won't be in seen list and will retry (acceptable)

## Integration Pattern
```python
# In purebrain_log_server.py main():
rss_thread = threading.Thread(target=rss_daemon_loop, daemon=True)
rss_thread.name = 'rss-to-email-daemon'
rss_thread.start()
```
- Same pattern as the welcome sequence scheduler
- `daemon=True` ensures clean exit with main process

## Brevo Campaign Flow
1. `POST /v3/emailCampaigns` — creates draft (returns campaign ID)
2. `POST /v3/emailCampaigns/{id}/sendNow` — sends immediately (returns 204)
- Both steps must succeed for GUID to be marked seen
- Campaign name format: `[Auto] Neural Feed — {title[:50]}`

## RSS Feed Facts (confirmed live 2026-02-23)
- URL: `https://purebrain.ai/feed/`
- Returns standard WordPress RSS 2.0
- Contains 10 items (WordPress default)
- GUIDs are permalink URLs (not UUID-based)
- `<description>` contains HTML entities and tag footers — strip with regex

## Testing Results
- Feed fetch: 10 items parsed successfully
- State load: 10 seen GUIDs, 0 sent campaigns
- New post detection: 0 new posts (correct — all seeded)
- HTML template: `{{ unsubscribe }}` tag present, CSS braces correct
- HTML size: 4,348 chars
