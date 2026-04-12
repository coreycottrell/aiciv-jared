# Memory: Assessment Page Orange Fix - Final Resolution

**Date**: 2026-02-20
**Type**: teaching
**Topic**: Fixing orange assessment page - root cause was nested DOCTYPE, clean Elementor widget solution

---

## Problem Statement

Page 577 (https://purebrain.ai/ai-adoption-review/) showing orange/broken state. Previous fix attempt used Elementor HTML widget but still showing orange per Jared.

## Root Cause Analysis

The previous Elementor HTML widget fix placed the FULL HTML document (including `<!DOCTYPE html>`, `<html>`, `<head>`, `<style>`, `<body>`) inside the widget. When Elementor renders the HTML widget, this creates a nested document structure in the final page HTML:

```html
<div class="elementor-widget-html">
  <!DOCTYPE html>          ← NESTED DOCTYPE (causes issues)
  <html lang="en">
  <head>
    <style>...</style>     ← CSS ends up in BODY context
  </head>
  <body>
    <!-- actual content -->
  </body>
  </html>
</div>
```

This caused:
1. Nested DOCTYPE (invalid HTML, browser behavior unpredictable)
2. `<style>` in body context (CSS may not apply correctly in all browsers)
3. `@import` in body-level `<style>` (non-standard, may fail for fonts)
4. Nested `<body>` tag (invalid, browser ignores it)

## The Fix

**Two-step approach:**

### Step 1: Content.raw fallback (intermediate)
Set `_elementor_edit_mode: ""` and put full HTML in `content.raw` with `<!-- wp:html -->` wrapper. This bypassed Elementor but still had nested DOCTYPE issue since the HTML was a full document.

### Step 2: Clean Elementor HTML widget (final - CORRECT)
Extracted ONLY the `<style>`, `<script>` from `<head>` and the body content, then rebuilt the Elementor widget with clean HTML (no document wrapper):

```python
# Extract components
head_content = html_between_head_tags
body_content = html_between_body_tags

style_blocks = re.findall(r'<style[^>]*>.*?</style>', head_content, re.DOTALL)
script_blocks_head = re.findall(r'<script[^>]*>.*?</script>', head_content, re.DOTALL)

# Build clean HTML (NO DOCTYPE/html/head/body wrappers)
clean_html = '\n'.join(style_blocks + script_blocks_head + [body_content])

# Deploy as Elementor HTML widget
elementor_data = [{
    "id": "a1b2c3d4",
    "elType": "section",
    ...
    "elements": [{
        "id": "e5f6g7h8",
        "elType": "column",
        "settings": {"_column_size": 100},
        "elements": [{
            "id": "i9j0k1l2",
            "elType": "widget",
            "widgetType": "html",
            "settings": {"html": clean_html},
            "elements": []
        }]
    }]
}]
```

## Verification Results

All 14 checks passed:
- elementor-template-canvas (full-width)
- elementor-widget-html (clean rendering)
- No nested DOCTYPE (only 1 in page)
- #080a12 dark background
- Assessment content (wrapper, hero, CTA, JS)
- No orange error color
- Brevo integration

## Key Lessons

1. **Always strip document wrapper from Elementor HTML widgets** - Only put `<style>`, `<script>`, and body content in the widget. NOT `<!DOCTYPE>`, `<html>`, `<head>`, `<body>`.

2. **CDN cache complication** - GoDaddy/Cloudflare may cache old versions for up to 31 days (`max-age=2678400`). If a deploy doesn't show, check `cf-cache-status` header. Fresh deploys update the cache when Cloudflare revalidates.

3. **Content.raw with wp:html** - This approach works but places the entire HTML in the body context (after WP's body tag). The `<!-- wp:html -->` wrapper prevents wpautop from mangling content. But still has nested document structure issue.

4. **`_elementor_edit_mode: ''`** (empty string) disables Elementor builder mode, causing WP to render `content.raw` directly. This IS a valid approach for pages where you don't need Elementor.

5. **Template: elementor_canvas** - Keeps full-width rendering without theme header/footer regardless of whether `_elementor_edit_mode` is set.

## Final State

- WordPress DB: Elementor HTML widget with clean HTML (52377 chars)
- Template: elementor_canvas (full-width)
- `_elementor_edit_mode: builder`
- `_elementor_data`: valid JSON with 1 section → 1 column → 1 HTML widget
- Live HTML: 162159 bytes, 1 DOCTYPE, dark theme, assessment functional
- Cloudflare cache: HIT with last-modified 2026-02-20T16:36:35

## Reference Files

- Live URL: https://purebrain.ai/ai-adoption-review/
- WP Page ID: 577
- Assessment HTML source: /home/jared/projects/AI-CIV/aether/to-jared/ai-adoption-assessment-deployed.html
