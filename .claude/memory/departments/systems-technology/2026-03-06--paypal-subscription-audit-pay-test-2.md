# PayPal Subscription Audit — pay-test-2 and All Pay Pages
**Date**: 2026-03-06
**Trigger**: ST# audit request from Jared
**Status**: AUDIT COMPLETE — NO CHANGES MADE

---

## Summary

Zero subscription-type PayPal links found on any page. All PayPal integrations either:
- Are completely broken (function called but not defined, no SDK loaded)
- Use ONE-TIME payment (createOrder + intent=capture) instead of SUBSCRIPTION (createSubscription + plan_id)

---

## Page-by-Page Findings

### pay-test-2 (page 689) — STATUS: BROKEN
- PayPal SDK: NOT loaded (zero paypal.com references in live page)
- Pricing buttons for Partnered + Unified call `openPayPalModal()` — function is NEVER DEFINED on the page
- Awakened button calls `openWaitlistModal()` — this is correct (waitlist, not payment yet)
- Clicking Partnered or Unified triggers a silent JavaScript ReferenceError — does nothing
- Root: Code comments reference `/tmp/paypal-popup-integration.js` — a LOCAL dev file, never deployed to production

### pay-test-sandbox-3 (page 1232) — STATUS: BROKEN
- Identical to pay-test-2 in every way
- Same `openPayPalModal()` calls with no definition
- No PayPal SDK loaded

### Partnered live product page (/partnered/) — STATUS: FAIL
- PayPal SDK IS loaded from `sandbox.paypal.com` (SANDBOX environment, not production)
- Uses `createOrder` + `intent=capture` = ONE-TIME PAYMENT API
- `PRICE = '499.00'` hardcoded as a one-time amount
- Description says "Monthly Subscription" but this is misleading — it's a one-time order
- No `plan_id`, no `createSubscription` anywhere
- `PAYPAL_CLIENT_ID = 'AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_'` (sandbox)

### Unified live product page (/unified/) — STATUS: FAIL
- Same as Partnered — sandbox environment, `createOrder`, `intent=capture`
- ONE-TIME PAYMENT
- `PRICE = '999.00'`

---

## Root Cause

1. **No subscription plans exist in PayPal**: No `plan_id` has been configured in the PayPal developer dashboard for any tier
2. **Wrong payment method**: `createOrder()` is for one-time payments. `createSubscription()` with a `plan_id` is required for recurring billing
3. **Missing popup integration file**: `paypal-popup-integration.js` (referenced in page comments) was a local dev file at `/tmp/` that was never deployed to the WordPress site — all 404s
4. **Sandbox environment**: Both partnered and unified pages load from `sandbox.paypal.com`, not `www.paypal.com` — no real money can be taken even if users tried

---

## What Fix Requires

### Step 1 — PayPal Developer Dashboard (Jared must do this manually or via API)
Create recurring billing plans for each tier:
- Awakened: $149/month
- Partnered: $499/month
- Unified: $999/month

Each plan gets a `plan_id` like `P-XXXXXXXXXXXXXXXXXXXX`

### Step 2 — Code Change
Replace in partnered, unified, and pay-test pages:

**Old (one-time):**
```js
intent=capture  // in SDK URL
createOrder: function(data, actions) { return actions.order.create({...}) }
```

**New (subscription):**
```js
intent=subscription&vault=true  // in SDK URL
createSubscription: function(data, actions) {
  return actions.subscription.create({ plan_id: 'P-XXXXXXXXX' });
}
onApprove: function(data, actions) {
  // data.subscriptionID is the ID to store
}
```

### Step 3 — Switch to Production
Change `sandbox.paypal.com` to `www.paypal.com` and use live client ID

### Step 4 — pay-test-2 Button Fix
Either:
a) Write the `openPayPalModal()` function that redirects to /partnered/ or /unified/ as appropriate
b) Or embed inline PayPal buttons directly on pay-test-2 with subscription plan IDs

---

## Files Checked
- `/tmp/paytest2_rendered.html` — page 689 rendered HTML (no PayPal)
- `/tmp/sandbox3_rendered.html` — page 1232 rendered HTML (no PayPal)
- Elementor data for both pages fetched via `?context=edit` API
- Live HTML for: pay-test-2, pay-test-sandbox-3, partnered, unified, pay-test, pay/

---

## Memory Tag
Type: audit-finding
Topic: PayPal one-time vs subscription — all pages using wrong payment method
