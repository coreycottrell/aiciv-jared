# Mobile Hamburger Menu Broken — IIFE Scope Bug

**Date**: 2026-03-08
**Type**: gotcha
**Agent**: browser-vision-tester
**Topic**: onclick attribute calling function trapped inside IIFE

---

## Context

Investigating why `#mobile-hamburger` More button in PureBrain portal bottom nav doesn't open the flyout menu on mobile viewport.

## Discovery

The root cause is a **JavaScript scope isolation bug**:

1. The HTML element uses `onclick="toggleMobileMenu()"` which resolves to `window.toggleMobileMenu`
2. The function `toggleMobileMenu()` is defined inside a wrapping IIFE: `(function() { ... })();`
3. Functions defined inside an IIFE are NOT on the global `window` scope
4. Result: `window.toggleMobileMenu is not defined` — confirmed by browser page error

## Evidence

Browser page errors captured:
```
ERROR: toggleMobileMenu is not defined
ERROR: toggleMobileMenu is not defined
```

The function exists at `/home/jared/purebrain_portal/portal-pb-styled.html` line 4702, inside the IIFE that spans lines 3969-8457.

## The Fix

Add `window.toggleMobileMenu = toggleMobileMenu;` right after the function definition in the IIFE, OR change the onclick to use an event listener instead of inline handler.

**Option A — Global export (minimal change):**
```javascript
function toggleMobileMenu() {
  var menu = document.getElementById('mobile-more-menu');
  menu.style.display = (menu.style.display === '' || menu.style.display === 'none') ? 'block' : 'none';
}
window.toggleMobileMenu = toggleMobileMenu;  // ADD THIS LINE
```

**Option B — Remove inline onclick, use event listener (cleaner):**
Remove `onclick="toggleMobileMenu()"` from the HTML element and add:
```javascript
document.getElementById('mobile-hamburger').addEventListener('click', function(e) {
  e.stopPropagation();
  toggleMobileMenu();
});
```

## Additional Findings

- `#mobile-more-menu` exists, has z-index: 100000, position: fixed, bottom: 56px — correct
- Menu `style.display` stays `""` (empty string, defaults to `none` by CSS) — never gets set to `block`
- No overlay is blocking clicks — `upload-mode-overlay` exists but has `pointer-events: none`
- The tab bar itself is visible and the hamburger button renders correctly at position x:300-375, y:752-812
- 20 console errors are 404s (likely missing assets/fonts — separate issue, not blocking)
- The `nav` element (sidebar) has `display: none` correctly on mobile

## File Path

`/home/jared/purebrain_portal/portal-pb-styled.html`

## Pattern: IIFE + onclick inline handlers

Any function called from an inline `onclick=` attribute must be on `window`. If the main script wraps everything in `(function() { ... })()`, ALL inline handlers will break unless the functions are explicitly exported to `window`.

When you see `toggleX is not defined` in page errors + inline onclick attributes = IIFE scope isolation is the cause.
