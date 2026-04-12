# Memory: Invitation Page Orange Background Bug - Feb 27 2026
**Date**: 2026-02-27
**Type**: gotcha + technique
**Topic**: Elementor kit CSS overriding body background-color on custom pages

---

## Bug Found

On purebrain.ai/invitation/ (page-id-987, Elementor canvas template), body background computed to `rgb(241, 66, 11)` (PureBrain orange) instead of `#0a0e1a` (dark navy). All page sections had `background: transparent`, so the orange bled through on scroll past the hero.

## Root Cause

CSS cascade order:
1. `artistics/style.css`: `body { background-color: var(--e-global-color-black); }`
2. Elementor kit-10 dynamic CSS (CORS-protected, not JS-readable): redefines `--e-global-color-black` to `#f1420b`
3. Page inline CSS: `body { background: var(--bg); }` where `--bg: #0a0e1a` — BUT `var(--bg)` resolves to `rgba(0,0,0,0)` (transparent) when applied on child elements (CSS variable scoping quirk)
4. Result: Elementor kit orange wins

The page CSS had `body { background: #0a0e1a !important }` in one rule but a LATER rule in the same sheet `body { background: var(--bg) }` (without !important) overwrote it. The `var(--bg)` = transparent, so the Elementor kit orange showed through.

## The Fix

In the page's own CSS block:
```css
body {
    background-color: #0a0e1a !important;
    background: #0a0e1a !important;
}
```
Use literal hex value (not CSS variable) AND `!important` to beat Elementor kit.

## Detection Pattern

When full-page screenshot shows orange block below the hero:
1. Check `window.getComputedStyle(document.body).backgroundColor` — if orange, it's this bug
2. Check Elementor kit-10 CSS for `--e-global-color-black` value
3. Fix: override body background with literal hex + !important in page CSS

## Investigation Tools That Helped

- `document.elementFromPoint(720, 1000)` — find what element is at scroll y=1000
- Loop `document.styleSheets` looking for `rule.selectorText === 'body'` with background rules
- `document.body.style.setProperty('background-color', '#0a0e1a', 'important')` — test fix immediately

## What Was Working

Despite the orange bug, ALL other elements were correct:
- Countdown timer: LIVE at 06d 03h 43m (not zeros)
- All 4 pricing tiers: Awakened $79, Bonded $149, Partnered $499, Unified $999
- Michael Hancock testimonial: Present
- Jared quote: Present
- 4-step process: Present
- Chat mockup: Present
- Logo: Real icon (not SVG placeholder)
- CTA buttons: Orange gradient, link to /#awakening
- Console: Only 4 CSP errors (GTM, GoDaddy blocked) — no JS errors

## 3D Brain Animation Note

Cannot verify WebGL canvas in headless Playwright. `#pb-canvas-container` div IS in the DOM, styled correctly (`position:fixed; 100vw x 100vh; z-index:0; background:#0a0e1a`). Script length 27,149 chars, uses Three.js dynamic import. No console error about missing container. Should work in real browser — must verify manually.

## Files

- Audit script: `tools/test_invitation_audit_feb27.py`
- Deep brain check: `tools/test_invitation_brain_deep.py`
- Orange bug investigation: `tools/test_invitation_orange_bug.py`
- Report: `exports/invitation-page-audit-report-2026-02-27.md`
- Screenshots: `exports/screenshots/invitation-audit-2026-02-27/` (12 files)
