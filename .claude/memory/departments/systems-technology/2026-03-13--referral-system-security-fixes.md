# Referral System Security Fixes — 2026-03-13

## Summary
Fixed 4 security and UX issues in the PureBrain referral/affiliate system.

## Issue 1: Referral Link Format
**Status**: Was already CORRECT in portal_server.py (`_referral_link()` returns `/?ref=CODE`)
- All share links correctly use `https://purebrain.ai/?ref=CODE`
- `/refer/?code=CODE` is the dashboard URL — that is intentional and correct
- No change needed to portal-pb-styled.html share logic

## Issue 2: Affiliate Dashboard Password Protection
**Changes**:
- Added `password_hash` column to `referrers` table (SQLite ALTER TABLE migration for existing DBs)
- Added `_hash_affiliate_password()` / `_verify_affiliate_password()` helpers (SHA-256 + salt)
- New endpoint `POST /api/referral/login` — verifies password, returns referral_code
- `GET /api/referral/dashboard` now requires `?password=` unless portal bearer token is present
- `POST /api/referral/paypal-email` now requires `password` in body unless bearer auth
- Legacy accounts (no password_hash) get password set on first login — backwards compatible
- `affiliate-portal.html` updated with password fields in lookup + register forms

## Issue 3: /affiliate Redirect
**Changes**:
- `GET /affiliate` now returns 301 redirect to `https://purebrain.ai/refer/`
- With `?code=CODE` query param, redirects to `https://purebrain.ai/refer/?code=CODE`
- Canonical affiliate URL is now `purebrain.ai/refer/`

## Issue 4: Admin Dashboard Multi-User Access
**Changes**:
- New `admin_tokens` table: `(id, token, email, name, role, created_at)`
- New endpoint `POST /api/admin/invite` — generates viewer token (main bearer only)
- `GET /api/admin/affiliates` and `GET /api/admin/payouts` accept `?admin_token=XXX`
- `admin-referrals.html` reads `?admin_token=` from URL, auto-authenticates viewer
- Viewer mode hides `.action-btn-write` buttons + shows "Read-only view" banner
- Mark Paid button gets `action-btn-write` class so it's hidden from viewers

## Files Changed
- `/home/jared/purebrain_portal/portal_server.py`
- `/home/jared/purebrain_portal/affiliate-portal.html`
- `/home/jared/purebrain_portal/admin-referrals.html`
- No changes needed: `portal-pb-styled.html`, `refer/index.html`, `referral-program/index.html`

## Verification Results
- Register with password: OK — returns `/?ref=CODE` format
- Register without password: REJECTED (400)
- Login correct password: OK
- Login wrong password: 401
- Dashboard with password: OK
- Dashboard without password: 401
- Dashboard with bearer token: OK (portal owner bypass)
- Admin invite: OK — returns viewer token + dashboard URL
- Admin access with viewer token: 200
- Admin access without auth: 401
- /affiliate redirect: 301 → purebrain.ai/refer/
