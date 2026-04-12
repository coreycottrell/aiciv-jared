# Calculator Page Fix: Nested HTML Document Causing Orange Styling

**Date**: 2026-02-23
**Type**: teaching
**Topic**: WordPress wp:html block with full HTML document creates nested html tags - CSS body rules ignored

---

## Root Cause

When a self-contained HTML file (`<!DOCTYPE html><html><head>...<body>...</body></html>`) is wrapped
in `<!-- wp:html -->` and deployed to WordPress, the browser sees TWO `<html>` tags:
1. WordPress's outer `<html lang="en-US">`
2. The calculator's inner `<html lang="en">`

The browser strips the inner `<html>/<head>` structure. The inner `<style>` block ends up in the
body, but the CSS `body {}` and `:root` rules compete with WordPress theme styles that load earlier.
Since WordPress theme `body {}` rules are in `<head>` (higher in DOM order), they can win specificity
battles even when our CSS appears later — unless we use `!important`.

**Symptom**: Page appears "all orange" because WP theme's orange accent colors survive, while our
dark background (`#080a12`) gets overridden by the theme's lighter background.

---

## The Fix

### What NOT to do
- Do NOT store full `<!DOCTYPE html><html>...` files via wp:html block

### What TO do
1. **Strip the outer HTML wrapper** - extract only `<style>...</style>` + body content
2. **Add `!important` to body background** in the extracted style block
3. **Add `body.page` override** to target WordPress page context specifically:

```css
body {
  background: var(--pb-bg) !important;
  color: var(--pb-text) !important;
}
body.page {
  background: #080a12 !important;
  background-color: #080a12 !important;
  color: #e8edf3 !important;
}
```

4. **Use User-Agent header** when POSTing to WordPress REST API - Cloudflare blocks Python's
   default urllib user-agent with error 403/1010:
   ```python
   headers={'User-Agent': 'Mozilla/5.0 (compatible; Aether-AI/1.0)'}
   ```

---

## Verification Pattern

```python
# After deployment, verify:
html = fetch_live_page(url)
html_tag_count = len(re.findall(r'<html', html))
assert html_tag_count == 1, f"Nested HTML doc! Found {html_tag_count} <html> tags"
assert 'background: var(--pb-bg) !important' in html, "Missing !important on body bg"
assert 'body.page' in html, "Missing body.page WP override"
```

---

## Deployment

- Page: https://purebrain.ai/ai-tool-stack-calculator/
- Page ID: 777, template: elementor_canvas
- Source file: `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`
- Fixed: 2026-02-23
- After deploy: always run `DELETE /wp-json/elementor/v1/cache`

---

## Key Difference From wpautop Fix (2026-02-22)

- wpautop fix (page 620): CSS `</p>` injection inside `<style>` block → fix with wp:html wrapper
- This fix (page 777): Entire HTML doc with DOCTYPE inside wp:html → nested html tags →
  fix by extracting only style + body content, no DOCTYPE/html/head wrapper
- Both require `<!-- wp:html -->` wrapper, but the issue here is WHAT goes inside it
