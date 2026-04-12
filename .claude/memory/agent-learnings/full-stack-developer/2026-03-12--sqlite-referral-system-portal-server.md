# SQLite Referral System — Portal Server Migration

**Date**: 2026-03-12
**Type**: operational
**Topic**: Migrated WP plugin referral system to SQLite in portal_server.py

---

## What Was Built

Replaced 3 dead WordPress proxy endpoints with a full SQLite-backed referral system.

### Database: `/home/jared/purebrain_portal/referrals.db`
4 tables auto-created on startup via `_init_referral_db()`:
- `referrers` — user_email (UNIQUE), referral_code (UNIQUE), paypal_email
- `referrals` — referrer_id FK, referred_email, status (pending/completed), timestamps
- `referral_clicks` — referral_code, ip_hash (SHA256 truncated), clicked_at
- `rewards` — referrer_id, referral_id, reward_value, issued_at

### 7 New API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/referral/register` | POST | Register, returns PB-XXXX code |
| `/api/referral/dashboard` | GET | Stats by code or email |
| `/api/referral/track` | POST | Log click (hashed IP) |
| `/api/referral/complete` | POST | Mark complete + issue reward |
| `/api/referral/code/{email}` | GET | Look up code by email |
| `/api/referral/paypal-email` | POST | Save PayPal email |
| `/api/referral/leaderboard` | GET | Top referrers |

Plus existing: `payout-request`, `payout-history`, `admin/payout/mark-paid` (updated balance check from dead WP → SQLite)

### Code Format
`PB-XXXX` where X is from `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` (no ambiguous chars like 0/O/1/I)

---

## Key Patterns

### aiosqlite async pattern
```python
async with aiosqlite.connect(str(REFERRALS_DB)) as db:
    db.row_factory = aiosqlite.Row  # enables dict-style access
    cur = await db.execute("SELECT ...", (param,))
    row = await cur.fetchone()
    rows = [dict(r) async for r in cur]  # async iteration
    await db.commit()
```

### COLLATE NOCASE in SQLite
All email/code lookups use `COLLATE NOCASE` to make comparisons case-insensitive without lowercasing at query time.

### Startup hook
Added `await _init_referral_db()` to the existing `_startup()` async function. Tables created idempotently with `CREATE TABLE IF NOT EXISTS`.

### Payout balance check
Old code called dead WP endpoint for balance validation. Replaced with direct SQLite rewards SUM query.

---

## Files Changed

- `/home/jared/purebrain_portal/portal_server.py` — main changes
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/refer/index.html` — API base changed from WP to `/api/referral`
- `/home/jared/purebrain_portal/REFERRAL-PORTAL-CHANGES.md` — notes for portal-pb-styled.html changes (deferred — another agent working on it)

---

## Gotchas

- `aiosqlite` was already installed (v0.22.1) — no need to install
- Starlette path params use `{email}` in route but are accessed via `request.path_params.get("email")`
- The payout request handler still uses JSONL file (`payout-requests.jsonl`) for payout history — intentional, that's a separate manual review flow
- The `refer/index.html` dashboard also calls `/api/referral/paypal-email` and `/api/referral/payout-request` which were NOT in the original dead proxy set — needed to add paypal-email endpoint as new addition

---

## Deployment

CF Pages deploy: `CLOUDFLARE_API_TOKEN=... npx wrangler pages deploy exports/cf-pages-deploy/refer --project-name=purebrain-staging --branch=main`
Token env var is `CF_PAGES_TOKEN` in `.env` but wrangler needs it as `CLOUDFLARE_API_TOKEN`.
