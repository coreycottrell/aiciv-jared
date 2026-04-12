# PureBrain Portal 502 Recovery Guide

**Written by**: dept-systems-technology
**Date**: 2026-03-12
**Purpose**: Remote troubleshooting guide for customer portal 502 errors

---

## Quick Reference Card

> Customer says: "My portal is showing a 502 error"
> Translation: The web server can't reach the backend Python server
> Most likely cause: `portal_server.py` process crashed or never started
> Fastest fix: SSH in, restart the `aether-portal` systemd service

---

## 1. What a 502 Means in Our Stack

A 502 Bad Gateway error means the reverse proxy (nginx or Caddy) received the request successfully but could not get a response from the backend server behind it.

The full request path for a PureBrain customer portal is:

```
Browser → HTTPS (443)
    ↓
Cloudflare / DNS
    ↓
Nginx on Aether's VPS (port 8099 listener)
    ↓  (proxy_pass to customer container)
Customer Container (Hetzner Docker)
    ↓
Caddy inside container → localhost:8097
    ↓
portal_server.py (Python/Starlette, port 8097)
    ↓
tmux session (Claude Code running the AI)
```

A 502 can break at two points:

| Where the 502 fires | What it means |
|---|---|
| Nginx on Aether's VPS | Cannot reach the customer container (container down, Docker networking issue, container's Caddy is down) |
| Caddy inside the container | Cannot reach `portal_server.py` on port 8097 (the Python server is crashed or not running) |

**By far the most common cause**: `portal_server.py` is not running on port 8097 inside the container. This is what you should check first.

---

## 2. Remote Diagnosis Steps (via SSH)

### Step 1 — Confirm which domain is 502'ing

