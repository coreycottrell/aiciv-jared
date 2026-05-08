# Referral Attribution Audit — Pre-Cutover Findings

**Date**: 2026-05-07
**Type**: gotcha + pattern
**Topic**: Referral attribution flow has 3 cascading failures preventing any commission from being written automatically.

## Three Cascading Bugs (any one is fatal)

1. **Path mismatch in proxy**: portal-proxy strips `/api/referral` from incoming `/api/referral/complete`, forwards `/complete` to referrals-api. But referrals-api only has `/referrals/complete` and `/referrals/complete-by-email`. All homepage attribution calls 404. (`workers/purebrain-portal-proxy/src/worker.js:193-207`)
2. **No `pending` referral row ever gets created**: PayPal webhook calls `complete-by-email` which requires `WHERE r.status = 'pending'`. The only INSERTs into `referrals` table are admin manual endpoints. No customer-arrival flow seeds the row.
3. **Production payment pages don't fire attribution at all**: `/awakened/`, `/insiders/`, `/partnered/`, `/unified/` capture pb_ref cookie but `onApprove → verifyPaymentServerSide → handlePaymentSuccess` chain has no referral fetch. Only homepage + home-test/pay-test pages have it.

## Other Spec Gaps
- `BILLING.SUBSCRIPTION.UPDATED` not handled in webhook → no plan-change recalc.
- `complete-by-email` flips status to completed on first hit → recurring MRR commission never fires after month 1.
- PayPal Auto-Split (60/40 Corey/PT) is a manual Python CLI, not wired into webhook.
- `/referrer-discount` endpoint exists but no payment page calls it.
- Support Tier 25% rate not in `calculateCommission()` (hard cap 20%).
- Min payout $50 not enforced in code.

## Pattern Worth Remembering
When auditing a referral system, trace BOTH directions:
1. CLICK→COOKIE→DB (does click record persist?)
2. PAYMENT→ATTRIBUTION→COMMISSION (does payment trigger commission write?)

Most referral bugs live in step 2 and look fine in step 1. The cookie working tells you nothing about whether attribution fires.

## File Paths
- Audit deliverable: `/home/jared/projects/AI-CIV/aether/exports/portal-files/audit-payment-flow-2026-05-07.md`
