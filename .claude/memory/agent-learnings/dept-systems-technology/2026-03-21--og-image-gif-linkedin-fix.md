# OG Image GIF LinkedIn Fix — 2026-03-21

## Type: teaching

## Problem
LinkedIn was showing the logo PNG instead of the brain GIF on purebrain.ai shares.

## Root Causes Found (all three must be fixed together)

1. **Wrong dimensions** — `og:image:width` was 1200, `og:image:height` was 630. The ACTUAL GIF (Pure-Brain-Vid-3.gif) is **480x270 pixels**. LinkedIn verifies declared dimensions match actual image dimensions and rejects mismatches.

2. **Wrong twitter:image** — Both twitter:image tags (there were two twitter:card blocks in the HTML) pointed to `og-image.png` (the logo), NOT the GIF. The `og:image` tag was correct but `twitter:image` was stale.

3. **Missing og:image:secure_url** — Yoast always adds this as a duplicate HTTPS URL. LinkedIn prefers it present.

## What puremarketing.ai (Yoast) Does That Works
- `og:image:width` / `og:image:height` match actual GIF dimensions (480x270)
- `og:image:secure_url` = same URL as og:image (https version)
- `og:image:type` = `image/gif`
- `og:image:alt` = descriptive alt text
- `twitter:image` = same GIF URL (not a different PNG)
- `twitter:card` = `summary_large_image`

## Fix Applied
File: `exports/cf-pages-deploy/index.html`
- Changed width from 1200 to 480
- Changed height from 630 to 270
- Added `og:image:secure_url` with GIF URL
- Added `og:image:alt`
- Fixed BOTH twitter:image tags to point to GIF (there were two twitter:card blocks in the page)

## GIF File Facts
- Path: `exports/cf-pages-deploy/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif`
- Actual size: 480x270px, 128 frames, 9MB
- Content-Type served: `image/gif` (correct, no fix needed there)
- URL accessible: `https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif`

## Verification
After deploy, `curl -s https://purebrain.ai/ | grep og:image:width` returns 480.
All 8 OG/Twitter image tags now point to GIF with correct dimensions.

## Next Step for Jared
Re-inspect URL at: https://www.linkedin.com/post-inspector/inspect/https:%2F%2Fpurebrain.ai%2F
LinkedIn caches aggressively — the inspector forces a fresh crawl.
