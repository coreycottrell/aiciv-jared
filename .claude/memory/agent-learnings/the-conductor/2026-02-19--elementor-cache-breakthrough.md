# Elementor Cache Breakthrough - 2026-02-19

## The Discovery

Elementor has a REST API endpoint for cache clearing that we never knew about:

```
DELETE https://purebrain.ai/wp-json/elementor/v1/cache
Auth: Basic (Aether:PUREBRAIN_WP_APP_PASSWORD)
```

Returns HTTP 200 on success. This clears Elementor's PHP rendering cache.

## Why This Matters

Previously, when updating `_elementor_data` via the WordPress REST API, changes were saved to the database but NOT rendered on the live page. This was because Elementor caches its PHP-rendered HTML output separately from the database.

We thought the only fixes were:
1. Jared manually re-saving the page in Elementor editor
2. Jared clicking "Flush Cache" in wp-admin
3. Playwright automation to log into wp-admin

Now we can clear the cache programmatically after every REST API update.

## The Correct Update Pattern

When updating ANY Elementor page:

```python
import requests

auth = ("Aether", os.getenv("PUREBRAIN_WP_APP_PASSWORD"))

# 1. Update BOTH content.raw AND _elementor_data
requests.post(f"https://purebrain.ai/wp-json/wp/v2/pages/{PAGE_ID}",
    auth=auth,
    json={
        "content": new_content,
        "meta": {"_elementor_data": new_elem_data}
    })

# 2. ALWAYS clear Elementor cache after updating
requests.delete("https://purebrain.ai/wp-json/elementor/v1/cache", auth=auth)
```

## Critical Lesson: _elementor_data vs content.raw

Elementor renders from `_elementor_data`, NOT from `content.raw`. If you only update `content.raw`, the changes will NOT appear on the live page (Elementor ignores it).

You MUST update BOTH:
- `content.raw` (for non-Elementor fallback/search/raw access)
- `_elementor_data` (for what Elementor actually renders)

## Escaping in _elementor_data

The `_elementor_data` field stores content with specific escaping:
- Newlines are literal `\n` characters in the string (not escaped \\n)
- Double quotes are escaped as `\"`
- When reading from content.raw and injecting into _elementor_data:
  ```python
  escaped = new_text.replace('\n', '\\n').replace('"', '\\"')
  ```

## CDN Cache is Separate

Clearing Elementor cache does NOT clear CDN (Cloudflare/GoDaddy Varnish). However, in practice, the CDN seems to pick up changes after Elementor cache clear + cache-busting query param.

## Pages This Applies To

All Elementor pages on purebrain.ai:
- Homepage (11)
- PureBrain 2.0 (174)
- PureBrain 3.0 (338)
- PureBrain 4.0 (383)
- Pay-test (439)
- Pay-test-sandbox (468)
- Guide (405)
- Assessment (403)

Blog page (319) and individual blog posts are NOT Elementor pages.
