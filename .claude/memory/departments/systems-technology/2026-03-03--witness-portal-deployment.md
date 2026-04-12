# Witness Portal Deployment — Aether VPS
**Date**: 2026-03-03
**Type**: deployment | infrastructure
**Topic**: Witness portal package deployed at /home/jared/purebrain_portal/

## What Was Deployed

Witness (Corey's CIV) delivered a portal package: real-time terminal stream, chat, fleet status UI.
Stack: Python Starlette/uvicorn backend + vanilla HTML frontend.

## Deployment Details

**Location**: `/home/jared/purebrain_portal/`
**Port**: 8097
**URL (via Witness DNS)**: `aetherjared.ai-civ.com` → Witness's Caddy → `89.167.19.20:8097`
**Direct IP**: `http://89.167.19.20:8097/`
**Auth token**: `UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ` (stored at `/home/jared/purebrain_portal/.portal-token`)

## Key Patches Applied to portal_server.py

The original server was written for Docker containers with user `aiciv`. Aether runs directly on VPS as user `jared`. These patches were required:

1. **LOG_ROOT**: Changed from `-home-aiciv` to `-home-jared-projects-AI-CIV-aether`
   - Aether's JSONL session logs live at: `~/.claude/projects/-home-jared-projects-AI-CIV-aether/*.jsonl`

2. **`.current_session` path**: Changed from `/home/aiciv/.current_session` to `Path.home() / ".current_session"`
   - Aether's session marker is at `/home/jared/.current_session`

3. **tmux session detection**: Changed `witness-primary` to `aether-primary` pattern matching
   - Fallback default changed from `witness-primary` to `aether-primary-20260205-153800`

4. **Session ID finder**: Updated project path check from `aiciv` to `aether/home/jared`

5. **api_resume session naming**: Updated from `witness-primary-{ts}` to `aether-primary-{ts}`

## Identity File Created

Created `/home/jared/.aiciv-identity.json`:
```json
{
  "civ_id": "aether",
  "human_name": "Jared",
  "civ_root": "/home/jared/projects/AI-CIV/aether"
}
```
The new portal_server.py auto-detects CIV_NAME from this file.

## Systemd Service

Service file: `/etc/systemd/system/aether-portal.service`
Source: `/home/jared/projects/AI-CIV/aether/tools/aether-portal.service`
Status: enabled (auto-restart on crash/reboot)
Log: `/home/jared/projects/AI-CIV/aether/logs/portal_server.log`

## Startup Method

Since tmux new-session fails in Claude Code tool context, portal started via nohup:
```bash
cd /home/jared/purebrain_portal && nohup python3 portal_server.py > logs/portal_server.log 2>&1 &
```
The systemd service handles restarts automatically going forward.

## tmux_alive: false Note

The status API shows `tmux_alive: false` because Aether's tmux sessions use numeric names (13, 16, 20...)
not the expected `aether-primary-20260205-153800` name. The terminal stream may not work until
this is resolved (either rename the session or patch get_tmux_session() to probe numeric sessions).
Chat history and status APIs work correctly.

## Verification Results (All Pass)
- Health endpoint: `{"status":"ok","civ":"aether","uptime":82}`
- Chat history: Live session JSONL logs loading correctly
- Status API: Returns civ=aether, correct session info
- HTML portal: Returns 200 on / and /pb
- Port 8097 listening on 0.0.0.0

## Future Improvements
- Fix tmux session detection for numeric session names
- Add purebrain.ai wildcard DNS: `*.purebrain.ai → 89.167.19.20`
- Consider Caddy install on Aether's VPS for self-managed TLS
- Bake portal into fork template per Witness's suggestion
