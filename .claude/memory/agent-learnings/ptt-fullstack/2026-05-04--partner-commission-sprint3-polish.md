# Partner Commission System Sprint 3 - Final Polish

**Date**: 2026-05-04
**Type**: operational
**Agent**: ptt-fullstack

## What Was Done

Sprint 3 polish of the partner commission system: integration testing, edge case fixes, PayPal webhook integration, portal proxy route additions.

## Key Fixes

1. **Split validation tier-aware**: PATCH /admin/partners/:id/splits now validates total split percentages against tier-specific maximums (5% standard, 15%/17%/20% elite based on sales volume).
2. **Discount endpoint**: New GET /referrer-discount?code=XX public endpoint for checkout pages to detect partner discounts.
3. **Manual payment FK fix**: commission_payments has NOT NULL FK on referral_id. Fixed by auto-creating synthetic referral record for manual payments.
4. **Delete cascade FK-safe**: DELETE /admin/affiliate/delete now deletes commission_payments by referral_id (subquery) before deleting referrals. Also wrapped rewards/payout_requests in try/catch.
5. **PayPal webhook -> referrals**: New POST /referrals/complete-by-email endpoint. PayPal webhook worker calls this on SUBSCRIPTION.ACTIVATED and PAYMENT.SALE.COMPLETED.
6. **Portal proxy routes**: Added /admin/partners, /api/admin/partners, /api/admin/commission-report, /api/admin/splits, /api/admin/payments.

## Key Gotchas

- **D1 FK constraints are strict**: Cannot use NULL or string literals for FK columns with NOT NULL. Must create real records.
- **rewards table schema drift**: The rewards table in D1 doesn't have referrer_id column (different from what the code assumed). Always wrap optional table operations in try/catch.
- **Commission calculation**: $35 ops deducted first, then tier rate applied. Elite 0-99 sales = 15%.
- **Split validation math**: Compare against tier max rate, not 100%. A partner's splits cannot exceed what their tier allows.

## Files

- `workers/referrals-api/src/worker.js` (~72 KiB after changes)
- `workers/paypal-webhook/src/worker.js` (added completeReferralCommission function)
- `workers/purebrain-portal-proxy/src/worker.js` (added partner/commission routes)
