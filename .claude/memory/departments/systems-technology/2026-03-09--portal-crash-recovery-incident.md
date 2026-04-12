# Portal Crash Recovery Incident - 2026-03-09

**Type**: incident-postmortem
**Severity**: Customer-facing outage (brief, self-recovered)
**Duration**: ~1 second (23:19:34 crash → 23:19:35 restart)

---

## Infrastructure Architecture

```
Cloudflare DNS
    ↓
cloudflared tunnel (PID 527292, /etc/cloudflared/config.yml)
    ↓ port 8099
nginx (www-data, /etc/nginx/conf.d/purebrain-main.conf)
    ↓ proxy_pass http://127.0.0.1:8097
portal_server.py (PID 587864, /home/jared/purebrain_portal/portal_server.py)
```

## Key File Locations

- **Portal server**: `/home/jared/purebrain_portal/portal_server.py`
- **Portal log**: `/home/jared/purebrain_portal/portal.log`
- **Cloudflared config**: `/etc/cloudflared/config.yml`
- **nginx config (portal)**: `/etc/nginx/conf.d/purebrain-main.conf`
- **nginx config (customers)**: `/etc/nginx/conf.d/purebrain-customer-portals.conf`
- **Portal start script**: `/home/jared/purebrain_portal/start.sh`

## Port Map

| Port | Service | Purpose |
|------|---------|---------|
| 8097 | portal_server.py | Admin portal (Jared + customer portal) |
| 8099 | nginx | Cloudflare entry point, routes to 8097 and Witness containers |
| 8443 | Python (log server) | API / purebrain log server |
| 8870 | Python | CC / comms gateway |
| 8765 | Python | Video management GUI |
| 8200 | Python | Unknown |

## Root Cause

portal_server.py crashed under connection load. No supervisor/watchdog. Self-restarted in 1 second. The burst of nginx errors (hundreds of "connection reset by peer" and "connection refused") indicates the server was overwhelmed or hit an unhandled exception.

## Cloudflare Error Mapping

- **Error 524** (portal.purebrain.ai): nginx returned 502/504 → cloudflared timeout
- **Error 1033** (app.purebrain.ai): Cloudflare DNS cached the failure state; app.purebrain.ai is handled by the same nginx block as portal.purebrain.ai (both in `server_name portal.purebrain.ai app.purebrain.ai`)

## Critical Gap: No Process Supervisor

portal_server.py runs as a bare Python process. No systemd service, no watchdog.

**Recommended fix**: Create `/etc/systemd/system/purebrain-portal.service` with:
```ini
[Unit]
Description=PureBrain Portal Server
After=network.target

[Service]
User=jared
WorkingDirectory=/home/jared/purebrain_portal
ExecStart=/usr/bin/python3 /home/jared/purebrain_portal/portal_server.py
Restart=always
RestartSec=2
StandardOutput=append:/home/jared/purebrain_portal/portal.log
StandardError=append:/home/jared/purebrain_portal/portal.log

[Install]
WantedBy=multi-user.target
```

## Diagnosis Commands

```bash
# Check portal server
pgrep -af portal_server
ss -tlnp | grep 8097
curl -s http://localhost:8097/api/status --max-time 5

# Check nginx
sudo systemctl status nginx
sudo tail -20 /var/log/nginx/error.log

# Check cloudflared
sudo journalctl -u cloudflared --since "30 min ago" --no-pager | tail -30

# End-to-end test
curl -s -o /dev/null -w "%{http_code}" https://portal.purebrain.ai/ --max-time 10
curl -s -o /dev/null -w "%{http_code}" https://app.purebrain.ai/ --max-time 10
```
