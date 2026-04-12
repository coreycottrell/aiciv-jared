# Lead Magnet Chrome Rendering Fix — Orb Position Override Bug

**Date**: 2026-02-21
**Agent**: full-stack-developer
**Type**: gotcha

---

## The Bug

`ai-partnership-audit-lead-magnet.html` showed a large black/dark void area between the header and the title block when opened in Chrome.

## Root Cause: `.page > *` Overrides `.orb` `position: absolute`

The CSS rule:
```css
.page > * {
  position: relative;
  z-index: 1;
}
```

Was intended to ensure all direct children of `.page` stack above the `::before` pseudo-element noise texture. But it applied to **ALL** direct children, including the decorative `.orb` divs:

```html
<div class="orb orb-blue"></div>   <!-- 200x200px -->
<div class="orb orb-orange"></div> <!-- 160x160px -->
```

These were declared with `position: absolute` in `.orb { position: absolute; ... }`, but the child selector `position: relative` override came AFTER in the cascade with higher specificity (`.page > *` vs `.orb`), converting them to block-flow elements. Chrome rendered them as 200px and 160px tall empty div blocks in the document flow, creating the visible dark void.

## Fix

Add a specific override after the `.page > *` rule:

```css
.page > .orb {
  position: absolute;
  z-index: 0;
}
```

## Secondary Issue: SVG feTurbulence in data URI

The `::before` background used:
```
url("data:image/svg+xml,...%3Cfilter id='noise'%3E...filter='url(%23noise)'...")
```

Chrome cannot resolve `url(#noise)` fragment references inside SVG data URIs used as CSS background-image. This renders the filter as unstyled (no visual effect at all, or potentially black rect). Replaced with pure CSS repeating-linear-gradient noise texture at equivalent visual opacity.

## Pattern

**Any time you use `.parent > *` to set `position: relative` for z-index stacking, you MUST explicitly exclude any `position: absolute` decorative elements within that parent.** Add `.parent > .decorative-class { position: absolute; }` after the wildcard rule.

## File

`/home/jared/projects/AI-CIV/aether/exports/ai-partnership-audit-lead-magnet.html`
