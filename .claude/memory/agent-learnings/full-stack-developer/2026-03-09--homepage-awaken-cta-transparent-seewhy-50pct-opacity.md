# Homepage: Awaken CTA Transparent + See Why 50% Opacity

**Date**: 2026-03-09
**Type**: operational
**Agent**: full-stack-developer

## Task

Fix two section backgrounds on homepage (page 11) per Jared's annotation:
1. `pb-awaken-cta-section` → transparent (was `#080a12`)
2. `why_pb_688` "See Why PureBrain Is Different" → `rgba(8, 10, 18, 0.5)` (was `#0d1117`)

## Solution

Modified `_elementor_data` for page 11 via REST API. Three string replacements:

### Change 1: pb-awaken-cta-section transparent
- Old: `"background_background": "classic", "background_color": "#080a12"`
- New: `"background_background": "", "background_color": ""`
- Elementor treats empty string as no background → transparent

### Change 2a: why_pb_688 section-level background
- Old: `"background_background": "classic", "background_color": "#0d1117"`
- New: `"background_background": "classic", "background_color": "rgba(8, 10, 18, 0.5)"`

### Change 2b: why_pb_688 inline HTML div background
- The HTML widget inside why_pb_688 had: `background:linear-gradient(135deg,#0d1117 0%,#111827 100%)`
- Changed to: `background:rgba(8,10,18,0.5)`
- Both the section-level AND the HTML widget div needed updating for full visual effect

## Verification

Confirmed in Elementor-generated CSS file (`/wp-content/uploads/elementor/css/post-11.css?nocache=1`):
- `pb-awaken-cta-section`: only `padding:0px 0px 0px 0px` — no background-color (transparent)
- `why_pb_688`: `background-color:rgba(8, 10, 18, 0.5)` in motion-effects-layer selector
- Rendered HTML at position 581217 confirmed rgba(8,10,18,0.5) in inline div

## Key Pattern: Two Places Need Updating

When a section has `background_background: classic` + an HTML widget that also sets its own inline background:
- You must update BOTH the section settings AND the inline HTML
- Otherwise the section's Elementor CSS sets bg to new value, but the HTML div inside paints over it

## API Workflow

```bash
# 1. GET _elementor_data
curl "https://purebrain.ai/wp-json/wp/v2/pages/11?context=edit" -H "Authorization: Basic ..."

# 2. Modify via Python string replace

# 3. POST back
requests.post("https://purebrain.ai/wp-json/wp/v2/pages/11", auth=auth,
    json={"meta": {"_elementor_data": updated_ed}})

# 4. Clear cache
requests.delete("https://purebrain.ai/wp-json/elementor/v1/cache", auth=auth)
```

## Verification URL

`https://purebrain.ai/wp-content/uploads/elementor/css/post-11.css?nocache=1` — shows Elementor's compiled CSS per section ID