Get the customer's portal URL. It will be one of:
- `https://CUSTOMERNAME.ai-civ.com` (direct container URL via Caddy)
- `https://CUSTOMERNAME.purebrain.ai` (proxied through Aether's nginx)

Both point to the same container, but knowing which domain helps isolate whether the issue is Aether's nginx or the container itself.

### Step 2 — Test the health endpoint directly

```bash
# From any machine — does the portal respond at all?
curl -s https://CUSTOMERNAME.ai-civ.com/health
# Expected: {"status":"ok","civ":"...","uptime":N}
# 502: backend is down
# Connection refused: DNS/network issue before it even reaches the container
```

### Step 3 — SSH into the customer container

```bash
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new USER@CONTAINER_HOST
```

For Hetzner fleet containers, the host is the Hetzner VPS IP. Check your customer registry for the container SSH details.

### Step 4 — Run the full health check

Copy and paste this entire block:

```bash
echo "=== PORTAL PROCESS ==="
pgrep -af portal_server 2>/dev/null || echo "(NOT RUNNING)"

echo ""
echo "=== PORTAL SERVICE ==="
systemctl status aether-portal --no-pager 2>/dev/null || echo "(no systemd service found)"

echo ""
echo "=== PORT 8097 ==="
ss -tlnp 2>/dev/null | grep 8097 || echo "(nothing listening on 8097)"

echo ""
echo "=== CADDY ==="
pgrep -af caddy 2>/dev/null || echo "(Caddy not running)"
systemctl status caddy --no-pager 2>/dev/null | grep -E "Active:|●" || true

echo ""
echo "=== CLAUDE / TMUX ==="
pgrep -af claude | head -3 || echo "(Claude not running)"
tmux list-sessions 2>/dev/null || echo "(no tmux sessions)"

echo ""
echo "=== DISK ==="
df -h / | tail -1

echo ""
echo "=== MEMORY ==="
free -h | head -2

echo ""
echo "=== RECENT PORTAL LOGS ==="
tail -20 ~/projects/AI-CIV/*/logs/portal_server.log 2>/dev/null \
  || tail -20 ~/purebrain_portal/portal_server.log 2>/dev/null \
  || echo "(no log found)"
```

### Step 5 — Read the diagnosis

Use this table to identify the problem:

| What you see | Diagnosis | Go to section |
|---|---|---|
| `(NOT RUNNING)` for portal process | portal_server.py crashed | Section 3, Fix A |
| Service shows `failed` or `inactive` | Systemd service failed | Section 3, Fix B |
| Port 8097 empty but service looks active | Server bound to wrong port or crashed silently | Section 3, Fix A |
| Caddy not running | Reverse proxy inside container is down | Section 3, Fix C |
| Disk at 95%+ | Disk full causing crash | Section 3, Fix D |
| Memory near 100% | OOM causing crash | Section 3, Fix E |
| Everything looks fine but still 502 | Caddy config issue or networking | Section 3, Fix F |

---

## 3. Common Fixes Ranked by Likelihood

### Fix A — Restart portal_server.py (most common, ~70% of cases)

The Python server crashed or was never started. If a systemd service manages it:

```bash
# Restart via systemd (preferred — will auto-restart on future crashes)
sudo systemctl restart aether-portal
sleep 5

# Verify it came up
systemctl status aether-portal --no-pager
curl -s http://localhost:8097/health
```

If there is no systemd service, start it manually:

```bash
# Find the portal directory
PORTAL_DIR=$(find ~/purebrain_portal ~/portal -maxdepth 0 -type d 2>/dev/null | head -1)
echo "Portal dir: $PORTAL_DIR"

# Kill any zombie process first
pkill -f portal_server.py 2>/dev/null; sleep 2

# Start with logging
nohup python3 "$PORTAL_DIR/portal_server.py" >> "$PORTAL_DIR/portal_server.log" 2>&1 &
sleep 3

# Confirm
pgrep -af portal_server
curl -s http://localhost:8097/health
```

### Fix B — Systemd service in failed state (~15% of cases)

```bash
# Check why it failed
journalctl -u aether-portal -n 50 --no-pager

# Common causes shown in logs:
#   - "Address already in use" → port conflict (kill the conflict first)
#   - "ModuleNotFoundError" → missing Python dependency
#   - "Permission denied" → wrong user or file permissions

# Reset and restart
sudo systemctl reset-failed aether-portal
sudo systemctl start aether-portal
sudo systemctl status aether-portal --no-pager
```

If logs show a missing Python module:

```bash
pip3 install starlette uvicorn websockets
sudo systemctl start aether-portal
```

If logs show port already in use:

```bash
# Find what's using 8097
ss -tlnp | grep 8097
# Kill it
sudo fuser -k 8097/tcp
sudo systemctl start aether-portal
```

### Fix C — Caddy not running inside container (~8% of cases)

Caddy is the reverse proxy inside the container that routes HTTPS traffic to port 8097.

```bash
# Check Caddy
systemctl status caddy --no-pager
journalctl -u caddy -n 30 --no-pager

# Restart Caddy
sudo systemctl restart caddy
sleep 3

# Verify — test from outside (replace with actual domain)
curl -s https://CUSTOMERNAME.ai-civ.com/health
```

If Caddy shows a TLS cert issue (common after VPS reboots):

```bash
# Force cert renewal
sudo caddy reload --config /etc/caddy/Caddyfile 2>/dev/null \
  || sudo systemctl reload caddy
```

### Fix D — Disk full (~4% of cases)

When the VPS disk fills up, processes cannot write logs and crash.

```bash
# Check current usage
df -h /

# If >90%, free up space fast
# 1. Clear old Claude session logs (biggest offender)
find ~/.claude/projects -name "*.jsonl" -size +50M -mtime +7 -delete

# 2. Truncate large logs (don't delete — preserve recent entries)
find ~/projects/AI-CIV/*/logs -name "*.log" -size +100M \
  -exec truncate -s 10M {} \;

# 3. Check disk again
df -h /

# Then restart portal
sudo systemctl restart aether-portal
```

### Fix E — Out of memory (~2% of cases)

```bash
# Check memory
free -h

# If available < 100MB, the process is being OOM-killed
# Kill non-essential processes first
pkill -f telegram_bridge 2>/dev/null
sleep 2

# Check if portal can start now
sudo systemctl start aether-portal
free -h
```

If OOM is persistent, the VPS needs a RAM upgrade or the AI's context is too large (restart the Claude session to clear context).

### Fix F — Everything looks fine, still 502 (~1% of cases)

This usually means the proxy layer above the container is the issue.

```bash
# Test if portal_server actually responds locally
curl -s http://127.0.0.1:8097/health
# If this returns {"status":"ok",...} then the server IS running

# If local curl works but external URL is 502,
# the problem is in Caddy's routing or Aether's nginx upstream

# Check Caddy is binding to 0.0.0.0 (not just 127.0.0.1)
ss -tlnp | grep -E "8097|443|80"

# Reload Caddy config
sudo systemctl reload caddy
```

If you are an Aether operator and the customer's container is healthy but `CUSTOMERNAME.purebrain.ai` gives 502:

```bash
# On Aether's VPS — check nginx is routing correctly
sudo nginx -t
sudo systemctl reload nginx

# Check the customer's entry in the nginx config
grep -A 20 "CUSTOMERNAME" /etc/nginx/conf.d/purebrain-customer-portals.conf
```

---

## 4. Jared's Non-Technical Customer Script

Use this when walking a customer through recovery over message, email, or phone. They do not need to understand how it works.

---

**Script for Jared:**

> "Thanks for letting me know — let me get you back online. This should only take about 5 minutes.
>
> Your portal temporarily lost its connection to the AI behind it. It's like your phone losing its Wi-Fi — the portal is still there, it just can't talk to the AI right now.
>
> I'm going to restart it for you remotely. You don't need to do anything — I'll send you a message here once it's back up. Give me a few minutes."

Then you fix it via SSH using the steps in Section 3.

Once it is back up:

> "You're back online. Try refreshing your portal page — your AI is running normally again and has been notified you're back.
>
> For future reference: if you ever see this again, the best first step is always to refresh the page and wait 60 seconds. If it doesn't clear up, just message me and I'll have you back in under 5 minutes."

---

**If the customer sees a blank page instead of a 502:**

> "That blank page usually means your browser cached the error. Do a hard refresh: hold Shift and click the refresh button (or Ctrl+Shift+R on Windows, Cmd+Shift+R on Mac)."

---

**If the customer is asked for a login token they don't have:**

> "Your bearer token is in the welcome email I sent when your portal was set up — it's a long string of letters and numbers. If you can't find it, reply here and I'll send it again."

---

## 5. What Can Be Done Without SSH Access

Limited options exist without SSH, but they are worth trying first.

### Option 1 — Wait and retry (always try this first)

Brief process restarts can resolve themselves if systemd is configured with `Restart=always`. Wait 30-60 seconds and refresh.

### Option 2 — Check the health endpoint

```bash
curl -s https://CUSTOMERNAME.ai-civ.com/health
```

- Returns `{"status":"ok"}` → portal is up, the 502 was transient. Customer should do a hard refresh.
- Returns 502 → server is genuinely down. SSH required.
- Returns connection refused → network/DNS issue, not a server issue.

### Option 3 — Trigger a restart via the AI itself (if it's still running)

If the Claude tmux session is alive but the portal process died, and the AI has Telegram access, you can send the AI a message asking it to restart the portal:

> "Your portal server is down. Please restart it: `sudo systemctl restart aether-portal`"

The AI can run this command and confirm it is back up.

### Option 4 — Use the civ_recovery.sh script (if you have SSH to any machine)

If you have SSH to any machine that has SSH access to the customer VPS:

```bash
# Run the recovery tool (part of Aether's toolkit)
bash /home/jared/projects/AI-CIV/aether/tools/civ_recovery.sh USER@CUSTOMER_HOST --quick
```

This handles the restart automatically and notifies the customer via Telegram.

---

## 6. Prevention Measures

### Must-haves for every customer VPS

**1. Systemd with auto-restart**

The `aether-portal.service` file must be in place with `Restart=always` and `RestartSec=10`. This recovers the portal automatically after a crash without any human intervention.

```ini
[Service]
Restart=always
RestartSec=10
```

Verify: `systemctl is-enabled aether-portal` should return `enabled`.

**2. Adequate disk space**

Keep disk usage below 75%. Set up a cron job to alert when disk crosses 80%:

```bash
# Add to crontab: crontab -e
0 */6 * * * df / | awk 'NR==2 {if ($5+0 > 80) print "DISK ALERT: "$5" used on portal VPS"}' | \
  grep "ALERT" && bash ~/tools/tg_send.sh "DISK ALERT: Portal VPS disk over 80%" || true
```

**3. Log rotation**

Without rotation, Claude's JSONL session logs fill the disk within weeks on active systems.

```bash
# /etc/logrotate.d/aether-portal
/home/*/projects/AI-CIV/*/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    size 50M
}
```

**4. Memory headroom**

Provision each customer VPS with at minimum 4GB RAM. Claude's context window plus the portal server plus Telegram bridge typically use 1.5-2GB under normal operation. Running near the limit causes intermittent OOM kills that look like random crashes.

**5. Caddy auto-renewal**

Caddy handles TLS certificate renewal automatically as long as the service stays running. If you see certificate errors in Caddy logs, the fix is always to ensure Caddy is running and has outbound internet access on port 80.

### Monitoring recommendation

A simple uptime check against `/health` every 5 minutes will catch 502s before customers report them. Services like UptimeRobot (free tier) can do this and send a Telegram alert when the endpoint goes down.

---

## Appendix: Quick Command Reference

```bash
# Check if portal is running
pgrep -af portal_server

# Check port 8097
ss -tlnp | grep 8097

# Check health locally
curl -s http://127.0.0.1:8097/health

# Restart portal service
sudo systemctl restart aether-portal

# Check portal logs
journalctl -u aether-portal -n 50 --no-pager

# Kill and manually restart portal
pkill -f portal_server.py
nohup python3 ~/purebrain_portal/portal_server.py >> ~/purebrain_portal/portal_server.log 2>&1 &

# Check disk
df -h /

# Check memory
free -h

# Run full automated recovery (from any SSH-capable machine)
bash /home/jared/projects/AI-CIV/aether/tools/civ_recovery.sh USER@HOST --quick
```

---

*Guide maintained by dept-systems-technology. Update when architecture changes.*
