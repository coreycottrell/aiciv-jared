# Portal Chat Pipe Glitch Fix
**Date**: 2026-03-06
**Type**: bug-fix
**Domain**: app.purebrain.ai (Portal Team only)

## Bug Description
Chat messages from Aether appeared as tiny bubbles containing only "|" (pipe character) instead of actual message content. Multiple such bubbles visible at once. Refreshing the portal correctly loaded full history.

## Root Cause
Multi-layer rendering path issue. The `addMessage()` function in the frontend had a noise filter (skip if trimmed length <= 2 and all non-alphanumeric). However three other rendering paths did NOT have this filter:

1. `startStreamingMessage()` - only checked `!text || !text.trim()`, not short noise
2. WS `onmessage` update path (existing message ID) - only checked `msg.text && msg.text.trim()`
3. `_mirror_to_portal_log()` server function - no content length check
4. WS polling loop send condition - no content length check before sending

If a partial/transient JSONL entry or streaming artifact slipped through with content like `|`, it would render immediately and persist in portal-chat.jsonl.

## Clue Pattern
Jared: "this same info is here in telegram and the terminal.. plus if i refresh the portal it automatically populates"
- Data correct in Telegram = data arrives fine, issue is RENDERING
- Refresh loads correctly = `loadChatHistory` → `addMessage` has filter
- Live stream shows `|` = WS path bypasses filter

## Fix Applied
5 defensive layers added:

### Server (portal_server.py)
- `_mirror_to_portal_log`: skip messages with len < 3 or all non-alphanumeric ≤ 2 chars
- WS polling loop: same noise guard before `websocket.send_text()`

### Frontend (portal-pb-styled.html)
- `startStreamingMessage`: added same guard as `addMessage` (length ≤ 2 and all non-alphanumeric)
- WS `onmessage` update path: `_isNoise` check before updating existing bubble
- `addMessage` thinking branch: minimum 3-char length check

## Files Modified
- `/home/jared/purebrain_portal/portal_server.py`
- `/home/jared/purebrain_portal/portal-pb-styled.html`

## Backups
- `portal_server.py.bak.20260306_pipe_fix`
- `portal-pb-styled.html.bak.20260306_pipe_fix`

## Verification
- Server restarted (PID 2984502) and health check passing
- All 5 fix markers confirmed present in both files
- No other portal features touched (chat, terminal, referrals, settings intact)
