# Referral D1 Migration Fixes - Ghost Entries + Auto-Commission

**Date**: 2026-05-01
**Type**: operational
**Topic**: D1 migration gap fixes for referral system

## Key Findings

1. **Portal admin dashboard reads from LOCAL SQLite** (not D1) at `/api/admin/affiliates`. The `referrals_d1_client.py` module existed but was never imported by portal_server.py for admin endpoints. Fix: added D1-first proxy with SQLite fallback.

2. **D1 Worker had empty ADMIN_TOKENS secret** - despite being deployed, the wrangler secret was never set, so all admin API calls returned 401 silently. The portal's `D1_API_ADMIN_TOKEN` env var was correct but the Worker didn't recognize it.

3. **Auto-commission pattern**: When assigning referrals retroactively (after payment), commission must be created at assign-time, not payment-time. Solved by accepting optional `payment_amount` + `status` in the assign endpoint.

4. **`/api/refer/me` was never implemented** on portal server despite frontend already calling it. Frontend gracefully falls back to legacy SQLite path, which is why nobody noticed.

5. **Ghost entry dedup**: `GROUP BY ref.id` is correct but doesn't prevent duplicates when the `referrals` table has TWO rows for the same email under the same referrer (e.g., one pending + one completed). Fixed with correlated subquery that picks the best record per email.

## Architecture Understanding

- D1 Worker: `https://referrals-api.in0v8.workers.dev` (bound to purebrain-referrals D1 DB)
- Portal server: Local SQLite at `/home/jared/purebrain_portal/referrals.db`
- D1 client module: `/home/jared/purebrain_portal/referrals_d1_client.py`
- Admin token for D1: in portal's `.env` as `D1_API_ADMIN_TOKEN`
- Portal env flag `USE_D1_REFERRALS` exists but isn't checked by admin endpoints (they were SQLite-only)

## Gotchas

- commission_payments table in D1 does NOT have a `referrer_id` column (despite the Worker's delete cascade code referencing it). The delete endpoint has a pre-existing bug.
- D1 has 88 referrer rows but many have 0 referrals - these were mirrored from portal but referral assignments weren't mirrored
- The portal runs in a Hetzner container; local `/home/jared/purebrain_portal/` is dev copy
