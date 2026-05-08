# PurePartner2026 Spec Gaps — Pattern Analysis

**Date**: 2026-05-07
**Type**: pattern
**Confidence**: high

## Context
Audited public partner page (https://purebrain.ai/partners/) against `workers/referrals-api/src/worker.js` and `workers/paypal-webhook/src/worker.js`.

## Discovery: 5 systemic gaps blocking production

1. **Default tier rate is 5%, page promises 15%** — `worker.js:196-203, 905-906`. Public signup endpoint `/partners/signup` hardcodes `partner_tier='standard'` which gets 5% flat rate. The 15/17/20% tier ladder only applies if partner_tier='elite'. Highest-impact gap.

2. **No approval/30-day-use enforcement** — `partners/index.html:1709` posts application to Brevo (marketing list), NOT to any DB review table. `/partners/signup` accepts anyone with the access code 'PurePartner2026' and creates an immediately-active partner. Page explicitly promises personal review and 30-day prior usage.

3. **No retroactive rate recalc** — Code applies new rate going forward but never updates `commission_payments` rows when `total_sales` crosses 100/1000 thresholds. Page explicitly promises "+2% retroactive to all clients".

4. **No partner-facing payout endpoint, no $50 minimum check** — Only `/admin/payouts` (admin-only) and `/admin/payout/mark-paid` exist. No `POST /payouts/request` for partners. Page promises self-service payouts at $50 min.

5. **Page copy contradicts code** — Page says "updated monthly", "verified against Stripe", "Net-30 after first billing cycle". Code is real-time PayPal with immediate commission record. Easiest fix: rewrite page paragraphs.

## Why it matters
Live page is making contractual promises. Partners signing up TODAY expect 15% but will receive 5%. This is a money-on-the-line discrepancy that will burn trust the moment one partner does the math.

## When to apply this pattern
Whenever a marketing page goes live BEFORE the system that backs it. Always run a promise-vs-code audit before any "production cutover" claim. Especially watch for:
- Hardcoded defaults in signup endpoints that don't match published rates
- Form actions that point to marketing tools (Brevo, Mailchimp) when DB row creation was intended
- Tier/rate ladders where the "starting tier" name doesn't match the code's default value

## Tags
patterns, referrals, commission, spec-drift, partner-program
