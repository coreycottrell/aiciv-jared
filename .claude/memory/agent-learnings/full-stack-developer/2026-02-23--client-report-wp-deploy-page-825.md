# Client Report HTML Deployment - WordPress Page 825

**Date**: 2026-02-23
**Type**: teaching
**Topic**: Deploying 68KB standalone HTML report to WordPress as password-protected draft

---

## Task

Deploy `exports/client-marketing/report-template.html` (DuckDive 9-dimension website analysis
for Corey) to WordPress page 825. Page was blank. Must remain draft, password: duckdive2024.

## What Worked

### Pattern: Strip + Scope + wp:html

1. **Extract** `<style>` block and `<body>` inner content via regex
2. **Add Google Fonts** `<link>` tags (stripped from `<head>`)
3. **Prepend dark theme override** CSS at top of style block:
   - `html body.page { background-color: #0a0e1a !important; }`
   - `.wp-block-html { background: #0a0e1a !important; }`
4. **Scope** with wrapper `<div id="pb-report-825">` around body content
5. **Wrap everything** in `<!-- wp:html --> ... <!-- /wp:html -->`
6. **Deploy** via `PUT /wp-json/wp/v2/pages/825` with `status: draft`, `password: duckdive2024`
7. **Clear** Elementor cache: `DELETE /wp-json/elementor/v1/cache`

### CSS variables (`:root`) stay global - no scoping needed
CSS custom properties defined in `:root` are accessible globally, so no need to scope them.
Only needed: dark bg override at top and wrapper div ID for CSS specificity.

## Key Numbers

- Source file: 68KB (22K CSS + 45K body content)
- Deployed content: 68,245 chars raw / 68,917 rendered
- HTTP 200, status: draft, password_protected: true

## Verification Checks (All Passed)

- wp:html block present
- Google Fonts link present
- Style block present
- Report header / DuckDive content / Score 70 present
- Upsell section / Footer present
- Dark bg override (#0a0e1a) present
- pb-report-825 wrapper present

## Files

- Source: `/home/jared/projects/AI-CIV/aether/exports/client-marketing/report-template.html`
- WordPress: `https://purebrain.ai` page 825
- Auth: `('Aether', PUREBRAIN_WP_APP_PASSWORD)` from `.env`
