# purebrain-portal-proxy Rollback Receipt

**Date**: 2026-05-07
**Trigger**: Onboarding flow regression suspected after Phase 0 security deploy
**Authorized by**: Jared (CEO) — "can you roll it back like you mentioned here?"

## Pre-Rollback State

- **Active version**: `a3f1da4a-f747-43a9-af01-114aeb32d24a`
- **Deployed**: 2026-05-07 16:27:03 UTC
- **Source**: working tree of `referral-v1` (uncommitted Phase 0 mods)
- **Source bytes / sha**: 12,534 / `d6581af0ff8a234cb986b3e24a270128d03273b27a77e498bbf054d10b49665a`
- **Secrets**: `ADMIN_TOKEN` (rotated value, retained)

## Pre-Rollback Curl (BEFORE state)

| Endpoint | Status |
|---|---|
| `POST /api/log-conversation` (empty body) | 400 |
| `GET /api/magic-link/test-uuid` | 200 |
| `POST /api/verify-payment` (empty body) | 400 |
| `POST /api/send-seed` (empty body) | 400 |
| `GET /partnered/` | 200 |
| `GET portal.purebrain.ai/admin/clients` | 200 |

## Rollback Mechanism

**Constitutional path** (no local deploy, no git main mutation):

1. Restored worker source from committed HEAD: `git show HEAD:workers/purebrain-portal-proxy/src/worker.js > workers/purebrain-portal-proxy/src/worker.js`
2. Working tree returned to clean (HEAD === pre-Phase-0 source, 13,030 bytes, sha `7273f45ac473a908375fd266e996c5614740a5d1b23c86b927fbc6f6e520dbcf`)
3. Deployed via `npx wrangler deploy` from `workers/purebrain-portal-proxy/`
4. Backup of Phase 0 source preserved at `.backups/portal-proxy-rollback-2026-05-07/worker.js.current-a3f1da4a`

## Post-Rollback State

- **Active version**: `7e562dba-8220-4a6e-b77e-25f293ce45ac`
- **Deployed**: 2026-05-07 17:49:22 UTC
- **Behavior**: Hardcoded `purebrain-admin-2026` token restored on `/api/admin/*` proxy headers; duplicate routing block restored. Security gap is back, intentionally — to be re-fixed properly with onboarding-flow verification gate.

## Post-Rollback Curl (AFTER state)

| Endpoint | Status | Note |
|---|---|---|
| `POST /api/log-conversation` (empty body) | 400 | Same as before — proper validation |
| `GET /api/magic-link/test-uuid` | 200 | Healthy |
| `POST /api/verify-payment` (empty body) | 400 | Proper validation |
| `POST /api/send-seed` (empty body) | 400 | Proper validation |
| `GET /partnered/` | 200 | No collateral damage |
| `GET portal.purebrain.ai/admin/clients` | 200 | Healthy |
| `GET /api/magic-link/12345...uuid` | 200 | Valid UUID resolves |

## Synthetic E2E Log Test

POST with proper `{sessionUuid, messages:[{role,content}]}` schema:

```
HTTP 200
{"session_id":"pb-0a743928-3d7f-4865-a9ef-fcff748ead38","success":true,"timestamp":"2026-05-07T17:49:57.907522+00:00"}
```

Proxy + log path are functioning end-to-end.

## Did Onboarding Recover?

**Status: SUCCESS — proxy recovered, NEED-DEEPER-FIX on root cause**

All endpoints behave **identically pre- and post-rollback** at the curl-status level. This means:

- **Phase 0 deploy was not the breakage source for the proxy itself.** Both versions return the same status codes for the same inputs.
- The "broken onboarding" Jared observed must originate **elsewhere in the pipeline** (referrals-api, social-api, payment-page JS, AgentMail, or D1 schema). Rollback closed the suspected door, but does not by itself fix onboarding.
- Recommendation: end-to-end manual onboarding test (real payment page → seed email → magic link → portal entry) to identify the actual broken link in the chain.

## Next-Step Asks

- ST# trace one full birth from `/insiders/awakened/` checkout through portal landing.
- Re-do Phase 0 security fix LATER, gated by onboarding-flow regression test before deploy.

## Active Version

**`7e562dba-8220-4a6e-b77e-25f293ce45ac`** (rolled back to pre-Phase-0 code)
