# Sandbox-3 Blank Screen: sanitizeText Missing + IIFE Scope Bug

**Date**: 2026-03-03
**Agent**: browser-vision-tester
**Type**: gotcha + pattern
**Tags**: browser-vision, visual-testing, purebrain, paytest, sandbox3, chatbox, IIFE, scope, blank-screen

---

## Context

Diagnosed critical blank screen bug on `https://purebrain.ai/pay-test-sandbox-3/` where users see only a black screen after PayPal payment instead of the post-payment chatbox.

---

## Root Cause Found

### Bug 1 (CONFIRMED CRASH): sanitizeText not defined in pay-test-chat-flow-v4.js

`initPayTestFlow` calls `sanitizeText(aiName || 'Pure')` at line 1 of its body. `sanitizeText` is REFERENCED 3 times in the script but NEVER DEFINED. The script comment says "CRIT-004: sanitizeText() helper added" but the function was not included.

Error seen: `[PAGE-ERROR] sanitizeText is not defined`

This causes initPayTestFlow to crash immediately, leaving the black `#pay-test-post-payment` container empty.

**Fix**: Add to pay-test-chat-flow-v4.js BEFORE initPayTestFlow:
```javascript
function sanitizeText(str) {
  var div = document.createElement('div');
  div.appendChild(document.createTextNode(str || ''));
  return div.innerHTML;
}
```

### Bug 2 (STRUCTURAL): launchPostPaymentFlow not exposed on window

`pay-test-integration-glue.js` wraps everything in an IIFE `(function() { ... })()`.
`launchPostPaymentFlow` is defined inside this IIFE but NEVER set on `window`.
The script only exposes `window.showBrainStreamButton`.

`onPaymentComplete` (in the PayPal SDK IIFE, a SEPARATE IIFE) calls `launchPostPaymentFlow(tier, orderId)` which is out of scope — this is why `window.launchPostPaymentFlow` shows as `undefined`.

However: the black screen DOES appear, meaning `launchPostPaymentFlow` IS running somehow (possibly from within the same IIFE closure, called by checkForPaymentReturn or another internal mechanism). The chatbox crash is definitively the `sanitizeText` bug.

**Fix**: Add to integration glue before `})();`:
```javascript
window.launchPostPaymentFlow = launchPostPaymentFlow;
```

---

## Diagnostic Pattern That Worked

The key diagnostic move was checking `typeof window.launchPostPaymentFlow` AND calling `window.onPaymentComplete('Awakened', 'TEST-123', {})` then watching for PAGE-ERROR events.

```javascript
// Check function availability
page.evaluate("""
    var funcs = ['onPaymentComplete', 'launchPostPaymentFlow', 'initPayTestFlow'];
    funcs.forEach(fn => result[fn] = typeof window[fn]);
""")
// Then call simulation and watch page.on("pageerror", ...) for crashes
```

The `pageerror` event (not `console.error`) catches uncaught JS exceptions including `ReferenceError: sanitizeText is not defined`.

---

## Black Screen Visual Signature

When the black screen bug occurs:
- `#pay-test-post-payment` div IS in DOM (position:fixed, z-index:999999, 1440x900px, background:#0a0a0a)
- div has ZERO children (innerHTML empty)
- The div was created correctly but initPayTestFlow threw before rendering

To distinguish "container created but empty" from "container never created":
```javascript
var el = document.getElementById('pay-test-post-payment');
console.log(el ? el.children.length : 'not in DOM');  // 0 = created but empty
```

---

## Files Referenced

- Report: `/home/jared/projects/AI-CIV/aether/exports/sandbox3-blank-screen-diagnosis-20260303.md`
- Screenshots: `/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-debug-20260303/`
- Diagnostic script: `/home/jared/projects/AI-CIV/aether/tools/debug_sandbox3_v2.py`
