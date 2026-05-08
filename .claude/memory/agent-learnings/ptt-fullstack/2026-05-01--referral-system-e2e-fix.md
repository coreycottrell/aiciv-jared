# Referral System Full E2E Fix

**Date**: 2026-05-01
**Type**: operational
**Agent**: full-stack-developer

## What Was Done

Fixed 8 issues across the referral system (3 surfaces: refer/, admin, portal Refer & Earn). All 20 E2E tests pass.

## Key Fixes

1. **admin-api DNS**: Added AAAA record + worker route. Note: wildcard `*.purebrain.ai/*` takes precedence so direct subdomain access still 522. All traffic works via portal proxy.
2. **Proxy routing**: `/api/admin/clients` was going to social-api (wrong), fixed to admin-api. Removed duplicate routing block.
3. **Password hash**: Reset JAREDSB0 hash to SHA-256 salted format. Previous hash was from unknown source.
4. **BREVO_API_KEY**: Was in .env but not set as wrangler secret on referrals-api. Set via `wrangler secret put`.
5. **Assign field mismatch**: Frontend sends `referral_code`+`client_email`, backend expected `referrer_id`+`referred_email`. Added dual field acceptance + code-to-id resolution.
6. **Missing endpoints**: Added `GET /lookup`, `POST /register` for portal Refer & Earn integration.
7. **Dashboard admin bypass**: Portal proxy now passes X-Admin-Token for referral API requests, so portal users don't need separate referral session.

## Key Gotchas

- **Worker routing order matters**: POST endpoints placed AFTER `if (method !== "GET") return err(404)` guard won't be reached. Always place POST handlers before the GET section guard.
- **CF route priority**: Specific routes like `admin-api.purebrain.ai/*` don't override wildcard `*.purebrain.ai/*`. The portal proxy catches all subdomain traffic. Use `.in0v8.workers.dev` URLs for inter-worker calls.
- **ADMIN_TOKENS secret**: referrals-api uses comma-separated `ADMIN_TOKENS` (plural), admin-api uses `ADMIN_TOKEN` (singular). Different env var names.
- **D1 databases are separate**: `purebrain-referrals` (referrals-api) vs `purebrain-social` (admin-api). Session tokens in one DB can't be verified in the other.

## Files Modified

- `workers/purebrain-portal-proxy/src/worker.js`
- `workers/referrals-api/src/worker.js`
