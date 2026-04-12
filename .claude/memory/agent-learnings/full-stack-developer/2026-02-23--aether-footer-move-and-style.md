# Learning: Aether Footer Move & Style - Elementor Section Reordering

**Date**: 2026-02-23
**Type**: teaching
**Agent**: full-stack-developer
**Topic**: Moving Elementor sections above/below each other via REST API + JSON manipulation

---

## Task

Move the "Built by AETHER" footer widget from BELOW the main footer to ABOVE it, on 5 pages:
- Homepage (page 11)
- pay-test (page 439)
- pay-test-sandbox (page 468)
- pay-test-sandbox-2 (page 688)
- pay-test-2 (page 689)

Also upgrade styling from plain grey text to eye-catching branded design.

---

## How Elementor Section Reordering Works

`_elementor_data` is a JSON array of top-level sections. To reorder:

```python
import copy

parsed = json.loads(elem_data_str)  # Top-level list of sections

# Find indices
aether_idx = None
main_footer_idx = None
for i, section in enumerate(parsed):
    if section.get("id") == "aether_footer_11":
        aether_idx = i
    if section.get("id") == "fdf9e96":  # main footer
        main_footer_idx = i

# Remove aether section from current position
parsed_new = copy.deepcopy(parsed)
aether_section = parsed_new.pop(aether_idx)

# CRITICAL: Recalculate target index after pop
if aether_idx < main_footer_idx:
    insert_idx = main_footer_idx - 1  # compensate for removed element
else:
    insert_idx = main_footer_idx

# Insert BEFORE main footer
parsed_new.insert(insert_idx, aether_section)
```

Key: After `.pop(aether_idx)`, the target index shifts if `aether_idx < main_footer_idx`.

---

## Section ID Detection Pattern

To find the main footer section programmatically:

```python
for i, section in enumerate(parsed):
    for col in section.get("elements", []):
        for widget in col.get("elements", []):
            ws = widget.get("settings", {})
            html_content = ws.get("html", ws.get("editor", ""))
            if "footer__content" in html_content:
                main_footer_section_id = section.get("id")
```

---

## New Aether Footer Styling (Brand-Compliant)

```html
<div style="background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
     border-top: 2px solid #f1420b;
     border-bottom: 1px solid rgba(241,66,11,0.3);
     padding: 18px 24px; text-align: center;
     font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
  <p style="margin: 0 0 8px 0; font-size: 14px; color: #e2e8f0;">
    Built by <strong style="color: #f1420b; font-size: 16px; letter-spacing: 0.5px;">AETHER</strong> (an AI) for
    <a href="https://purebrain.ai" style="color: #2a93c1; text-decoration: none; font-weight: 600;">PureBrain.ai</a>, ...
  </p>
  <p style="margin: 0; font-size: 13px;">
    <a href="/why-purebrain/" style="color: #f1420b; text-decoration: none; font-weight: 600;">
      See Why PureBrain Is Different &#x2192;</a>
  </p>
</div>
```

Key design elements:
- Dark gradient background (#0d1117 → #111827)
- Orange top border (2px solid #f1420b)
- AETHER in bold orange, 16px
- .ai links in Pure Tech Blue (#2a93c1)
- "See Why" CTA in orange

---

## Verification Pattern

Always re-fetch from REST API and verify structure in WordPress database (not live site, which has CDN cache):

```python
resp = requests.get(f"{WP_URL}/wp-json/wp/v2/pages/{page_id}?context=edit", headers=headers)
parsed = json.loads(resp.json()["meta"]["_elementor_data"])
for i, section in enumerate(parsed):
    print(f"[{i}] {section.get('id')}")
```

Live site may show CDN-cached version - trust the database verification, not the live fetch.

---

## Pages Updated

All 5 pages: 11, 439, 468, 688, 689 - Aether footer now at index [3], main footer at [4].
