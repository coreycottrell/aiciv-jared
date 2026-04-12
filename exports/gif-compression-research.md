# GIF Compression & Platform-Specific OG Image Research

**Date**: 2026-02-23
**Agent**: web-researcher
**Topic**: Animated GIF (Pure-Brain-Vid-3.gif, 9MB, 480x270px) - platform social share compatibility

---

## Executive Summary

The 9MB animated GIF is causing broken or non-animated social share cards on Facebook and Twitter/X because:
1. Facebook treats GIFs as static (shows first frame only), and 9MB may trigger crawl timeout
2. Twitter/X has a hard 5MB limit on twitter:image - 9MB will fail silently
3. LinkedIn also officially only supports JPG/PNG for og:image - its "working" behavior is likely because it falls back gracefully

The solution is **a two-pronged approach**:
- Keep the GIF in WordPress (it can remain for LinkedIn's behavior)
- Use `twitter:image` to set a separate, smaller static image for Twitter/X
- Use `og:image` with a compressed static JPG for Facebook
- OR compress the GIF to under 5MB for platforms that show animated previews

**The good news**: You CAN set different images for Facebook vs Twitter/X using separate meta tags. LinkedIn reads og:image, so it gets whatever Facebook gets.

---

## Platform Specifications (Verified 2026)

### Facebook
- **Format support**: JPG, PNG, WebP, GIF (but GIF is treated as static - first frame only)
- **Maximum file size**: 8MB (official limit)
- **Practical recommendation**: Under 1MB for reliable loading (9MB risks crawler timeout)
- **Dimensions**: 1200x630px recommended, 1.91:1 aspect ratio
- **Animation support**: NONE - og:image GIFs do not animate on Facebook
- **Verdict on 9MB GIF**: May technically pass the 8MB limit, but shows as static, and 9MB will likely timeout Facebook's crawler (crawlers have time/size limits much lower than 8MB)
- **Debug tool**: https://developers.facebook.com/tools/debug/

### Twitter/X
- **Format support**: JPG, PNG, WebP, GIF (but GIF shows first frame only for link cards)
- **Maximum file size**: **5MB hard limit** - files over 5MB are rejected
- **Dimensions**: 1200x628px recommended for summary_large_image card
- **Animation support**: NONE for link preview cards - animated GIFs in twitter:image show as static
- **Verdict on 9MB GIF**: FAILS - exceeds 5MB limit, card will not render
- **Debug tool**: https://cards-dev.twitter.com/validator

### LinkedIn
- **Official spec**: JPG and PNG only for og:image (GIF not officially supported)
- **Maximum file size**: 5MB cap for uploads
- **Animation support**: Not supported in og:image previews per official documentation
- **Current behavior**: LinkedIn appears to render the GIF's first frame when you confirmed it "works" - it is rendering a static preview from the GIF
- **Verdict on 9MB GIF**: Working because LinkedIn is showing a static frame, not animating it

**Key insight**: No social platform currently animates og:image GIFs in link preview cards. The GIF is functioning everywhere as a static first-frame image. The issue is purely file size - 9MB breaks Twitter/X's 5MB limit.

---

## Platform-Specific OG Tags: Can We Set Different Images?

**YES** - this is fully supported via the HTML meta tag system:

```html
<!-- Facebook + LinkedIn + all others read this -->
<meta property="og:image" content="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-og-static.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />

<!-- Twitter/X reads twitter:image FIRST, falls back to og:image if absent -->
<meta name="twitter:image" content="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-og-twitter.jpg" />
<meta name="twitter:card" content="summary_large_image" />
```

**How platforms prioritize**:
- Twitter/X: Uses `twitter:image` if present, otherwise falls back to `og:image`
- Facebook: Uses `og:image` (ignores twitter: tags)
- LinkedIn: Uses `og:image` (ignores twitter: tags)
- WhatsApp, Slack, Discord: Use `og:image`

**Yoast SEO support**: Yoast has a "Social" tab in each post/page editor where you can set separate Facebook and Twitter images. This is the cleanest way to manage it in WordPress without custom code.

**Note from Yoast**: "It's impossible to specify different images for different networks, other than for Facebook and Twitter." LinkedIn gets whatever og:image is set for Facebook.

---

## Solution Options (Ranked by Recommendation)

### Option A: Static JPG for All Platforms (ALREADY DONE - Recommended for Most)

The team already generated `purebrain-homepage-og-image.jpg` (56KB, 1200x627). This is the clean solution.

- og:image = static 1200x627 JPG
- twitter:image = same static JPG (or omit, it will fall back to og:image)
- All platforms get a crisp, fast-loading preview
- No animation anywhere (since no platform animates og:image GIFs anyway)

### Option B: Compressed GIF for og:image + Static JPG for Twitter (Best of Both)

If Jared wants to attempt animation on platforms that might support it:
- Compress GIF to under 5MB using gifsicle (see commands below)
- Set compressed GIF as og:image
- Set static JPG as twitter:image (required since Twitter hard-caps at 5MB)
- LinkedIn gets the compressed GIF (will still show as static first frame)
- Facebook gets the compressed GIF (will show as static first frame)

### Option C: Keep GIF Only for LinkedIn

There is NO way to serve a different image specifically to LinkedIn vs Facebook since both read og:image. If you want the GIF on LinkedIn, Facebook gets it too.

---

## Tool Commands

### 1. Compress GIF to Under 5MB (gifsicle - Recommended)

gifsicle is available on Ubuntu via apt and now includes lossy compression (previously a separate tool called giflossy, now merged into gifsicle):

```bash
# Install gifsicle
sudo apt-get install gifsicle

# Check current file size
ls -lh Pure-Brain-Vid-3.gif

# Option 1: Moderate compression (best quality, ~40-50% reduction)
gifsicle -O3 --lossy=60 --colors 128 -o Pure-Brain-Vid-3-compressed.gif Pure-Brain-Vid-3.gif

# Option 2: Aggressive compression (60-70% reduction, some visible artifacts)
gifsicle -O3 --lossy=100 --colors 96 -o Pure-Brain-Vid-3-small.gif Pure-Brain-Vid-3.gif

# Option 3: Maximum compression (may show noticeable quality loss)
gifsicle -O3 --lossy=200 --colors 64 -o Pure-Brain-Vid-3-tiny.gif Pure-Brain-Vid-3.gif

# Check resulting file sizes
ls -lh Pure-Brain-Vid-3*.gif
```

**Expected results for 9MB input**:
- `--lossy=60 --colors 128`: ~4-5MB (30-50% reduction)
- `--lossy=100 --colors 96`: ~3-4MB (55-65% reduction)
- `--lossy=200 --colors 64`: ~2-3MB (65-75% reduction)

**Parameter guide**:
- `-O3`: Most aggressive lossless optimization (always include)
- `--lossy=N`: 30 = very light, 80 = moderate, 200 = heavy (default: 80)
- `--colors N`: Reduce color palette (256 default, 128 = good quality, 64 = smaller)

### 2. Compress GIF Using ffmpeg + gifsicle (Two-Pass Pipeline)

For better color quality, use ffmpeg for palette optimization then gifsicle for lossy pass:

```bash
# Step 1: Generate optimized palette
ffmpeg -i Pure-Brain-Vid-3.gif -vf 'palettegen=stats_mode=diff' palette.png

# Step 2: Re-encode with optimized palette (lossless quality improvement)
ffmpeg -i Pure-Brain-Vid-3.gif -i palette.png \
  -lavfi 'paletteuse=diff_mode=rectangle' \
  Pure-Brain-Vid-3-palette.gif

# Step 3: Apply lossy compression with gifsicle
gifsicle -O3 --lossy=80 --colors 128 \
  -o Pure-Brain-Vid-3-final.gif \
  Pure-Brain-Vid-3-palette.gif

# Check size
ls -lh Pure-Brain-Vid-3-final.gif
```

### 3. Reduce Frame Rate (ffmpeg - if still too large)

The GIF is 480x270. Keeping the same size but reducing frame rate:

```bash
# Reduce to 10fps (from original - check original fps first)
ffmpeg -i Pure-Brain-Vid-3.gif \
  -vf 'fps=10,split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5' \
  Pure-Brain-Vid-3-10fps.gif

# Then apply gifsicle lossy pass
gifsicle -O3 --lossy=80 Pure-Brain-Vid-3-10fps.gif -o Pure-Brain-Vid-3-10fps-compressed.gif
```

### 4. ImageMagick Optimization (Alternative to gifsicle)

```bash
# Check if ImageMagick is installed
convert --version

# Optimize using layer optimization + fuzz (similar colors treated as identical)
convert Pure-Brain-Vid-3.gif -layers optimize -fuzz 10% Pure-Brain-Vid-3-im.gif

# More aggressive fuzz (higher % = more compression, more color degradation)
convert Pure-Brain-Vid-3.gif -layers optimize -fuzz 20% Pure-Brain-Vid-3-im-agg.gif
```

### 5. Extract High-Quality Static Frame as Fallback JPG

#### Using Python + Pillow (Recommended - matches existing workflow)

```python
#!/usr/bin/env python3
"""
Extract first frame from animated GIF, resize to OG spec, save as JPG.
Pillow is already in the project environment.
"""
from PIL import Image

def extract_first_frame_as_jpg(
    gif_path: str,
    output_path: str,
    width: int = 1200,
    height: int = 627,
    quality: int = 90
):
    """Extract first frame of animated GIF and save as JPG at OG dimensions."""
    with Image.open(gif_path) as img:
        # Seek to first frame (frame 0 is default, but explicit is safer)
        img.seek(0)

        # Convert to RGBA first to handle GIF palette/transparency
        frame = img.convert("RGBA")

        # Create white background (JPG doesn't support transparency)
        background = Image.new("RGB", frame.size, (8, 10, 18))  # PureBrain dark bg
        background.paste(frame, mask=frame.split()[3])  # Use alpha as mask

        # Resize to OG dimensions using high-quality Lanczos resampling
        # Use thumbnail-style fit to avoid distortion, then pad if needed
        target_size = (width, height)

        # Calculate scale to fit within target while maintaining aspect ratio
        frame_ratio = background.width / background.height
        target_ratio = width / height

        if frame_ratio > target_ratio:
            # GIF is wider - fit by width
            new_w = width
            new_h = int(width / frame_ratio)
        else:
            # GIF is taller - fit by height
            new_h = height
            new_w = int(height * frame_ratio)

        resized = background.resize((new_w, new_h), Image.LANCZOS)

        # Create final canvas and center the frame
        canvas = Image.new("RGB", target_size, (8, 10, 18))
        x_offset = (width - new_w) // 2
        y_offset = (height - new_h) // 2
        canvas.paste(resized, (x_offset, y_offset))

        # Save as high-quality JPG
        canvas.save(output_path, "JPEG", quality=quality, optimize=True)
        print(f"Saved: {output_path}")
        print(f"Size: {canvas.size}")

        import os
        size_kb = os.path.getsize(output_path) / 1024
        print(f"File size: {size_kb:.1f} KB")


if __name__ == "__main__":
    gif_path = "/path/to/Pure-Brain-Vid-3.gif"
    output_path = "/home/jared/projects/AI-CIV/aether/exports/purebrain-og-static-frame.jpg"
    extract_first_frame_as_jpg(gif_path, output_path, width=1200, height=627, quality=90)
```

#### Using ffmpeg (One-liner)

```bash
# Extract frame 1 from GIF, scale to 1200x627, save as JPG
ffmpeg -i Pure-Brain-Vid-3.gif \
  -vf "select=eq(n\,0),scale=1200:627:force_original_aspect_ratio=decrease,pad=1200:627:(ow-iw)/2:(oh-ih)/2:color=080a12" \
  -vframes 1 \
  -q:v 2 \
  purebrain-og-static.jpg

# -vframes 1: extract only 1 frame
# scale with pad: fit 480x270 into 1200x627, pad with dark bg color
# -q:v 2: JPG quality (2 = very high, scale 1-31 where 1 is best)
```

#### Using ImageMagick (Simple)

```bash
# Extract frame 0 (first frame), resize, save as JPG
convert "Pure-Brain-Vid-3.gif[0]" \
  -resize 1200x627^ \
  -gravity center \
  -extent 1200x627 \
  -background "#080a12" \
  -quality 90 \
  purebrain-og-static.jpg
```

---

## Setting Platform-Specific OG Tags in Yoast SEO

### Method 1: Yoast Admin UI (No Code - Recommended)

1. Go to WordPress Admin
2. Edit the Homepage (page ID 11)
3. In Yoast SEO panel, click the "Social" icon (share icon tab)
4. Under "Facebook": set your Facebook/LinkedIn image (compressed GIF or static JPG)
5. Under "Twitter": set your Twitter-specific image (static JPG under 5MB)
6. Save

Yoast will output:
- `og:image` = your Facebook image (used by Facebook AND LinkedIn)
- `twitter:image` = your Twitter-specific image

### Method 2: PHP Filter in WordPress (Custom Code)

Add to WordPress theme's `functions.php` or a custom plugin:

```php
<?php
/**
 * Set platform-specific OG images.
 * og:image = for Facebook/LinkedIn (use compressed GIF or static JPG)
 * twitter:image = for Twitter/X (MUST be under 5MB, use static JPG)
 */

// Override og:image (Facebook/LinkedIn)
add_filter('wpseo_opengraph_image', 'purebrain_custom_og_image', 10, 2);
function purebrain_custom_og_image($image, $presentation) {
    // Only override homepage
    if (is_front_page()) {
        return 'https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3-compressed.gif';
        // OR use static: return 'https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg';
    }
    return $image;
}

// Override twitter:image (Twitter/X specific - overrides og:image for Twitter)
add_filter('wpseo_twitter_image', 'purebrain_custom_twitter_image', 10, 2);
function purebrain_custom_twitter_image($image, $presentation) {
    if (is_front_page()) {
        // Static JPG, must be under 5MB
        return 'https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg';
    }
    return $image;
}
?>
```

### Method 3: Direct HTML (if using custom head injection)

The cleanest technical approach if you need full control:

```html
<!-- In <head> section -->

<!-- Facebook and LinkedIn read this -->
<meta property="og:image" content="https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3-compressed.gif" />
<meta property="og:image:type" content="image/gif" />
<meta property="og:image:width" content="480" />
<meta property="og:image:height" content="270" />

<!-- Twitter/X reads twitter:image FIRST (ignores og:image for its card) -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg" />
```

---

## Recommended Action Plan

### Immediate Fix (Solves Twitter/X Broken Preview)

Twitter/X is broken because 9MB > 5MB limit. Fix with Yoast Social tab:

1. Go to Yoast SEO > Homepage > Social tab > Twitter
2. Set Twitter image to: `purebrain-homepage-og-image.jpg` (already generated, 56KB)
3. Leave og:image as the GIF for now
4. Scrape Twitter Card Validator to refresh cache

### Complete Fix (All Platforms)

Run compression and set up platform-specific images:

```bash
# 1. Navigate to where the GIF lives (likely WordPress uploads)
# Find it:
find /home -name "Pure-Brain-Vid-3.gif" 2>/dev/null

# 2. Run gifsicle compression
sudo apt-get install -y gifsicle
gifsicle -O3 --lossy=80 --colors 128 \
  -o /tmp/Pure-Brain-Vid-3-compressed.gif \
  /path/to/Pure-Brain-Vid-3.gif

# 3. Check compressed size
ls -lh /tmp/Pure-Brain-Vid-3-compressed.gif

# 4. If under 5MB, upload to WordPress and set as og:image
# 5. Set twitter:image = static JPG (already exists)
```

### What to Set Where

| Platform | Tag | Image | Expected Result |
|----------|-----|-------|-----------------|
| Facebook | `og:image` | Compressed GIF or static JPG | Static first frame shown |
| LinkedIn | `og:image` | Same as Facebook (same tag) | Static first frame shown |
| Twitter/X | `twitter:image` | Static JPG < 5MB | Clean preview card |

---

## Key Findings Summary

1. **No social platform animates og:image GIFs** in link preview cards as of 2026. The animation is irrelevant for social sharing previews.

2. **Twitter/X 5MB hard limit** is the critical blocking issue. The 9MB GIF fails silently on Twitter/X.

3. **Facebook 8MB official limit** - the GIF may technically pass but will likely timeout the crawler. Facebook shows static first frame even if it loads.

4. **LinkedIn "working" = first frame** - LinkedIn is showing a static frame of the GIF, not animating it. This is consistent with the other platforms.

5. **You CAN set different images per platform**: `twitter:image` overrides `og:image` for Twitter only. LinkedIn and Facebook both read `og:image`.

6. **gifsicle is the best tool** for GIF compression. `--lossy=80 --colors 128 -O3` should get 9MB to roughly 4-5MB. For under 3MB, use `--lossy=150 --colors 96`.

7. **MP4/WebM cannot be used as og:image** - neither Facebook nor Twitter support video in og:image tags. Videos require a separate `og:video` tag and do not work for link preview thumbnails.

8. **The team already generated** `purebrain-homepage-og-image.jpg` (56KB, 1200x627) - this is the ideal static fallback and is already ready to use.

---

## Sources

- [Facebook og:image Official Guide - ogpreview.app](https://ogpreview.app/guides/facebook-link-preview)
- [Twitter/X Summary Card with Large Image Spec](https://developer.x.com/en/docs/x-for-websites/cards/overview/summary-card-with-large-image)
- [LinkedIn Media File Types Supported](https://www.linkedin.com/help/linkedin/answer/a564109)
- [Gifsicle - Lossy GIF Compression](https://kornel.ski/lossygif)
- [Simon Willison - Compressing Animated GIF with gifsicle](https://til.simonwillison.net/imagemagick/compress-animated-gif)
- [Yoast - How Social Image Sharing Works](https://yoast.com/advanced-technical-seo-social-image-ogimage-tags/)
- [DigitalOcean - GIFs on the Command Line](https://www.digitalocean.com/community/tutorials/how-to-make-and-optimize-gifs-on-the-command-line)
- [FFmpeg GIF Optimization Guide](https://blog.dve2.com/archives/311/optimize-gif-size-with-ffmpeg-reduce-file-sizes-in-3-steps/)
- [giflossy (now merged into gifsicle)](https://github.com/kornelski/giflossy)
- [Open Graph Image Sizes for Social Media - Krumzi](https://www.krumzi.com/blog/open-graph-image-sizes-for-social-media-the-complete-2025-guide)
- [Best GIF Sizes for Social Media - FastMakerGif](https://fastmakergif.com/blog/best-gif-sizes-social-media)
- [Facebook Debugger Tool](https://developers.facebook.com/tools/debug/)
- [Video as og:image - Webflow Discussion](https://www.flowradar.com/answer/possible-to-use-video-mp4-or-gif-as-open-graph-image-url-on-facebook-and-instagram-using-webflow)
