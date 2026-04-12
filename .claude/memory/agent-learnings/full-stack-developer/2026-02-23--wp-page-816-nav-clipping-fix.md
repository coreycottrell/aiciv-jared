# WordPress Nav Clipping Fix — Page 816 (AI Website Analysis)

**Date**: 2026-02-23
**Type**: teaching
**Topic**: WordPress/Astra theme overrides clipping fixed-position nav elements

---

## Problem

Nav bar on `purebrain.ai/ai-website-analysis/` (page 816) showed logo text truncated as "PUREBR AI" and the "Get Your Report" CTA button was missing/hidden.

The nav had `position: fixed; width: 100%` but still got clipped.

## Root Cause

WordPress/Astra theme applies CSS to generic `<nav>` elements with high specificity via class-based selectors:
- `.entry-content nav` - content container wraps the nav and applies max-width
- `.ast-container nav` - Astra container applies max-width constraints
- Astra's header nav styles conflict with custom page nav

Additionally, the `wp:html` block wraps content in `.entry-content` which can have `overflow: hidden` or contain properties that affect `position: fixed` children in some browsers.

## Fix Applied

**Three-layer defense strategy:**

### 1. ID-based CSS (beats class-based Astra rules)
Changed generic `nav {}` to `#pb-site-nav {}` with multi-selector covering:
```css
.entry-content #pb-site-nav,
.ast-container #pb-site-nav,
.site-content #pb-site-nav,
#pb-site-nav { position: fixed !important; width: 100vw !important; ... }
```

### 2. Class name disambiguation
Changed `.blue`, `.orange`, `.gray` to `.pb-blue`, `.pb-orange`, `.pb-gray` to avoid conflicts with Astra's own color utility classes.

### 3. JavaScript DOM escape (nuclear option)
Added script that moves `#pb-site-nav` to be a direct child of `document.body`:
```javascript
function escapeNav() {
  var nav = document.getElementById('pb-site-nav');
  if (nav && nav.parentElement !== document.body) {
    document.body.appendChild(nav);
  }
}
```
This guarantees the nav cannot be clipped by ANY WordPress content container.

### 4. Additional CSS hardening
- `transform: translate3d(0, 0, 0)` — forces GPU compositing layer
- `clip: auto !important; clip-path: none !important; contain: none !important`
- `z-index: 2147483647` (max int32) instead of 100000
- `-webkit-backdrop-filter` added for Safari

## Files Modified
- `/home/jared/projects/AI-CIV/aether/exports/client-marketing/website-analysis/index.html`

## Deployment
- WordPress page 816: `https://purebrain.ai/ai-website-analysis/`
- Template: `elementor_canvas`
- Elementor cache cleared via `DELETE /wp-json/elementor/v1/cache`
- Verified live: all 11 checks passed

## Lesson for Future
**When WordPress clips a fixed-position nav:**
1. Give nav a unique ID (not just classes)
2. Rename color classes to avoid Astra utility class conflicts (.blue → .pb-blue)
3. Add the JS DOM escape to move nav to document.body
4. Use `100vw` not `100%` for width
5. Add `clip: auto; clip-path: none; contain: none` to the CSS
