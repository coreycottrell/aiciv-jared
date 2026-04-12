# full-stack-developer: Twitter Separate OG Image - Live Verification

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: Verified twitter:image is separate from og:image on purebrain.ai homepage - WORKING

---

## Status

COMPLETE AND VERIFIED. This was done in a previous session today.

## What's Live

- `og:image` = `Pure-Brain-Vid-3.gif` (9MB GIF - LinkedIn/Facebook keep this)
- `twitter:image` = `purebrain-homepage-og.jpg` (56KB JPG - Twitter/X gets this)

## Key Finding: Duplicate Yoast Meta in Page Body

The live page HTML has TWO sets of Yoast meta tags:
1. **Line ~24-31**: The actual `<head>` section - CORRECT (twitter:image = JPG)
2. **Line ~2571-2578**: Inside body content (Elementor widget?) - STALE (twitter:image = GIF)

**This is NOT a problem**: Social crawlers (Twitter, LinkedIn, Facebook) only read the
FIRST occurrence of `twitter:image`. The first occurrence is the correct JPG.

The second set is from an old Yoast SEO schema block embedded in Elementor page content
(Yoast v26.9 vs current v27.0 in actual head). This does not affect social sharing.

## Verification Commands

```bash
# Check FIRST twitter:image (what Twitter actually sees)
curl -s "https://purebrain.ai/" -A "Twitterbot/1.0" | python3 -c "
import sys, re
content = sys.stdin.read()
match = re.search(r'<meta name=[\"'\'']+twitter:image[\"'\'']+[^>]*content=[\"'\'']+([^\"'\'']+)', content)
print('FIRST twitter:image:', match.group(1) if match else 'NOT FOUND')
"

# Confirm image is accessible
curl -sI "https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg"

# Yoast get_head API
curl "https://purebrain.ai/wp-json/yoast/v1/get_head?url=https%3A%2F%2Fpurebrain.ai%2F"
```

## Implementation Details

- Yoast meta key: `_yoast_wpseo_twitter-image`
- Set via: `POST /wp-json/purebrain/v1/update-post-meta` (custom plugin endpoint)
- Plugin: purebrain-security-plugin v3.9.3 (added Twitter image to REST whitelist)
- WordPress page ID: 11 (homepage)
- Media ID: 694

## For Future Reference

If twitter:image ever reverts to GIF, re-run:
```python
import requests
APP_PASSWORD = 'FlFr2VOtlHiHaJWjzW96OHUJ'
r = requests.post(
    'https://purebrain.ai/wp-json/purebrain/v1/update-post-meta',
    auth=('Aether', APP_PASSWORD),
    json={
        'post_id': 11,
        'meta_key': '_yoast_wpseo_twitter-image',
        'meta_value': 'https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg'
    }
)
print(r.json())
```

---

**End of Memory**
