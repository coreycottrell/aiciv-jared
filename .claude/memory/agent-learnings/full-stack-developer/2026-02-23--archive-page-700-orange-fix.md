# Archive Page 700: Orange Fix (wpautop Bypass)

**Date**: 2026-02-23
**Type**: teaching
**Topic**: Page 700 (Neural Feed Memories archive) all-orange due to missing wp:html wrapper

---

## What Happened

Page 700 (https://purebrain.ai/blog-neural-feed-memories/) was created by plugin v4.0.0 with raw
HTML/CSS content but WITHOUT the `<!-- wp:html -->` Gutenberg block wrapper. WordPress wpautop
filter immediately corrupted the `<style>` block by injecting `</p>` tags inside CSS rules,
causing the entire page to fall back to WordPress default orange styling.

## Root Cause

Same pattern as page 620 (ai-partnership-audit). Any self-contained HTML page deployed to
WordPress via REST API WITHOUT the `<!-- wp:html -->` wrapper gets corrupted by wpautop.

**Evidence in rendered content**:
```html
<p>/* === RESET & BASE === */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }</p>
```
Paragraph tags injected inside CSS blocks = broken stylesheet = orange page.

## Fix (Applied 2026-02-23)

```python
# 1. Fetch raw content
raw = fetch_page_raw(700)  # 12,673 chars

# 2. Wrap in wp:html block
fixed = '<!-- wp:html -->\n' + raw.strip() + '\n<!-- /wp:html -->'

# 3. Deploy
POST /wp-json/wp/v2/pages/700 with {"content": fixed, "status": "publish"}

# 4. Clear Elementor cache
DELETE /wp-json/elementor/v1/cache
```

## Verification (All Passing)

- wpautop injection: False
- Dark background (#080a12) present: True
- nfm-page wrapper div present: True
- JS loadPosts function present: True
- PureBrain orange (#f1420b) in CSS: True (only on CTAs/buttons - correct)

## PERMANENT RULE FOR ALL WORDPRESS HTML PAGE DEPLOYMENTS

**EVERY page that contains inline `<style>` blocks deployed via REST API MUST use `<!-- wp:html -->` wrapper.**

This applies to: page 700, page 620, any future self-contained HTML pages.

```python
def ensure_wp_html_wrapped(content):
    content = content.strip()
    if not content.startswith('<!-- wp:html -->'):
        content = '<!-- wp:html -->\n' + content + '\n<!-- /wp:html -->'
    return content
```

Plugin v4.0.0 must be updated to include this wrapper when creating the archive page.

## Page Context

- Page ID: 700
- URL: https://purebrain.ai/blog-neural-feed-memories/
- Template: elementor_canvas
- Purpose: Full archive grid of all blog posts with dynamic JS loading
- Created by: Plugin v4.0.0 (2026-02-23)
