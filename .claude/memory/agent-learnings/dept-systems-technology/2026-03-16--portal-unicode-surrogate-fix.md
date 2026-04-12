# Portal 500: UnicodeEncodeError Surrogate Fix

**Date**: 2026-03-16
**Type**: bug-fix / gotcha
**Severity**: Production 500 on critical endpoint

## Root Cause

`UnicodeEncodeError: 'utf-8' codec can't encode character '\ud83c' in position 30896: surrogates not allowed`

Starlette's `JSONResponse.render()` calls:
```python
json.dumps(content, ensure_ascii=False, ...).encode("utf-8")
```

With `ensure_ascii=False`, surrogate characters (lone high/low surrogates like `\ud83c`) pass through `json.dumps` unchanged, then `.encode("utf-8")` raises `UnicodeEncodeError` because UTF-8 cannot encode surrogate code points.

## Two-Layer Defense Applied

### Layer 1 (already present): api_chat_history sanitizer
`portal_server.py` line ~885 — `_sanitize()` function walks the full response dict/list/str tree and applies `.encode('utf-8', errors='replace').decode('utf-8')` before returning JSONResponse.

### Layer 2 (fix applied): _load_portal_messages file open
`portal_server.py` line ~684 — changed:
```python
with PORTAL_CHAT_LOG.open("r") as f:
```
to:
```python
with PORTAL_CHAT_LOG.open("r", errors='replace') as f:
```

This prevents surrogates from entering the data pipeline at the source (file read), before they can reach the JSONResponse serialization path.

## Why This Matters

- Portal-chat.jsonl can contain surrogate characters from emoji input (e.g. emoji split across surrogate pairs by broken string handling upstream)
- Without `errors='replace'`, the Python `open()` with default UTF-8 codec will silently fail inside `try/except Exception: pass`, returning empty portal messages — OR in certain conditions will propagate a UnicodeDecodeError that bypasses the response sanitizer
- The sanitizer in `api_chat_history` is a last-line defense; the file-open fix prevents the issue upstream

## Verification

```bash
curl -s -o /dev/null -w "HTTP_CODE:%{http_code}" \
  -H "Authorization: Bearer $(cat /home/jared/purebrain_portal/.portal-token)" \
  "http://127.0.0.1:8097/api/chat/history"
# Returns: HTTP_CODE:200
```

Response parsed with 100 messages, zero surrogate chars in output.

## File Modified
`/home/jared/purebrain_portal/portal_server.py` — line ~684 in `_load_portal_messages()`

## Note on localhost vs 127.0.0.1
Portal binds to `0.0.0.0:8097`. On this machine, `localhost` resolves to `::1` (IPv6) which is NOT bound. Use `http://127.0.0.1:8097` for local curl verification.
