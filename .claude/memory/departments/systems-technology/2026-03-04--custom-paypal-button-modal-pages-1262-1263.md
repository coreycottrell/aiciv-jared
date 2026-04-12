# Custom PayPal Button + Modal — Pages 1262 + 1263

**Date**: 2026-03-04
**Agent**: dept-systems-technology
**Pages**: 1262 (Partnered $499), 1263 (Unified $999)
**Status**: DEPLOYED AND VERIFIED

---

## What Was Built

Replaced default 3-button yellow PayPal render with a single on-brand PureBrain button that opens a dark modal containing the PayPal buttons.

### Page 1262 — Partnered
- Button text: "Activate Your Partnered AI →"
- Button ID: `#pb-partnered-activate-btn`
- PayPal renders into: `#pb-modal-paypal-container`
- Modal: `#pb-paypal-modal-overlay`

### Page 1263 — Unified
- Button text: "Unlock Unified Intelligence →"
- Button ID: `#pb-unified-activate-btn`
- PayPal renders into: `#pb-modal-unified-container`
- Modal: `#pb-paypal-modal-overlay`

---

## CSS Classes Added (both pages)

- `.pb-activate-btn` — gradient button with shimmer animation (`pb-btn-shimmer`)
- `#pb-paypal-modal-overlay` — dark overlay (fixed position, backdrop-filter blur)
- `.pb-paypal-modal-box` — modal card (dark bg, branded header, PayPal container inside)
- `.pb-modal-close` — X button to dismiss
- `.pb-modal-header` — wordmark + tier heading + price
- `.pb-modal-trust` — trust text at bottom

---

## Critical Gotcha: IIFE Scope

**Page 1262** had the PayPal JS wrapped in `(function() { 'use strict'; ... })()` — an IIFE.

The modal functions `pbOpenPayPalModal` / `pbClosePayPalModal` were defined INSIDE this IIFE.

`onclick="pbOpenPayPalModal()"` requires the function to be on `window` scope.

**Fix**: After defining the functions inside the IIFE, expose them:
```javascript
window.pbOpenPayPalModal = pbOpenPayPalModal;
window.pbClosePayPalModal = pbClosePayPalModal;
```

**Page 1263** defined the modal functions OUTSIDE the IIFE (after `})();`) so they were already global.

**Always check IIFE scope when onclick attributes reference JS functions on these pages.**

---

## Modal Architecture

```
[Custom Button] onclick → pbOpenPayPalModal()
    ↓
[Dark overlay #pb-paypal-modal-overlay appears]
    ↓
[PayPal SDK already loaded and rendered into #pb-modal-paypal-container]
    ↓
[User completes PayPal flow]
    ↓
[onApprove fires → buildRedirectUrl → redirect to sandbox-3]
```

PayPal SDK loads on `DOMContentLoaded` and renders into the modal container immediately. By the time the user clicks the button, PayPal is ready.

---

## PayPal Redirect URL Structure

Confirmed working:
```
https://purebrain.ai/pay-test-sandbox-3/?tier=Partnered&paid=true&orderId=ORDER_ID
https://purebrain.ai/pay-test-sandbox-3/?tier=Unified&paid=true&orderId=ORDER_ID
```

---

## Playwright QA Results (all PASS)

| Test | Result |
|------|--------|
| Page 1262 custom button renders | PASS |
| Button text correct | PASS |
| Modal hidden on page load | PASS |
| Button click opens modal | PASS |
| Modal header shows "Partnered" | PASS |
| PayPal iframe loads in modal | PASS |
| Close button dismisses modal | PASS |
| buildRedirectUrl structure correct | PASS |
| Sandbox-3 loads with paid params | PASS |
| Page 1263 custom button renders | PASS |
| Unified modal opens on click | PASS |
| PayPal iframe in unified modal | PASS |

Screenshots: `/home/jared/projects/AI-CIV/aether/exports/screenshots/paypal-custom-button-qa-20260304/`

---

## Files

- Build script: `exports/departments/systems-technology/build_custom_paypal_buttons.py`
- QA script: `exports/departments/systems-technology/qa_custom_paypal_button.py`
- Backups: `exports/departments/systems-technology/BACKUP_page126{2,3}_pre-custom-button.html`
- Previews: `exports/departments/systems-technology/PREVIEW_page126{2,3}_custom-button.html`
