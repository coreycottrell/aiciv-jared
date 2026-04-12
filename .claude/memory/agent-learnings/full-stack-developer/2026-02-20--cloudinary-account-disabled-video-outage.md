# Cloudinary Account Disabled - Video Background Outage

**Date**: 2026-02-20
**Type**: operational + teaching
**Agent**: full-stack-developer

## Incident Summary

All background videos on purebrain.ai went down because the Cloudinary account `dq06qxzhz` was **disabled**.

**Error message from Cloudinary**: `cloud_name dq06qxzhz is disabled`
**HTTP response**: 401 Unauthorized

## Root Cause

The Cloudinary free tier has bandwidth/storage limits. The account `dq06qxzhz` that hosted the videos was disabled - likely due to bandwidth overage, inactivity, or plan expiration.

## Affected Pages

ALL 6 pages use the same two Cloudinary URLs:

| Page ID | Name | Widget Class |
|---------|------|--------------|
| 11 | Homepage | `video-background__` |
| 174 | PureBrain 2.0 | `video-background__` |
| 338 | PureBrain 3.0 | `video-background__` |
| 383 | PureBrain 4.0 | `pb4-video-bg` |
| 439 | pay-test | `video-background__` |
| 468 | pay-test-sandbox | `video-background__` |

## Dead Video URLs (Both 401)

1. **Background video**: `https://res.cloudinary.com/dq06qxzhz/video/upload/v1769961538/PureResearch.ai_1_nzlral.mp4`
2. **Demo modal video**: `https://res.cloudinary.com/dq06qxzhz/video/upload/v1770156001/Pure_Brain_Demo_Video_nyjoon.mp4`

## Fix Required

Jared needs to:
1. Re-upload the two video files to a new host (WordPress media library, or new Cloudinary account, or any CDN)
2. Provide the new URLs
3. We update `_elementor_data` on all 6 pages to swap the old URLs for new ones

## How to Fix Once URLs Are Available

The videos are referenced in HTML `<source src="...">` tags inside Elementor HTML widgets.
Simple string replacement across all 6 pages' `_elementor_data`:

```python
# Replace bg video URL
new_bg_url = "NEW_URL_HERE"
old_bg_url = "https://res.cloudinary.com/dq06qxzhz/video/upload/v1769961538/PureResearch.ai_1_nzlral.mp4"
elem_data_str = elem_data_str.replace(old_bg_url, new_bg_url)

# Replace demo video URL
new_demo_url = "NEW_DEMO_URL_HERE"
old_demo_url = "https://res.cloudinary.com/dq06qxzhz/video/upload/v1770156001/Pure_Brain_Demo_Video_nyjoon.mp4"
elem_data_str = elem_data_str.replace(old_demo_url, new_demo_url)
```

## What Visitors See Now

The `video-background__overlay` div renders the CSS fallback: orange/red gradient background with blue geometric lines (the Elementor section background-color fallback).

## Teaching

**Never rely on a free Cloudinary account for production video assets.** Free tiers have bandwidth limits and accounts can be disabled without warning. Always:
- Upload critical media to WordPress media library (served via GoDaddy CDN)
- Or use a paid/reliable CDN
- Keep local copies of all video assets
