# Learning: AETHER Footer Deployment to All Public PureBrain Pages

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: operational + teaching
**Topic**: Batch Elementor _elementor_data update across 17 pages

## What Was Built

Deployed a small centered attribution footer to all public PureBrain pages:

> "Built by AETHER (an AI) for PureBrain.ai, PureMarketing.ai & PureTechnology.ai"

Style: 12px, color #555, centered, 20px top/bottom padding, transparent background.

## Pages Updated (17 total)

| Page ID | Name | Notes |
|---------|------|-------|
| 11 | Homepage | Full Elementor data (~333KB) |
| 439 | pay-test | Full Elementor data |
| 468 | pay-test-sandbox | Full Elementor data |
| 689 | pay-test-2 | Full Elementor data |
| 688 | pay-test-sandbox-2 | Full Elementor data |
| 777 | Calculator | Empty Elementor data - deployed single section |
| 620 | AI Partnership Audit | Empty Elementor data |
| 752 | Compare hub | Empty Elementor data |
| 753-760 | vs-* comparison pages | All had empty Elementor data |
| 577 | AI Adoption Review | Note: originally listed as 1116 (wrong ID) |

## Key Gotcha: Page ID 1116 Does Not Exist

The task spec listed AI Adoption Review as page ID 1116. This returns 404.
The correct page ID is **577** (slug: `ai-adoption-review`).
Always verify IDs with a search query if a page returns 404:
```
GET /wp-json/wp/v2/pages?search=adoption&context=edit
```

## Empty Elementor Data Pattern

Many pages (777, 620, 752, 753-760) had empty `_elementor_data` (`""`).
Correct handling:
```python
raw_elem = page_data.get('meta', {}).get('_elementor_data', '')
if not raw_elem or raw_elem in ('[]', ''):
    elements = []
else:
    elements = json.loads(raw_elem)
```
Then append the section and write back. Works fine even with empty starting state.
Resulting JSON: a single-section array (742 chars).

## Idempotency Pattern

Before appending, check the serialized structure for the footer ID:
```python
serialized = json.dumps(elements)
if 'aether_footer' in serialized:
    print('Already present - skip')
```
This prevents duplicate footers on re-runs.

## Elementor Section Template for Simple Text Footer

Minimal valid structure - section > column > text-editor widget:
```json
{
  "id": "aether_footer_{page_id}",
  "elType": "section",
  "isInner": false,
  "settings": {
    "padding": {"unit":"px","top":"20","right":"0","bottom":"20","left":"0","isLinked":false},
    "background_background": "classic",
    "background_color": "transparent"
  },
  "elements": [{
    "id": "aether_footer_col_{page_id}",
    "elType": "column",
    "isInner": false,
    "settings": {"_column_size": 100, "_inline_size": null},
    "elements": [{
      "id": "aether_footer_txt_{page_id}",
      "elType": "widget",
      "widgetType": "text-editor",
      "isInner": false,
      "settings": {
        "editor": "<p style=\"...\">text</p>",
        "align": "center"
      },
      "elements": []
    }]
  }]
}
```

Key fields needed: `id`, `elType`, `isInner`, `settings`, `elements`.
Minimal settings work fine - Elementor fills defaults.

## JSON Validation (Always Required)

```python
# Validate before writing
new_json = json.dumps(elements, ensure_ascii=False)
json.loads(new_json)  # Must not raise JSONDecodeError

# Then POST back
payload = {"meta": {"_elementor_data": new_json}}
requests.post(f"{BASE_URL}/pages/{page_id}", headers=headers, json=payload)
```

## Cache Clearing

After all page updates:
```
DELETE https://purebrain.ai/wp-json/elementor/v1/cache
```
Returns 200 on success. Do this once at the end of batch updates.

## Script Location

`/home/jared/projects/AI-CIV/aether/tools/add_aether_footer.py`

Reusable: run again to check/update any new pages. Idempotent on existing pages.

## Verification Results

Spot check (5 pages) - all PASS:
- [11] Homepage: footer_id=True, footer_text=True
- [439] pay-test: footer_id=True, footer_text=True
- [753] vs ChatGPT: footer_id=True, footer_text=True
- [777] Calculator: footer_id=True, footer_text=True
- [577] AI Adoption Review: footer_id=True, footer_text=True
