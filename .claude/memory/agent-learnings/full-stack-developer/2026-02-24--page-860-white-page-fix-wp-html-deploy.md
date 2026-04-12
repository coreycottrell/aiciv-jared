# Page 860 White Page Fix — wp:html Deployment

**Date**: 2026-02-24
**Type**: operational
**Topic**: Fixed page 860 (ai-website-execution) showing all-white by stripping nested HTML document wrapper and deploying via wp:html block

---

## Root Cause

Page 860 stored a FULL HTML document (`<!DOCTYPE html>`, `<html>`, `<head>`, `<body>` tags) as WordPress page content. WordPress wraps all content in its own HTML structure, resulting in nested HTML documents. Browser rendering of nested `<html>` documents = broken/white page.

## The Fix

1. Read source HTML from `exports/ai-website-execution.html`
2. Extracted:
   - Font link tags (2 Google Fonts links)
   - `<style>` block (17,329 chars)
   - Body inner content (20,993 chars)
   - PayPal SDK script tag
3. Wrapped everything in `<!-- wp:html -->` block with `#ai-exec-wrapper` div
4. Deployed via WordPress REST API with `template: elementor_canvas`

## Content Layout

```
<!-- wp:html -->
<link rel="preconnect" ...>
<link href="fonts.googleapis.com/css2?family=Inter...">
<style>... (full CSS with magic-cursor overrides) ...</style>
<div id="ai-exec-wrapper" style="background: #080a12; min-height: 100vh;">
  ... all body content ...
</div>
<script src="https://www.paypal.com/sdk/js?..."></script>
<!-- /wp:html -->
```

## Verification Results

- `<!DOCTYPE` count in live page: 1 (only WordPress's own, not nested)
- `body.tt-magic-cursor` override: present
- `background: #080a12 !important`: present
- `body.page-id-860` override: present
- `#ai-exec-wrapper` div: present
- Hero text "You Saw the Gaps": present
- Pricing "Critical Fixes": present
- PayPal script: present

## Key Notes

- The source HTML already had the magic-cursor overrides built in (lines 11-37 of source)
- PayPal script extracted separately from body content to avoid duplication
- Template kept as `elementor_canvas`
- Page URL: `https://purebrain.ai/ai-website-execution/`
- WordPress Page ID: 860

## Pattern Reference

See: `2026-02-23--self-contained-html-wp-deployment-rules.md` for the full pattern
See: `MEMORY.md` — WP HTML DEPLOYMENT RULE: always wrap in `<!-- wp:html -->`
