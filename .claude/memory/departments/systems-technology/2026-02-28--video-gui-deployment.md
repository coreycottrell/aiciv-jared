# Video Management GUI Deployment
**Date**: 2026-02-28
**Type**: deployment pattern + gotcha

## What Was Deployed
- FastAPI video management GUI at `https://video.purebrain.ai`
- Handles video upload, HLS transcoding, Cloudflare R2 upload, Mux push, embed code generation
- Files: `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/gui/`

## Architecture Decision
Chose Option 2: Cloudflare tunnel reverse proxy.

Reasoning:
- FastAPI requires a running backend (not static) so WordPress embed not viable
- Cloudflare tunnel already existed (tunnel ID fa55839c-e753-4a96-935c-cc58cf24b4b8)
- Existing tunnel already routes api.purebrain.ai — just added a second ingress rule
- Zero new infrastructure cost

## Deployment Components

### 1. Systemd Service
File: `/etc/systemd/system/purebrain-video-gui.service`
- Runs as user `jared`
- FastAPI on port 8765
- Logs to `/home/jared/projects/AI-CIV/aether/logs/video_gui.log`
- Auto-restarts on failure

### 2. Cloudflare Tunnel Ingress
File: `/etc/cloudflared/config.yml`
- Added ingress rule for `video.purebrain.ai` → `http://localhost:8765`
- DNS CNAME created via: `sudo cloudflared tunnel route dns [tunnel-id] video.purebrain.ai`

### 3. HTTP Basic Auth Middleware
Added to `server.py`:
- `starlette.middleware.base.BaseHTTPMiddleware` (NOT `fastapi.middleware.base` — that module does NOT exist in fastapi 0.134.0)
- Credentials read from `.env`: `VIDEO_GUI_USER` and `VIDEO_GUI_PASS`
- Constant-time comparison via `secrets.compare_digest`

## Credentials
- URL: https://video.purebrain.ai
- Username: purebrain
- Password: stored in `/home/jared/projects/AI-CIV/aether/.env` as VIDEO_GUI_PASS

## Gotchas
1. `fastapi.middleware.base` does NOT exist — use `starlette.middleware.base` instead
2. cloudflared reload is `systemctl restart cloudflared` (not reload — it re-reads config on start)
3. `cloudflared tunnel route dns` requires root (sudo) — it calls Cloudflare API using the tunnel credentials
4. The tunnel credentials file lives at `/root/.cloudflared/{tunnel-id}.json` (only root-accessible)
5. `BaseHTTPMiddleware` must be added BEFORE `CORSMiddleware` via `add_middleware` call order (add_middleware is LIFO)

## Verification Commands
```bash
# Check service running
sudo systemctl status purebrain-video-gui

# Test auth gate (should 401)
curl -s -o /dev/null -w "%{http_code}" https://video.purebrain.ai/

# Test with credentials
curl -s -u "purebrain:PASSWORD" https://video.purebrain.ai/api/health

# Restart service after server.py changes
sudo systemctl restart purebrain-video-gui
```
