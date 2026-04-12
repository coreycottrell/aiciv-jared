# full-stack-developer: Duplicate twitter:image Meta Tag Fix

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: Fixed duplicate twitter:image tag on purebrain.ai homepage - stale GIF reference in Elementor HTML widget

---

## Problem

purebrain.ai homepage had TWO `twitter:image` meta tags:
1. Line 31 (in `<head>`): `purebrain-homepage-og.jpg` (correct JPG - from Yoast SEO)
2. Line 2578 (in body): `Pure-Brain-Vid-3.gif` (stale GIF - from Elementor HTML widget)

The second tag was coming from an **Elementor HTML widget** (`data-id="292c72a"`) that contained a full `<!DOCTYPE html><html><head>...</head><body>...</body></html>` dump from 2026-02-17. This old full-page dump had stale Yoast SEO meta tags including the GIF twitter:image.

## Root Cause

The Elementor HTML widget (element ID `292c72a`) stored an entire HTML page (314,696 chars) as its content. This was an old page snapshot from 2026-02-17 that predated the twitter:image being set to the JPG. The widget contained:
- Full `<head>` with old Yoast v26.9 meta tags
- Full `<body>` with the actual page content
- stale `twitter:image` pointing to the GIF

## Fix Applied

Performed a targeted string replacement in `_elementor_data` for page ID 11:

```python
old_str = 'name=\\"twitter:image\\" content=\\"https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif\\"'
new_str = 'name=\\"twitter:image\\" content=\\"https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg\\"'

new_elem_data = elem_data_str.replace(old_str, new_str, 1)

# Push via WP REST API
requests.post(
    'https://purebrain.ai/wp-json/wp/v2/pages/11',
    auth=('Aether', 'APP_PASSWORD'),
    json={'meta': {'_elementor_data': new_elem_data}},
    timeout=60
)
```

**Critical**: The `_elementor_data` is a JSON string stored as a meta value. Inside that string, HTML attribute values are escaped as `\\"` (backslash + double-quote), NOT as standard HTML entities. The replacement must use Python's `\\` escaping to match.

## What Was NOT Changed

- `og:image` tags (both still point to GIF for LinkedIn - per Jared's explicit instruction)
- `og:image:width`, `og:image:height`, `og:image:type` tags
- Any other meta tags

## Verification Result

```
twitter:image tags: 2 total
  - Both now point to: purebrain-homepage-og.jpg (JPG)
  - GIF twitter:image count: 0 ✓

og:image tags: 2 total
  - Both still point to: Pure-Brain-Vid-3.gif (GIF) ✓ (LinkedIn keeps working)
```

## Key Lessons

1. **Elementor HTML widgets can contain full page HTML dumps** - when you see duplicate meta tags in the page body, check for an `elementor-widget-html` widget with data-id
2. **Elementor widget HTML uses JSON string escaping** (`\\"`) inside `_elementor_data` - not HTML entity encoding
3. **Cache clears**: After updating `_elementor_data`, touching the post status to "publish" triggers a regeneration (5 second delay may be needed)
4. **CRITICAL RULE**: When told "DO NOT TOUCH og:image", be surgical - only replace `twitter:image` occurrences, not `og:image` ones
5. **elementor_data strings are nested JSON** - the HTML content is JSON-stringified, so you're working with escaped-escaped content

## Elementor Widget Identification

```bash
# Find the widget via HTML
curl -s "https://DOMAIN/" | grep -B5 -A5 "duplicate-meta-content"

# Or via Elementor data
python3 -c "
import json
elem = json.loads(open('elem_data.json').read())
def find_html_widgets(elements):
    for el in elements:
        if el.get('widgetType') == 'html.default':
            html = el.get('settings', {}).get('html', '')
            if 'your-pattern' in html:
                print(f'Widget ID: {el[\"id\"]}')
        for child in el.get('elements', []):
            find_html_widgets([child])
find_html_widgets(elem)
"
```

---

**End of Memory**
