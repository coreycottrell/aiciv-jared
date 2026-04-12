# Referral Commission Model: Changed to 5% Recurring

**Date**: 2026-03-13
**Directive**: Jared — "5% of all payments from the monthly payments from each person they sign up"

## What Changed

### portal_server.py
- Removed: `REWARD_PER_REFERRAL = 5.0` (flat $5 per referral)
- Added: `REFERRAL_COMMISSION_RATE = 0.05` (5% recurring)
- Added: `commission_payments` table in SQLite DB (tracks each payment + commission)
- Added: `api_referral_record_commission` endpoint — `POST /api/referral/commission`
- Changed: `api_referral_complete` no longer issues flat reward, just records the referral relationship
- Changed: Dashboard `reward_tiers` now shows 5% recurring with tier examples
- Changed: Dashboard history query now joins `commission_payments` instead of `rewards` for per-referral earnings
- Added route: `/api/referral/commission`

### purebrain_log_server.py
- After every real (non-sandbox) payment is verified in `/api/verify-payment`
- Calls `https://app.purebrain.ai/api/referral/commission` in background thread
- Sends: payer_email, order_id, amount, tier
- Commission endpoint checks if payer was referred, issues 5% if so, deduplicates by order_id

### Frontend (CF Pages)
- `refer/index.html` — updated 3 text strings to reflect 5% recurring
- `refer-and-earn/index.html` — updated meta descriptions (reward_tiers come from API)
- `affiliate-portal.html` — updated tagline
- `admin-referrals.html` — added "5% recurring commission model" label in header

## Key Design Decisions
1. `commission_payments` table is separate from `rewards` — clean audit trail per payment
2. `rewards` still gets an INSERT for each commission so balance queries stay consistent
3. Deduplication by `order_id` prevents double-commissions on retries
4. Only fires for real payments (not sandbox/E2E/test)
5. Sandbox pattern check: uses same `is_sandbox_or_test` flag as spots counter

## Backup Files
- `/home/jared/purebrain_portal/portal_server.py.bak.referral-commission-20260313`
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py.bak.referral-commission-20260313`
