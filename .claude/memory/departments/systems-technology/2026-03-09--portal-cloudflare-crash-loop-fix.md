# Portal Cloudflare Error Fix — 2026-03-09

## Problem
- Error 1033 (Cloudflare Tunnel error) on app.purebrain.ai
- Error 524 (timeout — origin took too long) on portal.purebrain.ai
- Portal taking 7+ seconds to respond
- aether-portal.service had 1930 restart attempts in ~8 minutes

## Root Cause
**Port 8097 "address already in use" crash-loop.**

When the portal process is killed (SIGKILL or crash), the OS keeps the port in
TIME_WAIT for ~60s. Systemd's `Restart=always` immediately starts a new process,
which fails to bind port 8097, exits with code=1, triggering another restart in 10s.
This cascaded 1930 times before the process finally won a race.

The 7-second timeout and Error 524 were secondary effects of the process starting
while the port was still in TIME_WAIT — the first successful bind happened 1930
restarts later, and the cold start of the new process was slow.

## Fixes Applied

### 1. systemd: ExecStartPre port kill + StartLimitBurst
File: `/etc/systemd/system/aether-portal.service`

Added:
```
ExecStartPre=/bin/bash -c "fuser -k 8097/tcp 2>/dev/null || true"
ExecStartPre=/bin/sleep 1
RestartSec=15          # was 10s — more breathing room
StartLimitIntervalSec=300
StartLimitBurst=10     # circuit-breaker: stop after 10 fails in 5 min
```

The `fuser -k 8097/tcp` kills any lingering process on port 8097 before
the new server tries to bind. `|| true` prevents failure if port is clear.

### 2. Cloudflare config: connectTimeout 30s → 120s
File: `/etc/cloudflared/config.yml`

Changed portal.purebrain.ai and *.purebrain.ai entries:
```yaml
connectTimeout: 120s     # was 30s
keepAliveConnections: 10  # new
keepAliveTimeout: 90s     # new
```

Prevents Error 524 during legitimate slow starts (cold start, heavy load).
WebSocket connections are long-lived — need keepalive settings.

### 3. Nginx: add proxy_connect_timeout
File: `/etc/nginx/conf.d/purebrain-main.conf`

Added:
```nginx
proxy_connect_timeout 90s;   # was default 60s
```

Aligns with Cloudflare tunnel timeout (120s) so nginx doesn't give up before CF does.

### 4. Health endpoint (already existed)
`/health` on portal_server.py returns `{"status":"ok","civ":"...","uptime":...}` — no auth required.
Useful for external monitoring without Cloudflare authentication.

## Verification Results
After fix:
- `LOCAL_8097 /health`: 200 in 0.098s
- `NGINX_8099 /health` (with Host header): 200 in 0.003s
- `https://portal.purebrain.ai/health`: 200 in 0.188s
- `https://app.purebrain.ai/health`: 200 in 0.166s
- `https://portal.purebrain.ai/` (homepage): 200 in 1.188s (was ~7s)
- Service restart counter: reset to 0, running clean

## Files Changed
- `/etc/systemd/system/aether-portal.service`
- `/etc/cloudflared/config.yml`
- `/etc/nginx/conf.d/purebrain-main.conf`

## Key Pattern for Future
Whenever `RestartSec` is short (under 30s) and the process binds a port:
ALWAYS add `ExecStartPre` to kill stale port holders. Otherwise crash-loops
compound instantly into hundreds of restart failures within minutes.

## Related Services NOT changed (tunnel intact)
- api.purebrain.ai (8443) — unchanged
- video.purebrain.ai (8765) — unchanged
- cc.purebrain.ai / comms.purebrain.ai (8870) — unchanged
