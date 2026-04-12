# pay-test DOMContentLoaded Fix - Complete Implementation & Cache Lessons

**Date**: 2026-02-18
**Type**: teaching + gotcha
**Topic**: WordPress/Elementor cache pipeline and how to deploy JS fixes correctly

---

## What Was Fixed

Applied DOMContentLoaded wrapper to the main chat script on purebrain.ai/pay-test/ (Page ID 439).

Root cause: `const chatMessages = document.getElementById('chatMessages')` captured `null` at script parse time because the script ran before DOM was ready. The fix wrapped the entire 56,568-char script in `document.addEventListener('DOMContentLoaded', function() { ... });`

Script identifier: `// IMMERSIVE FLOWING BACKGROUND SYSTEM`

---

## Files

- Fix script: `/home/jared/projects/AI-CIV/aether/tools/fix_paytest_domcontentloaded.py`
- REST API: `https://purebrain.ai/wp-json/wp/v2/pages/439?context=edit`
- WordPress credentials: Aether / FlFr2VOtlHiHaJWjzW96OHUJ (or use PUREBRAIN_WP_APP_PASSWORD from .env)

---

## Critical Discovery: WordPress + Elementor Cache Pipeline

**The pipeline has 3 layers that must ALL be cleared:**

```
WordPress DB (_elementor_data)
    ↓ Elementor PHP renders → PHP object cache (APCu/Memcached)
    ↓ Elementor PHP → GoDaddy gateway cache
    ↓ GoDaddy origin → Cloudflare CDN cache
    ↓ Cloudflare → User's browser
```

### Layer 1: WordPress DB (_elementor_data)
- Update via REST API: `POST /wp-json/wp/v2/pages/{ID}` with `meta._elementor_data`
- ALSO update `content.raw` for redundancy (though Elementor ignores it during rendering)
- This layer: **Easy to update, always works**

### Layer 2: Elementor PHP cache (most critical)
- Elementor caches rendered HTML internally using WordPress object cache
- Even when DB is updated, PHP serves cached version
- **The key endpoint**: `DELETE /wp-json/elementor/v1/cache` (HTTP 200 = success)
- This MUST be called after updating _elementor_data or changes won't render

### Layer 3: GoDaddy gateway cache
- x-gateway-cache-status header shows MISS/HIT/BYPASS
- Auto-clears when Elementor cache is cleared
- Headers: `x-gateway-cache-key`, `x-gateway-cache-status`

### Layer 4: Cloudflare CDN
- CF-Cache-Status: HIT/MISS/DYNAMIC headers
- max-age is 2,678,400 seconds (31 days!) for WordPress pages
- Cloudflare re-fetches from origin on next request after cache expires OR when content changes
- **Trick to force CF re-fetch**: Update page via REST API (`POST /wp-json/wp/v2/pages/{ID}` with any change) + delete Elementor cache → then wait for CF to make a fresh request
- CF propagates new cached version after first MISS returns new content

---

## Correct Deployment Sequence

```python
# Step 1: Update _elementor_data in WordPress DB
requests.post(f'{WP_BASE}/wp-json/wp/v2/pages/{PAGE_ID}',
    auth=(WP_USER, WP_PASS),
    json={'meta': {'_elementor_data': new_elementor_json}})

# Step 2: CRITICAL - delete Elementor's PHP cache
requests.delete(f'{WP_BASE}/wp-json/elementor/v1/cache', auth=(WP_USER, WP_PASS))

# Step 3: Touch page to update modified timestamp (helps CF re-fetch)
requests.post(f'{WP_BASE}/wp-json/wp/v2/pages/{PAGE_ID}',
    auth=(WP_USER, WP_PASS),
    json={'status': 'publish'})

# Step 4: Wait ~10 seconds, then verify with cache-bypassed request
time.sleep(10)
# Verify: fetch live page, check CF-Cache-Status header
```

---

## What Doesn't Work for Cache Clearing

- `DELETE /elementor/v1/clear-cache` - 404 (wrong route)
- Touching `meta._elementor_css` - triggers regeneration but of CSS only, not HTML
- `X-Cache-Bypass: 1` headers - Cloudflare ignores these
- HTTP PURGE method - Cloudflare blocks it (400)
- GoDaddy-specific endpoints (`/wp-json/wpaas/v1/cache/purge`) - 404
- WP Super Cache / W3TC endpoints - 404 (not installed)
- `POST /wp-admin/admin-ajax.php` with action=elementor_clear_cache - needs cookie auth nonce

---

## Other Scripts Checked for Same Issue

Checked all 25 script tags in pay-test HTML widget for bare DOM captures:
- Script 23 (PayPal popup, 30,186 chars): Has bare captures BUT already wrapped in DOMContentLoaded - SAFE
- Script 25 (integration glue, 3,857 chars): Has bare captures BUT already wrapped in IIFE + DOMContentLoaded - SAFE
- Script 24 (post-payment chat flow, 42,879 chars): No DOMContentLoaded BUT no bare DOM captures at top level (exports functions to window) - SAFE

---

## Verification Command

```python
import requests
import re

resp = requests.get('https://purebrain.ai/pay-test/', timeout=20)
content = resp.text
sp = re.compile(r'<script([^>]*)>(.*?)</script>', re.DOTALL | re.IGNORECASE)
for m in sp.finditer(content):
    if 'IMMERSIVE FLOWING BACKGROUND SYSTEM' in m.group(2):
        body = m.group(2)
        has_dcl = 'DOMContentLoaded' in body
        print(f'{len(body):,} chars, DCL={has_dcl}')
        break
# Expected: 56,633 chars, DCL=True
```

---

**Tags**: purebrain, pay-test, DOMContentLoaded, elementor, wordpress, cache, fix, javascript
