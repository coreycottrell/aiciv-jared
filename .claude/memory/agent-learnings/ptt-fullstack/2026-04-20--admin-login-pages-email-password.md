# Admin Pages: Email/Password Login Replacing Bearer Tokens

**Date**: 2026-04-20
**Type**: operational
**Agent**: cto (via ST# delegation)

## Problem
- portal.purebrain.ai/admin/clients and /admin/referrals required a portal bearer token
- Token changed every time portal_server.py restarted
- Jared couldn't log in

## Solution
Created two standalone admin HTML pages that authenticate via social.purebrain.ai's existing email/password login flow:

- `/home/jared/purebrain-site/admin/clients/index.html` -- Client admin dashboard
- `/home/jared/purebrain-site/admin/referrals/index.html` -- Referral admin dashboard

## Architecture
1. Both pages call `POST https://social.purebrain.ai/api/login` with email/password
2. Login returns `{status: "ok", token}` -- 12h session lifetime
3. Token stored in `localStorage` as `pb_admin_session` (shared between both pages)
4. On load, checks existing token via `GET /api/me` to auto-login
5. Clients page calls `GET https://social.purebrain.ai/api/admin/clients` with Bearer token
6. Referrals page tries portal proxy `/api/referral/admin/affiliates` with X-Admin-Token, falls back to public leaderboard

## Key Details
- social-api Worker: `workers/social-api/src/worker.js` -- has /api/login + /api/admin/clients
- referrals-api Worker: `workers/referrals-api/src/worker.js` -- /admin/affiliates needs X-Admin-Token (separate secret, set via wrangler secret)
- Portal proxy: `workers/purebrain-portal-proxy/src/worker.js` -- routes portal.purebrain.ai/api/admin/* to social-api, /api/referral/* to referrals-api

## Remaining Work
- Deploy to CF Pages via git (purebrain-site repo)
- Update portal proxy to serve admin pages from CF Pages instead of Chy container
- Referrals admin endpoint auth: the X-Admin-Token is a separate secret from social-api session tokens. Need to either:
  - Add social-api token validation to referrals-api, OR
  - Have portal proxy inject the admin token for authenticated requests
- Test Jared's social.purebrain.ai credentials work for admin access
