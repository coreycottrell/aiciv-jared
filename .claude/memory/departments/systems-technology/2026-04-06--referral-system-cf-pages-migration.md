# Referral System Migration to CF Pages Functions

**Date**: 2026-04-06
**Type**: system-architecture
**Topic**: Migration of referral backend from portal_server.py to Cloudflare Pages Functions + D1

## What Was Done

Migrated the entire referral system backend from Chy's portal server (app.purebrain.ai) to
Cloudflare Pages Functions with D1 serverless database.

## Architecture Change

**Before**: Frontend on CF Pages -> Backend API on app.purebrain.ai (single point of failure)
**After**: Frontend on CF Pages -> Backend API on CF Pages Functions (same domain, D1 database)

## Files Created

### CF Pages Functions (12 endpoints)
- `exports/cf-pages-deploy/functions/api/referral/_shared.js` -- shared utilities, auth, hashing, CORS
- `exports/cf-pages-deploy/functions/api/referral/register.js` -- POST create referrer
- `exports/cf-pages-deploy/functions/api/referral/session.js` -- POST login, get session token
- `exports/cf-pages-deploy/functions/api/referral/dashboard.js` -- GET referrer stats
- `exports/cf-pages-deploy/functions/api/referral/track.js` -- POST log referral click
- `exports/cf-pages-deploy/functions/api/referral/forgot-password.js` -- POST send reset email
- `exports/cf-pages-deploy/functions/api/referral/reset-password.js` -- POST set new password
- `exports/cf-pages-deploy/functions/api/referral/complete.js` -- POST mark referral completed
- `exports/cf-pages-deploy/functions/api/referral/commission.js` -- POST record commission (admin)
- `exports/cf-pages-deploy/functions/api/referral/leaderboard.js` -- GET top referrers
- `exports/cf-pages-deploy/functions/api/referral/paypal-email.js` -- POST save PayPal email
- `exports/cf-pages-deploy/functions/api/referral/payout-request.js` -- POST request payout
- `exports/cf-pages-deploy/functions/api/referral/payout-history.js` -- GET payout history

### D1 Database
- `exports/cf-pages-deploy/d1-migrations/0001-referral-schema.sql` -- full schema
- Tables: referrers, referrals, referral_clicks, rewards, commission_payments,
  admin_tokens, affiliate_sessions, password_reset_tokens, rate_limits, payout_requests

### Migration Tools
- `tools/migrate-referrals-to-d1.sh` -- export from portal SQLite, import to D1

### Frontend Update
- `exports/cf-pages-deploy/refer/index.html` -- changed apiBase from
  `https://app.purebrain.ai/api/referral` to `/api/referral` (relative paths)

## Key Design Decisions

1. **Password hashing**: bcrypt not available in Workers runtime. Using PBKDF2-SHA256
   via Web Crypto API (100k iterations). Users with existing bcrypt hashes must reset
   password via forgot-password flow.

2. **Session storage**: Moved from in-memory dict to D1 table (affiliate_sessions).
   Workers are stateless -- no in-memory state persists between requests.

3. **Rate limiting**: Moved from in-memory dict to D1 table (rate_limits).

4. **Password reset tokens**: Moved from in-memory dict to D1 table (password_reset_tokens).

5. **Payout requests**: Moved from JSONL file to D1 table (payout_requests).

6. **Email**: Switched from Gmail SMTP to Resend API (Workers can't do SMTP).

7. **PayPal auto-payout**: NOT migrated to Workers. All payouts go to "pending" status.
   Admin processes manually. Can be added later via PayPal REST API from Workers.

## Deployment Steps Required

1. `wrangler d1 create purebrain-referrals` -- create D1 database
2. Apply schema via wrangler
3. Configure D1 binding `REFERRAL_DB` in CF Pages dashboard
4. Set secrets: `PORTAL_BEARER_TOKEN`, `RESEND_API_KEY`
5. Run data migration script
6. Deploy functions and updated refer/index.html via cf-deploy.py
7. Test all endpoints
8. Update remaining 225 pages that still use absolute portal server URL (follow-up task)

## Known Limitations

- 226 pages still reference `app.purebrain.ai/api/referral` (mostly /track endpoint).
  These will continue to work via portal server until bulk-updated.
- bcrypt password holders must use forgot-password to reset (cannot verify bcrypt in Workers)
- PayPal auto-payout not migrated (manual bridge only)
- Resend requires domain verification for purebrain.ai
