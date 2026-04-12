# CSS: overflow-x: hidden on html/body KILLS position: sticky

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: CSS overflow-x and position:sticky incompatibility

## The Rule

**`overflow-x: hidden` on `html` or `body` elements destroys `position: sticky` behavior.**

This is a browser specification behavior, not a bug. When an ancestor has `overflow: hidden` (or `overflow-x: hidden`), sticky positioning stops working because the element's scrolling container changes.

## The Fix

Replace `overflow-x: hidden` with `overflow-x: clip`:

```css
/* BROKEN - kills all sticky children */
html, body {
  overflow-x: hidden;
}

/* FIXED - prevents horizontal scroll WITHOUT killing sticky */
html, body {
  overflow-x: clip;
}
```

## Why `clip` Works

- `overflow-x: clip` visually clips content the same way `hidden` does
- But `clip` does NOT create a new scroll container
- So `position: sticky` children still reference the viewport scroll
- Browser support: All modern browsers (2024+)

## Related Pattern

Also learned in the same session:
- **CSS Grid + `grid-row: 1/-1` + sticky** doesn't work reliably for sidebar layouts
- Better approach: Use **flexbox** (`display: flex`) with the sidebar as a flex child using `position: sticky; top: 20px; align-self: flex-start`

## Context

Discovered fixing the AI Tool Stack Calculator (page 777) sidebar on purebrain.ai. The sidebar was supposed to stay visible while scrolling through 25+ tool categories, but WordPress theme CSS had `overflow-x: hidden` on body, killing the sticky behavior entirely.

## See Also

- `2026-02-23--page816-nuclear-nav-root-cause.md` - overflow-x:hidden also affects position:fixed (nav clipping)
- `2026-02-24--calculator-layout-3fixes-deployed.md` - the full calculator fix context
