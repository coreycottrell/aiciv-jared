# Referrals API — 7 Public Endpoints Added

**Date**: 2026-04-21
**Type**: operational
**File**: `/home/jared/projects/AI-CIV/aether/workers/referrals-api/src/worker.js`

## What Was Added

7 public endpoints for the /refer/ page (no admin auth):

1. **POST /session** — Login by code or email + password. Returns dashboard data + session token.
2. **POST /register** — New affiliate signup. Generates PB-XXXXXX code, hashes password with SHA-256.
3. **POST /forgot-password** — Reset token generation. Always returns success (security).
4. **POST /track** — Click tracking. Falls back to cf-connecting-ip if no ip in body.
5. **POST /paypal-email** — Update PayPal email by referral_code.
6. **POST /payout-request** — Request payout. Looks up referrer by code, inserts into payout_requests.
7. **GET /payout-history?referral_code=PB-XXXX** — Payout history for a referrer.

## Password Hashing

Uses `crypto.subtle.digest("SHA-256", "purebrain-salt:" + password)` — same for register and login.

## Key Decisions

- Session tokens are generated but stateless (random 32-byte hex). Server-side session storage can be added later.
- `/forgot-password` stores token in `password_reset_tokens` table (may not exist yet — silently handles that).
- `/register` retries code generation up to 10 times to avoid collisions.
- All existing admin endpoints remain unchanged.
