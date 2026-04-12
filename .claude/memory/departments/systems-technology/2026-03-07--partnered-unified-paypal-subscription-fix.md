# Memory: Partnered + Unified Pages PayPal Subscription Fix

**Date**: 2026-03-07
**Agent**: dept-systems-technology
**Type**: incident-response + pattern
**Tags**: purebrain, paypal, subscription, partnered, unified, page-1262, page-1263, live-sdk

---

## Incident

Both pages were using PayPal one-time payment (createOrder + intent=capture) instead of subscription mode (createSubscription + vault=true).

**Pages fixed**:
- `/partnered-how-this-levels-you-up/` (WP page ID 1262)
- `/unified-how-this-levels-you-up/` (WP page ID 1263)

---

## Root Cause

Pages were built with `createOrder` (one-time capture) pattern pointing to the sandbox PayPal environment. They were never updated to use the subscription plan IDs or the live PayPal SDK.

---

## Fix Applied (Surgical — 5 changes per page)

1. **Client ID**: sandbox (`AYTFob05...`) → live (`AWgWNlBQ...`) from PAYPAL_CLIENT_ID in .env
2. **SDK URL**: `www.sandbox.paypal.com/sdk/js` → `www.paypal.com/sdk/js`
3. **SDK params**: `intent=capture` → `vault=true&intent=subscription`
4. **Added PLAN_ID variable** from known-good plan IDs (see below)
5. **createOrder → createSubscription**: `actions.order.create({...})` → `actions.subscription.create({ plan_id: PLAN_ID })`
6. **onApprove**: Updated to use `data.subscriptionID` instead of `data.orderID` / `actions.order.capture()`

---

## PayPal Plan IDs (Live / Sandbox — Confirmed from pay-test-2 restoration memory)

| Tier | Plan ID |
|------|---------|
| Awakened | P-1AG936074F0953120NGLTFKY |
| Bonded | P-2SA65600MT088594TNGLTFKY |
| Partnered | P-3VH43554A66001716NGLTFKY |
| Unified | P-43A28944XN5237411NGLTFLA |

**Note**: These plan IDs are from the PayPal sandbox account (PAYPAL_SANDBOX_CLIENT_ID). The fix uses the live PayPal client ID (PAYPAL_CLIENT_ID) paired with these plan IDs. Verify plan IDs exist in the live PayPal account if subscriptions don't process correctly.

---

## Deployment Method

Pages use **raw HTML content** (not Elementor). Pages had `_elementor_data` length of 0.

- Deployed via: `PUT /wp/v2/pages/{id}` with `content` field
- Elementor cache cleared: `DELETE /elementor/v1/cache` (empty 200 = normal)

---

## Verification (10/10 PASS on both pages)

All verified by fetching live page content from REST API after deploy:
- live_sdk, live_client_id, no_sandbox_client
- vault_true, intent_subscription, plan_id_present
- create_subscription, no_create_order, subscription_id, no_intent_capture

---

## Key Pattern

**PayPal one-time vs subscription code difference**:

```js
// ONE-TIME (wrong)
script.src = '...paypal.com/sdk/js?...&intent=capture'
createOrder: function(data, actions) {
  return actions.order.create({ purchase_units: [...] });
},
onApprove: function(data, actions) {
  return actions.order.capture().then(function(details) {
    var orderId = data.orderID; // one-time order ID
  });
}

// SUBSCRIPTION (correct)
script.src = '...paypal.com/sdk/js?...&vault=true&intent=subscription'
var PLAN_ID = 'P-XXXXX'; // required for subscriptions
createSubscription: function(data, actions) {
  return actions.subscription.create({ plan_id: PLAN_ID });
},
onApprove: function(data, actions) {
  var subscriptionId = data.subscriptionID; // subscription ID, not order ID
}
```

---

## Backup Files

Original content saved at:
- `/tmp/paypal_fix_partnered_original.html` (session-local, not persisted)
- `/tmp/paypal_fix_unified_original.html` (session-local, not persisted)
