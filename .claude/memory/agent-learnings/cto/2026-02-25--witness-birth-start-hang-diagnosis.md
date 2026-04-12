# Memory: Witness /api/birth/start Hang — Root Cause Diagnosis

**Date**: 2026-02-25
**Agent**: cto
**Type**: operational + teaching
**Topic**: Complete diagnosis of why /api/birth/start hangs — it's a Witness-side issue, not our proxy

---

## The Problem

`POST http://104.248.239.98:8099/api/birth/start` accepts TCP connection but never returns a response.
Our proxy at `89.167.19.20:8443` correctly waits 180s then returns 504.

## Key Evidence From Logs

### Timeline (proxy log)

| Time UTC | Event |
|----------|-------|
| 11:53:58 | birth/start forwarded → 2m37s → status=500 (fast fail, Witness returned error) |
| 11:54:21 | portal-status forwarded → 15s timeout |
| 11:56:35 | birth/start → status=500 |
| 16:17:07 | birth/start forwarded |
| 16:19:44 | status=500 (responded ~2m37s, Witness processed but error) |
| 16:21:21 | birth/start forwarded (no response logged) |
| 16:21:37 | birth/start forwarded again (rapid retry) |
| 16:23:59 | status=500 for one of those |
| 16:24:37 | **TIMEOUT** at exactly 180s (Witness accepted but NEVER responded) |
| 16:34:17 | birth/start forwarded → 16:37:17 **TIMEOUT** at 180s |
| 16:41:31 | birth/start forwarded → 16:44:31 **TIMEOUT** |
| 16:42:19 | birth/start forwarded → 16:45:19 **TIMEOUT** |
| 16:43:07 | birth/start forwarded → 16:46:07 **TIMEOUT** |

### Pattern
- Sometimes Witness responds quickly with 500 (server error, at least it responds)
- Sometimes Witness accepts TCP connection and hangs forever (the main problem)
- Our proxy code is correct (threaded=True, requests library with timeout, Content-Type: application/json)

## Our Proxy Code — CONFIRMED CORRECT

```python
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
resp = _requests.post(url, data=body, headers=headers, timeout=timeout)
```

Body sent: `{"name":"js","email":"j@pt.com","human_name":"js","tier":"awakened"}`
Flask: threaded=True (not blocking on other requests)
Timeout: 180s (matches Witness's documented internal limit)

## Root Cause: Witness-Side Issue

The problem is on Witness's server (104.248.239.98:8099):

1. **When it returns 500**: Witness's birth_trigger.sh or birth_orchestrator.sh is starting but failing internally (likely container pool issue, DRY_RUN misconfiguration, or missing dependency)

2. **When it hangs**: The request handler starts but blocks on an async operation that never completes (container provisioning, SSH connection, Docker command that hangs)

3. **Critical clue**: Witness explicitly said their orchestrator takes 29-120s normally, up to 180s worst case. The hangs are exactly at 180s — meaning our timeout is firing BEFORE Witness's process finishes. But Witness's process never finished (evidence: multiple 180s timeouts in a row).

## What Witness Needs To Fix

1. **Check birth_orchestrator.sh / birth_trigger.sh** — something is hanging at one of the 10 steps
2. **Check container pool state** — aiciv-06..10 may be in a bad state from previous failed tests
3. **Check DRY_RUN flag** — confirm it's actually false in production
4. **Add response timeout on their side** — if orchestrator takes >120s, return an intermediate status instead of holding the connection
5. **Check if their server is single-threaded** — if Flask or gunicorn on their side is single-threaded, one hanging request blocks ALL subsequent requests (explains escalating hangs)

## Our Proxy — Possible Improvements

1. **Add `stream=False` explicitly** to requests call (already default, but explicit is clearer)
2. **Log response body on 500** — currently we suppress it for security (SEC-006), but temporarily enable to diagnose
3. **Reduce timeout** from 180s to 60s — Witness docs say 29s normal, 120s worst. 60s timeout would surface problems faster.
4. **Return Witness's actual error body** temporarily for debugging

## Files Referenced

- Proxy code: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` lines 191-241
- Log evidence: `/home/jared/projects/AI-CIV/aether/logs/purebrain_log_server.log` lines 344107-344697
- Witness build plan: `aiciv-comms-hub-bootstrap/_comms_hub/rooms/witness-aether/messages/2026/02/2026-02-25T143905Z-01KJAKTG6K4DJQ5MQKACW0B4CE.json`
