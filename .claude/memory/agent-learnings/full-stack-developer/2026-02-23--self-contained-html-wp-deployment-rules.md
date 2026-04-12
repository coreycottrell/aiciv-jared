# Self-Contained HTML Pages on WordPress — Deployment Rules

**Date**: 2026-02-23
**Type**: teaching
**Topic**: How to correctly deploy self-contained HTML pages to WordPress (the pattern + permanent rules)

---

## The Problem We Solved

`https://purebrain.ai/ai-website-analysis/` was "almost all orange" — all text and backgrounds turned orange.

### Root Cause

WordPress adds class `tt-magic-cursor` to the `<body>` element on the artistics theme.

The wp-custom-css (Additional CSS in WordPress Customizer) has this broad, unscoped selector:

```css
[class*="magic"] {
    color: #f1420b !important;
    fill: #f1420b !important;
    background-color: #f1420b !important;
    border-color: #f1420b !important;
}
```

Since `body` has class `tt-magic-cursor`, this selector matches the **entire body element** and applies orange to EVERYTHING. This affects any page on `elementor_canvas` template since it changes the body's background and text color.

---

## The Fix Pattern (MANDATORY FOR ALL SELF-CONTAINED HTML PAGES)

When deploying a self-contained HTML page to WordPress, the page's `<style>` block **MUST** include these overrides:

```css
/* Override WordPress [class*="magic"] selector that incorrectly matches
   body.tt-magic-cursor (class added by artistics theme).
   Specificity (0,1,1) > (0,1,0) so this wins even with !important. */
body {
  background: #YOUR_BG_COLOR !important;
  background-color: #YOUR_BG_COLOR !important;
  color: #YOUR_TEXT_COLOR !important;
  border-color: transparent !important;
}

/* Higher specificity override (0,1,1) beats [class*="magic"] (0,1,0) */
body.page-id-PAGEID,
body.tt-magic-cursor {
  background: #YOUR_BG_COLOR !important;
  background-color: #YOUR_BG_COLOR !important;
  color: #YOUR_TEXT_COLOR !important;
  border-color: transparent !important;
  fill: currentColor !important;
}
```

For the website analysis page specifically:
- BG color: `#0a0e1a` (dark navy)
- Text color: `#e8edf5` (light)

---

## Why This Works — CSS Cascade Rules

The `[class*="magic"]` selector has specificity `(0,1,0)`.
The `body.tt-magic-cursor` selector has specificity `(0,1,1)`.

For `!important` rules: **higher specificity wins**. So `body.tt-magic-cursor { ... !important }` definitively beats `[class*="magic"] { ... !important }`.

Additionally, our `<style>` is placed inside `<body>` (since it's in the `<!-- wp:html -->` block), which comes AFTER the `wp-custom-css` `<style>` in `<head>`. This provides extra cascade precedence.

---

## Plugin Fix (v4.7.1)

Also added to `purebrain-security-plugin.php` v4.7.1:

```php
// Runs on elementor_canvas pages only via wp_footer priority 1
body.tt-magic-cursor {
    color: initial;
    background-color: initial;
    border-color: initial;
}
```

This provides a baseline reset on canvas pages, though the page-specific !important rules are the primary fix.

---

## Complete Deployment Pattern

```python
# 1. Extract components from source HTML
font_links = re.findall(r'<link[^>]+googleapis\.com[^>]+>', raw_html)
paypal_script = re.search(r'<script src="https://www\.paypal\.com/sdk[^"]*"[^>]*></script>', raw_html)
style_block = re.search(r'<style>(.*?)</style>', raw_html, re.DOTALL).group(0)
body_content = re.search(r'<body>(.*?)</body>', raw_html, re.DOTALL).group(1)

# 2. ENSURE the style block has these anti-orange overrides (see above)
# 3. Wrap in wp:html block
content = f"""<!-- wp:html -->
{font_links}
{paypal_script}
{style_block}
{body_content}
<!-- /wp:html -->"""

# 4. Deploy via REST API
requests.post(
    'https://purebrain.ai/wp-json/wp/v2/pages/PAGE_ID',
    auth=('Aether', wp_pass),
    json={'content': content, 'status': 'publish', 'template': 'elementor_canvas'}
)

# 5. Clear Elementor cache
requests.delete('https://purebrain.ai/wp-json/elementor/v1/cache', auth=('Aether', wp_pass))

# 6. Verify: check for the body color override in live page
r = requests.get('https://purebrain.ai/PAGE-SLUG/')
assert 'background: #YOUR_BG_COLOR !important' in r.text
```

---

## What NOT To Do

1. **Do NOT just copy the HTML body without the style overrides** — the wp-custom-css will win.
2. **Do NOT use `body { color: #e8edf5 }` without `!important`** — `[class*="magic"]` uses `!important` and specificity matters within the `!important` layer.
3. **Do NOT assume `elementor_canvas` template protects you** — WordPress still loads ALL CSS including wp-custom-css on canvas pages.
4. **Do NOT use `<style>` in `<head>` extracted from source** — WordPress strips the `<html>`, `<head>`, and `<body>` tags, so your entire page content goes in `<body>`.

---

## Pages Using This Pattern

- `https://purebrain.ai/ai-website-analysis/` — WordPress Page ID 816
- `https://purebrain.ai/ai-partnership-audit/` — WordPress Page ID 620/1116
- Any future page deployed via `<!-- wp:html -->` on `elementor_canvas` template

---

## The Auto-Format Rule (Jared's Request)

**Going forward, whenever deploying a self-contained HTML page to WordPress:**

1. **Before deployment**: Check if the `body { }` rule in the `<style>` block has `!important` overrides for `background`, `background-color`, `color`, and `border-color`.
2. **Add the `body.page-id-X` and `body.tt-magic-cursor` selectors** with the same colors + `!important`.
3. **After deployment**: Verify by fetching the live page and checking that `background: #YOUR_COLOR !important` is present in the rendered HTML.

This prevents the "almost all orange" bug from recurring on ANY new page deployed to purebrain.ai.
