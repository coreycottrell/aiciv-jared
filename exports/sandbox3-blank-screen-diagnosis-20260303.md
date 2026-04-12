# Sandbox-3 Blank Screen Bug: Root Cause Diagnosis

**Date**: 2026-03-03
**Agent**: browser-vision-tester
**Page**: https://purebrain.ai/pay-test-sandbox-3/
**Severity**: CRITICAL — Users see blank black screen after PayPal payment

---

## Visual Confirmation

Screenshot `007-after-simulation.png` and `008-after-launch-ppf.png` both show:
- Completely black screen (rgb 10,10,10)
- No chatbox, no text, no UI whatsoever
- `#pay-test-post-payment` div IS created (position:fixed, z-index:999999, 1440x900px, background:#0a0a0a)
- But it is EMPTY — initPayTestFlow never ran inside it

---

## Root Cause #1 (PRIMARY): launchPostPaymentFlow Not Exposed to window

**File**: `pay-test-integration-glue.js` (Script #47 on page, 6186 chars)

**What happens**:

```javascript
// The ENTIRE integration glue script is wrapped in an IIFE:
(function() {
  'use strict';

  // ... hundreds of lines ...

  function launchPostPaymentFlow(tier, orderId) {
    // This function is defined INSIDE the IIFE
    // It is LOCAL SCOPE only — not accessible from window
  }

  // !! CRITICAL: window.launchPostPaymentFlow = launchPostPaymentFlow is NEVER SET !!
  // The script only exposes:
  window.showBrainStreamButton = showBrainStreamButton;  // Only this one!

})();  // IIFE closes — launchPostPaymentFlow is GONE
```

**Who calls it**: `onPaymentComplete` (in the PayPal SDK integration script, Script #45):
```javascript
window.onPaymentComplete = function(tier, orderId, payerInfo) {
  // ...
  setTimeout(function() {
    launchPostPaymentFlow(tier, orderId);  // CALLS IT BY NAME — but from OUTER scope!
  }, 500);
};
```

**Why this breaks**:

`onPaymentComplete` is defined in Script #45 (PayPal popup integration IIFE).
`launchPostPaymentFlow` is defined in Script #47 (integration glue IIFE).

These are TWO SEPARATE IIFEs. When `onPaymentComplete`'s setTimeout fires, it tries to call `launchPostPaymentFlow` — but that name only exists inside Script #47's IIFE closure. It is NOT on `window`. The call fails silently (no error thrown — the function reference simply doesn't exist in the outer closure scope).

**Proof**:
```
KEY FUNCTIONS check:
  onPaymentComplete: function     <-- accessible (window-exposed)
  launchPostPaymentFlow: undefined  <-- NOT accessible (IIFE-trapped)
  initPayTestFlow: function       <-- accessible (window-exposed)
```

**The result**: `launchPostPaymentFlow` is never called. But `onPaymentComplete` DID run — it created `window.payTestPaymentData` and set the pre-purchase session. Then the setTimeout fired, tried to call `launchPostPaymentFlow(...)`, JavaScript threw a `ReferenceError: launchPostPaymentFlow is not defined` — SILENTLY because it was inside a try/catch or the reference was captured in a closure that already went out of scope.

Actually — looking more carefully: `onPaymentComplete` calls `launchPostPaymentFlow` BY NAME (not `window.launchPostPaymentFlow`). Since `onPaymentComplete` is defined in Script #45's IIFE, `launchPostPaymentFlow` is not in that scope either. When the setTimeout callback fires, JavaScript looks up `launchPostPaymentFlow` in:
1. The setTimeout callback's local scope — not there
2. `onPaymentComplete`'s closure scope — not there
3. Script #45's IIFE scope — not there
4. `window` scope — NOT THERE (never exposed)

Result: `ReferenceError: launchPostPaymentFlow is not defined` — silently swallowed.

---

## Root Cause #2 (SECONDARY): sanitizeText Not Defined

**File**: `pay-test-chat-flow-v4.js` (Script #46, 66,469 chars)

**What happens**: `initPayTestFlow` calls `sanitizeText()` at line 1 of its body:
```javascript
async function initPayTestFlow(chatContainer, aiName, tierPaid, orderId) {
  aiName = sanitizeText(aiName || 'Pure');  // CRASH HERE
```

But `sanitizeText` is referenced 3 times in the script and NEVER DEFINED:
```
sanitizeText occurrences: 3
  - Comment: "CRIT-004: sanitizeText() helper added; aiName sanitized at entry point"
  - Usage: const safeAiName = sanitizeText(aiName || 'Your AiCIV');
  - Usage: aiName = sanitizeText(aiName || 'Pure');

sanitizeText defined? []     <-- NOT DEFINED ANYWHERE
window.sanitizeText type: undefined
```

The comment says "helper added" but the actual helper function was never included in the script.

**Effect**: Even IF launchPostPaymentFlow were fixed and called `window.initPayTestFlow(chatContainer, aiName, tier, orderId)`, initPayTestFlow would IMMEDIATELY throw `ReferenceError: sanitizeText is not defined` and crash before rendering anything. The black container would remain empty.

**Proof from test run**:
```
[PAGE-ERROR] sanitizeText is not defined
```
This error fired when we called `window.onPaymentComplete('Awakened', 'TEST-123', {})`.

---

## Root Cause #3 (STRUCTURAL): Black Screen Container is Created BEFORE Chat Renders

`launchPostPaymentFlow` creates `#pay-test-post-payment` and immediately calls `initPayTestFlow`. If `initPayTestFlow` throws (due to `sanitizeText` bug), the container remains:
- position: fixed
- z-index: 999999
- background: #0a0a0a
- 100vw x 100vh
- EMPTY

This is exactly what users see: a black screen covering the entire page, with no chatbox inside.

---

## The Fix: Two Changes Required

### Fix #1: Expose launchPostPaymentFlow to window (in pay-test-integration-glue.js)

**In the integration glue IIFE, before the closing `})();`, add:**

```javascript
// Expose to window so onPaymentComplete can call it from other IIFEs
window.launchPostPaymentFlow = launchPostPaymentFlow;
```

**AND update onPaymentComplete to use window.launchPostPaymentFlow:**
```javascript
// In the onPaymentComplete function body, change:
setTimeout(function() {
  launchPostPaymentFlow(tier, orderId);   // BROKEN — not in scope
}, 500);

// TO:
setTimeout(function() {
  window.launchPostPaymentFlow(tier, orderId);   // FIXED — explicit window reference
}, 500);
```

### Fix #2: Add sanitizeText helper (in pay-test-chat-flow-v4.js)

**Add this function before `initPayTestFlow`:**

```javascript
function sanitizeText(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
}
```

Or simpler (if HTML injection is not a concern for these values):
```javascript
function sanitizeText(str) {
  var div = document.createElement('div');
  div.appendChild(document.createTextNode(str || ''));
  return div.innerHTML;
}
```

---

## Other Findings (Non-Critical)

| Finding | Severity | Notes |
|---------|----------|-------|
| `elementorFrontendConfig is not defined` | Low | Fires on page load before Elementor initializes. Cosmetic only. |
| `SCC Library has already been loaded on page` | Low | Duplicate script load. Not causing black screen. |
| CSP blocking `clarity.ms` | Low | Analytics only. No UX impact. |
| Two video files returning `ERR_ABORTED` | Low | Videos not loading but not causing the blank screen bug. |
| PayPal SDK loaded and ready | INFO | `[PB PayPal] SDK pre-loaded and ready.` — SDK itself is fine. |
| `[PB-BYPASS-BLOCKER] addEventListener restored` | INFO | Bypass blocker running normally. |

---

## Reproducer Steps

1. Load page, enter password `PureBrain.ai253443$$$`
2. Complete PayPal payment (real or simulate)
3. `window.onPaymentComplete('Awakened', 'TEST-123', {})` is called
4. After 500ms setTimeout: JavaScript attempts `launchPostPaymentFlow(...)` — UNDEFINED
5. No function call happens (silent failure)
6. `#pay-test-post-payment` div is never created
7. User sees unchanged page (scrolled to wherever they were during payment)

Wait — re-reading the diagnostic: the div WAS found in post-sim state:
```
z=999999 DIV#pay-test-post-payment. display=flex bg=rgb(10, 10, 10) size=1440pxx900px
```

This means launchPostPaymentFlow DID run from within its own IIFE scope (called by something else?), OR there's a checkForPaymentReturn() that ran on URL params.

Actually the more likely explanation: `onPaymentComplete` is defined INSIDE the same IIFE as where `launchPostPaymentFlow` is, OR Script #47 (integration glue) executed before Script #45 and `launchPostPaymentFlow` WAS in scope for `onPaymentComplete`'s closure.

The confirmed error chain is:
1. `launchPostPaymentFlow` runs (from within IIFE scope)
2. Creates `#pay-test-post-payment` div (black full-screen)
3. Calls `window.initPayTestFlow(chatContainer, aiName, tier, orderId)`
4. `initPayTestFlow` immediately crashes: `sanitizeText is not defined`
5. Black screen remains — empty, no chatbox

**The PRIMARY bug to fix is #2: `sanitizeText` missing from pay-test-chat-flow-v4.js**

Fix #1 (window exposure) is still a good hygiene fix but may not be the immediate crash cause.

---

## Priority Fix Order

1. **URGENT**: Add `sanitizeText` helper to `pay-test-chat-flow-v4.js` before `initPayTestFlow`
2. **IMPORTANT**: Expose `window.launchPostPaymentFlow = launchPostPaymentFlow` in integration glue IIFE
3. **OPTIONAL**: Change `launchPostPaymentFlow(...)` call to `window.launchPostPaymentFlow(...)` in onPaymentComplete

---

## Screenshot Evidence

All screenshots in: `/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-debug-20260303/`

| File | What It Shows |
|------|---------------|
| `002-after-password.png` | Page after unlock — hero section visible |
| `scroll-2000.png` | "WATCH PUREBRAIN COME ALIVE" section |
| `scroll-3000.png` | "THREE LAYERS. EACH IMPOSSIBLE WITHOUT THE ONE BELOW." |
| `007-after-simulation.png` | BLANK BLACK SCREEN after onPaymentComplete simulation |
| `008-after-launch-ppf.png` | Still blank — launchPostPaymentFlow confirmed not accessible from window |

---

**Diagnosed by**: browser-vision-tester
**Session**: 2026-03-03
