# Referral E2E Diagnosis: Subscription payerInfo Missing Email

**Date**: 2026-03-20
**Type**: teaching
**Topic**: PureBrain referral system — root cause of auto-attribution failure

## Summary

Joe (PB-JJ8N) referred Vishal who paid $149 Awakened. Attribution was NOT auto-recorded.
Diagnosed and fixed 2026-03-20.

## Root Cause

**Subscription payment path does not provide payer email in onApprove callback.**

Payment pages use PayPal subscription billing (createSubscription -> onApprove(data)).
The data object from subscription onApprove has no email_address or name.
This data object was passed as payerInfo -> onPaymentComplete(tier, orderId, payerInfo).

Inside onPaymentComplete, the referral/complete fetch:
  var refEmail = (payerInfo && payerInfo.email_address) ? payerInfo.email_address : '';
  // refEmail = '' (undefined property)

Backend /api/referral/complete validated: if not referred_email -> return 400.
Result: 400 error silently caught, referral never recorded.

## What Was Working Correctly

- referral-tracker.js fires on invitation page (only script on that page)
- Cookie pb_ref set with path=/; SameSite=Lax — persists across navigation on same domain
- getPbRef() reads cookie/localStorage correctly
- CORS allows purebrain.ai -> app.purebrain.ai
- api/referral/complete endpoint is public (no auth) — correctly configured

## Architecture Notes

- Invitation page: NO inline referral JS, only referral-tracker.js (defer)
- Payment pages: BOTH inline JS AND referral-tracker.js. Inline has no first-touch guard, no toUpperCase.
- referral-tracker.js: Has first-touch guard, stores ref.toUpperCase()
- Subscription path: createSubscription -> onApprove(data) -> data has no payer email
- One-time path: createOrder -> onApprove -> actions.order.capture() -> details.payer has email

## Fix Applied

Backend (portal_server.py api_referral_complete):
- Made referred_email optional
- If empty and order_id provided, records with placeholder: paypal_{order_id}@pending
- Placeholder rows skip single-referrer dedup check

Frontend (all payment pages):
- Added order_id: orderId to referral/complete JSON payload
- orderId is PayPal subscription ID, in scope as 2nd param of onPaymentComplete

Files changed:
- /home/jared/purebrain_portal/portal_server.py
- exports/cf-pages-deploy/awakened/index.html
- exports/cf-pages-deploy/partnered/index.html
- exports/cf-pages-deploy/unified/index.html
- exports/cf-pages-deploy/live/index.html
- exports/cf-pages-deploy/insiders/index.html
- exports/cf-pages-deploy/pay-test-sandbox-3/index.html

## Verification

curl -s https://app.purebrain.ai/api/referral/complete -X POST \
  -H "Content-Type: application/json" \
  -d '{"referral_code":"PB-JJ8N","order_id":"I-TESTSUBSCRIPTION123"}'
Returns: {"ok": true, "message": "Referral recorded..."}

CF Pages deployed: https://b1df0341.purebrain-staging.pages.dev
