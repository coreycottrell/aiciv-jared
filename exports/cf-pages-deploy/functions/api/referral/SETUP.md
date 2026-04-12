# Referral System — CF Pages Functions Setup Guide

## Architecture

The referral system backend runs entirely on Cloudflare Pages Functions with D1 database.
No server dependency. No single point of failure.

## Prerequisites

1. Cloudflare account with Pages project `purebrain-staging`
2. `wrangler` CLI installed and authenticated

## Step 1: Create D1 Database

```bash
wrangler d1 create purebrain-referrals
```

Copy the `database_id` from the output. You will need it for the binding.

## Step 2: Apply Schema

```bash
wrangler d1 execute purebrain-referrals \
  --file=exports/cf-pages-deploy/d1-migrations/0001-referral-schema.sql \
  --remote
```

## Step 3: Configure D1 Binding in CF Pages

Go to Cloudflare Dashboard:
1. Pages > purebrain-staging > Settings > Functions
2. Under "D1 database bindings", add:
   - Variable name: `REFERRAL_DB`
   - D1 database: `purebrain-referrals`

## Step 4: Set Environment Variables (Secrets)

In CF Pages Dashboard > Settings > Environment variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `PORTAL_BEARER_TOKEN` | (same as portal server) | For admin API calls |
| `RESEND_API_KEY` | (from resend.com) | For password reset emails |

**Resend Setup**: Create account at resend.com, verify `purebrain.ai` domain,
get API key. Free tier is 100 emails/day (plenty for password resets).

## Step 5: Migrate Existing Data

```bash
./tools/migrate-referrals-to-d1.sh
```

This exports data from the portal server SQLite and provides the import command.

## Step 6: Update Frontend

The refer/index.html apiBase needs to change from:
```
https://app.purebrain.ai/api/referral
```
to:
```
/api/referral
```

This is a relative path, so it hits the same CF Pages domain (purebrain.ai/api/referral/*).

## Step 7: Deploy

```bash
python3 tools/cf-deploy.py functions/api/referral/
python3 tools/cf-deploy.py refer/index.html
```

## Step 8: Verify

Test each endpoint:
```bash
# Track click
curl -X POST https://purebrain.ai/api/referral/track \
  -H "Content-Type: application/json" \
  -d '{"referral_code":"JAREDSB0"}'

# Leaderboard (public, no auth)
curl https://purebrain.ai/api/referral/leaderboard
```

## Step 9: Deprecate Old Endpoints

Once verified, the old endpoints on app.purebrain.ai can be commented out.
The frontend will no longer call them.

## Endpoints

| Path | Method | Auth | File |
|------|--------|------|------|
| /api/referral/register | POST | Public | register.js |
| /api/referral/session | POST | Public (login) | session.js |
| /api/referral/dashboard | GET | Session/Admin | dashboard.js |
| /api/referral/track | POST | Public | track.js |
| /api/referral/forgot-password | POST | Public | forgot-password.js |
| /api/referral/reset-password | POST | Public | reset-password.js |
| /api/referral/complete | POST | Public | complete.js |
| /api/referral/commission | POST | Admin bearer | commission.js |
| /api/referral/leaderboard | GET | Public | leaderboard.js |
| /api/referral/paypal-email | POST | Session/Admin | paypal-email.js |
| /api/referral/payout-request | POST | Session/Admin | payout-request.js |
| /api/referral/payout-history | GET | Session/Admin | payout-history.js |

## Password Migration Note

The portal server uses bcrypt for password hashing. CF Workers cannot run bcrypt
(no native C bindings). The new system uses PBKDF2-SHA256 (Web Crypto API).

- Users with bcrypt hashes will be prompted to use "Forgot Password" to reset
- On reset, new PBKDF2 hash is stored
- Legacy SHA-256 hashes (salt:hash format) are verified and auto-migrated on login
- New registrations use PBKDF2 from the start
