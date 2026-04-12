# Incident: Mia Harrison Portal Restart — Already Self-Recovered

**Date**: 2026-03-23
**Customer**: Harrison (Mia)
**AI CIV Name**: Mia
**Type**: operational | incident-resolved
**Resolution Time**: ~5 minutes (portal had already self-recovered before CTS intervention)

---

## Incident Summary

CTS# request to SSH into Harrison's container and restart the portal server.
Witness had flagged the portal as down overnight. On investigation, the portal
server's tmux auto-restart loop had already brought it back up at ~09:58 this
morning. Portal was fully healthy on arrival.

---

## Container Facts

| Field | Value |
|-------|-------|
| SSH Port | 2244 |
| Host | 37.27.237.109 |
| SSH User | aiciv |
| Portal Port | 8097 (internal) / 8144 (external) |
| CIV Name | Mia |
| Human | Harrison |
| Public URL | https://mia-harrison.app.purebrain.ai/ |

---

## Root Cause

Portal server (portal_server.py) received a SIGTERM and shut down gracefully
(log showed clean shutdown sequence: "Shutting down" → "Application shutdown complete").
The tmux session named `portal-server` had a restart loop configured that
automatically re-launched the portal at ~09:58 on 2026-03-23 with:

```
cd /home/aiciv/purebrain_portal && PORT=8097 nohup python3 portal_server.py >> /home/aiciv/logs/portal_server.log 2>&1 &
```

The portal was serving live requests (HTTP 200 on /api/context, /api/status,
/api/compact/status, /api/boop/config) by the time CTS arrived.

---

## What CTS Found on Arrival

- PID 1033318: `python3 portal_server.py` running for 51 minutes
- `curl http://localhost:8097/` returned HTTP 200
- `https://mia-harrison.app.purebrain.ai/` returned HTTP 200
- `http://37.27.237.109:8144/` returned HTTP 200
- tmux `portal-server` pane showing active inbound API requests

---

## Actions Taken

1. SSH'd in as `aiciv` (fleet shared credential, same pattern as Greg and Joy)
2. Verified process state — portal already running healthy
3. Confirmed external endpoint responding
4. Reviewed tmux portal-server pane — confirmed clean restart had occurred
5. Added Harrison to SSH key registry (no-keypair status, dedicated key not yet provisioned)

---

## Pattern Notes

This is the same self-recovery behavior seen in Greg Adamo's container.
The tmux auto-restart loop is working. SIGTERM kills are non-catastrophic
because the loop catches them and relaunches.

Key fleet pattern: shared `aiciv` user on 37.27.237.109, each customer gets
a unique SSH port. No dedicated CTS keypair for Harrison yet — should be
provisioned before the next incident to avoid relying on the shared credential.

---

## What Would Have Happened Without the Auto-Restart Loop

Portal would have stayed down. Container has no systemd portal unit. All
fleet containers appear to rely on the tmux restart loop as the availability
mechanism. This is worth flagging to devops-engineer as a resilience concern
— if tmux itself dies, no portal recovery.

---

## Prevention / Follow-Up

1. Provision dedicated CTS keypair for Harrison (action: CTS SSH Specialist)
2. Consider flagging to devops-engineer: tmux-as-supervisor is fragile compared
   to a proper systemd service or supervisor daemon
3. Witness alert was accurate — portal was down at some point overnight. The
   SIGTERM source is unknown (OOM? manual? host reboot?). Worth monitoring.

---

## Memory Type

- operational: what happened, how it resolved
- teaching: tmux auto-restart loop is the fleet recovery mechanism — check it
  first on any "portal down" report before assuming active intervention needed
