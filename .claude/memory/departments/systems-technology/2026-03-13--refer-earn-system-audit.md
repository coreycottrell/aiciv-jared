# ST# Memory: Refer & Earn System Audit

**Date**: 2026-03-13
**Type**: audit
**Topic**: Comprehensive status check of the overnight Refer & Earn system build

---

## Audit Summary

Four-part investigation: code location, CF Pages live status, API endpoint status, SQLite DB.

---

## What EXISTS and is WORKING

### SQLite Database
- **Path**: `/home/jared/purebrain_portal/referrals.db`
- **Size**: 32KB (initialized, no rows yet — clean schema)
- **Tables confirmed**: `referrers`, `referrals`, `referral_clicks`, `rewards`, `sqlite_sequence`
- **Schema**: Full columns match the architecture spec from CTO memory

### Portal Server API (7 endpoints wired, ALL respond)
- **Server**: Running as `/usr/bin/python3 /home/jared/purebrain_portal/portal_server.py`
- **Base URL**: `https://app.purebrain.ai`
- Endpoints registered in routing table (lines 2747-2756 of portal_server.py):
  - `POST /api/referral/register` — register referrer, get code
  - `GET /api/referral/dashboard` — referrer stats
  - `POST /api/referral/track` — click tracking
  - `POST /api/referral/complete` — mark referral complete
  - `GET /api/referral/code/{email}` — lookup code by email
  - `POST /api/referral/paypal-email` — save PayPal email
  - `GET /api/referral/leaderboard` — top referrers (returns 200)
  - `POST /api/referral/payout-request` — request payout
  - `GET /api/referral/payout-history` — payout history

**Live test**: `GET /api/referral/leaderboard` → HTTP 200. `GET /api/referral/dashboard` (no params) → HTTP 400 (correct — missing required param).

### CF Pages — Both Refer Pages Are Live
- `https://purebrain.ai/refer/` → HTTP 200
- `https://purebrain.ai/refer-and-earn/` → HTTP 200
- Files exist at `exports/cf-pages-deploy/refer/index.html` and `exports/cf-pages-deploy/refer-and-earn/index.html`

---

## CRITICAL BUG: Pages Still Point to Dead WP Endpoints

Both refer pages have `API_BASE = 'https://purebrain.ai/wp-json/pb-referral/v1'` hardcoded.

**Evidence:**
- `exports/cf-pages-deploy/refer/index.html` line: `var API_BASE = 'https://purebrain.ai/wp-json/pb-referral/v1';`
- `exports/cf-pages-deploy/refer-and-earn/index.html` line: same
- `purebrain-site/public/refer/index.html` line: same

**Dead endpoint proof**: `curl https://purebrain.ai/wp-json/pb-referral/v1/register` returns homepage HTML, NOT a REST API response. HTTP 200 but completely broken.

**Required fix**: Replace `API_BASE` in both CF Pages HTML files with `https://app.purebrain.ai` and redeploy.

---

## What's MISSING / Not Done

1. **API_BASE URL swap** — the single most important missing step. Backend built, frontend not updated to point at it.
2. **Zero data in DB** — expected for a fresh build, but means no end-to-end test has been run
3. **purebrain-site/public/refer/index.html** is actually the homepage (wrong file mapped there) — separate issue

---

## Fix Required

In both `exports/cf-pages-deploy/refer/index.html` and `refer-and-earn/index.html`:
```
BEFORE: var API_BASE = 'https://purebrain.ai/wp-json/pb-referral/v1';
AFTER:  var API_BASE = 'https://app.purebrain.ai';
```
Then redeploy to CF Pages + purge CF cache.
