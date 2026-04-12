# web-researcher: GIF Compression & Platform OG Image Research

**Date**: 2026-02-23
**Type**: teaching + synthesis
**Topic**: Social platform og:image GIF support, size limits, compression tools, platform-specific meta tags
**Confidence**: high (verified from official docs + multiple sources)

---

## Context

Jared has a 9MB animated GIF (Pure-Brain-Vid-3.gif, 480x270) set as og:image on purebrain.ai homepage.
LinkedIn "works" (shows static first frame), but Facebook may timeout and Twitter/X is broken.

## Key Discoveries

### Platform Limits (VERIFIED)

| Platform | Max Size | Animated GIF? | Notes |
|----------|----------|---------------|-------|
| Twitter/X | **5MB hard limit** | No (static first frame) | 9MB FAILS silently |
| Facebook | 8MB official | No (static first frame) | 9MB risks crawler timeout |
| LinkedIn | 5MB cap | No (static first frame) | og:image = JPG/PNG officially |

**No social platform animates og:image GIFs in link previews.** Animation is irrelevant for social sharing.

### Platform-Specific Tags Work

- `og:image` = read by Facebook, LinkedIn, WhatsApp, Slack, Discord
- `twitter:image` = read by Twitter/X FIRST, then falls back to og:image
- You CANNOT target LinkedIn separately from Facebook (both read og:image)

### Yoast SEO Support

Yoast has a Social tab per post/page with separate Facebook and Twitter image fields.
WordPress hooks: `wpseo_opengraph_image` and `wpseo_twitter_image`

### Compression Tool: gifsicle

Best tool for GIF compression, available via `sudo apt-get install gifsicle`

Key command for 9MB GIF to ~4MB:
```bash
gifsicle -O3 --lossy=80 --colors 128 -o output.gif input.gif
```

Expected reductions from 9MB:
- `--lossy=60 --colors 128`: ~4-5MB
- `--lossy=100 --colors 96`: ~3-4MB
- `--lossy=200 --colors 64`: ~2-3MB

### Static Frame Extraction

```bash
# ffmpeg one-liner (fastest)
ffmpeg -i input.gif -vf "select=eq(n\,0),scale=1200:627:force_original_aspect_ratio=decrease,pad=1200:627:(ow-iw)/2:(oh-ih)/2:color=080a12" -vframes 1 -q:v 2 output.jpg

# ImageMagick
convert "input.gif[0]" -resize 1200x627^ -gravity center -extent 1200x627 -quality 90 output.jpg

# Python Pillow
img = Image.open("input.gif"); img.seek(0); frame = img.convert("RGBA"); ...
```

## Recommended Fix

1. **Twitter/X (immediate)**: Set `twitter:image` = static JPG (already at `exports/overnight-content/purebrain-homepage-og-image.jpg`, 56KB)
2. **Facebook/LinkedIn**: Either use compressed GIF (<5MB via gifsicle) or same static JPG
3. **No code needed**: Yoast Social tab in WordPress admin handles this via UI

## Sources

- ogpreview.app/guides/facebook-link-preview
- developer.x.com/en/docs/x-for-websites/cards/overview/summary-card-with-large-image
- linkedin.com/help/linkedin/answer/a564109
- kornel.ski/lossygif
- til.simonwillison.net/imagemagick/compress-animated-gif
- yoast.com/advanced-technical-seo-social-image-ogimage-tags/

## Full Report

`/home/jared/projects/AI-CIV/aether/exports/gif-compression-research.md`
