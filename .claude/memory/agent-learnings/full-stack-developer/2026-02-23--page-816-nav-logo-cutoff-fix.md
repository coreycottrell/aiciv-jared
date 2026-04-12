# Page 816 Nav Logo Cutoff Fix

**Date**: 2026-02-23
**Type**: teaching + operational
**Topic**: Fixed PUREBRAIN.ai logo text cutoff and missing "Get Your Report" button on purebrain.ai/ai-website-analysis/

---

## Problem

The nav bar on page 816 was showing "PUREBR AI" (cut off) instead of "PUREBRAIN.ai", and the "Get Your Report" orange CTA button was not visible at all.

**Root Cause**: The page uses generic CSS selectors (`nav {}`, `.nav-brand {}`, etc.) which conflict with WordPress/Astra theme's own `nav` styles. The theme applies `overflow: hidden`, `max-width` constraints, and other layout-breaking styles to generic `<nav>` elements.

---

## Fix Applied

Added `!important` to ALL critical nav CSS properties to override WordPress theme interference:

```css
nav {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  width: 100% !important;
  max-width: none !important;
  overflow: visible !important;
  z-index: 100000 !important;        /* raised from 100 to beat WP header */
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  justify-content: space-between !important;
  ...
}

.nav-brand {
  flex-shrink: 0 !important;
  white-space: nowrap !important;
  overflow: visible !important;
  ...
}

.nav-cta {
  flex-shrink: 0 !important;
  white-space: nowrap !important;
  display: inline-block !important;
  visibility: visible !important;
  opacity: 1 !important;
  overflow: visible !important;
  ...
}
```

---

## Key Lessons

1. **Generic nav selectors ALWAYS conflict in WordPress** - When deploying HTML pages inside `<!-- wp:html -->` blocks, any `nav {}` CSS rule will fight with WordPress/Astra theme styles. Always use `!important` or scope under a unique page ID like `#pb-web-analysis nav {}`.

2. **The "Get Your Report" button was hidden** - Not just cut off, but completely invisible because `flex-shrink` was letting it collapse. Adding `flex-shrink: 0` and `visibility: visible !important` fixed it.

3. **`overflow: visible` is critical** - WordPress theme sets `overflow: hidden` on nav elements which clips content that extends beyond the natural bounds.

4. **z-index should be high** - WordPress header z-index is typically 9999 or similar. Changed nav z-index from 100 to 100000.

---

## Pages/Files Changed

- **Source**: `/home/jared/projects/AI-CIV/aether/exports/client-marketing/website-analysis/index.html`
- **WordPress**: `https://purebrain.ai/ai-website-analysis/` (page ID 816)
- **Template**: `elementor_canvas`

---

## Deployment Pattern

1. Edit source HTML nav CSS (add `!important` to all properties)
2. Extract head content (link + style) + body content
3. Wrap in `<!-- wp:html -->` block
4. POST to `https://purebrain.ai/wp-json/wp/v2/pages/816`
5. DELETE `https://purebrain.ai/wp-json/elementor/v1/cache`

---

## Prevention Going Forward

For ANY new HTML page deployed to WordPress with a nav bar, immediately add `!important` to:
- `nav`: overflow, width, max-width, display, flex-direction, flex-wrap, align-items, justify-content
- Nav children: flex-shrink, white-space, visibility, overflow

Better long-term fix: Wrap all custom CSS under a unique page ID (`#pb-web-analysis nav {}`) so WordPress theme styles can never conflict. This avoids needing `!important` everywhere.
