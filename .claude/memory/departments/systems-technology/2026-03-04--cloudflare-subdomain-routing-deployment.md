# Cloudflare Flat Subdomain Routing — Customer Portals
**Date**: 2026-03-04
**Type**: deployment | infrastructure | pattern

## What Was Built

Full `*.purebrain.ai` customer portal routing system. Customers get URLs like `keenjared.purebrain.ai` instead of `keenjared.ai-civ.com`.

## Architecture Decision

Chose: **cloudflared tunnel (catch-all wildcard) → nginx (dynamic reverse proxy)**

Rejected:
- Cloudflare Workers (adds complexity, cost, separate deployment)
- Per-customer cloudflared ingress rules (doesn't scale, requires restart on each add)
- app.purebrain.ai/{name} path routing (WebSocket conflicts, auth cookie scope issues)

## Key Files

- `/etc/nginx/conf.d/purebrain-customer-portals.conf` — auto-generated, managed by subdomain_router.py
- `/etc/nginx/conf.d/purebrain-main.conf` — portal.purebrain.ai → port 8097
- `/home/jared/purebrain_routes.json` — routing database
- `/home/jared/projects/AI-CIV/aether/tools/subdomain_router.py` — CLI + API for managing routes

## Critical Gotchas

1. **nginx upstream DNS resolution at startup**: MUST use `set $backend "url"` + `resolver 1.1.1.1` pattern. Without this, nginx fails to start if upstream hostname doesn't resolve yet (which it won't for brand new containers).

2. **nginx conf.d is root-owned**: Must use `sudo tee` to write files. Use `subprocess.run(['sudo', 'tee', str(path)])`.

3. **cloudflared restart vs reload**: Config changes require `systemctl restart cloudflared`. There is no graceful reload.

4. **Wildcard DNS**: `*.purebrain.ai` CNAME created once covers all subdomains. Individual per-customer CNAMEs are also created (idempotent) for explicitness.

## Auto-Provisioning Integration

`purebrain_log_server.py` patched to call `add_customer_route()` in the birth webhook handler. Subdomain derived as `{civ_name}{human_first_name}` (lowercase, alphanumeric).

## Verification State (2026-03-04)

- portal.purebrain.ai → 200 OK (live)
- *.purebrain.ai DNS → Cloudflare tunnel IPs (live)
- nginx running, cloudflared running, log server running
- keenjared.purebrain.ai → 502 (demo, container doesn't exist on Witness — expected)
