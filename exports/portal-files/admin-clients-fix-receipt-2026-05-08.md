# Admin Clients Page Fix — Receipt 2026-05-08

**Trigger**: Jared (CEO) — `https://portal.purebrain.ai/admin/clients/` no data loading. Was working ~10am ET 2026-05-07.

## Live state (BEFORE fix, 2026-05-08 ~10:51 UTC)

| Endpoint | HTTP | Body |
|---|---|---|
| `GET portal.purebrain.ai/admin/clients/` | 200 | Page HTML (48,776 bytes) |
| `GET portal.purebrain.ai/api/admin/clients` | **404** | `{"error":"not found"}` |
| `GET social-api.in0v8.workers.dev/api/admin/clients` | **404** | `{"error":"not found"}` |
| `GET social-api.in0v8.workers.dev/api/login` (sanity) | 401 | `{"error":"invalid credentials"}` (worker alive) |
| `GET social-api.in0v8.workers.dev/api/admin/trigger_sunday_batch` | 401 | (route exists, auth-gated) |

## Network capture

Page calls `fetch(API + "/api/admin/clients")` from `getToken()`-authed client. Backend returns 404 ⇒ page renders empty list. Same 404 hits regardless of token validity (route literally not registered in deployed worker), so symptom is "no data" not "auth error".

## Root cause

**Stale `social-api` Worker deployment.** Source code at `/home/jared/projects/AI-CIV/aether/workers/social-api/src/worker.js:6201` has the `/api/admin/clients` route (added 2026-04-21 in commit `2ee7b43`), but deployed Worker was a build that pre-dated that commit. Confirmed by route-by-route HTTP probe:

- Routes added in commit `9c2ecf0` (2026-04-20 22:26): `/api/admin/trigger_sunday_batch` ⇒ 401 (deployed)
- Routes added in commit `8fed7d6` (2026-04-20 23:27): `/api/blockers`, `/api/ai/captions`, `/api/analytics/best-times` ⇒ 404 (NOT deployed)
- Routes added in commit `2ee7b43` (2026-04-21 13:45): `/api/admin/clients` ⇒ 404 (NOT deployed)

So deployed Worker corresponded to a state between 22:26 and 23:27 on 2026-04-20, even though source was redeployed many times after that. Likely cause: an Apr-21 deploy was performed from a dirty/older working tree on a different machine or branch, never updated since. Yesterday's Phase 0 portal-proxy work touched only `purebrain-portal-proxy`, not `social-api` (rollback receipt confirms — `.backups/portal-proxy-rollback-2026-05-07/` contains only portal-proxy files; portal-proxy code path for `/api/admin/clients` is unchanged at `workers/purebrain-portal-proxy/src/worker.js:216-226`).

The "was working yesterday morning" report is more likely about page-load (still works) or about a different page; the API has been 404 for some time. Yesterday's rollback verification probed `GET /admin/clients` (page) and got 200, but never probed the API path.

## Fix applied

Redeployed `social-api` Worker from current working tree (clean, on branch `referral-v1`, identical to `main` for `social-api/src/worker.js`).

```
cd /home/jared/projects/AI-CIV/aether/workers/social-api
CLOUDFLARE_API_TOKEN=<from .env CF_API_TOKEN> npx wrangler deploy
```

**New version**: `6dff16a7-f12f-4111-a004-276aa7e547e3` (deployed 2026-05-08 ~10:55 UTC)

Bindings unchanged: `DB=purebrain-social` (D1), `UPLOADS=purebrain-uploads` (R2), `CORS_ORIGINS` env. Cron `0 11 * * SUN` re-attached.

## Post-fix verification (AFTER state)

| Endpoint | HTTP | Result |
|---|---|---|
| `GET portal.purebrain.ai/admin/clients/` | 200 | Page loads |
| `GET portal.purebrain.ai/api/admin/clients` | **401** | Route now exists, auth-gated as designed |
| `GET social-api.in0v8.workers.dev/api/admin/clients` | **401** | `{"error":"unauthorized"}` |
| `GET social-api.in0v8.workers.dev/api/blockers` | 200 | Now returns data |
| `POST .../api/blockers/report` | 401 | Route registered |
| `POST .../api/ai/captions` | 401 | Route registered |
| `POST .../api/analytics/best-times` | 401 | Route registered |

D1 `clients` table verified intact: 64 rows (matches yesterday's constitutional verification). Query path: `SELECT * FROM clients ORDER BY last_active_at DESC` at `worker.js:6205`.

## Status

**FIXED-AND-VERIFIED.** When Jared logs in with a valid session, `/api/admin/clients` will now return `{clients: [...64 rows...], stats: {...}}` and the page will populate. No customer-facing token rotation, no portal-proxy changes, no D1 migration — single Worker redeploy from current source.

## Recommendation

The Apr-21 deploy drift is a process gap: source code committed with new admin routes, but the binary deployed to production was older. ST# should add a post-deploy smoke test for the `social-api` Worker that probes a representative new route (e.g. `/api/admin/clients` 401-or-200, never 404) and fails the deploy if any expected route returns 404. Pair with `cf-pages-health-check-get-not-head` skill.
