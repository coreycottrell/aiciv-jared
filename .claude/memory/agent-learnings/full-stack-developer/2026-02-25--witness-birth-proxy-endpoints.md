# Memory: Witness Birth Pipeline — Server-Side Proxy Endpoints

**Date**: 2026-02-25
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: Added 3 proxy endpoints to purebrain_log_server.py to solve mixed-content (HTTP) and CORS issues for browser-to-Witness calls

---

## Problem Solved

The PureBrain chatbox (v4, on purebrain.ai HTTPS) was calling Witness's birth API directly at `http://104.248.239.98:8099`. This caused two issues:
1. **Mixed content**: HTTPS page calling HTTP endpoint blocked by browsers
2. **CORS**: IP:port endpoint not configured to allow `purebrain.ai` origin

Solution: server-side proxy on our VPS (89.167.19.20:8443) — already HTTPS, already CORS-configured.

---

## What Was Built

Three endpoints added to `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`:

### POST /api/proxy/birth/start
- Proxies to: `POST http://104.248.239.98:8099/api/birth/start`
- Accepts: empty `{}` OR `{"container": "name"}` — validates JSON if body present
- Rate limit: 5 calls/minute per IP (sliding window deque — prevents pool exhaustion)
- Timeout: 120s (provisioning can take ~145s)
- Returns: Witness response pass-through OR generic error dict

### POST /api/proxy/birth/code
- Proxies to: `POST http://104.248.239.98:8099/api/birth/code`
- Passes body through unchanged after JSON validation
- Timeout: 30s
- Returns: Witness response pass-through

### GET /api/proxy/birth/portal-status/<container>
- Proxies to: `GET http://104.248.239.98:8099/api/birth/portal-status/<container>`
- Container name sanitized: `^[a-zA-Z0-9_-]{1,50}$` regex
- Timeout: 15s
- Returns: `{"ready": false|true, "portal_url": "..."}` pass-through

---

## Architecture Decisions

### Why `_requests` library (not `urllib`)
`_requests` (already imported as `import requests as _requests` for Brevo) supports `.exceptions.Timeout` and `.exceptions.ConnectionError` cleanly. Timeouts and connection failures each get specific HTTP status codes (504, 503).

### Upstream IP hardcoded — never from request
`WITNESS_BASE_URL = 'http://104.248.239.98:8099'` at module level. The proxy will ONLY ever call this one IP. No SSRF risk.

### Rate limiter implementation
Sliding-window deque per IP, protected by a threading.Lock. Simple, no external dependencies, works with Flask's threaded mode. Evicts expired timestamps on each call.

### Error wrapping
`_proxy_to_witness()` never raises — wraps all exceptions into `{'error': '...', 'details': '...'}` dicts with appropriate HTTP status (502/503/504). Browser never sees Witness internals.

---

## New Imports Added
```python
import re
from collections import deque
```

---

## New Module-Level Constants
```python
WITNESS_BASE_URL = 'http://104.248.239.98:8099'
WITNESS_START_TIMEOUT = 120
WITNESS_CODE_TIMEOUT = 30
WITNESS_PORTAL_STATUS_TIMEOUT = 15
_birth_start_rate: Dict[str, deque] = {}
_birth_start_rate_lock = threading.Lock()
BIRTH_START_RATE_MAX = 5
BIRTH_START_RATE_WINDOW = 60.0
_CONTAINER_NAME_RE = re.compile(r'^[a-zA-Z0-9_-]{1,50}$')
```

---

## New Helper Functions
- `_check_birth_start_rate_limit(client_ip: str) -> bool`
- `_proxy_to_witness(method, path, body, timeout) -> tuple[dict, int]`

---

## How to Update Chatbox to Use Proxy

After deployment, the chatbox (v4.x) should replace direct Witness calls:

```javascript
// OLD (direct — causes mixed-content on HTTPS pages)
const resp = await fetch('http://104.248.239.98:8099/api/birth/start', {...})

// NEW (via proxy — HTTPS, CORS-OK)
const resp = await fetch('https://89.167.19.20:8443/api/proxy/birth/start', {...})
// OR if using the domain alias:
const resp = await fetch('https://api.purebrain.ai/api/proxy/birth/start', {...})
```

All three endpoints follow the same swap pattern:
- `/api/birth/start` → `/api/proxy/birth/start`
- `/api/birth/code` → `/api/proxy/birth/code`
- `/api/birth/portal-status/{container}` → `/api/proxy/birth/portal-status/{container}`

---

## File Modified
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`
  - New content: lines 114–134 (constants), 154–225 (helper functions), 1516–1647 (route handlers)

## Related Memory
- `.claude/memory/agent-learnings/full-stack-developer/2026-02-24--witness-birth-pipeline-chatbox-v4.md`
- `.claude/memory/agent-learnings/full-stack-developer/2026-02-24--witness-birth-pipeline-chatbox-integration-audit.md`
- `.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-birth-pipeline-contract.md`
