# WP HTML Block: Bypass wpautop for Self-Contained HTML Pages

**Date**: 2026-02-23
**Type**: teaching
**Topic**: Deploying full HTML pages to WordPress without wpautop destroying CSS

---

## Problem

When deploying a self-contained HTML page to WordPress via the REST API `content` field,
WordPress's `wpautop` filter automatically wraps newlines inside `<style>` blocks with `<p>` tags.

This turns valid CSS like:
```css
:root {
  --bg-primary: #0a0e1a;
}
```

Into broken garbage like:
```html
:root {</p>
<p>  --bg-primary: #0a0e1a;</p>
<p>}</p>
```

This completely destroys the stylesheet and makes the page look broken.

---

## Root Cause

WordPress `wpautop` runs on content rendered via the `content` field in the REST API.
It treats multi-line text blocks as paragraphs, which corrupts any CSS in `<style>` tags.

---

## The Fix: `<!-- wp:html -->` Block Wrapper

Wrap the entire HTML content in a Gutenberg raw HTML block:

```
<!-- wp:html -->
[your HTML here]
<!-- /wp:html -->
```

This tells WordPress to render the content as **raw HTML** without applying any text
filters including `wpautop`. The block editor recognizes this as a "Custom HTML" block.

---

## Deployment Pattern

```python
# Extract style tag + body content from source HTML
import re

with open('/path/to/source.html', 'r') as f:
    raw_html = f.read()

style_match = re.search(r'<style>(.*?)</style>', raw_html, re.DOTALL)
style_content = style_match.group(0) if style_match else ''

body_match = re.search(r'<body>(.*?)</body>', raw_html, re.DOTALL)
body_content = body_match.group(1) if body_match else ''

font_links = re.findall(r'<link[^>]+googleapis\.com[^>]+>', raw_html)
font_link_html = '\n'.join(font_links)

paypal_match = re.search(r'<script src="https://www\.paypal\.com/sdk[^"]*"[^>]*></script>', raw_html)
paypal_script = paypal_match.group(0) if paypal_match else ''

# Wrap in wp:html block - bypasses wpautop completely
complete_content = f"""<!-- wp:html -->
{font_link_html}
{paypal_script}
{style_content}
{body_content}
<!-- /wp:html -->"""

# Deploy via REST API
response = requests.post(
    'https://purebrain.ai/wp-json/wp/v2/pages/{PAGE_ID}',
    auth=(wp_user, wp_pass),
    json={
        'content': complete_content,
        'status': 'publish',
        'template': 'elementor_canvas'  # blank canvas, no header/footer
    }
)
```

---

## Key Points

1. **`<!-- wp:html -->` is the Gutenberg "Custom HTML" block** - completely raw
2. **Don't use Elementor HTML widget** for large self-contained HTML pages - it can truncate or mangle content
3. **`elementor_canvas` template still works** even when NOT using Elementor data - it provides a blank page template
4. **Clear Elementor cache after** with `DELETE /wp-json/elementor/v1/cache`
5. **Verify by checking** that CSS `</p>` tags are NOT present inside the `<style>` block in the rendered output

---

## Verification Command

```python
r = requests.get('https://purebrain.ai/page-slug/')
content = r.text
style_start = content.find('<style>')
style_end = content.find('</style>')
if '</p>' in content[style_start:style_end]:
    print("BROKEN: wpautop still running")
else:
    print("GOOD: CSS intact")
```

---

## Page Fixed

- **Page**: https://purebrain.ai/ai-website-analysis/
- **WordPress Page ID**: 816
- **Template**: elementor_canvas
- **Source file**: `/home/jared/projects/AI-CIV/aether/exports/client-marketing/website-analysis/index.html`
