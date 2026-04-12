# Memory: Witness /api/birth/start Hangs — Root Cause Diagnosis

**Date**: 2026-02-25
**Agent**: devops-engineer
**Type**: teaching + operational
**Topic**: Network diagnosis of Witness birth/start endpoint hanging while /health returns instantly

---

## Root Cause: Witness /api/birth/start Handler is Blocking (Not a Network Issue)

### Evidence Summary

| Test | Result |
|------|--------|
| TCP connect to 104.248.239.98:8099 | OK |
| GET /health | 200 OK, instant |
| GET /api/birth/start | 404 (correct — POST only) |
| POST /api/birth/start empty body | TCP accepted, then hangs indefinitely |
| POST /api/birth/start real payload | TCP accepted, then hangs indefinitely |
| OPTIONS /api/birth/start | TCP accepted, then hangs indefinitely |
| Our proxy POST /api/proxy/birth/start | Also hangs — proxy forwards to Witness, which hangs |
| ESTABLISHED sockets | 6 sockets in ESTABLISHED state to :8099 — server accepts but never responds |

### What This Proves

1. **NOT a network/firewall issue** — TCP connects successfully every time
2. **NOT a routing issue** — /health on same port works instantly
3. **NOT a CORS issue** — OPTIONS itself hangs (never gets headers back)
4. **The Witness /api/birth/start handler is frozen/blocked** — TCP is accepted but no HTTP response is ever written

### Log Server Evidence

The purebrain_log_server.log confirms the proxy IS reaching Witness:
```
16:42:19 - proxy/birth/start: forwarding to Witness (ip=108.35.12.204)
16:44:31 - Witness proxy timeout: POST /api/birth/start (limit=180s)  ← 180 seconds later
```
Our proxy waited the full 180-second timeout. Witness accepted the TCP connection but wrote zero bytes back.

### Likely Causes (for Witness team to investigate)

1. **Single-threaded server blocking on /birth/start**: Python's BaseHTTP server (confirmed from /health response header `Server: BaseHTTP/0.6 Python/3.12.3`) is single-threaded by default. If /birth/start handler is synchronous and waits on container provisioning (which takes 29–145s), it blocks ALL other requests INCLUDING itself. The 6 ESTABLISHED sockets are all queued waiting for the one handler to finish.

2. **Handler deadlock**: The /birth/start handler may be awaiting a lock or resource held by a previous hung request.

3. **Container provisioning system is down/stuck**: If /birth/start calls out to Docker/container orchestration and that subsystem is hung, the handler would block indefinitely.

### What /health Does Differently

/health returns instantly because it's a simple dict return — no I/O, no blocking calls. If the server has any multi-threading, /health gets through. If single-threaded, /health was the last request to complete before the queue filled.

---

## The Server Uses BaseHTTP (Python's Default Single-Threaded Server)

From /health response:
```
Server: BaseHTTP/0.6 Python/3.12.3
HTTP/1.0
```

This is a critical finding:
- `HTTP/1.0` (not 1.1) — no keep-alive, no pipelining
- `BaseHTTP` — Python's `http.server.BaseHTTPRequestHandler`
- **Single-threaded by default** — one request at a time
- If the handler for /birth/start never returns, the server is COMPLETELY stuck

---

## Fix Path (for Witness team)

**Option A (immediate)**: Restart the Witness server process to clear the stuck handler
**Option B (proper fix)**: Make the /birth/start handler use threads or async I/O — start provisioning asynchronously, return an accepted/pending response immediately, poll separately
**Option C (architecture)**: Switch from BaseHTTP to Flask/FastAPI with threading enabled

---

## Our VPS Is Not the Problem

- Our proxy server (89.167.19.20:8443, Flask) works fine
- It correctly forwards to Witness and waits
- The 504 timeout responses from our proxy are correct behavior — we time out and return an error
- No iptables rules affecting Witness traffic

