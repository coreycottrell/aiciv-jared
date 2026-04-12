# Partnered Tier Page ($499) QA Patterns

**Date**: 2026-03-04
**Agent**: browser-vision-tester
**Type**: technique + pattern + synthesis
**Tags**: browser-vision, visual-testing, purebrain, paypal, partnered, pricing-page, sandbox3

---

## Context

QA audit of newly created `https://purebrain.ai/partnered-how-this-levels-you-up/` — the $499/mo Partnered tier sales page with PayPal checkout built inline.

---

## Key Findings

### Page Architecture

Self-contained pricing page with:
- Hero section: H1 "How PureBrain Partnered Levels You Up"
- Price badge: "$499/mo" (with strikethrough $25,000–$47,000/mo comparison)
- CTA: "Get Partnered Now →" button (class `.pb-hero-cta`) — scrolls to PayPal
- Part A: Five Core Deliverables (cards with icon + description + badge)
- Part B: Six Categories of High-Value Intelligence (grid layout)
- Comparison table: "What This Would Cost You Elsewhere"
- Payment section: "Ready to Level Up?" with PARTNERED TIER card + PayPal buttons

### Background Color: PASS

Body background = `rgb(10, 14, 26)` — dark navy blue, compliant with dark background rule.

### PayPal Implementation Pattern

Payment script (IIFE, 3738 chars) at bottom of page. Key config:
```javascript
var PAYPAL_CLIENT_ID = 'AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_';
var CURRENCY = 'USD';
var PRICE = '499.00';
var TIER = 'Partnered';
var VERIFY_URL = 'https://api.purebrain.ai/api/verify-payment';
var SANDBOX3_URL = 'https://purebrain.ai/pay-test-sandbox-3/';
```

Redirect builder:
```javascript
function buildRedirectUrl(orderId) {
    return SANDBOX3_URL
      + '?tier=' + encodeURIComponent(TIER)
      + '&paid=true'
      + '&orderId=' + encodeURIComponent(orderId);
}
```

After payment: 1200ms delay then `window.location.href = buildRedirectUrl(orderId)`.

This sends user to: `https://purebrain.ai/pay-test-sandbox-3/?tier=Partnered&paid=true&orderId=XXX`

### PayPal Rendering: PASS in headless

PayPal SDK renders all 3 buttons in headless mode:
- "Pay with PayPal" (gold pill button)
- "Pay with SEPA" (white pill button)
- "Debit or Credit Card" (dark pill button)

NOTE: This is different from sandbox-2 which had PayPal iframe rendering issues. The integrated approach (rendering directly into `#pb-paypal-container` div on the page) works in headless. No separate modal/overlay pattern used here.

### CTA Button Behavior

`.pb-hero-cta` click scrolls page to y=3708 (payment section) via JS smooth scroll. Works correctly.

### CSP Warnings (Non-blocking)

4 CSP errors appear — all Google Tag Manager / third-party scripts being blocked. These are intentional (security policy) and non-blocking for payment flow.

---

## Confirmed Selectors

- Hero CTA: `.pb-hero-cta` (button text: "Get Partnered Now →")
- Payment container: `#pb-paypal-container`
- PayPal status: `#pb-payment-status`
- PayPal SDK: `https://www.sandbox.paypal.com/sdk/js?client-id=...`

---

## Mobile QA

375px width: Page renders cleanly. Hero title wraps correctly. "Partnered" in orange. PayPal buttons stack vertically. Fully readable.

---

## Files Referenced

- Screenshots: `/home/jared/projects/AI-CIV/aether/exports/screenshots/partnered-page-qa-20260304/`
  - 001: Initial load (hero)
  - 002-003: Deliverables section
  - 004-005: Six categories + cost comparison
  - 006: Pricing table with PUREBRAIN Partnered row
  - 007: Bottom with PayPal buttons
  - 010-011: Mobile view
  - 012: After CTA click (scrolled to payment section)
- QA scripts: `/home/jared/projects/AI-CIV/aether/tools/qa_partnered_page.py`

---

## What to Watch For (Future Visits)

- Verify `tier=Partnered` reaches sandbox-3 chatbox correctly (sandbox-3 reads URL params to initialize)
- SEPA button may need EU IP to be fully functional
- The `verify-payment` endpoint is called in background (non-blocking) — check API logs if payment data is needed
