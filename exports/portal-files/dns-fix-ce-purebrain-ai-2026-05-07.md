# DNS/SSL Fix — ce.purebrain.ai HTTP 530 → 200

**Date:** 2026-05-07
**Owner:** Aether → ST# (full-stack-developer)
**For:** Morphe (CE SME QA), Jared
**Customer impact:** Phil at Canada's Entrepreneur unblocked

---

## TL;DR

`ce.purebrain.ai` returned **HTTP 530** (CF Error 1016 — Origin DNS error). Root cause was **NOT** DNS or SSL — it was a too-greedy CF Worker route. **Fixed** by adding a more specific Worker route. Domain now returns **HTTP 200**.

---

## What Was Broken

CF Pages custom domain config was actually correct:

- DNS CNAME `ce.purebrain.ai` → `purebrain-production-23b.pages.dev` (proxied) — present and correct
- Custom domain registered on `purebrain-production` Pages project — `status: active`
- SSL cert (Google Trust Services) — issued, valid, TLS handshake succeeded

The 530 happened **after** TLS, at the application layer. Error body revealed CF was trying to resolve `ce.ai-civ.com` (which has no DNS), not `ce.purebrain.ai`.

## Root Cause

CF Worker route `*.purebrain.ai/*` → `purebrain-portal-proxy` was matching `ce.purebrain.ai` and rewriting the host to `ce.ai-civ.com` to proxy to a customer container.

That Worker is designed for customer portal containers (e.g., `corey.purebrain.ai` → `corey.ai-civ.com` on Witness 37.27.237.109). It has a `SYSTEM_SUBDOMAINS` allowlist (api, www, voice, etc.) for non-container subdomains. **`ce` was missing from that allowlist**, so the proxy treated CE SME as a customer container — and `ce.ai-civ.com` doesn't exist → CF error 1016 → wrapped as 530.

This violates the constitutional rule "NOTHING IN CONTAINERS" — `ce.purebrain.ai` is correctly a CF Pages site, the Worker just didn't know.

## The Fix

Added a more specific Worker route that bypasses the proxy (matches the established pattern used for `api.`, `creator.`, `777.`, `brainiac.`, etc.):

```
POST /zones/{zone}/workers/routes
{ "pattern": "ce.purebrain.ai/*", "script": null }
```

Route ID: `eef98a8dc02d4bcc934060d05235171f`

Also added `'ce'` to `SYSTEM_SUBDOMAINS` in `workers/purebrain-portal-proxy/src/worker.js` (belt-and-suspenders — committed but not deployed; the Worker route is sufficient on its own).

## Verification

- `curl -s -o /dev/null -w "%{http_code}" https://ce.purebrain.ai/` → **200** (was 530)
- Response headers: `server: cloudflare`, `cf-cache-status: DYNAMIC`, `cf-ray` present — serving from CF Pages
- TLS cert valid through Aug 5 2026
- DNS unchanged, SSL unchanged — only the Worker routing was broken

## ⚠️ Follow-up for Morphe

The 530 is fixed but `ce.purebrain.ai` currently serves the **purebrain.ai homepage**, NOT CE SME content. Reason: both domains are bound to the same `purebrain-production` Pages project, so they get identical output.

To serve distinct CE SME content at `ce.purebrain.ai`, options:

1. **Separate Pages project** for CE SME, move `ce.purebrain.ai` custom domain over to it (cleanest)
2. **Pages Functions / `_routes.json`** on `purebrain-production` to serve different content per Host header
3. **Keep `ce.purebrain.ai` on a different `*.pages.dev`** and update the CNAME

Decide which path; ST# can implement once direction is clear. Deploy itself stays git-driven (no local deploys, no `wrangler pages deploy`).

## Constraints Honored

- Used GET, not HEAD, for all CF Pages health checks (per `cf-pages-health-check-get-not-head` skill)
- No local deploys — Worker route created via CF API only
- No code touched in `ce-sme` project
- DNS untouched; only Worker routing changed
- `wrangler pages deploy` not used
