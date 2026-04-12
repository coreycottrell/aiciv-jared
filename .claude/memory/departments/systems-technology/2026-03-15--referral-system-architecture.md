# PureBrain Referral System — Architecture Reference

**Date**: 2026-03-15
**Type**: system-architecture
**Topic**: PureBrain referral system tech stack, API contract, and test approach

## System Overview

Custom-built WordPress plugin system. No third-party referral platform.

## Components

- **WordPress Plugin**: `purebrain-referral-system.php` v2.2.0
  - Path: `tools/security/purebrain-referral/purebrain-referral-system.php`
  - REST namespace: `pb-referral/v1`
  - Base URL: `https://purebrain.ai/wp-json/pb-referral/v1/`
- **Portal Server**: `app.purebrain.ai` — proxies dashboard/register/lookup, handles payouts
- **Payment Page**: fires `POST https://app.purebrain.ai/api/referral/complete` after PayPal captures

## Database Tables

- `wp_pb_referrals` — individual referral records
- `wp_pb_referral_users` — referrer accounts (code, email, totals, paypal_email)
- `wp_pb_reward_ledger` — ledger entries (revenue_share, conversion_credit, milestone_bonus)

## Commission Logic

- 5% of payment amount, minimum $5 floor
- $10 milestone bonus on 5th completed referral
- $25 minimum payout threshold (manual PayPal)

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/wp-json/pb-referral/v1/convert` | POST | Core attribution — fires on payment |
| `/wp-json/pb-referral/v1/dashboard?code=XXX` | GET | Referrer stats |
| `/wp-json/pb-referral/v1/register` | POST | Create referrer account |
| `/wp-json/pb-referral/v1/rewards?code=XXX` | GET | Ledger entries |
| `app.purebrain.ai/api/referral/complete` | POST | Portal wrapper — triggers /convert |

## Attribution Mechanism

1. `/r/XXXXXXXX` → WP rewrite → `/?ref=XXXXXXXX`
2. JS injected via `wp_footer` reads `?ref=`, stores in localStorage + cookie (30-day)
3. `window.getPbRef()` global reads it back at payment time
4. Payment page fires `/api/referral/complete` with code + payer email

## Jared's Referral Code

Pre-seeded: `JAREDSB0`
Dashboard: `https://purebrain.ai/wp-json/pb-referral/v1/dashboard?code=JAREDSB0`

## Testing Approach (No Real Money)

Call `/convert` directly — skip PayPal entirely. The endpoint is idempotent by email + code pair.

```bash
curl -X POST "https://purebrain.ai/wp-json/pb-referral/v1/convert" \
  -H "Content-Type: application/json" \
  -d '{"referrer_code":"JAREDSB0","referred_email":"test@example.com","referred_name":"Test","amount":79.00}'
```

Full plan: `exports/departments/systems-technology/2026-03-15--referral-system-e2e-test-plan.md`

## Known Issues / Tech Debt

- Repo export (`exports/app-purebrain-ai-full-repo/`) is stale — live server has newer routes
- No `is_test` flag on `/convert` — test records must be cleaned up manually
- Payout is manual (Jared sends PayPal by hand) — will not scale
- WP REST API at `purebrain.ai/wp-json/pb-referral/v1/dashboard` may return HTML
  instead of JSON when accessed externally (redirect/auth issue); always access via
  `app.purebrain.ai/api/referral/dashboard?code=XXX` instead (uses portal proxy)
