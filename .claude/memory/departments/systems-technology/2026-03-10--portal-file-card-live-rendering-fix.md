# Portal File Card Live Rendering Bug Fix
**Date**: 2026-03-10
**Agent**: dept-systems-technology
**Type**: bug-fix

## Bug Description
File download cards in the portal chat only appeared after a full page refresh.
When Aether sends a file via `portal_send_file.sh`, the file card did not render
live — Jared had to manually refresh portal.purebrain.ai to see it.

## Root Cause Analysis

### 1. No immediate WS push from api_deliverable (PRIMARY)
`api_deliverable` wrote the file message to `portal-chat.jsonl` and relied on the
0.8s WS poll loop to deliver it. The fix: after `_save_portal_message()`, immediately
call `asyncio.create_task(_push_message_to_clients(entry))` to push directly to all
connected WS clients without waiting for the poll cycle.

Same fix applied to `api_notify`.

### 2. In-place update rendered raw PORTAL_FILE text (SECONDARY)
In `chatWs.onmessage`, when a message ID was already in `knownMsgIds`, the in-place
update did `bubble.innerHTML = renderMarkdown(msg.text)`. Since `msg.text` contained
the raw `[PORTAL_FILE:stored:original]` tag, this rendered as visible literal text.
Fix: strip PORTAL_FILE tags before `renderMarkdown` in the in-place update path.

### 3. Missing data-portal-stored attribute on initial renders
Cards rendered by `addMessage` (history load) and `startStreamingMessage` (live
delivery) did not set `data-portal-stored` on the card element. This caused the
in-place update path to not find the existing card via
`.ai-file-card[data-portal-stored="..."]`, potentially rendering duplicate cards.
Fix: set `data-portal-stored` attribute on the card element in both code paths.

### 4. PORTAL_FILE text showing mid-stream (COSMETIC)
During typewriter streaming, periodic `renderMarkdown(revealed)` calls would render
partial `[PORTAL_FILE:...` text as visible characters. Fix: strip PORTAL_FILE tags
from `revealed` before periodic re-renders, and from `displayText` before the final
completion render.

## Files Modified
- `/home/jared/purebrain_portal/portal_server.py` (and git repo copy)
- `/home/jared/purebrain_portal/portal-pb-styled.html` (and git repo copy)

## Architecture Context
- Portal server: port 8097, run by systemd `aether-portal.service`
- Cloudflare tunnel: `portal.purebrain.ai` → nginx:8099 → proxy_pass 127.0.0.1:8097
- File messages use `[PORTAL_FILE:stored_name:display_name]` tag format
- Cards rendered by `renderAiFileCards()` function, appended to message div
- WS poll loop runs every 0.8s in `ws_chat()`, deduplicates via `seen_texts` dict

## Test Command
```bash
TOKEN=$(cat ~/purebrain_portal/.portal-token)
echo "Test content" > /tmp/test.md
curl -s -X POST http://localhost:8097/api/deliverable \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path":"/tmp/test.md","name":"test.md","message":"Test caption"}'
# Should return {"ok":true,...}
# File card should appear LIVE in portal without refresh
```
