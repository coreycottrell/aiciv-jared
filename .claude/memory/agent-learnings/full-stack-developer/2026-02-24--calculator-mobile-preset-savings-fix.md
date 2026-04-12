# Calculator Mobile: Preset Pills Fixed + Inline Savings Bar
**Date**: 2026-02-24
**Type**: teaching
**Topic**: Two mobile UX fixes for AI Tool Stack Calculator page 777

## Problems Fixed

### Problem 1: Preset pills "stuck to bottom"
The pills used `position: sticky; top: 0` on mobile. This is unreliable in WordPress embedded contexts (full HTML doc inside `<!-- wp:html -->`). The sticky positioning may have been calculated relative to an unexpected scroll container, causing pills to visually appear at the wrong position.

**Fix**: Changed to `position: fixed; top: 0; left: 0; right: 0` with `z-index: 500`. This is 100% reliable - pills are always at the top of the viewport on mobile regardless of scroll container ancestry.

**CSS adjustment**: Added `padding-top: 60px` to `.calc-wrap` on mobile via CSS, and JS `adjustMobilePresetPadding()` function that measures the exact preset bar height and sets `wrapEl.style.paddingTop` dynamically. Runs on load and on window resize.

### Problem 2: Sidebar/savings invisible on mobile
The previous solution hid the sidebar and showed a bottom bar that required a **tap** to see savings. Jared's requirement: users MUST see savings without having to tap.

**Fix**: Added a new `calc-mobile-savings` inline element that sits at the top of `.calc-wrap` on mobile (below the preset pills). It shows:
- Zero state: "Your Savings Will Appear Here" with friendly explanation
- Active state (when tools selected):
  - Your AI Spend vs PureBrain side-by-side (big numbers)
  - "You save $X/mo" green pill
  - Recommended plan badge with tier color theming
  - "View Full Breakdown & Get Started ↑" button (opens bottom sheet)

**JS**: `updateMobileSavingsBar(spend, tier, savings)` function called from `refreshUI()`. Adds/removes `has-data` class on the container to toggle zero/active states.

## Architecture Notes

- `.calc-mobile-savings` is `display: none` on desktop, `display: block` on mobile (`@media max-width: 960px`)
- Zero state: `.calc-mobile-savings-zero` div (visible by default)
- Active state: `.calc-mobile-savings-active` div (hidden by default, shown when `.has-data` class present)
- The bottom bar + bottom sheet still exist as before — they're the secondary/confirmation path
- The mobile savings bar is the PRIMARY visibility path (no tap required)

## WordPress Color Override Pattern

Added `body.page-id-777 .calc-mobile-savings-*` rules to lock down colors against theme overrides and magic cursor plugin interference.

## Files Changed

- Source: `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`
- Deployed: WP page 777 via REST API PUT
- Elementor cache cleared: DELETE /wp-json/elementor/v1/cache

## Verification

- HTTP 200 deploy + cache clear
- Live page: all 16 checks PASS
- 1 `<html>` tag count (no nesting)
- Page size: 272355 bytes
