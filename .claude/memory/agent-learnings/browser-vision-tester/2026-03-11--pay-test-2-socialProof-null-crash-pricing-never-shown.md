# Memory: pay-test-2 Pricing Never Shown - socialProof Null Crash

**Date**: 2026-03-11
**Type**: teaching + operational
**Topic**: closeCelebrationAndShowPricing() crashes on missing #socialProof element, pricing never shows

---

## Root Cause

`closeCelebrationAndShowPricing()` in pay-test-2 crashes with:

```
TypeError: Cannot read properties of null (reading 'style')
```

at this line:

```javascript
document.getElementById('socialProof').style.display = 'block';
```

The `#socialProof` element does NOT exist in the DOM. The function references it without a null-check. When it crashes, the `showPricing()` call never executes, so the pricing tiers section stays hidden (`display: none`).

Additionally, the `classList.remove('active')` on `#celebrationMoment` runs BEFORE the crash, so the celebration screen disappears but pricing never appears — the page appears to "snap back" to the top/hero section. This matches the reported bug: "loops back to the chat."

---

## Key Facts

- `#pricing` element EXISTS in DOM, starts with `display: none`
- `.pricing-section.active` CSS = `display: block` (CSS is correct)
- `window.closeCelebrationAndShowPricing` IS exported to window correctly
- `#socialProof` element: MISSING from DOM entirely
- `#compare` element: EXISTS (also shown via `classList.add('active')` in showPricing)
- Function is inside `DOMContentLoaded` closure, exported via `window.closeCelebrationAndShowPricing = closeCelebrationAndShowPricing`

---

## The Fix

Add a null-check before accessing `.style.display`:

**Before (broken)**:
```javascript
function closeCelebrationAndShowPricing() {
    document.getElementById('celebrationMoment').classList.remove('active');

    // Show social proof
    document.getElementById('socialProof').style.display = 'block';  // CRASHES - null ref

    showPricing();
}
```

**After (fixed)**:
```javascript
function closeCelebrationAndShowPricing() {
    document.getElementById('celebrationMoment').classList.remove('active');

    // Show social proof
    const spEl = document.getElementById('socialProof'); if (spEl) spEl.style.display = 'block';

    showPricing();
}
```

Fix applied to: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pay-test-2/index.html` at line 10936.

---

## Verification

After fix (local Playwright test):
- `closeCelebrationAndShowPricing()` call: SUCCESS (no error)
- Pricing element after call: `{ display: 'block', classList: 'pricing-section active', hasActive: true }`

---

## Console Errors on page (non-breaking)

- `JQMIGRATE: Migrate is installed, version 3.4.1` — jQuery migrate, cosmetic
- `[PB PayPal] SDK pre-loaded and ready.` — informational
- `[PB-BYPASS-BLOCKER] addEventListener restored` x2 — informational
- Zero page errors on load

---

## Next Step

Redeploy `exports/cf-pages-deploy/pay-test-2/index.html` to Cloudflare Pages at `purebrain-staging.pages.dev/pay-test-2/` for Jared to verify.

---

## Debugging Pattern

When a button appears to "loop back" or "do nothing visible" on a page using CSS class toggling for show/hide:
1. Check if the function actually runs WITHOUT errors (call it in console)
2. If it throws, find the crash point — often a missing DOM element
3. The crash may happen mid-function AFTER some DOM changes, creating a partial state
4. Always add null-checks for `document.getElementById()` before accessing properties

**Tags**: pay-test-2, celebration, pricing, socialProof, null-reference, TypeError, closeCelebrationAndShowPricing, show-pricing, bug-fix
