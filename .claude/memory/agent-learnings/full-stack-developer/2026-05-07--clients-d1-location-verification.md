# Clients D1 Location — Independent Verification (Drift Found)

**Date**: 2026-05-07
**Type**: operational + teaching
**Trigger**: Jared questioned ptt-fullstack claim that clients table is in purebrain-social. Chy reportedly intended separate DB.

## Verified Facts

- `clients` table EXISTS in: `purebrain-social` (PROD, 64 rows), `purebrain-social-staging` (0 rows), `hancock-law-staging` (6 rows, unrelated tenant schema)
- `clients` table DOES NOT EXIST in: `purebrain-referrals` (confirmed via fresh `sqlite_master` query)
- No standalone `purebrain-clients` or `clients-db` D1 exists on the account (12 D1s total, all named)
- ptt-fullstack's claim was factually correct

## Live Routing Chain (verified)

`portal.purebrain.ai/admin/clients` flow:
1. `purebrain-portal-proxy` worker line 206-217 routes `/api/admin/*` to `social-api.in0v8.workers.dev`
2. `social-api` (worker.js:6201) handles GET — wrangler.toml binds DB → `purebrain-social` (uuid 625dde70-0a60-45e7-bf81-e18e5ac4d854)
3. `admin-api` worker also bound to same `purebrain-social` D1
4. CF Pages serves the HTML at `/admin/clients/index.html`

## Drift Documented

Apr 20 strategic recommendation (in this same memory dir, ptt-fullstack):
> "Migrate to D1 (purebrain-clients OR add clients table to purebrain-referrals)"

**Neither option was taken.** Clients landed in `purebrain-social` instead — likely due to transactional convenience with PayPal/social flows. Chy's reported architectural intent (separate setup, no touch with social) was NOT implemented.

## Legacy Co-existence

`/home/jared/purebrain_portal/portal_server.py` still has a local `clients.db` SQLite (40KB, actively written today 15:46) with full `/admin/clients` Flask routes. The portal-proxy worker now intercepts `/admin/clients*` and routes away from portal_server.py to CF Pages + workers. Two systems exist; live traffic goes to D1.

## Teaching

- When verifying claims about DB location, NEVER trust prior agent self-assertion. Re-run `wrangler d1 list` + per-DB `SELECT FROM sqlite_master`.
- "Architectural intent" memory entries (e.g. recommendations) are NOT proof of implementation. Always re-verify against wrangler.toml bindings + live workers.
- Drift between intent and implementation is common. Document it explicitly; don't pick a side without owner alignment.
- ptt-fullstack's halt was correct — but drift question (refactor vs ratify) needs Jared + Chy alignment before any clients schema change.

## File Paths

- Deliverable: `/home/jared/projects/AI-CIV/aether/exports/portal-files/clients-d1-independent-verification-2026-05-07.md`
- Live worker: `/home/jared/projects/AI-CIV/aether/workers/social-api/wrangler.toml` (DB binding line 6-9)
- Live worker: `/home/jared/projects/AI-CIV/aether/workers/admin-api/wrangler.toml` (same DB binding)
- Routing: `/home/jared/projects/AI-CIV/aether/workers/purebrain-portal-proxy/src/worker.js:206-217`
- Legacy: `/home/jared/purebrain_portal/portal_server.py:5766-6143` + `/home/jared/purebrain_portal/clients.db`
