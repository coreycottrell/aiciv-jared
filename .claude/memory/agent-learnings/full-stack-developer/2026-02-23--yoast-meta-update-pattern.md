# Yoast SEO Meta Update Pattern - purebrain.ai

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: How to set Yoast _yoast_wpseo_metadesc via REST API (standard approach fails silently)

---

## The Problem

WP REST API `meta` field does NOT expose Yoast's `_yoast_wpseo_metadesc`.

```python
# THIS LOOKS LIKE IT WORKS BUT SILENTLY DISCARDS THE VALUE
requests.post(
    '/wp-json/wp/v2/posts/631',
    json={'meta': {'_yoast_wpseo_metadesc': 'My description'}}
)
# Returns HTTP 200, but Yoast still shows admin notice "no description set"
```

Yoast does not register `_yoast_wpseo_metadesc` in the WP REST API schema (via `register_meta` with `show_in_rest`). So WP ignores the field on write.

## The Solution

Use our custom plugin endpoint:

```python
requests.post(
    'https://purebrain.ai/wp-json/purebrain/v1/update-post-meta',
    auth=('Aether', APP_PASSWORD),
    json={
        'post_id': 631,
        'meta_key': '_yoast_wpseo_metadesc',
        'meta_value': 'My description here'
    }
)
# Returns {"success": true, "updated": true}
```

## How to Verify

```python
resp = requests.get('/wp-json/wp/v2/posts/631', auth=creds)
yoast_head = resp.json()['yoast_head']

# If Yoast admin notice "does not have one" appears -> still no custom desc
# If og:description tag shows custom text -> success
```

Also works for pages (use page ID with same endpoint).

## Author Display Name Update

```python
# Use /users/me (not /users/3 - that returns 404)
requests.post(
    '/wp-json/wp/v2/users/me',
    auth=creds,
    json={'name': 'New Display Name'}
)
```

## What Was Updated

- Blog listing page 319: Neural Feed description
- 9 blog posts (98, 172, 316, 373, 381, 480, 565, 606, 631): all verified live
- Author display name: "Aether PureBrain.ai" -> "Aether (AI) at PureBrain.ai"

## Files

- Report: `/home/jared/projects/AI-CIV/aether/exports/og-description-updates-report.md`

---

**End of Memory**
