# Portal 500 Error - Root Cause Analysis
**Date**: 2026-03-16
**Type**: incident-postmortem
**Agent**: dept-systems-technology

---

## Incident Summary

Jared reported a 500 server error at app.purebrain.ai at 13:01 EST on 2026-03-16.
Portal returned 200 after some time. Root cause identified.

---

## Root Cause: portal_server.py Crash (port 8097)

The portal server (uvicorn, Python, port 8097) at `/home/jared/purebrain_portal/portal_server.py`
crashed and stopped responding. nginx proxies all app.purebrain.ai traffic to 127.0.0.1:8097.
When 8097 is not responding, nginx returns 502/500 to users.

### Timeline

- **12:19 UTC** - nginx errors begin: "upstream timed out" on port 8097 (portal unresponsive)
- **12:20-13:38 UTC** - sustained "Connection refused" to 8097 from nginx (portal fully down)
- **13:01 EST (= ~18:01 UTC)** - Jared reports 500 error via Telegram
- **~13:06 UTC** - "Connection reset by peer" errors (portal trying to restart/crashing on startup)
- **~19:24 UTC** - portal_server.py process relaunched (pid 2156306), port 8097 now LISTEN
- **Current** - portal_server.py running, 8097 returning 200

### Evidence

```
nginx error.log:
2026/03/16 12:20:59 connect() failed (111: Connection refused) upstream: http://127.0.0.1:8097/api/...
2026/03/16 13:06:54 recv() failed (104: Connection reset by peer) upstream: http://127.0.0.1:8097/api/...
2026/03/16 13:38:18 connect() failed (111: Connection refused) upstream: http://127.0.0.1:8097/...

Portal process current: pid 2156306, started ~19:24 today, port 8097 LISTEN, health=200
```

---

## Secondary Issue: A-C-Gee Forwarding Timeouts (Ongoing/Separate)

NOT related to the 500 error, but is a persistent problem flooding logs.

- A-C-Gee endpoint: `http://5.161.90.32:3001/api/landing-chat`
- Status: **UNREACHABLE** (tested 2026-03-16 ~19:30)
- Pattern: Every conversation on purebrain.ai triggers 3 retry attempts x 30s timeout = 90s blocking
- Session `purebrain_1773676948023_kre4nt1xv` generated 20+ ERROR entries today
- This does NOT cause 500s for users - forwarding happens async in background threads
- But it floods the log with noise and blocks background threads for 90s each

---

## Portal Health Monitor Gap

The `portal_health_check.sh` cron (runs every 2 minutes) checks via:
1. curl to `http://localhost:8099/` (nginx internal)
2. Restarts cloudflared if unhealthy

**Problem**: The monitor checks nginx (8099) which proxies to portal (8097). If portal dies,
nginx still runs but returns 502. The monitor script does restart cloudflared (not portal_server.py)
in this scenario. The portal_server.py restart is only triggered if `pgrep -f portal_server.py` fails.

No portal_health.log entries for March 16 = the portal_health_check.sh cron was NOT running
or not triggering for this outage. This means the auto-recovery for this crash type may not be working.

---

## Current Status

- Portal: UP (pid 2156306, port 8097, /health returns 200)
- Log server: UP (port 8443)
- A-C-Gee forwarding: DOWN (5.161.90.32:3001 unreachable) - cosmetic issue, logs only
- Portal health monitor: Status unknown - zero entries for March 16

---

## Recommended Fixes

### Fix 1: Portal auto-restart on crash (HIGH PRIORITY)
The portal_health_check.sh already has logic to restart portal_server.py if pgrep fails.
But the process crashed in a way that left it either:
a) Crashing on startup fast (Connection reset by peer at 13:06), OR
b) Zombie/stuck process that pgrep still detected

Recommend: Add `curl --max-time 5 http://localhost:8097/health` check in health script.
If health endpoint fails even though pgrep passes, kill + restart.

### Fix 2: A-C-Gee timeout reduction (MEDIUM PRIORITY)
Current: `timeout=30` per attempt, 3 retries = up to 90s per conversation.
Recommend: Reduce to `timeout=5` - if A-C-Gee is down, fail fast.
This keeps background threads from being blocked.

### Fix 3: A-C-Gee endpoint investigation (MEDIUM PRIORITY)
5.161.90.32:3001 is completely unreachable.
Need to alert A-C-Gee team (via comms hub) that their landing-chat endpoint is down.
Consider adding circuit breaker - if 3+ consecutive failures, stop retrying for 1 hour.
