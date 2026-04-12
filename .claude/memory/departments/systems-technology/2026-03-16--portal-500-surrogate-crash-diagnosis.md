# Portal 500 Error - Lone Surrogate UnicodeEncodeError - 2026-03-16

## Date
2026-03-16 13:01 EST

## Root Cause
**GET /api/chat/history** returned HTTP 500 due to `UnicodeEncodeError: 'utf-8' codec can't encode character '\ud83c' in position 71110: surrogates not allowed`

The crash path:
1. Jared's portal chat log (`purebrain_web_conversations.jsonl`) contains 874+ lone surrogate sequences (`\ud83d`, `\ud83c` etc.) from emoji sequences logged as split surrogates
2. `json.loads()` on these lines produces Python string objects containing actual lone surrogate codepoints
3. `JSONResponse({"messages": messages})` calls `json.dumps(...).encode('utf-8')` — Python's UTF-8 codec refuses to encode lone surrogates
4. Starlette raises the UnicodeEncodeError unhandled → uvicorn returns 500

## Service Impact
- `aether-portal.service` restarted 5 times between 13:01 and 13:38
- Each restart lasted ~1-2 minutes before hitting same crash on first `/api/chat/history` call
- Portal was DOWN or CYCLING during 13:01-13:38 EST

## Fix Applied (14:28 EST same day)
Added `_sanitize()` function in `api_chat_history` (portal_server.py line 886-895):
```python
def _sanitize(obj):
    if isinstance(obj, str):
        return obj.encode('utf-8', errors='replace').decode('utf-8')
    ...
messages = _sanitize(messages)
```
This replaces lone surrogates with `?` before JSONResponse serializes.

## Remaining Risk
The WebSocket path (`/ws/chat`) also calls `_parse_all_messages()` and sends via `json.dumps(msg)`. Python's `json.dumps` escapes lone surrogates as `\ud83c` (keeps them in JSON string, doesn't try UTF-8 encode) so it does NOT fail — different code path, no crash there.

However the underlying data is still dirty. The surrogate sequences come from:
- Emoji in user/assistant messages stored as split surrogate pairs in JSONL
- `_parse_jsonl_messages_from_file` uses `errors='replace'` on file read (bytes→str) but `json.loads` then reconstructs lone surrogates in Python objects

## A-C-Gee Forwarding
Separate issue: `A-C-Gee forward failed after 3 attempts` — endpoint `http://5.161.90.32:3001/api/landing-chat` is unreachable (connection timeout). This is A-C-Gee's server issue, NOT our problem. Our log server handles failure gracefully (logs warning, continues). Needs A-C-Gee to restart their Witness service.

## Current Status (18:34 UTC)
- Portal: STABLE, all endpoints 200
- Log server: STABLE, POST /api/log-conversation 200
- A-C-Gee forwarding: FAILING (their side, out of our control)

## Files
- `/home/jared/purebrain_portal/portal_server.py` (modified 14:28 — fix applied)
- `/home/jared/projects/AI-CIV/aether/logs/portal_server.log` (crash tracebacks at lines 29823+)
- `/home/jared/projects/AI-CIV/aether/logs/purebrain_web_conversations.jsonl` (source of surrogates)
