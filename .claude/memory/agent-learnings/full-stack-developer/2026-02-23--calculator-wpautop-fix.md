# Calculator wpautop Fix - 2026-02-23

**Agent**: full-stack-developer
**Type**: teaching
**Topic**: WordPress wpautop breaking custom HTML/CSS/JS pages

## Problem

AI Tool Stack Calculator (page 777, https://purebrain.ai/ai-tool-stack-calculator/) broke after adding "Website / Page Builders" category.

Root cause: The page content had NO `<!-- wp:html -->` Gutenberg block wrapper. WordPress was running `wpautop` (auto paragraph formatter) on the raw content, injecting `<p>` tags into the `<style>` block - **150 `<p>` tags** were injected inside the CSS. This silently broke all CSS and JavaScript.

The new category was added to the content, triggering a save, and the lack of `<!-- wp:html -->` protection was always there but just now became obvious.

## Detection Pattern

```bash
# Check for wpautop injection in live page
curl -s https://purebrain.ai/PAGE-SLUG/ > /tmp/check.html

python3 << 'EOF'
import re
with open('/tmp/check.html') as f: content = f.read()
style_blocks = re.findall(r'<style[^>]*>.*?</style>', content, re.DOTALL)
calc_style = [b for b in style_blocks if 'IDENTIFIER_KEYWORD' in b]
print(f'P tags in style: {calc_style[0].count("<p>")}')
EOF
```

If count > 0: wpautop is mangling the content.

## Fix

Wrap ALL content in `<!-- wp:html -->` / `<!-- /wp:html -->` Gutenberg block markers.

```python
# The correct WP content format:
wp_content = f'<!-- wp:html -->\n{body_content}\n<!-- /wp:html -->'

# Deploy via REST API:
requests.post(
    'https://purebrain.ai/wp-json/wp/v2/pages/PAGE_ID',
    auth=(wp_user, wp_pass),
    json={'content': wp_content, 'status': 'publish'}
)
```

**Important**: The `<!-- wp:html -->` wrapper appears in WP's RAW content but is stripped from the rendered HTML. That is correct behavior. Only check for it via `?context=edit` API endpoint.

## Rule

Any page deployed with raw `<style>` or `<script>` blocks directly in the WP content field MUST use `<!-- wp:html -->` wrapper or wpautop will destroy the content.

This applies to: ai-tool-stack-calculator, audit page, assessment page, any custom HTML page.

## Files

- Local source: `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`
- WP Page ID: 777
- WP Site: purebrain.ai
