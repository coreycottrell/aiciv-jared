# Systems & Technology: Full Site SEO OG Image & Meta Description Audit + Fix
**Date**: 2026-03-03
**Type**: pattern + gotcha + data-state
**Topic**: Comprehensive SEO audit - Yoast OG image and meta description across all 78 pages/posts

---

## What Was Done

Full audit of purebrain.ai: 62 pages + 16 posts.
Fixed OG image on 14 pages, meta description on 16 blog posts + 10 pages.
Focus keywords set on 9 key blog posts.

---

## Key Findings

### Yoast Meta Registration Gotcha (PERMANENT)

`_yoast_wpseo_metadesc` and `_yoast_wpseo_opengraph-image` behave differently for pages vs posts:
- **Pages**: Registered with `show_in_rest=true` via `register_meta`. Can read/write via standard REST API `meta` object.
- **Posts**: NOT registered for REST API. Standard REST write silently ignores these fields.
- **Fix for posts**: Use `purebrain/v1/update-post-meta` custom endpoint which calls `update_post_meta()` directly.

### Blog Post Description Gotcha

If a blog post has no custom `_yoast_wpseo_metadesc` set AND no excerpt, Yoast generates og:description from the first paragraph of content.
If the first paragraph is a byline (like post 1139), this looks terrible in social shares.
- **Fix**: Set explicit excerpt AND `_yoast_wpseo_metadesc` via custom endpoint.

### Authoritative SEO Verification Command

```python
import subprocess, json, re, urllib.parse

url = "https://purebrain.ai/YOUR-SLUG/"
encoded = urllib.parse.quote(url)
result = subprocess.run([
    "curl", "-s",
    f"https://purebrain.ai/wp-json/yoast/v1/get_head?url={encoded}"
], capture_output=True, text=True, timeout=30)

d = json.loads(result.stdout)
html = d.get('html', '')
desc = re.search(r'name="description"\s+content="([^"]*)"', html)
og_img = re.search(r'property="og:image"\s+content="([^"]*)"', html)
print("desc:", desc.group(1) if desc else "NOT SET")
print("og:image:", og_img.group(1) if og_img else "NOT SET")
```

### Setting OG Image on Pages (REST API)

```bash
curl -s -X POST "https://purebrain.ai/wp-json/wp/v2/pages/PAGE_ID" \
  -u "Aether:APP_PASS" \
  -H "Content-Type: application/json" \
  -d '{"meta": {"_yoast_wpseo_opengraph-image": "URL", "_yoast_wpseo_opengraph-image-id": "694"}}'
```

### Setting Meta Desc on Posts (Custom Endpoint)

```bash
curl -s -X POST "https://purebrain.ai/wp-json/purebrain/v1/update-post-meta" \
  -u "Aether:APP_PASS" \
  -H "Content-Type: application/json" \
  -d '{"post_id": 1139, "meta_key": "_yoast_wpseo_metadesc", "meta_value": "Description here."}'
```

---

## State After This Audit (2026-03-03)

### All Public Pages (indexed): OG image = OK, Meta desc = OK

Key pages confirmed:
- All comparison pages (vs ChatGPT, Claude, Gemini, etc.) - OK
- Graham Martin client pages (1150, 1153, 1154, 1155, 1156, 1196, 1200) - FIXED
- New competitor comparison (1190 purebrain-vs-glbgpt) - FIXED
- Investor intelligence (1205) - FIXED
- Hunden Partners (1206) - FIXED
- Terms (541), Privacy (3), Training (1115) - OG image FIXED

### All Blog Posts: Meta desc = OK, OG image = OK (featured image)

- Post 1139 required excerpt update (byline was poisoning the auto-description)
- All 16 posts now have custom metadesc via `purebrain/v1/update-post-meta`
- 9 posts have focus keywords set

### Default OG Image

- URL: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg`
- Media ID: 694
- Dimensions: 1200x627

---

## Noindex Page List (Skip These in Future SEO Audits)

689, 688, 1118, 439, 963, 859, 855, 854, 843, 811, 532, 468, 383, 338, 309, 174, 95, 1128

---

## Twitter Card Note

Yoast sets `twitter:card: summary_large_image` on all pages/posts.
No explicit `twitter:image` is needed - Twitter/X falls back to `og:image`.
This is correct and acceptable behavior.
Exception: if a page needs a different image for Twitter vs LinkedIn (like the homepage GIF strategy) - then set `_yoast_wpseo_twitter-image` separately.
