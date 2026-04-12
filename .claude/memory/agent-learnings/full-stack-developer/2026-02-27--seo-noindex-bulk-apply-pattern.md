# SEO noindex Bulk Apply — purebrain.ai

**Date**: 2026-02-27
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: Setting noindex on internal/test pages + SEO meta for special pages via WP REST API

---

## What Was Done

Applied noindex to 16 pages on purebrain.ai. Applied SEO meta (OG title, desc, image) to 3 special pages.

---

## Key Patterns

### 1. noindex via Standard REST API (Pages)

`_yoast_wpseo_meta-robots-noindex` is registered with `show_in_rest => true` for pages only.
Use POST to `/wp-json/wp/v2/pages/{id}` with meta payload:

```bash
curl -X POST -u "Aether:PASS" \
  -H "Content-Type: application/json" \
  -d '{"meta":{"_yoast_wpseo_meta-robots-noindex":"1"}}' \
  "https://purebrain.ai/wp-json/wp/v2/pages/PAGE_ID"
```

### 2. noindex Value Semantics

- `"1"` = noindex (blocked)
- `""` (empty string) = default = `index` (allowed)
- Setting to `"0"` results in `""` being stored — Yoast normalizes this. Both mean "allow indexing"

**Don't be fooled by the REST response returning `""` after setting `"0"` — this IS correct.**

Verify actual state via Yoast API:
```bash
curl -s "https://purebrain.ai/wp-json/yoast/v1/get_head?url=ENCODED_URL" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('json',{}).get('robots',{}))"
```
Look for `{'index': 'noindex', ...}` vs `{'index': 'index', ...}`

### 3. OG Meta Fields Need Custom Plugin Endpoint

Standard REST API silently ignores most Yoast fields.
Use `/wp-json/purebrain/v1/update-post-meta` for:
- `_yoast_wpseo_title`
- `_yoast_wpseo_opengraph-title`
- `_yoast_wpseo_opengraph-description`
- `_yoast_wpseo_opengraph-image`
- `_yoast_wpseo_opengraph-image-id`
- `_yoast_wpseo_metadesc`

### 4. Excerpt via Standard REST API

```python
requests.post(f"{BASE_URL}/pages/{id}", auth=AUTH, json={"excerpt": "text here"})
```

Works normally via standard REST API.

---

## Pages Changed

### Newly Noindexed
- ID 963 /demo-no-bs/ — confirmed `noindex, follow` via Yoast API
- ID 532 /living-avatar/ — confirmed `noindex, follow` via Yoast API

### Legal Pages Restored to Indexed
- ID 3 /privacy-policy/ — now `index, follow`
- ID 541 /terms-of-service/ — now `index, follow`

### SEO Meta Applied
- ID 403 /ai-readiness-assessment/ — OG title, desc, image (media 694), meta desc, excerpt
- ID 3 /privacy-policy/ — SEO title, OG title, excerpt
- ID 541 /terms-of-service/ — SEO title, OG title, excerpt

---

## Media Notes

- Media 694 = `purebrain-homepage-og.jpg` = 1200x627 JPEG
- URL: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg`
- Used as OG image for AI Readiness Assessment page

---

## Files

- Script: `/home/jared/projects/AI-CIV/aether/tools/seo_noindex_apply.py`
- Report: `/home/jared/projects/AI-CIV/aether/exports/seo-noindex-report.md`

---

**End of Memory**
