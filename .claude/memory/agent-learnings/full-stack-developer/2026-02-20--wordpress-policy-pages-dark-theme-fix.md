# WordPress Policy Pages - Dark Theme Fix

**Date**: 2026-02-20
**Type**: teaching
**Topic**: Fixing WordPress pages with full HTML document structure using Gutenberg HTML block

---

## Problem

Pages saved with full `<!DOCTYPE html>` / `<html>` / `<head>` / `<body>` document structure were being mangled by WordPress's `wpautop` filter. The filter inserts `<p>` and `<br>` tags around content, breaking `<style>` tags and `<div>` layouts.

Additionally, the CSS itself had a bug: `h2` and `h3` used `color: var(--dark)` which was `#1a1a2e` - the exact same dark color as the section backgrounds, making headings invisible.

## Pages Fixed

- Privacy Policy: page ID 3 at purebrain.ai/privacy-policy/
- Terms of Service: page ID 541 at purebrain.ai/terms-of-service/

## Fix Strategy

### 1. Strip Document Wrapper
Extract only the `<style>...</style>` block content and `<body>...</body>` inner content from the HTML files. Discard `<!DOCTYPE>`, `<html>`, `<head>`, `</html>` etc.

```python
import re
style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
body_match = re.search(r'<body>(.*?)</body>', html, re.DOTALL)
```

### 2. Fix Dark Theme CSS Issues
These CSS rules used `var(--dark)` = `#1a1a2e` (dark color) on dark backgrounds, making text invisible:
- `h2 { color: var(--dark); }` → change to `color: #ffffff`
- `h3 { color: var(--dark); }` → change to `color: #e0e0e0`
- `.service-table th { color: var(--dark); }` → change to `color: #e0e0e0`
- `.plan-table th { color: var(--dark); }` → change to `color: #e0e0e0`
- `.contact-label { color: var(--dark); }` → change to `color: #e0e0e0`
- Table hover/nth-child with light backgrounds (`#fafcff`) → change to dark-theme-appropriate colors

### 3. Wrap in Gutenberg HTML Block
This is THE key fix. Wrapping content in `<!-- wp:html -->` markers tells WordPress to treat the entire block as raw HTML and skip `wpautop` processing:

```
<!-- wp:html -->
<style>
  /* all CSS here */
</style>
<div class="page-header">
  <!-- all body content here -->
</div>
<!-- /wp:html -->
```

### 4. Update via REST API

```bash
curl -X POST "https://purebrain.ai/wp-json/wp/v2/pages/{ID}" \
  -u "Aether:${PUREBRAIN_WP_APP_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d @/tmp/content.json
```

Where the JSON file contains: `{"content": "<!-- wp:html -->..<!-- /wp:html -->"}`

## Verification Checks

After update, fetch the live page and verify:
1. Dark background colors present (`#0a0a0a`, `#1a1a2e`)
2. Light text colors present (`#e0e0e0`)
3. NO `<p><div>` wrapping (wpautop signature)
4. NO `<p><style>` wrapping
5. `h2` headings have `color: #ffffff` (visible on dark bg)

## Results (Session 34 - First Fix)

Both pages verified working:
- Dark bg `#0a0a0a`: present 4x in CSS
- Section bg `#1a1a2e`: present 4-5x
- Light text `#e0e0e0`: present 4x
- Brand blue `#2a93c1`: present 59x (throughout styling)
- Zero `<p><div>` or `<p><style>` mangling
- h2 `color: #ffffff`: confirmed 44x in TOS page

## Session 35 - Re-Fix (WordPress Theme Override Still Winning)

Jared reported the pages still showed light background. Investigation showed:
- wp:html block was PRESENT (previous fix worked for Gutenberg)
- BUT the WordPress Artistics theme CSS still overrode `body { background }` because inline CSS without `!important` loses to theme stylesheets

**Root cause**: WordPress theme CSS (Artistics) applies `body { background-color: ... }` at higher specificity or later in cascade than inline `<style>` blocks inside wp:html. `body { background: var(--bg-light) }` in the page CSS is not enough.

**The additional fix needed**: Add a critical override block with `!important` targeting ALL WordPress wrapper selectors:

```css
/* === DARK THEME OVERRIDE - Force dark bg on WordPress wrappers === */
html, body, .site, .page, #page, #content, .entry-content, main, article,
.elementor, .elementor-section, .elementor-container, .elementor-column,
.elementor-widget-wrap, .elementor-element, .wp-block-html {
  background: #0a0a0a !important;
  background-color: #0a0a0a !important;
}
body {
  background: #0a0a0a !important;
  background-color: #0a0a0a !important;
  color: #e0e0e0 !important;
}
/* === END DARK THEME OVERRIDE === */
```

This was injected at the TOP of the `<style>` block (before `:root` variables).

**Session 35 Verification**:
- `DARK THEME OVERRIDE` block confirmed in live HTML
- `background: #0a0a0a !important` present 4x
- h2 `color: #ffffff` confirmed
- 599 occurrences of `important` keyword in page (CSS doing its job)

## Key Lessons (Updated)

1. **Gutenberg `<!-- wp:html -->` bypasses wpautop** - still true and needed

2. **`body { background }` alone is NOT enough** - WordPress theme CSS overrides it. You MUST use `!important` on both `html, body` AND all the WordPress/Elementor wrapper selectors.

3. **The full override selector list is**: `html, body, .site, .page, #page, #content, .entry-content, main, article, .elementor, .elementor-section, .elementor-container, .elementor-column, .elementor-widget-wrap, .elementor-element, .wp-block-html`

4. **Always add the critical override block** when deploying dark-theme pages to WordPress. This is now the standard pattern.

## Files Referenced

- Source HTML: `/home/jared/projects/AI-CIV/aether/to-jared/privacy-policy.html`
- Source HTML: `/home/jared/projects/AI-CIV/aether/to-jared/data-policy.html`
- WP Password: `.env` as `PUREBRAIN_WP_APP_PASSWORD`
