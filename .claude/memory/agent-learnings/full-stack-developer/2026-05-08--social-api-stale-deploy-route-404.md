# Stale social-api Worker deploy — admin/clients 404

**Date**: 2026-05-08
**Type**: gotcha / operational
**Topic**: Production CF Worker drift between source and deployment

## Symptom

`portal.purebrain.ai/admin/clients/` page loaded (200) but rendered no client data. API call `/api/admin/clients` returned `{"error":"not found"}` HTTP 404.

## Root cause

Deployed `social-api` Worker (account `d526a3e9...`) was older than the source tree. Specifically:

- `workers/social-api/src/worker.js:6201` had the route since commit `2ee7b43` (2026-04-21)
- Deployed binary corresponded to a build from 2026-04-20 22:26-23:27 window
- Routes from commits AFTER that window all returned 404 (`/api/admin/clients`, `/api/blockers`, `/api/ai/captions`, `/api/analytics/best-times`)
- Routes BEFORE that window returned 401 correctly (`/api/admin/trigger_sunday_batch`)

The diagnostic technique: bisect routes by commit date and see which return 404 vs 401. When auth-gated routes return 404 instead of 401, the route literally doesn't exist in the deployed Worker.

## Fix

Single command:

```bash
cd workers/social-api
CLOUDFLARE_API_TOKEN=$(grep ^CF_API_TOKEN= .env | cut -d= -f2-) npx wrangler deploy
```

New version `6dff16a7-f12f-4111-a004-276aa7e547e3`. All routes now respond correctly.

## Why this happened (likely)

Phase 0 portal-proxy security work yesterday touched ONLY `purebrain-portal-proxy`, not `social-api`. Rollback receipt at `exports/portal-files/portal-proxy-rollback-receipt-2026-05-07.md` only verified `GET /admin/clients` (the page HTML, which still worked) — did not probe the API endpoint behind it.

Drift was probably from an Apr-21 partial deploy that uploaded an older worker.js, never reconciled. `wrangler deploy` warned: "You are about to publish a Workers Service that was last updated via the script API. Edits that have been made via the script API will be overridden by your local code and config." This is a tell that someone deployed via a different mechanism in between.

## Patterns

1. **Probe API not just page**: When a CF Pages → Worker → D1 chain has "no data" symptom, the page returning 200 proves nothing about the data path. Always curl the API endpoint the page calls.

2. **404 vs 401 disambiguation**: Auth-gated route returning 404 (not 401) means the route is missing from the deployed binary. Distinguishes deploy drift from auth/secret rotation issues.

3. **Route bisect by commit timestamp**: When a worker has many routes added across multiple commits, test routes from different commits to identify the deployed-version cutoff. Faster than diffing binaries.

4. **Verification scope must match symptom**: Yesterday's rollback verified the page (200) but the symptom was the API. Curl coverage in receipts should include the actual data path the page calls.

## Files

- Receipt: `exports/portal-files/admin-clients-fix-receipt-2026-05-08.md`
- Worker source: `workers/social-api/src/worker.js:6201` (route definition)
- Portal-proxy routing: `workers/purebrain-portal-proxy/src/worker.js:216-226` (correctly proxies `/api/admin/*` to social-api — was never the bug)
- D1 binding: `workers/social-api/wrangler.toml` (database_id `625dde70-...`, 64 rows in `clients` table verified)

## ST# follow-up

Add post-deploy smoke test that probes representative routes for 401-or-200 (never 404). Catches drift like this immediately.
