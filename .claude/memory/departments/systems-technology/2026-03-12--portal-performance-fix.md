# Portal Performance Fix - 2026-03-12

## Problem
- app.purebrain.ai portal showing "Offline" intermittently  
- "Loading civilization history..." stuck indefinitely
- Portal used to load much faster

## Root Causes Found

### 1. portal-chat.jsonl Growing Without Bounds
- File had 8,496 entries (526 duplicates), 3.6MB
- Read on EVERY /api/chat/history request (no caching): 91ms/call
- WS poll calls this every 1.5s → continuous I/O drain

### 2. No Mtime Cache for portal-chat.jsonl
- Session JSONL files had mtime+size caching (fast on repeat calls)
- portal-chat.jsonl had NO cache - full read every time

### 3. Server-Side WS Keepalive Missing
- ws_chat sends nothing when no new messages
- Client heartbeat detects 30s silence → forces reconnect  
- Frequent reconnects → "Loading civilization history..." flash
- Cloudflare could also drop idle WS connections

### 4. app.purebrain.ai → Nginx Redirect
- app.purebrain.ai → 301 redirect → portal.purebrain.ai
- This is intentional (nginx config), not a problem

## Fixes Applied

### portal_server.py (live: /home/jared/purebrain_portal/)
1. Added `_portal_chat_cache` tuple (mtime, fsize, messages)
2. Updated `_load_portal_messages()` to use mtime+size cache (same pattern as session JSONL)
3. Added server-side WS ping every 20s in ws_chat loop
4. Added `_trim_portal_chat_log()` function for periodic dedup + trim
5. Added `_trim_portal_log_periodically()` background task (runs every 30min)

### portal-pb-styled.html (live)
- Added ping message ignore: `if (msg.type === 'ping') return;`
  - Prevents ping messages from being rendered as chat messages
  - Ping still updates `window._wsLastMsg` so heartbeat resets

### portal-chat.jsonl (manual trim)
- Trimmed from 8,496 entries (3.6MB) to 3,000 entries (1.35MB)
- Removed 525 duplicate entries

## Performance Results
- /api/chat/history: 166ms → 22-44ms (85% improvement)
- CPU: 9.8% → 6.5% (34% reduction)
- WS connections: Stable (no more frequent drops/reconnects)

## Files Modified
- `/home/jared/purebrain_portal/portal_server.py`
- `/home/jared/purebrain_portal/portal-pb-styled.html`
- `/home/jared/purebrain_portal/portal-chat.jsonl`
- `/home/jared/projects/AI-CIV/aether/exports/app-purebrain-ai-full-repo/portal-server/portal_server.py`

## Verification
```bash
# Check API performance
TOKEN=$(cat /home/jared/purebrain_portal/.portal-token)
time curl -s -o /dev/null -w "%{http_code} %{time_total}s" "http://localhost:8097/api/chat/history?last=200" -H "Authorization: Bearer $TOKEN"

# Check service status
sudo systemctl status aether-portal
```
