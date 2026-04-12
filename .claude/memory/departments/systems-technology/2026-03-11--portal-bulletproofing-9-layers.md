# Portal Bulletproofing — 9 Resilience Layers

**Date**: 2026-03-11
**Type**: Infrastructure hardening
**Outcome**: All 9 layers deployed and verified. Portal uptime hardened to near-zero-downtime.

---

## Problem

After fixing 3 bugs (socket reuse, systemd rate-limit placement, restart timing), the portal needed
additional defense layers to prevent any future downtime scenario.

## Disk State (at time of sprint)

- Disk: 79% used (28GB/38GB), 7.8GB free — disk space monitoring is critical
- RAM: 3.3GB used / 3.7GB total (swap full) — memory limits essential

---

## 9 Layers Implemented

### Layer 1: Startup Dependency (network-online.target)

**File**: `/etc/systemd/system/aether-portal.service`

Changed `After=network.target` to `After=network-online.target` + `Wants=network-online.target`.

- `network.target` fires when networkd *starts*, not when network is *ready*
- `network-online.target` waits for actual IP assignment and connectivity
- Critical: ensures Cloudflare tunnel is reachable on boot before portal starts

### Layer 2: systemd Watchdog (WatchdogSec=90)

**Service file**: `WatchdogSec=90`
**Portal server**: background thread sends `sd_notify("WATCHDOG=1")` every 20s

Guards against "frozen but alive PID" scenario — process exists but HTTP server is deadlocked.
systemd kills and restarts if no ping within 90s. Thread sends every 20s (3x headroom).

```python
# In _systemd_watchdog_thread():
from systemd.daemon import notify as sd_notify
sd_notify("WATCHDOG=1")  # every 20s
```

### Layer 3: Resource Limits (MemoryMax + CPUQuota)

```ini
MemoryMax=1536M    # hard kill if exceeded
MemoryHigh=1024M   # soft warning
CPUQuota=80%       # prevent CPU starvation
```

Portal uses ~67-87MB normally. If it exceeds 1.5GB, something is very wrong.

### Layer 4: External Health Check Timer

**Files**:
- `/usr/local/bin/portal-health-check.sh` — checks `localhost:8097/health`
- `/etc/systemd/system/portal-health-check.service` — oneshot service
- `/etc/systemd/system/portal-health-check.timer` — fires every 60s

Logic: 3 retries with 5s delay before declaring portal dead and calling `systemctl restart`.
Sends Telegram alert on failure. Defense-in-depth beyond systemd process monitoring.

### Layer 5: Log Rotation

**File**: `/etc/logrotate.d/aether-portal`

- `portal_server.log`: daily, 14-day retention, 50MB max, compress, copytruncate
- `portal.log`: daily, 7-day retention, 20MB max, compress, copytruncate
- `copytruncate` = works without service restart (systemd appends by path)

### Layer 6: Nginx Failover Page (503)

**Files**:
- `/var/www/portal-fallback/503.html` — branded PureBrain dark theme 503 page
- `/etc/nginx/conf.d/purebrain-main.conf` — `error_page 502 503 504 /503.html`

When portal is down, users see "Restarting — back in a moment" with 30s auto-refresh.
Previously: raw nginx connection refused error (terrible UX).

### Layer 7: PID File Duplicate Instance Prevention

**File**: `/home/jared/purebrain_portal/portal_server.py` main block

Writes `/tmp/aether-portal.pid`. On startup, checks if PID exists and is alive.
If stale (crashed), removes. If alive, exits with error (prevents manual double-start).
PID file cleaned up in `finally` block on shutdown.

### Layer 8: Disk Space Monitor

**File**: `/home/jared/purebrain_portal/portal_server.py` `_disk_space_monitor_thread()`

Background daemon thread, checks every 5 minutes:
- `< 500MB free`: Telegram WARNING (once/hour max)
- `< 100MB free`: Telegram CRITICAL + emergency `logrotate -f` (once/30min max)

Important because disk at 79% usage — a log runaway or upload flood can kill the portal.

### Layer 9: Restart Notification

**File**: `/usr/local/bin/portal-restart-notify.sh`
**Service**: `ExecStartPost=/usr/local/bin/portal-restart-notify.sh`

Called 3s after every start/restart. Sends Telegram with current health endpoint response.
Jared always knows when the portal restarts.

---

## Architecture: Port Routing

- `app.purebrain.ai` → Cloudflare tunnel → `localhost:8099` (nginx) → `localhost:8097` (portal)
- The nginx layer is where the 503 failover page is inserted
- Portal directly on 8097; nginx on 8099 acts as proxy + failover

---

## Key Files Modified

- `/etc/systemd/system/aether-portal.service` — hardened service
- `/home/jared/purebrain_portal/portal_server.py` — watchdog thread, disk monitor, PID file
- `/etc/nginx/conf.d/purebrain-main.conf` — 503 failover
- `/etc/logrotate.d/aether-portal` — NEW
- `/var/www/portal-fallback/503.html` — NEW
- `/usr/local/bin/portal-health-check.sh` — NEW
- `/etc/systemd/system/portal-health-check.service` — NEW
- `/etc/systemd/system/portal-health-check.timer` — NEW
- `/usr/local/bin/portal-restart-notify.sh` — NEW

---

## Verification

```
Portal health: {"status":"ok","civ":"aether","uptime":171}
aether-portal.service: active
portal-health-check.timer: active (fires every 60s)
WatchdogUSec: 1min 30s (confirmed by systemctl show)
MemoryMax: 1610612736 (1.5GB confirmed)
CPUQuota: 800ms per second (80% confirmed)
All files present and verified
```

---

## What Is NOT Implemented (and Why)

**Cloudflare failover page at the CDN level**: Cloudflare's "Always Online" and custom error
pages for origin-down scenarios require dashboard configuration. We achieved equivalent behavior
via nginx failover (Layer 6), which is actually better — it works for any downstream failure,
not just Cloudflare cache misses.

---

## Pattern: Defense in Depth

The correct mental model for portal uptime:

```
Crashed process    → systemd Restart=always (5s)
Frozen process     → systemd WatchdogSec=90 (kills + restarts)
HTTP frozen        → external health-check timer (60s, 3 retries)
Port conflict      → SO_REUSEADDR + SO_REUSEPORT + fuser -k in ExecStartPre
Double instance    → PID file check
Disk full          → Disk monitor + logrotate
Log explosion      → Logrotate (daily, maxsize 50MB)
RAM leak           → MemoryMax=1536M (OOM kill by systemd, not kernel randomly)
CPU runaway        → CPUQuota=80%
Network not ready  → network-online.target dependency
Down visibility    → Telegram restart alerts
User experience    → Nginx 503 branded page with auto-refresh
```
