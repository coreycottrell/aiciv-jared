# Admin API Worker Split from Social API

**Date**: 2026-04-23
**Type**: operational
**Topic**: Created standalone admin-api CF Worker, split from social-api

## What Was Done

Split admin dashboard endpoints out of `workers/social-api` into new `workers/admin-api` Worker so admin dashboard operates independently of social content deploys.

## Endpoints Moved to admin-api

- `GET /api/admin/clients` -- list clients with stats
- `PATCH /api/admin/clients/by-email/{email}` -- update by email (no auth, internal)
- `PATCH /api/admin/clients/{id}` -- update by ID (leader only)
- `POST /api/admin/invite` -- create team invite
- `GET /api/admin/invites` -- list invites
- `DELETE /api/admin/invites/{id}` -- delete invite

## What Stayed in social-api

- `POST /api/admin/trigger_sunday_batch` -- tightly coupled to content generation logic (runSundayBatch function)
- All content, user, meeting, blocker endpoints

## Auth Approach

admin-api supports dual auth:
1. `X-Admin-Token` header (set by portal proxy, value: `purebrain-admin-2026`)
2. Bearer token / session cookie (reads from same D1 sessions table as social-api)

## Portal Proxy Changes

Updated `purebrain-portal-proxy` routing:
- `/api/admin/clients*` and `/api/admin/invite*` -> admin-api.in0v8.workers.dev (with X-Admin-Token)
- Other `/api/admin/*` -> social-api.in0v8.workers.dev (fallback for trigger_sunday_batch)

## Key Files

- `workers/admin-api/src/worker.js` -- new worker
- `workers/admin-api/wrangler.toml` -- D1 binding to purebrain-social
- `workers/purebrain-portal-proxy/src/worker.js` -- updated routing
- `workers/social-api/src/worker.js` -- removed admin endpoints (comment at line ~2721)

## Deploy Credentials

Workers deployed with: `CLOUDFLARE_API_KEY` + `CLOUDFLARE_EMAIL` + `CLOUDFLARE_ACCOUNT_ID` (from .env)

## Deployment Order (Safe Migration Pattern)

1. Deploy admin-api FIRST (new endpoints live)
2. Deploy updated portal proxy (routes to admin-api)
3. Deploy updated social-api LAST (removes old endpoints)
4. Test at each step
