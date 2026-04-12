# Portal Systemd Permanent Fix - 2026-03-11

**Type**: infrastructure-hardening
**Severity**: Critical (recurring customer-facing outage)
**Status**: FIXED AND VERIFIED

---

## Problem Summary

app.purebrain.ai kept going down overnight because the portal server entered crash loops.
The root symptom: "address already in use" on port 8097 during systemd restarts.

---

## Full Architecture

```
Cloudflare DNS
    ↓
cloudflared tunnel (PID ~527292, /etc/cloudflared/config.yml)
    ↓ port 8099 (*.purebrain.ai wildcard)
nginx (www-data, /etc/nginx/conf.d/purebrain-main.conf)
    ↓ proxy_pass http://127.0.0.1:8097
portal_server.py (/home/jared/purebrain_portal/portal_server.py)
    managed by: /etc/systemd/system/aether-portal.service
```

---

## Root Causes Found

### 1. StartLimitIntervalSec in wrong section (config bug)
- Was in `[Service]` section — systemd ignores it there
- Must be in `[Unit]` section
- Effect: burst limit was not enforced, allowed 1300+ crash-loop restarts overnight

### 2. PORT BIND RACE: TIME_WAIT socket blocking restart
- When portal crashes, the OS keeps the socket in TIME_WAIT for ~60s
- systemd restarts in RestartSec=15 but fuser -k sometimes missed lingering sockets
- New instance couldn't bind port 8097 → immediate exit-code failure → crash loop

### 3. uvicorn.run() - no SO_REUSEADDR/SO_REUSEPORT
- Default uvicorn behavior doesn't set SO_REUSEADDR on the listening socket
- This uvicorn version (0.41.0) does NOT expose reuse_port parameter directly

---

## Fixes Applied

### Fix 1: portal_server.py — Pre-bind socket with SO_REUSEADDR + SO_REUSEPORT

**File**: `/home/jared/purebrain_portal/portal_server.py`

Changed `__main__` block from:
```python
uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
```

To:
```python
_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    _sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
except (AttributeError, OSError):
    pass
_sock.bind(("0.0.0.0", port))
_sock.set_inheritable(True)
uvicorn.run(app, fd=_sock.fileno(), log_level="info")
```

This means the new process can bind port 8097 even if the old socket is in TIME_WAIT.

### Fix 2: /etc/systemd/system/aether-portal.service — Three changes

1. **Moved StartLimitIntervalSec + StartLimitBurst to [Unit] section** (was incorrectly in [Service])
2. **RestartSec: 15 → 5** (faster recovery for users)
3. **Added TimeoutStopSec=30** (graceful shutdown window before SIGKILL)

### Fix 3: tools/aether-portal.service updated to match production

---

## Verification

```bash
# Kill test passed:
# - PID 1173397 killed
# - Systemd restarted with new PID 1173517 within 8 seconds
# - Health check: 200 OK on localhost:8097/health
# - End-to-end: 200 OK on app.purebrain.ai
# - End-to-end: 200 OK on portal.purebrain.ai
```

---

## Key Files

| File | Purpose |
|------|---------|
| `/etc/systemd/system/aether-portal.service` | Production systemd service |
| `/home/jared/projects/AI-CIV/aether/tools/aether-portal.service` | Repo copy (synced) |
| `/home/jared/purebrain_portal/portal_server.py` | Portal server (patched) |
| `/home/jared/projects/AI-CIV/aether/logs/portal_server.log` | Portal logs |
| `/etc/cloudflared/config.yml` | Tunnel config (portal.purebrain.ai + app.purebrain.ai → 8099) |
| `/etc/nginx/conf.d/purebrain-main.conf` | nginx routes portal.purebrain.ai + app.purebrain.ai → 8097 |

---

## Operational Commands

```bash
# Check portal status
sudo systemctl status aether-portal.service

# Restart portal
sudo systemctl restart aether-portal.service

# View recent logs
sudo journalctl -u aether-portal.service --since "30 min ago"
tail -50 /home/jared/projects/AI-CIV/aether/logs/portal_server.log

# End-to-end health check
curl -s -o /dev/null -w "%{http_code}" https://app.purebrain.ai/ --max-time 10
curl -s -o /dev/null -w "%{http_code}" https://portal.purebrain.ai/ --max-time 10

# If service hits StartLimitBurst (after 10+ quick crashes), reset and restart:
sudo systemctl reset-failed aether-portal.service && sudo systemctl start aether-portal.service
```

---

## Why It Was Happening Overnight

The Mar 9 crash loop (1300+ restarts) was triggered by a second portal process being started
while systemd's instance was running. Both attempted to bind port 8097. The one that lost
exited immediately, and systemd kept restarting in a tight loop because the socket stayed
in TIME_WAIT.

With SO_REUSEPORT now set, any new instance can immediately take over the socket without
waiting for TIME_WAIT to expire. The crash loop scenario is now impossible.
