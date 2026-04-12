# Memory: Witness Proxy No-Response Root Cause

**Date**: 2026-02-25
**Type**: teaching
**Topic**: Witness birth API at 104.248.239.98:8099 timing out on all requests from our proxy

## What Happened

Our proxy at `https://89.167.19.20:8443/api/proxy/birth/start` was hitting 504 timeouts every time.
Logs showed "forwarding to Witness" but no response after 180s.

## Root Cause: WITNESS SERVER IS DOWN / NOT RESPONDING TO HTTP

The TCP connection on port 8099 establishes successfully (SYN/SYN-ACK), but the server never
sends back an HTTP response. The 3-way handshake completes, our side sends the full HTTP request
body, then... nothing. No HTTP/1.1 response line. No headers. No body.

This is NOT a proxy code bug. The proxy code (`_proxy_to_witness`) is correct:
- Uses `requests` library (proper connection handling)
- `Content-Type: application/json` header is correct
- `data=body` passes raw bytes correctly
- timeout=180s is appropriate
- No firewall blocking (OUTPUT iptables chain is wide open)

## Evidence

1. `curl -v --max-time 15 http://104.248.239.98:8099/health` → TCP connects, body sent, timeout
2. `curl -v --max-time 10 http://104.248.239.98:8099/api/birth/start -X POST ...` → same result
3. All 3 proxy endpoints (birth/start, birth/code, portal-status) time out identically
4. But Witness DID respond on Feb 25 at 11:56 and 16:17/16:24 — with HTTP 500s (~2.5 min delay)

## Timeline Pattern (Feb 25)

- 11:53:58 → forwarding
- 11:56:35 → status=500 (2m37s later) — Witness was alive but erroring
- 16:17:07 → forwarding
- 16:19:44 → status=500 (2m37s later) — still responding but erroring
- 16:21:21 → forwarding (two concurrent requests)
- 16:21:37 → forwarding (second)
- 16:23:59 → one 500 back — only ONE of the two concurrent calls got a response
- 16:24:37 → first call timed out (180s) — Witness may have crashed handling concurrent load
- 16:34:17 → forwarding — NO RESPONSE (180s timeout)
- 16:41-16:43 → 3 more forwarding calls — all 3 timed out

**Hypothesis**: Witness server is crashing/hanging under concurrent requests. After the 16:21/16:23
double-request, Witness stopped responding entirely.

## What Is NOT Wrong on Our Side

1. `_proxy_to_witness()` code is clean and correct
2. Flask is running threaded=True (no single-thread blocking)
3. iptables OUTPUT chain: ACCEPT all (no firewall blocking outbound)
4. Content-Type header is correct
5. Body is forwarded as raw bytes (correct for `requests.post(data=body, ...)`)
6. Connection pooling is fine (requests library handles this)
7. Timeout 180s matches Witness's stated internal limit

## Fix Required

The Witness server team (A-C-Gee / Corey) needs to:
1. Restart the Witness process on 104.248.239.98
2. Check Witness logs for crash reason
3. Fix the ~2.5 min response time on /api/birth/start (too slow for user UX)
4. Fix crash under concurrent requests

## Proxy Code Improvements We Could Make (optional)

1. Add `X-Request-ID` header to _proxy_to_witness for traceability across systems
2. Add a connect timeout separate from read timeout (currently both are `timeout=180`)
   - Example: `timeout=(10, 180)` = 10s connect, 180s read
   - This would catch "TCP open but no HTTP response" faster
3. Add a health check before proxying (not worth the extra call though)
