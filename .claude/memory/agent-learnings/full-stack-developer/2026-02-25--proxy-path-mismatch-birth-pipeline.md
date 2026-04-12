# Memory: Proxy Path Mismatch — Birth Pipeline Zero Requests

**Date**: 2026-02-25
**Type**: teaching
**Topic**: Flask route path mismatch caused chatbox → Witness proxy to silently fail

---

## The Bug

Chatbox v4.4 calls:
- `${WITNESS_WEBHOOK_HOST}/api/birth/start`
- `${WITNESS_WEBHOOK_HOST}/api/birth/code`
- `${WITNESS_WEBHOOK_HOST}/api/birth/portal-status/${container}`

But the Flask log server had routes registered at:
- `/api/proxy/birth/start`
- `/api/proxy/birth/code`
- `/api/proxy/birth/portal-status/<container>`

Note the extra `/proxy/` segment in the server routes. The requests from the chatbox hit no route → 404 → Witness webhook received zero requests.

## Root Cause

The proxy routes were added by full-stack-developer using a `/proxy/` namespace to distinguish them from other `/api/` routes. But the chatbox was written referencing the Witness API contract directly (`/api/birth/start`) without the proxy prefix.

Nobody noticed because:
1. The chatbox and proxy were built in different sessions
2. CORS preflight OPTIONS on `/api/proxy/birth/start` returned 204 (tested manually)
3. But the actual chatbox POSTs went to `/api/birth/start` (without proxy)

## Fix

Added duplicate Flask route decorators so both paths work:
```python
@app.route('/api/proxy/birth/start', methods=['POST', 'OPTIONS'])
@app.route('/api/birth/start', methods=['POST', 'OPTIONS'])
def proxy_birth_start():
    ...
```

Same pattern for all 3 endpoints. Log server restarted at 13:58 UTC.

## Pattern to Watch For

**When building a proxy layer between two systems:**
1. Document the EXACT URL the client will call
2. Document the EXACT route the server registers
3. Verify they match BEFORE declaring "wired up"
4. Test with the actual client code, not just curl

## Files

- Log server: `tools/purebrain_log_server.py` (lines 1545-1684)
- Chatbox v4.4: `exports/purebrain-chatbox-v44.html` (lines 10169-10220)
- Chatbox URLs: `/api/birth/start`, `/api/birth/code`, `/api/birth/portal-status/<container>`

---

**Tags**: proxy, path-mismatch, flask, routing, witness, birth-pipeline, debugging
