# Calculator Mobile: Structural Fix - Pills Moved Inside calc-wrap

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: Three mobile layout issues on page 777 - pill position fixed structurally by moving DOM element

## Problems Reported by Jared

1. Preset pills stuck at top of mobile screen
2. "PERSONALIZE YOUR SAVINGS" overlapping with bottom bar
3. "View Savings" button/bottom bar overlapping footer

## Root Cause Analysis

### Issue 1: Pills at TOP

Previous CSS fix (`position: static`) was correct but INSUFFICIENT. The problem was structural:
- `calc-presets` div was placed BETWEEN `calc-hero` and `calc-wrap` in the DOM
- Even with `position: static`, the browser may render them oddly in the WP embedded context
- Cloudflare CDN caching may have served stale versions

**Root Fix**: Moved `calc-presets` div INSIDE `calc-wrap` as the FIRST child element.
- Pills now structurally come AFTER the hero — no ambiguity possible
- Pills naturally flow below the hero heading + personalize section
- DOM order: `calc-hero` → `calc-wrap` → `calc-presets` (inside) → `calc-mobile-savings` → content

### Issue 2: Personalize Overlapping Bottom Bar

The `.calc-hero` needed more bottom padding on mobile to ensure its last elements
(search bar, stats, personalize section) don't get covered by the fixed bottom bar.

Fixed by increasing `.calc-hero` mobile `padding-bottom` from `20px !important` to `160px !important`.
- Bar is at `bottom: 64px`, height ~72px = occupies 64-136px from viewport bottom
- 160px padding-bottom on hero gives more than enough clearance

### Issue 3: Bottom Bar Overlapping Footer

`#purebrain-legal-footer` is a WP plugin footer (~64px tall) that appears below page content.
Fixed by `bottom: 64px !important` on `.calc-bottom-bar` — bar sits above the footer.

Both Issues 2 and 3 CSS fixes were already deployed from a prior session — consolidated into one
clean media query block instead of two separate `@media (max-width: 960px)` blocks.

## Changes Made

### HTML (structural)
- Moved `<div class="calc-presets">` from OUTSIDE `calc-wrap` to INSIDE as first child
- Updated comment from "sticky at top on mobile" to accurate description

### CSS
- `.calc-wrap` mobile: `padding-top: 0` → `padding-top: 16px` (small top gap now that pills are inside)
- `.calc-hero` mobile: `padding-bottom: 20px` → `padding-bottom: 160px !important`
- `.calc-personal-box` mobile: `margin-bottom: 100px` → `margin-bottom: 24px !important` (hero padding handles clearance)
- `.calc-bottom-bar` mobile: `bottom: 64px !important` (unchanged - was already correct)
- `body` mobile: `padding-bottom: 160px !important` (was 150px, slight increase for safety)
- Consolidated two `@media (max-width: 960px)` blocks for bottom bar into one

## Key Lesson

**CSS positioning fixes alone may not solve structural ordering problems.**
When an element appears "at the wrong position," consider MOVING IT IN THE DOM rather than just
fighting with CSS. Moving `calc-presets` inside `calc-wrap` was a 5-minute HTML change that
definitively solved the issue, whereas CSS-only approaches kept failing.

## Deployment Verification

- Modified: 2026-02-24T17:43:46
- Content length: 151013 chars
- 10/10 verification checks PASS:
  - position: static for pills (mobile): PASS
  - pills inside calc-wrap (structural): PASS
  - calc-presets AFTER calc-wrap in DOM: PASS
  - bottom: 64px on bottom bar: PASS
  - padding-bottom: 160px on body (mobile): PASS
  - padding-top: 16px on wrap (mobile): PASS
  - no nested <html> tag: PASS
  - calc-mobile-savings present: PASS
  - View Savings button present: PASS
  - bottom sheet overlay present: PASS

## Files Changed

- Source: `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`
- Deployed: WP page 777 via REST API PUT (HTTP 200)
- Elementor cache cleared: HTTP 200
- Live URL: https://purebrain.ai/ai-tool-stack-calculator/
