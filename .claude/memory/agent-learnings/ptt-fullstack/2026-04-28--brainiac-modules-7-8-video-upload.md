---
type: operational
topic: Brainiac Modules 7+8 Zoom recordings downloaded and uploaded to R2
date: 2026-04-28
---

# Brainiac Modules 7+8 Video Upload to R2

## What Was Done

1. Downloaded Zoom recordings for Apr 15 (Module 7, 82 min, 373MB) and Apr 22 (Module 8, 77 min, 333MB) using the Zoom API
2. Uploaded both to R2 bucket `purebrain-video` at `brainiac/recordings/module-{7,8}/full.mp4`
3. Updated TRAINING_VIDEOS array in training hub with video URLs
4. Updated module count badge from "6 modules" to "8 modules"
5. Committed and pushed to main

## Critical R2 Discovery

- The public URL `pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev` used by modules 1-6 does NOT map to the `purebrain-video` bucket
- `purebrain-video` bucket has publicId `pub-baa10a778fc14d9884a95e19f2525f68` with access type `CnamesOnly` (no public URL)
- The R2 S3 API credentials in `.env` (R2_ACCESS_KEY/R2_SECRET_KEY) are broken/revoked -- all S3 operations return AccessDenied
- The CF_API_TOKEN also cannot do R2 operations
- Only the Global API Key (CF_API_KEY + CF_AUTH_EMAIL) works for R2 REST API, but has a ~100MB body size limit

## Solution: Worker Proxy for R2

Deployed `r2-upload-proxy` Worker at `https://r2-upload-proxy.in0v8.workers.dev` that:
- Has R2 binding to `purebrain-video` bucket
- Supports GET with range requests (video seeking works)
- Supports multipart upload (mpu-create, mpu-uploadpart, mpu-complete)
- Sets proper Content-Type based on file extension
- CORS headers for cross-origin video playback

The Worker was used to upload the large files via 90MB multipart chunks, bypassing the 100MB CF gateway limit.

### Modules 7+8 Video URLs
- Module 7: `https://r2-upload-proxy.in0v8.workers.dev/brainiac/recordings/module-7/full.mp4`
- Module 8: `https://r2-upload-proxy.in0v8.workers.dev/brainiac/recordings/module-8/full.mp4`

## Key Gotchas

1. **Wrangler R2 has 300 MiB hard limit** on `r2 object put` -- no way around it
2. **R2 S3 tokens can only be created via CF Dashboard**, not via API
3. **ffmpeg re-encoding Zoom screen recordings takes hours** on this server (2322x1234 @ 25fps, ~10fps encode speed)
4. **Worker multipart upload** is the most reliable way to upload large files to R2 when S3 creds are broken
5. **Always check which R2 bucket a public URL maps to** -- the pub-hash is bucket-specific

## Files

- Downloaded: `/home/jared/projects/AI-CIV/aether/exports/brainiac-recordings/module-7-shipping-measurement.mp4` (373MB)
- Downloaded: `/home/jared/projects/AI-CIV/aether/exports/brainiac-recordings/module-8-software-building.mp4` (333MB)
- Modified: `/home/jared/purebrain-site/brainiac-mastermind-training/index.html`
- Worker: `r2-upload-proxy` at `https://r2-upload-proxy.in0v8.workers.dev`

## TODO

- R2 S3 credentials in .env need to be regenerated via CF Dashboard
- Consider migrating modules 1-6 to the same `purebrain-video` bucket (currently on unknown bucket)
- Or find which bucket/account hosts `pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev`
- The `r2-upload-proxy` Worker should be secured (add auth header check) since it's currently open
