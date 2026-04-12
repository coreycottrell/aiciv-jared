# investors-v8 Infinite Scroll Bug Fix
**Date**: 2026-03-21
**Type**: bug-fix / teaching
**Agent**: dept-systems-technology

## Problem
On mobile, users could scroll infinitely past the last section (data-section="13", Ask Aether).
The voice/AI area disappeared and scroll continued into empty space.

## Root Causes (3 compounding issues)

### 1. GSAP scrub end value extended past the viewport bottom
The "sink back" ScrollTrigger animation used `end: 'bottom -10%'` which tells GSAP the animation
should keep running until the trigger element is 10% PAST the bottom of the viewport.
GSAP adds actual scroll distance to accommodate this — the browser extends the scrollable area
so the animation can complete. On mobile with short viewports, this creates several hundred
pixels of empty scroll space.

**Fix**: Changed `end: 'bottom -10%'` to `end: 'bottom 5%'` so the animation completes
BEFORE the section fully exits, eliminating the phantom scroll extension.

### 2. Last section had min-height: 100vh
All `.content-section` elements had `min-height: 100vh`. On the final section this forced
the page to have at least one full viewport of height AFTER all visible content ends.
On mobile where the fixed bottom banner takes up space, this left visible empty area.

**Fix**: Added `content-section[data-section="13"]{min-height:auto;padding-bottom:100px}`
so the last section is only as tall as its content needs.

### 3. #scroll-root missing overflow-x: hidden
Without overflow-x: hidden, any element that accidentally extended horizontally
would create horizontal scrolling AND could contribute to incorrect scroll height
calculations by the browser layout engine.

**Fix**: Added `overflow-x:hidden` to `#scroll-root`.

## Files Modified
- `exports/cf-pages-deploy/investors-v8/index.html` (v3.0 → v3.1)

## Deployment
- CF Pages purebrain-staging — deployed successfully
- Deployment URL: https://f8ee234d.purebrain-staging.pages.dev

## Pattern: GSAP scrub + negative end values cause phantom scroll
When GSAP ScrollTrigger uses a negative end percentage (e.g., `end: 'bottom -20%'`),
it instructs the browser to extend page height so the animation can complete after the
element has scrolled out of view. On mobile this manifests as infinite empty scroll.
ALWAYS use positive end values on the LAST section to prevent this.

## Pattern: Last section min-height:100vh
Never apply `min-height:100vh` to the last section of a page without also setting it
on the final wrapper. Add a specific override for `[data-section="13"]` or the last
section class to reset min-height to auto.
