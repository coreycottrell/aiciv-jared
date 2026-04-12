# PayPal Popup Integration Module for purebrain.ai

**Date**: 2026-02-18
**Type**: teaching + operational
**Agent**: full-stack-developer

## What Was Built

A self-contained JavaScript module (`/tmp/paypal-popup-integration.js`, 846 lines) that
replaces `openWaitlistModal(tier)` on purebrain.ai/pay-test with a real PayPal in-page
popup checkout. Works as a drop-in replacement — no HTML button changes required.

## Two Approaches in One File

### Approach B (DEFAULT — works right now, no setup)
- PayPal `/cgi-bin/webscr` form POST with `target="pb-paypal-popup"`
- `window.open()` opens a centered 600×700 browser popup
- Polls for popup close, then shows "Did you pay? Yes / No" confirmation UI
- Toggle: `USE_SDK_APPROACH = false` (already the default)

### Approach A (SDK Smart Buttons — requires PayPal Client ID from Jared)
- Loads `https://www.paypal.com/sdk/js?client-id=REAL_ID&currency=USD`
- Smart Buttons render inside the modal — true in-page checkout
- Supports both one-time payment (`createOrder`) and recurring subscription (`createSubscription`)
- Toggle: `USE_SDK_APPROACH = true` + replace `PAYPAL_CLIENT_ID_PLACEHOLDER`

## Key Design Patterns

### IIFE Encapsulation
Entire module wrapped in `(function(){ 'use strict'; })()` to avoid polluting global scope.
Only intentional globals are exposed: `window.openWaitlistModal`, `window.openPayPalCheckout`,
`window.paymentConfirmed`, `window.paymentTier`, `window.paymentOrderId`, `window.onPaymentComplete`.

### CSS Injection
All modal CSS is injected once via `<style id="pb-paypal-styles">` in `<head>`. No external
stylesheet needed. Modal uses `position:fixed; inset:0` overlay pattern.

### Payment Success Contract
```js
window.paymentConfirmed = true;
window.paymentTier      = tier;         // "Awakened" | "Bonded" | "Partnered"
window.paymentOrderId   = orderId;      // PayPal order ID or "FALLBACK-{timestamp}"
window.onPaymentComplete(tier, orderId, payerInfo);  // callback hook
window.location.hash = 'awakening';    // redirect to section
```

### Popup Blocked Fallback
If `window.open()` is blocked by the browser, form target reverts to `_blank` and submits
normally (standard tab open). Prevents silent failure.

## Price Mapping
```js
{ Awakened: '79.00', Bonded: '149.00', Partnered: '499.00' }
```
These match the purebrain.ai homepage pricing tiers.

## Tier Name Normalization
`openWaitlistModal()` normalises tier casing with `String.prototype.toLowerCase()` comparison
so `openWaitlistModal('awakened')` and `openWaitlistModal('Awakened')` both work.

## Constants (for reference)
- Business email: `support@puremarketing.ai`
- Return URL: `https://purebrain.ai/thank-you/`
- Cancel URL: `https://purebrain.ai/pay-test/`
- PayPal form endpoint: `https://www.paypal.com/cgi-bin/webscr`
- cmd: `_xclick-subscriptions` (recurring), t3: `M` (monthly), src: `1`

## How to Deploy to WordPress
1. Upload file to `/wp-content/uploads/` via Media Library or file manager
2. Add `<script src="/wp-content/uploads/paypal-popup-integration.js"></script>` via
   Elementor HTML widget at bottom of page, OR via Appearance > Customize > Additional JS
3. No other HTML changes needed — `openWaitlistModal` is already called by existing buttons

## Upgrade Path to SDK (Approach A)
1. Jared gets Client ID from developer.paypal.com > My Apps & Credentials
2. Replace `PAYPAL_CLIENT_ID_PLACEHOLDER` in the file (line 38)
3. Set `USE_SDK_APPROACH = true` (line 762)
4. Optionally add Plan IDs in `PLAN_IDS` object (lines 51-55) for subscription billing
5. Re-upload file and cache-bust the URL

## Prior Art Applied
- Used `support@puremarketing.ai` business email (from purebrain3 memory)
- Used `PB-AWAKENED` / `PB-BONDED` / `PB-PARTNERED` item_number pattern (from purebrain3 memory)
- Used `_xclick-subscriptions` PayPal cmd for recurring (from web-researcher memory)
- Used `t3=M` (monthly) + `src=1` (recurring) + `a3` (price) fields (from web-researcher memory)
