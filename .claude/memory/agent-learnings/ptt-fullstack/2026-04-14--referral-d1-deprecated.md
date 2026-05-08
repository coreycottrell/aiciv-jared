# Referral System — D1 Deprecated, VPS SQLite is Sole Source of Truth

Type: operational
Date: 2026-04-14
Agent: ptt-fullstack

## Verified State (production)
- `/refer/` frontend (`exports/cf-pages-deploy/refer/index.html`) already calls `https://app.purebrain.ai/api/referral/*` — VPS Python backend, NOT CF D1.
- `app.purebrain.ai` DNS/routing sends traffic to `portal_server.py` (VPS), so CF Pages Functions under `functions/api/referral/*` are unreachable in practice.
- `api_referral_dashboard` (portal_server.py:4036) exists, scoped by `?code=PB-XXXX` with session/password/portal auth.
- Admin endpoint `api_admin_affiliates` (portal_server.py:5128) hits same SQLite — that's why both views match when data is clean.
- JAREDSB0 in SQLite: referrer_id=1, 10 referrals (all completed), rewards_sum=$70.775, 43 clicks.
- Live dashboard endpoint returns HTTP 401 without auth — confirms endpoint present and enforcing auth.

## Action Taken
- Added `⚠️ DEPRECATED` header banners to:
  - `exports/cf-pages-deploy/functions/api/referral/dashboard.js`
  - `exports/cf-pages-deploy/functions/api/referral/complete.js`
- Both headers point future agents to portal_server.py as SOT, warn against edits.

## Skipped (and why)
- **D1 JSON archive dump**: Local box has no `wrangler.toml` and no `~/.wrangler` creds — cannot `npx wrangler d1 execute purebrain-referrals`. Flagged for Jared: run from machine with CF account auth OR delegate to infra agent with those creds.
- **Frontend repoint**: Not needed — `apiBase = 'https://app.purebrain.ai/api/referral'` already in place at `refer/index.html:815`.
- **CF Pages deploy**: Change is comments-only on unreachable files. Low value to push; will ride along with next deploy.
- **SQLite UPDATE/DELETE**: Requires Jared approval per scope. Admin view confirms clean data; no drift observed for JAREDSB0.

## Follow-Ups for Jared
1. Archive D1 from a box with wrangler auth: `npx wrangler d1 execute purebrain-referrals --command "SELECT * FROM referrals" --json > /tmp/d1-referrals-archive-2026-04-14.json` (repeat for `referrers`, `rewards`, `commission_payments`, `referral_clicks`).
2. After archive confirmed, remove D1 binding from Pages project settings so deprecated functions can't accidentally write.
3. Consider deleting `functions/api/referral/*.js` entirely in a future cleanup PR to prevent cargo-culting.

## Files Referenced
- `/home/jared/purebrain_portal/portal_server.py` (lines 4036, 5128)
- `/home/jared/purebrain_portal/referrals.db`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/refer/index.html` (apiBase @ 815)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/functions/api/referral/dashboard.js` (deprecated)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/functions/api/referral/complete.js` (deprecated)
