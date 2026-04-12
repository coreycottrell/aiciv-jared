# Calculator Page 777 - Orange Text Fix

**Date**: 2026-02-23
**Type**: teaching
**Topic**: CSS catch-all + :not() compound selector limitation causing color override failure

## Problem
Page 777 (ai-tool-stack-calculator): `<em>Thousands</em>` and `<span class="orange">Tool Sprawl</span>` showing WHITE instead of orange in the hero h1.

## Root Cause (Multi-Layer)

### Layer 1: Additional CSS - [class*="magic"] poison
In Additional CSS (block 4), this rule applies:
```css
[class*="magic"] {
  color: #f1420b !important;
  background-color: #f1420b !important;
}
```
Body has class `tt-magic-cursor` → `[class*="magic"]` matches body → sets body `color: #f1420b !important`.

### Layer 2: Catch-all rule using invalid :not() compound selectors
The page had:
```css
body.page-id-777.tt-magic-cursor *:not(.calc-hero h1 em):not(.calc-hero h1 .orange) {
  color: inherit;
}
```
CSS Level 3 `:not()` only supports SIMPLE selectors. `.calc-hero h1 em` is a COMPOUND selector (descendant). This `:not()` is INVALID and ignored by browsers. So `em` and `.orange` DO get `color: inherit` applied.

### Layer 3: Why !important didn't save it
The page had `.calc-hero h1 em { color: var(--pb-orange) !important; }` BUT there appears to be a specificity/cascade interaction where the CSS variable `var(--pb-orange)` may not resolve before the `body.page-id-777.tt-magic-cursor *` rule applies `color: inherit` setting the resolved value to white.

## Fix Applied

### Fix 1: Changed :not() to use SIMPLE selectors only
```css
/* BEFORE (invalid) */
body.page-id-777.tt-magic-cursor *:not(.calc-hero h1 em):not(.calc-hero h1 .orange) { color: inherit; }

/* AFTER (valid CSS3 simple selectors) */
body.page-id-777.tt-magic-cursor *:not(a):not(button):not(.calc-logo):not(...):not(.orange):not(em) {
  color: inherit;
}
```

### Fix 2: Added force-override AFTER catch-all with hardcoded hex
```css
/* ORANGE TEXT FORCE-OVERRIDE (AFTER catch-all) */
body.page-id-777 .calc-hero h1 em,
body.page-id-777.tt-magic-cursor .calc-hero h1 em,
.page-id-777 .calc-hero h1 em {
  font-style: normal !important;
  color: #f1420b !important;  /* hardcoded, not CSS var */
}
body.page-id-777 .calc-hero h1 .orange,
body.page-id-777.tt-magic-cursor .calc-hero h1 .orange,
.page-id-777 .calc-hero h1 .orange {
  color: #f1420b !important;
}

/* Fix [class*="magic"] body pollution */
body.page-id-777[class*="magic"],
body.page-id-777.tt-magic-cursor {
  color: #e8edf3 !important;
  background-color: #080a12 !important;
}
```

## Key CSS Lesson
**CSS3 `:not()` only accepts simple selectors.** Descendant selectors like `.parent .child` inside `:not()` are INVALID and the browser ignores the entire `:not()` clause. CSS Level 4 supports complex selectors in `:not()` but browser support varies.

**The safe pattern**: Always use SIMPLE selectors in `:not()` (single class, type, or ID).

## Badge Text
The stored content already had "151+" everywhere. "140+" in Jared's screenshot was likely a CDN/browser cache issue.

## Files Changed
- WordPress page 777 via REST API PUT
- Elementor cache cleared via DELETE /wp-json/elementor/v1/cache
