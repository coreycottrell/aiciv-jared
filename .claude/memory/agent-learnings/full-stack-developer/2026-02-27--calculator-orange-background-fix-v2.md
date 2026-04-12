# Calculator Page 777 Orange Background Fix v2

**Date**: 2026-02-27
**Type**: gotcha + fix
**Agent**: full-stack-developer

## The Bug

WP page 777 (AI Tool Stack Calculator) showed entire page background as orange (#f1420b).

## Root Cause Analysis

Multiple unscoped CSS rules in the PureBrain security plugin bleed onto ALL pages:

1. `.elementor-post__title { background: linear-gradient(135deg, #f1420b 0%, ...) !important }` - meant for blog listing, bleeds everywhere
2. `[class*="category"] a:hover { background: #f1420b !important }` - bleeds to any page with category links
3. The Artistics theme sets `body { background-color: var(--e-global-color-black) }` via style.css
4. The calculator's original `body { background: var(--pb-bg) }` had NO `!important` so it could be overridden

The combination of theme CSS and unscoped plugin CSS created a cascade where orange backgrounds won.

## The Fix

**In the calculator HTML file** (`/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`):

Added immediately after `:root { }` block:

```css
/* CRITICAL BG FIX v2: Dark background beats ALL theme/plugin CSS. */
html, body {
  background: #080a12 !important;
  background-color: #080a12 !important;
}

body {
  background: #080a12 !important;
  background-color: #080a12 !important;
  ...
}
```

**Key principles applied:**
1. Used hardcoded hex `#080a12` instead of `var(--pb-bg)` - variables can be overridden
2. Added `!important` to beat all plugin and theme rules
3. Set on BOTH `html, body` (joint selector) AND `body` (separate selector) for maximum specificity
4. Both `background` shorthand AND `background-color` longhand set to prevent any shorthand override

## Deployment

- File: `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`
- Deployed via WP REST API POST to page 777
- Deployed at: 2026-02-27T11:59:19 UTC

## Verification

Live page body rules after fix:
```css
html, body { background: #080a12 !important; background-color: #080a12 !important; }
body { background: #080a12 !important; background-color: #080a12 !important; ... }
```
These are in block 7 of the page's style blocks.

## Pattern for Future Reference

For ANY self-contained HTML page deployed to WordPress:
- ALWAYS add `html, body { background: #HEXCOLOR !important; background-color: #HEXCOLOR !important; }` at the top of the style block
- NEVER rely on CSS variables alone for background color in WordPress context
- NEVER omit `!important` on body background when deploying to WordPress
- Also add a plugin-level page-specific override as belt-and-suspenders: `body.page-id-{N} { background: #HEXCOLOR !important; }`
