# Portal 500 Error - Memory Pressure Crash Loop
**Date**: 2026-03-16
**Agent**: dept-systems-technology
**Type**: gotcha + pattern

## Incident Summary
Jared reported 500 error at 13:01 on app.purebrain.ai. Portal was in a crash-restart loop
from ~12:20 UTC through ~13:38 UTC (over 1 hour of degraded/down service).

## Root Cause: Memory Pressure Crash Loop

### Timeline (UTC)
- 12:20 — Manual `systemctl restart aether-portal.service` (Jared or agent triggered)
- 12:36 — Portal deactivated again (only ~15 min runtime before crash)
- 13:06 — Portal crashed, systemd auto-restart (restart counter: 1), ran 13 seconds then crashed again (exit code 1/FAILURE)
- 13:06:53 — Restart counter: 2, ran ~19 min before crash
- 13:25 — Restart counter: 3, ran ~12 min
- 13:37 — Restart counter: 4, ran 4.5 seconds — fastest crash yet
- 13:38:08 — Restart counter: 5, **portal stabilized and has been running since**
- 13:38–16:xx — Nginx logged ~40 "Connection refused" errors during the down window

### Evidence for Memory Pressure
- Server has 3.7Gi RAM total
- portal_server.py currently consuming 795MB RSS (20.8% of RAM) — already approaching its 1.5GB memory max
- `claude` main session consuming 514MB (13.1%)
- Swap at 987Mi / 2.0Gi (nearly half used)
- Disk at 81% used (29G/38G)
- During the crash window, multiple claude instances + portal + comms-gateway were competing for limited RAM
- Crash pattern: progressively shorter run times before crash (15min → 19min → 12min → 4.5s) = classic memory exhaustion spiral

### A-C-Gee Timeout Correlation
- The A-C-Gee forwarding timeouts (visible throughout the log) are a symptom, NOT a cause
- They indicate A-C-Gee hub is unreachable, likely independently — not causing portal 500s
- Log server correctly retries 3x then logs ERROR and moves on — this is safe behavior

### Why Portal Recovered at 13:38
Likely one of:
1. Memory freed up as a competing process (claude BOOP or other) completed
2. systemd ExecStartPre kills anything on port 8097 (`fuser -k 8097/tcp`) which may have freed leaked sockets
3. 5th restart attempt happened to land in a moment of sufficient available RAM

## Current State (as of 16:33 UTC)
- portal HTTP: 200 OK (0.36s response time)
- /api/compact/status: responding (returns {"error":"unauthorized"} = expected for unauthenticated)
- aether-portal.service: active (running) since 13:38:14, ~3h uptime
- No new nginx errors since 13:38

## Recommended Fixes (Priority Order)
1. **IMMEDIATE**: Add memory limit tuning to portal_server.py startup or nginx to detect OOM earlier
2. **SHORT TERM**: Add health check endpoint monitoring with auto-alert to Telegram when portal is down
3. **MEDIUM TERM**: Upgrade server RAM (currently 3.7Gi — marginal for this workload)
4. **MEDIUM TERM**: Investigate portal_server.py memory leak — why does it grow to 795MB+?
5. **LONG TERM**: Consider portal memory profiling to find leak source

## Key Files
- Portal service: `/etc/systemd/system/aether-portal.service`
- Portal server: `/home/jared/purebrain_portal/portal_server.py`
- Nginx error log: `/var/log/nginx/error.log`
- Log server: `/home/jared/projects/AI-CIV/aether/logs/purebrain_log_server.log`
