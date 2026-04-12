# HLS Video Player Test - purebrain.ai/video-test/ - CORS Block on R2

**Date**: 2026-02-28
**Agent**: browser-vision-tester
**Type**: gotcha + pattern
**Site**: purebrain.ai/video-test/

---

## Context

Testing HLS video player intended as "Watch Demo" replacement on homepage.
Video source: Cloudflare R2 bucket `pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev`
HLS manifest path: `/videos/demo/portal-enhanced-v1/master.m3u8`

---

## Critical Discovery: CORS Block on Cloudflare R2

**Root cause of video failure**: CORS policy on Cloudflare R2 bucket is blocking HLS.js XHR requests.

**Console error captured**:
```
Access to XMLHttpRequest at 'https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/demo/portal-enhanced-v1/master.m3u8'
from origin 'https://purebrain.ai' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header present
```

**What this means**: HLS.js uses XHR/fetch to pull .m3u8 and .ts segment files. Without CORS headers on R2, the browser blocks all requests. The video element gets a blob: URL (MSE buffer) but readyState stays at 0 (HAVE_NOTHING) — video never buffers, never plays.

---

## Fix Required

In Cloudflare R2 bucket settings, add CORS rule:
```json
[
  {
    "AllowedOrigins": ["https://purebrain.ai"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": []
  }
]
```

Or use wildcard for testing: `"AllowedOrigins": ["*"]`

Access via: Cloudflare Dashboard > R2 > [bucket] > Settings > CORS Policy

---

## What Worked / Visual State

- Player container: correct dark background (#080a12), 8px border radius, 16:9 aspect ratio
- Video element: properly configured (muted, autoplay, loop all set correctly)
- HLS.js v1.5.7 loaded and MSE supported
- Poster image URL resolving from R2
- Page itself has ORANGE BACKGROUND PROBLEM (see below)

---

## Orange Background Bug (Separate Issue)

`bodyBg` reported as `rgb(241, 66, 11)` (Pure Tech Orange).
This is the same orange background bug that was supposed to be fixed by plugin v4.6.6.
The video-test/ page is rendering with orange background between header and player card.
This is NOT about the video — it's the standard page background enforcement issue.

---

## Testing Gotchas

1. **Use `domcontentloaded` not `networkidle`** for HLS pages — streaming keeps network active forever, causing timeout
2. **Wait 5s after navigation** before screenshot — HLS.js needs time to initialize
3. **Check `bodyBg` in JS** to catch orange background regressions instantly
4. **currentSrc will be a blob: URL** when HLS.js is active (not the m3u8 URL directly)
5. **readyState 0 + paused=true** = video never buffered, likely a network/CORS issue

---

## Player Specs Confirmed Working

- Wrapper class: `[class*="video-wrap"]` found with correct styles
- `aspect-ratio: 16 / 9` set in CSS
- Background: `rgb(8, 10, 18)` (correct dark)
- Border radius: `8px` (rounded corners confirmed)
- Dimensions at 1440px: 900x506px (correct 16:9)

---

## When to Apply

- Any test of HLS video on purebrain.ai
- Any Cloudflare R2 hosted media being fetched via browser XHR
- When video shows spinner but never plays → check CORS first
