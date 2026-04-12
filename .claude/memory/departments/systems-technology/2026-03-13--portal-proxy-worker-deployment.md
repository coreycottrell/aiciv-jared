# Cloudflare Worker — Portal Proxy for *.purebrain.ai
**Date**: 2026-03-13
**Agent**: dept-systems-technology
**Type**: deployment | infrastructure | pattern

---

## What Was Built

Cloudflare Worker `purebrain-portal-proxy` deployed on route `*.purebrain.ai/*`.
Proxies customer portal subdomains (`{ainame}-{firstname}-{lastname}.purebrain.ai`)
directly to Witness containers (`{subdomain}.ai-civ.com`) at IP 37.27.237.109.

## Architecture

```
Customer browser
  → greg-lucas-neuteufel.purebrain.ai
  → Cloudflare DNS (CNAME: *.purebrain.ai → cloudflared tunnel)
  → Worker intercepts (route: *.purebrain.ai/*)
  → Worker detects: portal subdomain (not in SYSTEM_SUBDOMAINS)
  → Worker proxies: fetch(https://greg-lucas-neuteufel.ai-civ.com, {cf: {resolveOverride: 37.27.237.109}})
  → Witness Caddy/container handles request
  → Response returned with purebrain.ai host headers
```

System subdomains (portal, api, app, video, cc, comms, www, etc.) are passed through
unchanged via `return fetch(request)` — the cloudflared tunnel handles these via
its explicit ingress rules.

## Key Files

- Worker source: `exports/departments/systems-technology/2026-03-13--portal-proxy-worker.js`
- Worker name: `purebrain-portal-proxy` (deployed to CF account d526a3e9498dd167509003004df03290)
- Worker route: `*.purebrain.ai/*` (zone: 49400cad1527af716705f6cb8c22bb65, route ID: 83066cd29696421a8bcd87ae47011492)
- Log server: `tools/purebrain_log_server.py` (updated domain format)

## Log Server Changes (2026-03-13)

Two changes to `tools/purebrain_log_server.py`:

### 1. Domain: `.app.purebrain.ai` → `.purebrain.ai`
All magic link rewrites now use flat `.purebrain.ai` (no `app.` prefix).

### 2. Subdomain format: `{ainame}{firstname}` → `{ainame}-{firstname}-{lastname}`
Old: `keenjared.purebrain.ai`
New: `keen-jared-sanborn.purebrain.ai`
Matches Witness container format: `keen-jared-sanborn.ai-civ.com`

Both sections updated:
- Line ~1674: magic link URL rewrite in birth_complete_webhook
- Line ~1738: nginx subdomain_router provisioning call (step 7 of webhook)

## Critical Gotcha: Worker Routes Override Tunnel Ingress

Cloudflare Worker routes take priority over DNS-based routing (including the cloudflared
tunnel). When the route `*.purebrain.ai/*` is active, ALL subdomain requests go through
the Worker first — even portal.purebrain.ai, api.purebrain.ai, etc.

**Fix**: Worker checks SYSTEM_SUBDOMAINS set and calls `return fetch(request)` for those.
This passes the request back to Cloudflare's normal routing, which then uses the CNAME
to route through the tunnel as before.

Do NOT use early-return error responses for system subdomains. Use `fetch(request)` to
pass through cleanly.

## Verification (2026-03-13)

All passing:
- greg-lucas-neuteufel.purebrain.ai → HTTP 200 (Witness portal content)
- portal.purebrain.ai → HTTP 200 (admin portal via tunnel)
- app.purebrain.ai → HTTP 200 (via tunnel)
- purebrain.ai → HTTP 200 (Cloudflare Pages homepage)
- api.purebrain.ai/api/health → {status: ok}

## Deploy Commands (for re-deploy if needed)

```bash
cp exports/departments/systems-technology/2026-03-13--portal-proxy-worker.js /tmp/index.js

CF_EMAIL="jared@puretechnology.nyc"
CF_GLOBAL_API_KEY="<from .env CF_GLOBAL_API_KEY>"
CF_ACCOUNT_ID="d526a3e9498dd167509003004df03290"
ZONE_ID="49400cad1527af716705f6cb8c22bb65"

# Upload
curl -s -X PUT \
  "https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/workers/scripts/purebrain-portal-proxy" \
  -H "X-Auth-Email: $CF_EMAIL" \
  -H "X-Auth-Key: $CF_GLOBAL_API_KEY" \
  -F 'metadata={"main_module":"index.js","compatibility_date":"2024-01-01"};type=application/json' \
  -F "index.js=@/tmp/index.js;type=application/javascript+module"

# Route (already created, use PUT to update)
curl -s -X PUT \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/workers/routes/83066cd29696421a8bcd87ae47011492" \
  -H "X-Auth-Email: $CF_EMAIL" \
  -H "X-Auth-Key: $CF_GLOBAL_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{"pattern":"*.purebrain.ai/*","script":"purebrain-portal-proxy"}'
```
