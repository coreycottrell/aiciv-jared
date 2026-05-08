---
name: Top 10 LinkedIn standalone image batch - FLUX Pro + PIL v4 composition
type: technique
date: 2026-05-04
agent: 3d-design-specialist
tags: [flux, pil, oswald-bold, standalone-v4, linkedin, batch, social-api, r2-upload]
confidence: high
---

# Top 10 LinkedIn Standalone Image Batch (May 5, 2026)

## Context

Generated 10 branded standalone LinkedIn images (2160x2700, v4 format) for posts in social.purebrain.ai that had no images. Full pipeline: FLUX Pro 1.1 (Replicate) -> PIL composite -> Upload to R2 -> PATCH media_refs on D1.

## Output paths

All 10 at `/home/jared/projects/AI-CIV/aether/exports/content-batch-images-may5/final/`:
- 01-hardest-part-final.png (2045 KB)
- 02-tired-of-demos-final.png (2781 KB)
- 03-ai-got-wrong-final.png (2202 KB)
- 04-shipped-4-features-final.png (2105 KB)
- 05-32-specialist-agents-final.png (4303 KB)
- 06-40-percent-die-final.png (1406 KB)
- 07-delegation-test-final.png (2870 KB)
- 08-sunday-math-final.png (1447 KB)
- 09-see-the-work-final.png (2193 KB)
- 10-stop-guessing-cost-final.png (2285 KB)

## Key technique: Title overlay on FLUX image area

Added centered title overlay with stroke text on the FLUX image area, in addition to the title in the top bar. This makes the image work as a standalone visual even without the bars visible (e.g., in LinkedIn feed cropping).

- Overlay font: 124px Oswald Bold (2x from 62px spec), falls back to 100px if too wide
- Stroke: 6px dark (#080a12) border drawn via circular offset pattern
- Scrim: vertical gaussian-style alpha gradient behind text (160 max alpha, quadratic falloff)

```python
def draw_text_with_stroke(draw, pos, text, font, fill, stroke_fill, stroke_width):
    x, y = pos
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx * dx + dy * dy <= stroke_width * stroke_width:
                draw.text((x + dx, y + dy), text, fill=stroke_fill, font=font)
    draw.text((x, y), text, fill=fill, font=font)
```

## FLUX prompt pattern that works for LinkedIn

Lead with "Cinematic" + specific photographic style. Embed brand hex colors directly:
- "cerulean blue at hex 2a93c1"
- "warm orange at hex f1420b"
- "dark background at hex 080a12"

End with: "No text, no logos, no watermarks, negative space dominant"

Aspect ratio: 4:5 portrait for standalone images.

## R2 upload + social API attach pattern

1. Login: POST /api/login with email/password, UA=curl/7.81.0 (default Python UA is CF-banned)
2. Upload: POST /api/uploads multipart form, returns R2 key + URL
3. Convert URL to proxy format: `social.purebrain.ai/media/{key}`
4. PATCH /api/content/{id} with `media_refs: [url]` (NOT `image_url`)

## Known issue: R2 media proxy 404

ALL R2-served images (both old and new) return 404 via `social.purebrain.ai/media/`. The R2 objects exist in the bucket (upload succeeds) but the Worker proxy route does not serve them. This is a pre-existing infrastructure issue requiring ST# fix.

The media_refs are correctly stored in D1. Once the proxy is fixed, all 10 images will serve.

## Content item ID mapping

```
01-hardest-part -> 7da025e7-9d2e-4b40-b026-90b7b18e1a4f (RESERVE/FLEX)
02-tired-of-demos -> a37aed7c-4008-447b-9e43-c4e28b891c28
03-ai-got-wrong -> 1fd51746-b970-475f-892a-71fb5dbb49b4
04-shipped-4-features -> 33f3dd48-5954-4702-85e2-458078c266a9
05-32-specialist-agents -> 18478c21-b493-4264-848e-8152848a4487
06-40-percent-die -> ca009537-c7bd-4079-8576-ff41c8fe2027
07-delegation-test -> 6153b626-0252-4a82-a71b-cde1261043b1
08-sunday-math -> ae8080e1-f2d0-4f59-b3aa-3871ec589b2e
09-see-the-work -> 0d8af6be-f8d7-499d-8113-7eec33830148
10-stop-guessing-cost -> 542384c5-dc14-4137-b965-075d7e2c5761
```

## Performance

- FLUX Pro 1.1: ~6-10s per image, ~$0.04 each = ~$0.40 for 10 images
- PIL compositing: <1s per image
- Upload to R2: ~2s per image
- Total wall time: ~4 minutes (including 15s rate limit delays)
- Replicate account: jaredspuretech (token verified working 2026-05-04)

## Scripts

- Generator: `/home/jared/projects/AI-CIV/aether/exports/content-batch-images-may5/generate_top10.py`
- Upload+Attach: `/home/jared/projects/AI-CIV/aether/exports/content-batch-images-may5/upload_and_attach.py`
- Manifest: `/home/jared/projects/AI-CIV/aether/exports/content-batch-images-may5/manifest.json`
- Upload results: `/home/jared/projects/AI-CIV/aether/exports/content-batch-images-may5/upload-results.json`
