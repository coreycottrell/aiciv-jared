# Referral System Security + PayPal Payouts
**Date**: 2026-03-15
**Agent**: dept-systems-technology
**Type**: feature build

---

## What Was Built

### Task 1: Dashboard Security (Password-Gated Login)

**Problem**: `GET /api/referral/dashboard?code=XXXX` returned full PII (earnings, emails, referral names) to anyone who knew a referral code. Codes are public (they're in share URLs).

**Solution implemented**:
- Added `_AFFILIATE_SESSIONS` dict (in-memory, 7-day TTL session tokens)
- Added `_AFFILIATE_LOGIN_ATTEMPTS` dict for rate-limiting (10 attempts / 15 min window per IP)
- New `POST /api/referral/session` endpoint: email+password → session token
- Dashboard now requires: portal bearer token OR valid session token OR password param
- Existing accounts with no password_hash: first login sets the password (no friction for legacy users)
- All affiliate-facing endpoints updated to accept session tokens: dashboard, payout-request, payout-history, paypal-email

**Frontend changes** (`refer/index.html`):
- Added login gate div (`#pb-ref-login-gate`) shown when no session present
- `sessionStorage` used for session token (cleared on tab close)
- `loadDashboard()` function now wraps fetch; handles 401 by showing login gate
- Register form now has password field; auto-logs in and stores session after registration
- All API calls pass session token in body + `X-Affiliate-Session` header

### Task 2: Automated PayPal Payouts

**Problem**: Payout requests went to Jared's Telegram for manual action. Not scalable.

**Solution implemented**:
- `_paypal_get_access_token()`: OAuth2 client_credentials grant
- `_execute_paypal_payout(paypal_email, amount, request_id, note)`: Payouts API call
- `POST /api/referral/payout-approve`: bearer-gated endpoint that reads a pending request, fires PayPal payout, updates status to "completed", logs PayPal batch_id, notifies Telegram
- Supports `dry_run=true` for testing without sending money
- Sandbox mode: `PAYPAL_SANDBOX=true` (default) uses `PAYPAL_SANDBOX_CLIENT_ID` + `PAYPAL_SANDBOX_SECRET`
- Live mode: `PAYPAL_SANDBOX=false` uses `PAYPAL_CLIENT_ID` + `PAYPAL_SECRET`
- Payout status flow: pending → completed (success) or failed (PayPal error)

---

## Credentials Needed for Full Operation

- `PAYPAL_SANDBOX_CLIENT_ID` / `PAYPAL_SANDBOX_SECRET`: present in `.env` (for testing)
- `PAYPAL_CLIENT_ID` / `PAYPAL_SECRET`: present in `.env` (for live)
- Switch to live: set `PAYPAL_SANDBOX=false` in environment

---

## Files Changed

- `/home/jared/purebrain_portal/portal_server.py`
  - Backup at: `portal_server.py.bak-st-referral-20260315`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/refer/index.html`

---

## Architecture Notes

- Session tokens are in-memory only — they reset on portal restart. This is intentional for now (7-day TTL, affiliates re-login after restart).
- Rate limit (10 attempts / 15 min) is per IP, in-memory. For production scale, SQLite-backed would be more robust but current volume doesn't need it.
- PayPal Payouts API requires a Business account. The payout sender is support@puremarketing.ai (determined by the PayPal app credentials).
- The `/api/referral/payout-request` endpoint no longer requires portal bearer token — affiliates call it with their session token.

---

## Testing Instructions

### Dashboard Security
1. Visit `https://purebrain.ai/refer/` without `?code=` param — should show login gate
2. Visit with `?code=JAREDSB0` — should show login gate (not the dashboard)
3. Login with email + password — should load dashboard
4. Verify `GET /api/referral/dashboard?code=JAREDSB0` with no session returns 401
5. Jared's portal bearer token still bypasses: `?token=BEARER` or `Authorization: Bearer TOKEN`

### PayPal Payouts (Sandbox)
1. Create a pending payout request via the frontend
2. Call `POST /api/referral/payout-approve` with bearer token + `{"request_id": "...", "dry_run": true}` — should return dry run confirmation
3. Call without `dry_run` — should fire PayPal sandbox payout and return batch_id
4. Check payout-requests.jsonl — status should be "completed" with paypal_batch_id

### Switch to Live
- Set `PAYPAL_SANDBOX=false` in portal environment
- Restart portal
