# Portal 500 Error - Surrogate Unicode in Chat History

**Date**: 2026-03-16
**Incident Time**: ~13:01 ET
**Reporter**: Jared
**Severity**: High (chat load broken for users connecting to portal)

---

## Root Cause

`UnicodeEncodeError: 'utf-8' codec can't encode character '\ud83c' in position 76183: surrogates not allowed`

The `/api/chat/history` endpoint in `/home/jared/purebrain_portal/portal_server.py` was returning raw `messages` from `_parse_all_messages()` directly into `JSONResponse()`. A message in the chat JSONL log contained a surrogate character (`\ud83c`) — an invalid UTF-8 sequence that Python's `json.dumps` cannot encode. This caused a 500 Internal Server Error every time the chat history was loaded.

**Endpoint**: `GET /api/chat/history?last=200`
**File**: `/home/jared/purebrain_portal/portal_server.py` line 870 (at time of crash), now line 897 after fix
**Log**: `/home/jared/projects/AI-CIV/aether/logs/portal_server.log`

---

## Fix Applied

A `_sanitize()` function was added to `api_chat_history()` before returning the JSONResponse:

```python
def _sanitize(obj):
    if isinstance(obj, str):
        return obj.encode('utf-8', errors='replace').decode('utf-8')
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    return obj

messages = _sanitize(messages)
```

This was applied at 19:23 UTC (15:23 ET), then the portal service restarted at 19:24 UTC.

---

## Verification

- Portal health: `{"status":"ok","civ":"aether","uptime":4371}` - OK
- `/api/chat/history?last=5` returns 5 messages with HTTP 200 - OK
- No 500 errors in log since the restart

---

## Key Infrastructure Facts

- Portal server: `/home/jared/purebrain_portal/portal_server.py`
- Port: 8097
- Systemd service: `aether-portal.service`
- Real log: `/home/jared/projects/AI-CIV/aether/logs/portal_server.log` (NOT `/home/jared/purebrain_portal/portal_server.log` — that is an internal copy)
- Log server (separate): port 8443, `/home/jared/projects/AI-CIV/aether/logs/purebrain_log_server.log`

---

## Pattern to Watch

Surrogate characters (`\ud800`-`\udfff`) can appear in emoji sequences sent via mobile clients. Any endpoint that reads from JSONL and returns raw strings via `JSONResponse` is vulnerable. The `_sanitize` pattern should be applied defensively wherever JSONL content is serialized to HTTP.
