# OG Image Fix - CF Pages Social Share

**Date**: 2026-03-21
**Type**: teaching + operational
**Topic**: Social share / OG image broken on CF Pages after WordPress migration

---

## Root Cause

After migrating purebrain.ai from WordPress to CF Pages, OG image meta tags still pointed to:
`https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif`

Two compounding problems:
1. GIF format - LinkedIn and most social crawlers do NOT display animated GIFs as OG images
2. 9MB file size - LinkedIn has a ~5MB limit for OG images; the GIF exceeded it
3. Eventually the wp-content path will 404 when WP hosting is dropped entirely

## Fix Applied

1. Generated a proper branded OG image (1200x630 PNG, 52KB) using Python/PIL
   - Brand colors: bg #080a12, orange #f1420b, blue #2a93c1
   - Used favicon-192x192.png as the logo on the left
   - Text: PURE (blue) BRAIN (orange), tagline, URL
   - Path: `exports/cf-pages-deploy/og-image.png`

2. Replaced ALL 5 occurrences of the old wp-content GIF URL in index.html
   - Used Python string replacement (not sed - multiline sed is unreliable)
   - Also updated og:image:width 480→1200, height 270→630, type gif→png

3. Deployed to purebrain-staging CF Pages - 3 new files uploaded

## Key Details

- The CF Pages token (`CF_PAGES_TOKEN`) does NOT have zone list permissions
  - Cannot look up zone ID via API to purge cache
  - Not needed: homepage has `max-age=0, must-revalidate` and CF Pages auto-invalidates on deploy
  - og-image.png served fresh (cf-cache-status: MISS on first request)

- There is one remaining wp-content reference in index.html at line ~11322
  - This is inside Elementor's JS config blob (`elementorFrontendConfig.post.featuredImage`)
  - It is NOT a meta tag - social crawlers ignore it
  - Do not remove it as it could break Elementor functionality

## OG Image Dimensions Standard

- LinkedIn / Facebook: 1200x630 (1.91:1 ratio) — use this
- Twitter: 1200x628 or 1200x600
- Minimum: 600x315

## How to Regenerate OG Image

```python
python3 << 'EOF'
from PIL import Image, ImageDraw, ImageFont
# See /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/og-image.png for result
# Logo source: exports/cf-pages-deploy/assets/favicon-192x192.png
EOF
```

## Verification

- Live: `curl -s https://purebrain.ai/ | grep og:image`
- Image check: `curl -I https://purebrain.ai/og-image.png`
- LinkedIn inspector: https://www.linkedin.com/post-inspector/

## Files Modified

- `exports/cf-pages-deploy/index.html` - OG meta tags updated
- `exports/cf-pages-deploy/og-image.png` - NEW: 1200x630 branded PNG
