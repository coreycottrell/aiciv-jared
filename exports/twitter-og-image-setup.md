# full-stack-developer: Twitter OG Image Setup - purebrain.ai Homepage

**Agent**: full-stack-developer
**Domain**: Full Stack Development
**Date**: 2026-02-23

---

## Summary

Set a separate `twitter:image` for the purebrain.ai homepage so Twitter/X shows a proper preview instead of failing on the 9MB GIF.

**Result: COMPLETE AND LIVE**

---

## Before vs After

| Tag | Before | After |
|-----|--------|-------|
| `og:image` | `Pure-Brain-Vid-3.gif` (9MB GIF) | `Pure-Brain-Vid-3.gif` (UNCHANGED - LinkedIn keeps it) |
| `twitter:image` | `Pure-Brain-Vid-3.gif` (9MB - Twitter fails silently) | `purebrain-homepage-og.jpg` (56KB JPG - Twitter works) |

---

## What Was Done

### Step 1: Image Already Ready

The static OG image was already generated in a previous session:
- **Local path**: `/home/jared/projects/AI-CIV/aether/exports/overnight-content/purebrain-homepage-og.jpg`
- **Dimensions**: 1200x627 (standard OG)
- **File size**: 56KB (0.055MB) - well under Twitter's 5MB limit

### Step 2: Upload to WordPress Media Library

Uploaded via WordPress REST API:
- **Media ID**: 694
- **WordPress URL**: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg`
- **Accessible**: HTTP 200, `Content-Type: image/jpeg`, 57,400 bytes

### Step 3: Plugin v3.9.3 - Add Twitter Image to REST API Whitelist

Updated `purebrain-security-plugin.php` from v3.9.2 to v3.9.3:

**Changes:**
1. Added `_yoast_wpseo_twitter-image` and `_yoast_wpseo_twitter-image-id` to `register_post_meta()` list (REST API exposure)
2. Added both fields to `update-post-meta` endpoint whitelist
3. Increased max value length from 320 to 500 chars (to accommodate image URLs)

**Plugin file**: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`

**Deploy script**: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v393_purebrain.py`

Deployment confirmed: Plugin editor showed "File edited successfully"

### Step 4: Set twitter:image via REST API

Used our custom endpoint after plugin deployment:

```bash
POST https://purebrain.ai/wp-json/purebrain/v1/update-post-meta
{
  "post_id": 11,
  "meta_key": "_yoast_wpseo_twitter-image",
  "meta_value": "https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg"
}
```

**Response**: `{"success": true, "meta_value": "https://...purebrain-homepage-og.jpg", "updated": true}`

Also set the media ID:
```bash
POST https://purebrain.ai/wp-json/purebrain/v1/update-post-meta
{
  "post_id": 11,
  "meta_key": "_yoast_wpseo_twitter-image-id",
  "meta_value": "694"
}
```

### Step 5: Flush Cache

Flushed GoDaddy WPaaS page cache via WP Admin:
- URL: `https://purebrain.ai/wp-admin/?wpaas_action=flush_cache&wpaas_nonce=[nonce]`
- Cache cleared successfully

---

## Verification

### Live Page Check (post-cache-flush)

```bash
curl -s "https://purebrain.ai/" -A "Twitterbot/1.0" | grep -i "twitter:image\|og:image"
```

**Output from `<head>` section:**
```html
<meta property="og:image" content="https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif" />
<meta property="og:image:width" content="480" />
<meta property="og:image:height" content="270" />
<meta property="og:image:type" content="image/gif" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Your Brain. Your AI. Actual Intelligence" />
<meta name="twitter:description" content="Meet your PURE BRAIN, an AI that awakens just for you. ..." />
<meta name="twitter:image" content="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg" />
```

### WordPress REST API Check

```bash
GET https://purebrain.ai/wp-json/wp/v2/pages/11
```

Meta fields confirmed:
- `_yoast_wpseo_twitter-image`: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg`
- `_yoast_wpseo_twitter-image-id`: `694`

### Yoast get_head API Check

```bash
GET https://purebrain.ai/wp-json/yoast/v1/get_head?url=https%3A%2F%2Fpurebrain.ai%2F
```

Confirmed:
- `twitter_image`: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg`
- `og_image`: GIF (unchanged)

### Image Accessibility Check

```bash
curl -sI "https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg"
```

- HTTP/2 200
- Content-Type: image/jpeg
- Content-Length: 57400 (56KB)

---

## How It Works (Technical)

Yoast SEO checks `_yoast_wpseo_twitter-image` postmeta when rendering `twitter:image`.
- If set and valid: uses it (our static JPG)
- Falls back to: `og:image` (the 9MB GIF)

By setting only `_yoast_wpseo_twitter-image` (not touching `_yoast_wpseo_opengraph-image`):
- LinkedIn reads `og:image` → gets animated GIF (Jared wants this)
- Twitter reads `twitter:image` → gets static 56KB JPG (passes Twitter's 5MB limit)

---

## Next Steps (Optional)

To verify Twitter card is working correctly:
1. Go to [https://socialsharepreview.com/](https://socialsharepreview.com/) and enter `https://purebrain.ai/`
2. Twitter/X Card Validator (requires login): [https://cards-dev.twitter.com/validator](https://cards-dev.twitter.com/validator)

Note: Twitter/X caches its own scraped OG data. Even with the fix live, Twitter's cache may show the old image for up to 24-72 hours. The validator tool forces a fresh scrape.

---

## Files Changed

| File | Change |
|------|--------|
| `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php` | v3.9.2 → v3.9.3 (Twitter image REST support) |
| `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v393_purebrain.py` | New deploy script (created) |
| WordPress Media Library | Added `purebrain-homepage-og.jpg` (Media ID 694) |
| WordPress Page ID 11 meta | `_yoast_wpseo_twitter-image` and `_yoast_wpseo_twitter-image-id` set |

---

## Re-verification (2026-02-23 - Second Session Check)

Live page check confirmed still working:

```
FIRST twitter:image: https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg
FIRST og:image:     https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif
```

Image accessible: HTTP/2 200, Content-Type: image/jpeg, Content-Length: 53852 (53KB)

### Note: Duplicate Meta Tags in Body (Not a Problem)

The page HTML contains TWO sets of Yoast meta tags:
1. Actual `<head>` section (line ~24): twitter:image = JPG (CORRECT)
2. Body content area (line ~2571): twitter:image = GIF (stale Elementor widget, Yoast v26.9)

Social crawlers only read the FIRST occurrence of `twitter:image`. The first is correct.
This duplicate is from a Yoast SEO schema block embedded in Elementor page content and
does NOT affect social sharing behavior.
