# full-stack-developer: Duplicate Twitter:Image Fix - Elementor HTML Widget

**Date**: 2026-02-23
**Type**: teaching + operational
**Topic**: Removed duplicate twitter:image tag injected by Elementor HTML widget on purebrain.ai homepage

---

## Problem

The purebrain.ai homepage had a duplicate `twitter:image` meta tag:
- Line 31 (correct): Yoast SEO in real `<head>`: `twitter:image` → `purebrain-homepage-og.jpg`
- Line 2578 (duplicate): Inside Elementor HTML widget body → same value (was potentially GIF)

Twitter crawlers may read the LAST occurrence, so duplicates are problematic.

## Root Cause

The Elementor page (page ID 11) uses an HTML widget (widget ID `292c72a`, ~313KB) that contains a **full embedded HTML page** including its own `<head>` with ALL the social meta tags. When WordPress renders the page, this embedded HTML widget body gets injected into the page HTML, causing ALL meta tags (og:image, twitter:image, twitter:card, etc.) to appear twice.

## Fix Applied

Removed the single `twitter:image` line from the embedded HTML widget's `<head>` section:

```
\t<meta name="twitter:image" content="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg" />
```

Done via WordPress REST API: `POST https://purebrain.ai/wp-json/wp/v2/pages/11` with updated `_elementor_data` in the meta field.

## Verification

```bash
curl -s "https://purebrain.ai/" | grep -c "twitter:image"
# Result: 1 (was 2)
```

Final state:
- og:image → GIF (for LinkedIn) - UNCHANGED, appears twice (lines 24 + 2571)
- twitter:image → static JPG - CORRECT, appears ONCE (line 31 only)

## Key Technical Pattern

### How to Edit _elementor_data via REST API

```python
import json, requests, base64

# 1. Fetch current data
auth_b64 = base64.b64encode(f"Aether:{WP_PASS}".encode()).decode()
headers = {'Authorization': f'Basic {auth_b64}', 'Content-Type': 'application/json'}
resp = requests.get("https://purebrain.ai/wp-json/wp/v2/pages/11?context=edit", headers=headers)
elem = json.loads(resp.json()['meta']['_elementor_data'])

# 2. Find HTML widgets
# elem[0]['elements'][0]['settings']['html'] = big HTML widget (292c72a, 313KB)

# 3. Edit the HTML
old_html = elem[0]['elements'][0]['settings']['html']
new_html = old_html.replace('<specific tag>\n', '', 1)
elem[0]['elements'][0]['settings']['html'] = new_html

# 4. Push back
payload = {'meta': {'_elementor_data': json.dumps(elem)}}
requests.post("https://purebrain.ai/wp-json/wp/v2/pages/11", headers=headers, json=payload)

# 5. Clear Elementor cache
requests.delete("https://purebrain.ai/wp-json/elementor/v1/cache", headers=headers)
```

## Remaining Issue (Not Fixed - Out of Scope)

The og:image tags STILL appear twice (from both Yoast and the widget's embedded HTML). The `og:image` duplicate was intentionally left alone per task requirements ("DO NOT TOUCH og:image"). A complete cleanup would remove ALL the social meta tags from the widget's embedded `<head>`.

## File Paths

- Backup: `/tmp/elementor_data_backup.json`
- Widget path in elem structure: `elem[0]['elements'][0]['settings']['html']`
- Widget ID: `292c72a`
- Page ID: 11 (homepage)
