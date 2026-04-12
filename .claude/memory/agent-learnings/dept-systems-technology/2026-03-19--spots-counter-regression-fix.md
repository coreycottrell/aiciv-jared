# Spots Counter Regression Fix + API Endpoint Restore

**Date**: 2026-03-19
**Type**: bug-fix | regression | root-cause
**Impact**: Invitation page counter was stuck at 15 (fallback), API /spots-status was 404

---

## Root Cause

When the referral commission update was applied on 2026-03-13, the backup file created was:
`tools/purebrain_log_server.py.bak.referral-commission-20260313`

Two critical pieces of code were NOT carried forward into the live server:

1. **Spots counter increment block** inside `verify_payment()` — responsible for writing
   to `logs/spots_state.json` when a real (non-sandbox) payment is verified.

2. **`/api/spots-status` endpoint** — the GET endpoint that the invitation page fetches
   to display the live counter.

Without the endpoint, every fetch from the invitation page returned 404, and the JS
silently kept the hardcoded fallback value (15 at time of regression).

## Evidence of Regression

- `grep "spots" tools/purebrain_log_server.py` returned nothing (before fix)
- `curl https://api.purebrain.ai/api/spots-status` returned 404 (before fix)
- The actual `logs/spots_state.json` was at 17 (correct, from manual backfills)
- The page showed 15 because the API was broken

## Fixes Applied

### 1. tools/purebrain_log_server.py
Restored two blocks from `.bak.referral-commission-20260313`:
- Spots counter increment inside `verify_payment()` (lines ~590-640 after fix)
- `/api/spots-status` GET endpoint (lines ~642-668 after fix)

### 2. exports/cf-pages-deploy/invitation/index.html line 2157
Updated hardcoded fallback: `var CLAIMED = 15` → `var CLAIMED = 17`
(So users see correct count immediately on page load, before API responds)

### 3. aether-logserver service restarted

### 4. CF Pages deployed (purebrain-staging)

## Verification
- `curl https://api.purebrain.ai/api/spots-status` → `{"spots_claimed":17,"spots_total":25}` ✓
- `curl https://localhost:8443/api/spots-status` → `{"spots_claimed":17,"spots_total":25}` ✓
- New deployment URL: https://ad08fd3f.purebrain-staging.pages.dev
- Fallback in HTML: `CLAIMED = 17` ✓

## Payment Page Counter Status (verified)

All 5 payment pages call `/api/verify-payment` correctly:
- `/live/` — YES, calls verify-payment
- `/insiders/` — YES, calls verify-payment
- `/awakened/` — YES, calls verify-payment
- `/partnered/` — YES, calls verify-payment
- `/unified/` — YES, calls verify-payment

None of the 5 pages send `isSandbox: true` (that flag is only in pay-test-sandbox-3).
Deduplication is active — same order ID cannot double-increment.

## Key Lesson

After ANY log server update (referral code, auth changes, etc.), always verify:
1. `grep "spots" tools/purebrain_log_server.py` (both counter block and endpoint exist)
2. `curl https://api.purebrain.ai/api/spots-status` (endpoint is reachable)

The backup naming pattern `.bak.{feature}-YYYYMMDD` helps identify what was replaced,
but does not guarantee the new code preserved all endpoints.

## Files Changed
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/invitation/index.html`
