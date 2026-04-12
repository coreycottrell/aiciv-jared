# CTO Memory: Referral Payout System — Phase 3 Architecture Research

**Date**: 2026-03-06
**Type**: teaching
**Agent**: cto
**Confidence**: high
**Tags**: referral-system, payout, paypal, stripe, architecture, phase3

---

## Context

Phase 2 referral system is live. `wp_pb_reward_ledger` has `status ENUM (pending | approved | paid)` already built.
Task was to research withdrawal/payout mechanisms for referral earners.

---

## Key Decisions

### Recommended: PayPal Payouts API
- $0.25/domestic transaction (cheapest option)
- Requires PayPal Payouts API approval (apply at developer.paypal.com → My Account → Payouts → Enable)
- Same PayPal Business account PureBrain already uses for payments
- Likely fast approval given existing transaction history
- Recipient only needs a PayPal email address — no bank KYC

### Do NOT Use Stripe Connect
- Express accounts deprecated
- Custom accounts require full KYC per recipient
- Massive compliance overhead for small payout volumes

### Do NOT Switch to AffiliateWP or SliceWP
- Phase 2 custom system is production-ready
- Plugins would abandon the existing WP plugin + portal proxy architecture
- Ongoing licensing cost for features already built

---

## Phased Approach

### Phase 3a (Days) — Manual Bridge
1. "Request Payout" button in portal referral panel (min $25 threshold)
2. WP endpoint writes pending ledger entry, Telegrams Jared
3. Jared pays manually via PayPal.com
4. Admin marks ledger as `paid`

### Phase 3b (Post-approval) — Automated
1. Portal server `/admin/process-payouts` endpoint
2. Batches pending requests to PayPal Payouts API
3. Auto-marks ledger as `paid` on success

---

## Security Rules Established

- Never auto-pay without admin review (Phase 3a)
- Verify balance before payout
- 1 payout request per referral code per 30 days
- 14-day refund grace period before payout eligibility
- Admin capability check on mark-paid endpoint
- $600/year 1099 threshold — flag to finance
- Maintain PayPal balance buffer with Telegram alert at $200

---

## Files

- Research report: `exports/referral-payout-research.md`
- Phase 2 plugin: `tools/security/purebrain-referral/purebrain-referral-system.php` v2.0.0
