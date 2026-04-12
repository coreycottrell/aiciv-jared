# Magic Link Domain Swap — Research Record
**Date**: 2026-03-18
**Agent**: full-stack-developer
**Type**: teaching | operational
**Topic**: How magic link domain rewriting works, where it lives, how to extend it to the portal

---

## Summary

Two separate code paths handle magic link domain rewriting. Both convert `{subdomain}.ai-civ.com` → `{subdomain}.purebrain.ai`.

### Path 1: Webhook (log server)
`tools/purebrain_log_server.py` — `/api/birth/webhook` endpoint.
Witness POSTs `birth_complete` event. Log server rewrites magic link inline at lines ~2081-2114.
Formula: `{civ_name}-{firstname}-{lastname}.purebrain.ai` (hyphens, matches Witness container format).

### Path 2: AgentMail Monitor
`tools/agentmail_monitor.py` — watches `aether-aiciv@agentmail.to`.
Witness sends magic link via email. `parse_magic_link_body()` at line 324 rewrites:
`re.sub(r"(https?://)([^./]+)\.ai-civ\.com", r"\1\2.app.purebrain.ai", raw_link)`
NOTE: This still uses `.app.purebrain.ai` — diverges from Path 1.

### Infrastructure (proxy layer)
Cloudflare Worker `purebrain-portal-proxy` (route: `*.purebrain.ai/*`) proxies
`{subdomain}.purebrain.ai` → `https://{subdomain}.ai-civ.com` on Witness at 37.27.237.109.
Worker source: `exports/departments/systems-technology/2026-03-13--portal-proxy-worker.js`
Routes DB: `/home/jared/purebrain_routes.json`
nginx conf: `/etc/nginx/conf.d/purebrain-customer-portals.conf` (managed by subdomain_router.py)

### Frontend validation (chatbox)
`allowedDomains = ['purebrain.ai', 'puremarketing.ai', 'aiciv.dev', 'ai-civ.com']`
`.hostname.endsWith('.' + d)` pattern — so `*.purebrain.ai` passes automatically.
This lives in the pay-test chatbox JS.

### Portal server magic_link_token
Column exists in `clients.db` but only defined in schema — NOT populated by any code found.
Separate from the birth pipeline.

---

## Key File Locations
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` — webhook + rewrite logic
- `/home/jared/projects/AI-CIV/aether/tools/agentmail_monitor.py` — email path + rewrite
- `/home/jared/projects/AI-CIV/aether/tools/subdomain_router.py` — nginx route provisioning
- `/home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/2026-03-13--portal-proxy-worker.js` — CF Worker
- `/home/jared/purebrain_routes.json` — routing DB

---

## Gotcha: Inconsistent domain pattern
Path 1 (webhook): `{sub}.purebrain.ai` (NO `app.` prefix — updated 2026-03-13)
Path 2 (agentmail): `{sub}.app.purebrain.ai` (OLD pattern — NOT updated)
Needs to be synced.

