# Referral System Fixes Round 2 - 2026-05-01

## Issue 1: Ghost "rejected" Laurie entry in admin dashboard

**Root Cause**: The admin dashboard was reading from local SQLite (portal_server.py) which may have stale/duplicate records. D1 (the single source of truth) has only 1 Laurie Clifton record (id=42, status=completed) under Ian Wheaton.

**Fix Applied** (two layers):
1. **Portal server** (`portal_server.py` line ~5128): `/api/admin/affiliates` now tries D1 first via `referrals_d1_client.admin_affiliates()`. Falls back to SQLite only if D1 returns 0 results or errors.
2. **Deduplication query** (both Worker and portal SQLite fallback): Changed `GROUP BY ref.id` to include a subquery that picks only ONE record per `(referred_email, referrer_id)` pair, preferring the 'completed' status entry. This eliminates ghosts from duplicate referral rows.

**Verification**: D1 `/admin/affiliates` shows exactly 1 Laurie Clifton (completed) under Ian Wheaton with $7.45 earnings. No rejected ghost.

---

## Issue 2: Auto-commission when referral assigned after payment

**Fix Applied** (Worker `POST /admin/referral/assign`):
- Accepts new optional fields: `status` (default 'pending'), `payment_amount`, `commission_rate` (default 0.05)
- When `status=completed` AND `payment_amount > 0`, auto-creates a `commission_payments` row with:
  - `order_id = 'retroactive-assign'`
  - `commission_value = payment_amount * commission_rate`
  - `tier = 'Awakened'`
- Works for all three paths: new assignment, status update (same referrer), and referrer move
- **Portal mirror**: `/api/admin/referral/assign` on portal_server.py now also proxies to D1 with the client's average payment amount auto-calculated from the clients table

**Verification**: Tested with `payment_amount=149`, confirmed commission of $7.45 (149 * 0.05) appears in D1.

**Usage from admin frontend**:
```json
POST /admin/referral/assign
{
  "referral_code": "PB-XXXX",
  "client_email": "client@example.com",
  "client_name": "Client Name",
  "status": "completed",
  "payment_amount": 149
}
```

---

## Issue 3: Portal Refer & Earn section sync to D1

**Root Cause**: The portal frontend calls `/api/refer/me` as its primary path (D1-backed, auto-provisioning). This endpoint didn't exist on the portal server, so it always fell back to the legacy SQLite path (`/api/referral/register` + `/api/referral/dashboard`).

**Fix Applied** (`portal_server.py`):
- Added `api_refer_me()` endpoint at `/api/refer/me`
- Uses `referrals_d1_client` to:
  1. Look up existing referrer by email
  2. Auto-provision a new referral account if none exists (generates PB-XXXX code)
  3. Fetch dashboard stats from D1
  4. Returns shape expected by frontend: `{ok, referrer, stats, referral_link}`
- Falls back gracefully to `{disabled: true}` if D1 is unavailable (triggers frontend legacy path)
- Route registered in Starlette routes list

**Env Requirements** (already set in portal .env):
- `D1_API_URL=https://referrals-api.in0v8.workers.dev`
- `D1_API_ADMIN_TOKEN=<token>`

---

## Deployment Status

- **Worker**: Deployed to `https://referrals-api.in0v8.workers.dev` (version cc1f6465)
- **ADMIN_TOKENS secret**: Updated to include all three known tokens (D1 client, admin viewer, .env)
- **Portal server**: Changes in `/home/jared/purebrain_portal/portal_server.py` - needs portal restart to take effect

## Files Modified

1. `/home/jared/projects/AI-CIV/aether/workers/referrals-api/src/worker.js`
   - `/admin/referral/assign`: Added `status`, `payment_amount`, `commission_rate` params with auto-commission logic
   - `/admin/affiliates` history query: Deduplication subquery

2. `/home/jared/purebrain_portal/portal_server.py`
   - `api_admin_affiliates()`: D1-first with SQLite fallback + dedup query
   - `api_admin_referral_assign()`: D1 mirror with auto-commission from clients DB
   - `api_refer_me()`: New endpoint for D1-backed Refer & Earn

## Notes

- D1 has real data (88 referrers, commission_payments table populated)
- The portal's ADMIN_TOKENS secret was not previously set on the Worker (was empty), causing all admin calls from portal to D1 to fail silently. Now fixed.
- Test referrer (id=88, code=TEST-001) left in D1 from verification - can be cleaned up
