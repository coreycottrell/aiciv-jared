# Referral Dashboard — Wired to Production Data + PayPal

**Date**: 2026-04-06
**Type**: operational
**Topic**: Referral dashboard production wiring, data seed, PayPal payout integration

## What Was Done

### 1. Data Architecture Fix
- **Problem**: purebrain.ai migrated from WordPress to CF Pages, killing the WP REST API (`/wp-json/pb-referral/v1/*`)
- The portal server (37.27.237.109) was proxying to the dead WP endpoint
- The standalone referral API (157.180.69.225:8099) had empty DB — only 1 referrer, 0 referrals
- **Solution**: Seeded the standalone API DB with real affiliate data and made it the single source of truth

### 2. Production Data Seeded
- 5 affiliates: JAREDSB0 (Jared), PB-K22P (MJ S), PB-AYXE (Apex People), PB-MH7K (Michael Hancock), PB-AL3X (Alex Logie)
- 20 referral records with commission/reward data
- Click tracking data (101 total clicks across all affiliates)
- Idempotent seed script: `/opt/referral-api/seed_referral_data.py`

### 3. PayPal Payout Integration
- Added `payout_requests` table to DB schema
- `POST /api/referral/payout-request` — user requests payout (min $25, 30-day cooldown)
- `GET /api/referral/payout-history` — view payout history
- `POST /api/referral/admin/payout-action` — admin approves/rejects (triggers PayPal Payouts API)
- PayPal credentials added to systemd service env vars
- Telegram notifications on payout events

### 4. Frontend Unified
- All API calls now point to `surf.purebrain.ai/api/referral/*` (was split between `app.purebrain.ai` and `surf.purebrain.ai`)
- `app.purebrain.ai` routes to portal server which proxied to dead WP — unusable for referral API
- Deployed to CF Pages, cache flushed

## Key Files
- API: `/opt/referral-api/referral_api.py` on 157.180.69.225
- Local copy: `exports/referral-api/referral_api.py`
- Seed: `exports/referral-api/seed_referral_data.py`
- Frontend: `exports/cf-pages-deploy/refer/index.html`
- Service: `purebrain-referral-api.service` on 157.180.69.225

## Architecture (Current)
```
purebrain.ai/refer/ (CF Pages static)
  → JS calls surf.purebrain.ai/api/referral/*
    → Caddy on 157.180.69.225 reverse proxies to localhost:8099
      → FastAPI referral_api.py
        → SQLite at /opt/referral-api/referrals.db
        → PayPal Payouts API (for approved payouts)
```

## Security
- Session tokens (random 64-char hex, 7-day TTL, stored in DB)
- Session isolation: each API call validates session matches the requested referral code
- PayPal email changes require active session
- Payout requests require active session + admin approval to trigger PayPal
- Rate limiting on login (10 attempts/15 min) and tracking (30/5 min)
- Bcrypt password hashing with PBKDF2 migration support

## Dead Code / Cleanup Needed
- Portal server (37.27.237.109) still has dead WP proxy endpoints — harmless but misleading
- `app.purebrain.ai/api/referral/*` routes to portal, not standalone API — should be redirected or removed
