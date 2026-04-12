# Blog Neural Feed Memories — Banner Image Fit Fix

**Date**: 2026-03-18
**Type**: operational / gotcha
**File fixed**: `exports/cf-pages-deploy/blog-neural-feed-memories/index.html`

## Root Cause

The two newest blog posts ("Prompting Is Dead" March 17, "The Meeting Your AI Should Already Know About" March 14) were added to `blog-neural-feed-memories/index.html` WITHOUT the required inline styles on their img tags.

All older posts (line 335+) had:
```
style="width:100%;height:100%;object-fit:cover;display:block;"
```

The two new posts were missing this, resulting in the browser rendering the 1920x1080 images at their natural size within the fixed aspect-ratio: 16/9 container — causing overflow/crop.

## Why It Happened

The .nfm-card-banner-img CSS class had NO corresponding rule in the stylesheet. The previous developer was relying entirely on inline styles to control image sizing. When new posts were added without the inline style, no CSS fallback existed.

## Fix Applied

1. Added CSS rule to cover all .nfm-card-banner-img images globally:
   .nfm-card-banner-img { width:100%; height:100%; object-fit:cover; display:block; }

2. Added inline styles to the two problem img tags for consistency with all other posts.

## Verification

All 31 nfm-card-banner-img images now have object-fit: cover coverage.
Both problem posts confirmed fixed.

## Pattern for Future

When adding new blog posts to blog-neural-feed-memories/index.html, the img tag should include:
style="width:100%;height:100%;object-fit:cover;display:block;"

Now the CSS class handles this automatically as a fallback.

## Architecture Note

- blog/index.html uses wp-block-latest-posts structure with height: auto — no crop issue possible
- blog-neural-feed-memories/index.html uses nfm-card structure with fixed aspect-ratio: 16/9 — requires object-fit: cover on images
