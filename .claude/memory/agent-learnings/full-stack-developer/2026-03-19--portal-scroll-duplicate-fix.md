# Portal: Auto-scroll regression + duplicate messages (2026-03-19)

## Task
Fix messages appearing below chat input box + duplicate messages on reply/attachment sends.

## Auto-scroll Root Cause
The March 17 MVP used `_userWasNearBottom` (simple boolean, event-tracked on every scroll).
A subsequent commit replaced it with `_userIsReading` + `_lastScrollTop` — intended to be smarter
but introduced a race condition: programmatic scrolls (history load rAFs firing rapidly)
could trigger the "scrolled UP" detection, permanently locking `_userIsReading = true` and
blocking all future auto-scrolls.

**Fix**: Revert to `_userWasNearBottom` approach. Simpler = more reliable.
- Updated on every scroll event (including programmatic)
- Captured BEFORE DOM append in addMessage
- Reset to `true` explicitly when user sends a message or clicks scroll-to-bottom

## Duplicate Message Root Causes

### Server-side (primary cause)
`_clean_user_text()` used `text.startswith("[PORTAL] ")` (uppercase) but
`api_chat_send` injects `[portal] message` (lowercase). Session JSONL captured
`[portal] message` — the prefix was NOT stripped → displayed as `[portal] msg` text.
Meanwhile portal-chat.jsonl had clean text. Different IDs = both appeared in history.

**Fix**: Use `re.sub(r'^\[portal(?:-react)?\]\s*', '', text, flags=re.IGNORECASE)`

### Server-side (secondary cause)
`_parse_all_messages` deduplicates by ID only. Session JSONL uuid ≠ portal log id,
so same message appeared from both sources.

**Fix**: Add text+timestamp secondary dedup — portal entries that match session JSONL
text within 30s window are suppressed.

### Client-side (partial fix already present)
`_dispatchChatMessage` already pre-registers `data.msg_id` from `/api/chat/send`
response into `knownMsgIds` (added in a previous fix). This suppresses the portal-log
WS echo. The session JSONL echo was still slipping through (different uuid) until
the server-side prefix fix made texts match the `lastSentOptimisticText` check.

## Files Modified
- `/home/jared/purebrain_portal/portal-pb-styled.html` — scroll logic, addMessage
- `/home/jared/purebrain_portal/portal_server.py` — _clean_user_text, _parse_all_messages

## Git
- Commit: `7ec1b65` in purebrain-portal repo
- Pushed to: `git@github-interciv:coreycottrell/purebrain-portal.git main`

## Pattern: Prefer simple event-tracked booleans over stateful intent detection
When tracking scroll intent for auto-scroll, a simple "was near bottom on last scroll event"
boolean is more robust than trying to detect "user INTENDS to read". Programmatic scrolls
can corrupt intent-based flags. Let the event listener be the single source of truth.
