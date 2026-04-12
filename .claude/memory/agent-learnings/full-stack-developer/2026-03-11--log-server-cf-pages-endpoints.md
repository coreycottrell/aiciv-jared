# Log Server: CF Pages Lead Capture Endpoints

**Date**: 2026-03-11
**Type**: operational

## What was built

Added two new Flask endpoints to `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`:

### POST /api/guide-unlock
- Logs to `logs/purebrain_guide_unlocks.jsonl`
- Sends Telegram notification via `_send_telegram_notification` helper (non-blocking thread)
- Validates email required, accepts: email, name, page_url, timestamp
- Returns `{"success": true, "message": "...", "server_timestamp": "..."}`

### POST /api/investor-lead
- Logs to `logs/purebrain_investor_leads.jsonl`
- Sends Telegram notification (non-blocking thread)
- Accepts: email, name, company, interest, page_url, timestamp
- Returns same success shape

## CF Pages _headers file
Created `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/_headers`
- Security headers for all paths (`/*`)
- NO CSP header — site uses extensive inline scripts/styles

## Patterns to remember
- `_send_telegram_notification(msg)` helper already exists in the file — use it for all Telegram alerts
- Wrap Telegram in `threading.Thread(target=..., daemon=True)` — non-blocking
- `_cors_preflight()` helper handles CORS for OPTIONS requests
- `_file_lock` (threading.Lock) wraps all file writes for thread safety
- All new endpoints go inside `register_routes(app)` function closure
- JSONL log constants defined at top of `register_routes` closure (same pattern as `GOVERNANCE_LOG`)
- After edits: kill with `fuser -k 8443/tcp`, restart with `nohup python3 tools/purebrain_log_server.py >> logs/purebrain_log_server.log 2>&1 &`
- Health check: `curl -sk https://localhost:8443/api/health`
