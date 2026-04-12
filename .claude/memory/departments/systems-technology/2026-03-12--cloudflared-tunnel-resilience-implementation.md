# Cloudflared Tunnel Resilience Implementation

**Date**: 2026-03-12
**Agent**: dept-systems-technology
**Topic**: CF Load Balancer + tunnel resilience for app.purebrain.ai / portal.purebrain.ai

---

## What Was Found (Existing Infrastructure)

The portal stack already had substantial resilience built in before this task:

- `cloudflared.service` — `Restart=always`, `RestartSec=5s`
- `cloudflared-health-check.timer` — runs every 60s, restarts cloudflared on failure
- `aether-portal.service` — `Restart=always`, `StartLimitBurst=10`
- `portal-health-check.timer` — runs every 60s, restarts portal if HTTP frozen
- nginx on 8099 with branded 503 fallback page (`/var/www/portal-fallback/503.html`)
- `/health` endpoint on port 8097 returning `{"status":"ok","civ":"aether","uptime":N}`

### Key Architecture
```
Cloudflare edge → cloudflared tunnel (fa55839c) → nginx:8099 → portal_server.py:8097
                                                  └─ *.purebrain.ai → Witness containers
```

## What Was Missing / Gaps Fixed

### Gap 1: cloudflared.service missing crash loop guard and restart alerts
**Fixed**: Added `StartLimitIntervalSec=300`, `StartLimitBurst=10`, `ExecStartPost` notify script.
**File**: `/etc/systemd/system/cloudflared.service`
**Backup**: `/etc/systemd/system/cloudflared.service.bak-20260312`

### Gap 2: cloudflared health check used log grep (unreliable) and wrong health URL
**Fixed**: Now uses `localhost:20241/ready` JSON `readyConnections` field directly.
Also added nginx-level check via new dedicated health port 8098.
**File**: `/usr/local/bin/cloudflared-health-check.sh`
**Backup**: `/usr/local/bin/cloudflared-health-check.sh.bak-20260312`

### Gap 3: No host-header-free internal health endpoint for nginx stack monitoring
**Fixed**: Added `server { listen 127.0.0.1:8098; }` block to nginx config that proxies
`/health` to portal_server.py without needing a Host header. Verified: returns 200.
**File**: `/etc/nginx/conf.d/purebrain-main.conf`
**Backup**: `/etc/nginx/conf.d/purebrain-main.conf.bak-20260312`

### Gap 4: CF Load Balancer not set up (CF_API_TOKEN + CF_ZONE_ID missing)
**Created**: Setup script ready to run once credentials are added to .env.
**File**: `/home/jared/projects/AI-CIV/aether/tools/cf_load_balancer_setup.sh`

---

## CF Load Balancer: Blocked on Credentials

To complete the CF Load Balancer setup, Jared needs to:

1. Add to `.env`:
   ```
   CF_API_TOKEN=<token with Load Balancing edit permission>
   CF_ZONE_ID=<purebrain.ai zone ID from CF Dashboard>
   ```
2. Run: `bash /home/jared/projects/AI-CIV/aether/tools/cf_load_balancer_setup.sh`

**Important note**: CF Load Balancing requires Pro plan or above. If on Free plan, the existing
watchdog infrastructure (4 ready tunnel connections + auto-restart) is functionally equivalent.

---

## Port Reference

| Port | Service | Purpose |
|------|---------|---------|
| 8097 | portal_server.py | Aether portal (Jared's admin portal) |
| 8098 | nginx internal | Health check relay (no Host header needed) |
| 8099 | nginx | All *.purebrain.ai routing + customer portals |
| 8443 | purebrain_log_server | Log/API server |
| 8765 | video GUI | PureBrain video management |
| 8870 | comms/cc | Command center |
| 20241 | cloudflared metrics | Tunnel metrics + /ready endpoint |

---

## Verification Commands

```bash
# Tunnel ready connections
curl -s http://localhost:20241/ready

# Internal health (no Host header)
curl -s http://127.0.0.1:8098/health

# Portal health direct
curl -s http://localhost:8097/health

# Test cloudflared health check manually
sudo /usr/local/bin/cloudflared-health-check.sh && echo "PASSED"

# Test portal health check manually
sudo /usr/local/bin/portal-health-check.sh && echo "PASSED"
```

---

## Files Changed

1. `/etc/systemd/system/cloudflared.service` — added crash loop guard + restart alerts
2. `/usr/local/bin/cloudflared-health-check.sh` — improved to use metrics API + nginx check
3. `/usr/local/bin/cloudflared-restart-notify.sh` — NEW: Telegram alert on tunnel restart
4. `/etc/nginx/conf.d/purebrain-main.conf` — added internal health server on 8098
5. `/home/jared/projects/AI-CIV/aether/tools/cf_load_balancer_setup.sh` — NEW: CF LB setup script
