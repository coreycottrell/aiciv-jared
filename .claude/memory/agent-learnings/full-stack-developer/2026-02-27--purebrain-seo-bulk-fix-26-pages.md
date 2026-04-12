# PureBrain SEO Bulk Fix — 26 Pages

**Date**: 2026-02-27
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: WordPress REST API Yoast SEO bulk update — OG tags, excerpts, featured images

---

## What Was Done

Bulk-updated SEO on 26 key public pages on purebrain.ai via the WordPress REST API:
- Yoast SEO title + meta description
- OG title, OG description, OG image, OG image ID
- Twitter title, description, image, image ID (mirrors OG)
- featured_media (for pages missing it)
- excerpt

All 26 pages verified PASS via REST API read-back.

---

## Critical Gotcha: Yoast Image IDs Must Be Strings

**The most important learning from this session.**

When setting Yoast OG/Twitter image ID fields via the REST API, WordPress returns HTTP 400 with:
```
meta._yoast_wpseo_opengraph-image-id is not of type string.
```

**Wrong:**
```python
meta['_yoast_wpseo_opengraph-image-id'] = 694  # int — causes 400
```

**Correct:**
```python
meta['_yoast_wpseo_opengraph-image-id'] = '694'  # string — works
meta['_yoast_wpseo_twitter-image-id'] = '694'
```

This applies to ALL Yoast image ID meta fields. Despite being integer IDs internally, the REST API schema expects them as strings.

---

## Yoast Meta Field Names (REST API)

```
_yoast_wpseo_title              -> SEO title
_yoast_wpseo_metadesc           -> Meta description
_yoast_wpseo_opengraph-title    -> OG title
_yoast_wpseo_opengraph-description -> OG desc
_yoast_wpseo_opengraph-image    -> OG image URL
_yoast_wpseo_opengraph-image-id -> OG image ID (STRING not int)
_yoast_wpseo_twitter-title      -> Twitter title
_yoast_wpseo_twitter-description -> Twitter desc
_yoast_wpseo_twitter-image      -> Twitter image URL
_yoast_wpseo_twitter-image-id   -> Twitter image ID (STRING not int)
```

---

## Excerpt Verification Gotcha

Password-protected pages show empty `excerpt.rendered` in public context, but the excerpt IS set. Use `?context=edit` to see the `raw` field:
```python
r = requests.get(f'{BASE}/pages/{pid}?context=edit', auth=AUTH)
exc = r.json()['excerpt']['raw']  # always correct
```

---

## Pages Updated

| ID  | Key Change |
|-----|-----------|
| 11  | excerpt added |
| 319 | full SEO + featured_media=694 |
| 777 | OG/Twitter + excerpt |
| 752-760 | OG/Twitter + excerpt (9 comparison pages) |
| 284 | SEO title + OG + excerpt |
| 577,731,794,923,929 | OG title/desc + excerpt |
| 405 | SEO title + OG + excerpt |
| 620,800,816 | featured_media=694 + OG + excerpt |
| 700,860 | OG + excerpt |
| 970 | SEO title/metadesc + OG + featured_media + excerpt |
| 987 | full SEO with media 997 (amplify-founder image) |

---

## Files

- `/home/jared/projects/AI-CIV/aether/tools/purebrain_seo_fix.py` — main update script
- `/home/jared/projects/AI-CIV/aether/tools/verify_seo.py` — verification script
- `/home/jared/projects/AI-CIV/aether/exports/seo-audit-fixes.md` — final report

---

## Pattern for Future Bulk SEO Updates

```python
# Build payload — never touch page content
payload = {}
meta = {}

if 'featured_media' in cfg:
    payload['featured_media'] = cfg['featured_media']
if 'excerpt' in cfg:
    payload['excerpt'] = cfg['excerpt']
if 'og_title' in cfg:
    meta['_yoast_wpseo_opengraph-title'] = cfg['og_title']
    meta['_yoast_wpseo_twitter-title'] = cfg['og_title']
if 'og_image_id' in cfg:
    meta['_yoast_wpseo_opengraph-image-id'] = str(cfg['og_image_id'])  # MUST be string
    meta['_yoast_wpseo_twitter-image-id'] = str(cfg['og_image_id'])

if meta:
    payload['meta'] = meta

requests.put(f'{BASE}/pages/{pid}', auth=AUTH, json=payload)
```
