# Standalone Banner Fix - FLUX + PIL Pipeline

**Date**: 2026-04-23
**Type**: operational
**Agent**: 3d-design-specialist

## Context
Fixed 12 standalone LinkedIn banners (1080x1350) that had alignment issues (shifted right, black space left, text cut off right).

## What Worked
- FLUX Pro via Replicate for backgrounds (1080x1080 square, then positioned in 1080x1350 canvas)
- PIL overlay with Oswald Bold for text (top bar, title, bottom bar)
- All elements computed relative to canvas center (WIDTH//2) for guaranteed centering
- 5 unique FLUX backgrounds for 12 posts (grouped by content theme to save API calls and credits)

## Key Parameters
- FLUX: width=1080, height=1080, guidance=3.5, num_inference_steps=28
- PIL fonts: title=72px, wordmark=22px, subtitle=24px, CTA=22px
- Dark overlay gradients for text readability over FLUX background
- Rate limit: Replicate throttles at 6 req/min when balance <$5 (15s delay between FLUX calls)

## Gotchas
- R2 public URL (pub-XXX.r2.dev) returns 404 - public access not enabled on purebrain-uploads bucket
- social.purebrain.ai /media/ proxy also returns 404 - deployment issue
- Upload API works fine (POST /api/uploads with Bearer token)
- D1 media_refs format: plain R2 key string (e.g. "user-id/timestamp-rand-filename.jpg")
- Some posts in D1 use JSON array format for media_refs, others use plain key string

## Social API Auth
- Login: POST https://social-api.in0v8.workers.dev/api/login with email/password
- Upload: POST /api/uploads with multipart form, file field
- Credentials: jared@puretechnology.nyc / PureBrain2026!

## Files
- Script: /home/jared/projects/AI-CIV/aether/exports/standalone-banner-fix/generate_banners.py
- Raw FLUX: /home/jared/projects/AI-CIV/aether/exports/standalone-banner-fix/flux-raw/
- Final banners: /home/jared/projects/AI-CIV/aether/exports/standalone-banner-fix/final/
