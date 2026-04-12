# Calculator Share Modal X Button Fix

**Date**: 2026-02-24
**Type**: gotcha + technique
**Agent**: full-stack-developer
**File**: `exports/ai-tool-stack-calculator-v3.html` → WP page 777

---

## The Bug

The X (close) button on the "Share Your Stack Cost" modal was not responding to clicks.

The button had:
- `type="button"` (correct)
- `onclick="closeShareModal()"` (correct)
- `addEventListener('click', ...)` with `e.stopPropagation()` (correct)
- `closeShareModal()` function correctly implemented (correct)

All the JS was wired right. But clicks weren't registering.

## Root Cause

**Missing `z-index` on `position: absolute` button inside a stacking context.**

The `.calc-share-modal-close` button was:
- `position: absolute` inside the modal (which is `position: relative`)
- No `z-index` set

Within WordPress/Elementor, other stacking contexts can interfere. Without an explicit `z-index`, the button renders visually in the right place but other elements (potentially transparent overlays or sibling elements with higher stacking order) intercept the clicks before they reach the button.

## The Fix

Added exactly two lines to `.calc-share-modal-close` CSS:

```css
.calc-share-modal-close {
  position: absolute;
  top: 16px; right: 16px;
  z-index: 10;          /* ADDED - ensures button sits above modal content */
  /* ... rest unchanged ... */
  pointer-events: auto; /* ADDED - explicit guarantee clicks reach the button */
}
```

**Surgical. Touch nothing else.**

## Key Lesson

**When a visually-correct button doesn't respond to clicks in WordPress/Elementor:**

1. First suspect: missing `z-index` on `position: absolute` element
2. Second suspect: `pointer-events: none` inherited from a parent
3. Third suspect: transparent overlay element on top (check z-index stack)
4. Fourth suspect: `e.stopPropagation()` somewhere in the event chain blocking bubbling

For modal close buttons specifically: **always set `z-index: 10` on `.modal-close` buttons** that are `position: absolute`. This is a permanent pattern.

## Deployment

- Local file: `exports/ai-tool-stack-calculator-v3.html`
- WP page: 777 (`https://purebrain.ai/ai-tool-stack-calculator/`)
- Deployed via: REST API PUT to `/wp-json/wp/v2/pages/777`
- Cache cleared: DELETE `/wp-json/elementor/v1/cache`
- Verification: All 8 functional checks passed on live page

## Pattern: Absolute-Positioned Button in Modal

Always include these in modal close button CSS:
```css
.modal-close {
  position: absolute;
  z-index: 10;           /* Prevent click interception */
  pointer-events: auto;  /* Explicit guarantee */
  cursor: pointer;
}
```
