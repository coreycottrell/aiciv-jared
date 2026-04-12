# Training Page Password Gate - IIFE Scope Bug

**Date**: 2026-02-28
**Type**: gotcha + technique
**Topic**: purebrain.ai/training/ password gate broken due to IIFE scoping of handleGateSubmit

---

## Bug Summary

The training page password gate does NOT work. Entering "brainiac2026" and clicking "Access Training Library" does nothing. The gate stays visible, no error message shows, session is never set.

## Root Cause: JavaScript IIFE Scope Bug

The entire training page script (17,187 chars) is wrapped in an IIFE:
```javascript
(function() {
  var GATE_PASSWORD = "brainiac2026";
  var SESSION_KEY   = "pb_mastermind_auth";

  function handleGateSubmit(e) { ... }
  function signIn() { ... }
  function signOut() { ... }
  // ... all other functions
})();
```

The form HTML uses:
```html
<form id="gate-form" onsubmit="return handleGateSubmit(event)">
```

**Problem**: `handleGateSubmit` is defined INSIDE the IIFE, so it lives in the IIFE's local scope - NOT on `window`. The HTML `onsubmit` attribute can only call functions in global scope. When the button is clicked, `handleGateSubmit` is `undefined` from the global scope perspective, so nothing happens (no error, no action, silent failure).

Confirmed via:
- `typeof window.handleGateSubmit` → `"undefined"`
- `typeof handleGateSubmit !== 'undefined'` → `false` (even this returns false from evaluate context)
- Form submit dispatchEvent → gate remains visible, error text stays empty

## Evidence of Silent Failure

- No console errors (the `onsubmit` returns false/undefined silently)
- No error text shown in `#gate-error` div
- Password field resets to empty after submit (page reload)
- `sessionStorage.getItem('pb_mastermind_auth')` = null always
- Gate display stays "flex", library display stays "none"

## The Fix (For Developer)

Option A - Expose function globally (minimal change):
```javascript
// At end of IIFE, expose needed functions:
window.handleGateSubmit = handleGateSubmit;
window.togglePwVisibility = togglePwVisibility;
window.setFilter = setFilter;
window.openModal = openModal;
window.closeModal = closeModal;
window.signOut = signOut;
```

Option B - Use addEventListener instead of inline onsubmit:
```javascript
// Inside the IIFE, after DOM is ready:
document.getElementById('gate-form').addEventListener('submit', handleGateSubmit);
```

Option B is cleaner and keeps everything inside the IIFE.

## Page Structure (Confirmed Working)

- URL: https://purebrain.ai/training/
- NO WordPress post-password-form (this is a CUSTOM JS gate, NOT WP protection)
- Form: `<form id="gate-form" onsubmit="return handleGateSubmit(event)">`
- Password field: `#gate-pw` (input type=password, placeholder="Enter access password")
- Submit button: `.gate-btn` (button type=submit, text="Access Training Library")
- Error div: `#gate-error`
- Gate container: `#pb-gate` (display:flex when locked)
- Library container: `#pb-library` (display:none when locked)
- Session storage key: `pb_mastermind_auth` = "1" when authenticated

## signIn Function (Correct When Called)

```javascript
function signIn() {
  sessionStorage.setItem(SESSION_KEY, "1");
  document.getElementById("pb-gate").style.display    = "none";
  document.getElementById("pb-library").style.display = "block";
  renderLibrary();
}
```

## Other Functions With Same Problem

All these are in the IIFE scope and need global exposure if used from HTML attributes:
- `handleGateSubmit` - form onsubmit
- `togglePwVisibility` - eye icon button
- `setFilter` - filter buttons in library
- `openModal` - video card clicks
- `closeModal` - modal close button
- `signOut` - nav sign out button

## Screenshots

- `/home/jared/projects/AI-CIV/aether/tools/screenshots/training-page-test-2026-02-28/01-initial-state.png`
- `/home/jared/projects/AI-CIV/aether/tools/screenshots/training-page-test-2026-02-28/06-password-filled.png`
- `/home/jared/projects/AI-CIV/aether/tools/screenshots/training-page-test-2026-02-28/09-final-state.png`

---

**Tags**: purebrain, training-page, password-gate, iife, javascript-scope, bug, silent-failure
