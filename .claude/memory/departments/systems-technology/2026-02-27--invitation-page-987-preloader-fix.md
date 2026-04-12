# Invitation Page 987 — Preloader Spinner Fix

**Date**: 2026-02-27
**Agent**: dept-systems-technology
**Type**: incident, gotcha, pattern
**Status**: Resolved

---

## Incident Summary

Page https://purebrain.ai/invitation/ (WP page ID 987) was stuck on the spinning blue circle (Artistics/Awaiken theme preloader) after a previous deployment added two new sections.

## What Was Added (Breaking Changes)

1. `<div id="pb-content-overlay">` — a fixed-position dark gradient overlay div
2. `<section id="pb-discovery">` — a "Find Your AI Partner Profile" multi-step widget
3. New CSS with backdrop-filter, animations (pb-pulse-dot), and complex styling
4. New IIFE JavaScript for the discovery widget

Content grew from 78,725 chars (stable) to 103,592 chars (broken).

## Root Cause

The Artistics/Awaiken theme's `function.js` manages `.theme-preloader` dismissal via the `window.load` event. The `window.load` event fires only after ALL resources on the page have finished loading (images, scripts, stylesheets).

The 25KB of new content introduced:
- `backdrop-filter: blur(28px)` on multiple elements (GPU-intensive)
- Animation loops (pb-pulse-dot continuous animation)
- Additional DOM elements that the theme's GSAP-based preloader logic may be waiting on

When `window.load` is delayed or its handler encounters unexpected DOM state, the theme's preloader management keeps the spinner visible indefinitely.

Key nuance: Script 13 (async Three.js IIFE) includes a preloader kill:
```js
var preloaders = document.querySelectorAll('.theme-preloader, .loading-container, .loading');
preloaders.forEach(function(el) { el.style.cssText = 'display:none!important;...'; });
```
This runs before `await import('three@...')`. BUT the theme's function.js can re-trigger or maintain the spinner if its own load handler doesn't complete cleanly.

## Fix Applied

Reverted page 987 to WordPress Revision 989 (created 2026-02-27T01:55:02), which was the stable pre-enhancement state.

```bash
# REST API revert pattern
curl -s -X POST \
  -u "Aether:${PUREBRAIN_WP_APP_PASSWORD}" \
  "https://purebrain.ai/wp-json/wp/v2/pages/987" \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/update-payload.json
```

## Verification

- REST API confirmed: `modified: 2026-02-27T12:14:59`, `status: publish`
- Live fetch: 193,715 bytes, no pb-content-overlay, no pb-discovery
- All core elements present: pb-loader, pb-page, pb-canvas-container, importmap, preloader kill code

## Safe Re-Addition Pattern

When re-adding enhancements to pages that use the Artistics/Awaiken theme preloader:

1. **Add CSS-only changes first** — no new div elements with fixed positioning
2. **Test spinner clears** before adding more
3. **Use `window.addEventListener('load', ...)` guards** for any new JS that might interfere
4. **Avoid `position: fixed` with `backdrop-filter`** on multiple elements — this delays GPU composition and can delay window.load
5. **Stage enhancements one at a time**, verifying after each

## File References

- Broken version: `exports/invitation-page-v2-2026-02-27.html` (110KB)
- Revisions available: Rev 1000 (broken), Rev 989 (stable), Rev 988 (earlier)

## Key Learning

**The Artistics theme preloader is controlled by `function.js` via `window.load`**. Adding content that delays the load event (fixed overlays, backdrop-filters, heavy animations, additional DOM weight) can prevent the spinner from ever dismissing — even when custom JS tries to hide `.theme-preloader` inline.

For self-contained HTML pages on elementor_canvas template, always verify the spinner clears after adding new heavy content.
