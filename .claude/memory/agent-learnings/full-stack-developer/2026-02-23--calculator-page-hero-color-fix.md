# Calculator Page Hero Color Fix + 151+ Update

**Date**: 2026-02-23
**Type**: operational
**File**: exports/ai-tool-stack-calculator-v3.html → WordPress page 777

## What Was Fixed

1. **Hero headline "Thousands" + "Tool Sprawl" showing white** instead of orange
   - Root cause: `.calc-hero h1 em` had `color: var(--pb-blue)` (wrong color)
   - Root cause 2: The `body.page-id-777.tt-magic-cursor *:not(...)` override was killing the color
   - Fix: Changed em color to `var(--pb-orange) !important`
   - Fix: Added `:not(.calc-hero h1 em):not(.calc-hero h1 .orange)` to the :not() exclusion chain

2. **"140+" updated to "151+"** across all instances (title, meta, og tags, stats, eyebrow, JS comments)
   - Used replace_all=true on the Edit tool - caught all 10 instances cleanly

## CSS Override Pattern (IMPORTANT)

The `body.page-id-777.tt-magic-cursor *:not(...)` pattern is a "magic cursor poison fix" -
it forces `color: inherit` on everything to prevent the WordPress theme from injecting orange.
But it ALSO kills intended colored text unless those selectors are excluded via `:not()`.

**Lesson**: When adding colored text inside page-id-777, ALWAYS:
1. Add `!important` to the color rule
2. Add the selector to the `:not()` exclusion chain on line 1655

## Deploy Pattern

- Extracted lines 17-1659 (style block) + 1662-3407 (body content)
- Wrapped in `<!-- wp:html --> ... <!-- /wp:html -->`
- PUT to /wp-json/wp/v2/pages/777
- Cleared Elementor cache: DELETE /wp-json/elementor/v1/cache

## Verification Results

- HTTP 200, page published
- `151+` appears 6 times on live page (0 instances of `140+`)
- `.calc-hero h1 em { color: var(--pb-orange) !important; }` present
- `:not(.calc-hero h1 em)` exclusion in override rule
- heroToolCount shows `151+`, globalToolCount shows `0 of 151+`
