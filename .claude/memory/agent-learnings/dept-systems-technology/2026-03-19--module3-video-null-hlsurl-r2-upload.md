# Module 3 Video: Null hlsUrl — R2 Upload Missing

**Date**: 2026-03-19
**Type**: operational
**Topic**: Brainiac Training page Module 3 video not playing — hlsUrl was null, MP4 never uploaded to R2

## Root Cause

Module 3 was added to the TRAINING_VIDEOS array in the HTML with `status: "live"` but `hlsUrl: null`. The session recording existed on disk but was never uploaded to Cloudflare R2.

When a video card has `status: "live"` but `hlsUrl: null`, the player opens the modal but has no src — video silently fails to play.

## Fix Applied

1. Uploaded `exports/brainiac-training/downloads/2026-03-18/...mp4` (189MB) to R2
2. R2 path: `brainiac/recordings/module-3/full.mp4`
3. Public URL: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/brainiac/recordings/module-3/full.mp4`
4. Updated hlsUrl in brainiac-mastermind-training/index.html
5. Deployed to purebrain-staging

## R2 Credentials Location

`tools/video-pipeline/gui/.env` — CF_ACCOUNT_ID, R2_ACCESS_KEY, R2_SECRET_KEY
Account ID: 19bb52a20bc7fc1b34036fea91f6860c
Bucket: purebrain-video
Public base: https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/

## Training Page Video Pattern

All modules use direct MP4 URLs (NOT HLS):
- Module 1: brainiac/recordings/module-1/full.mp4
- Module 2: brainiac/recordings/module-2/full.mp4
- Module 3: brainiac/recordings/module-3/full.mp4

## Checklist For Adding New Modules

1. Download recording -> exports/brainiac-training/downloads/YYYY-MM-DD/
2. Upload MP4 to R2 brainiac/recordings/module-N/full.mp4 (use boto3 multipart)
3. Verify: curl -sI URL | grep "200\|Accept-Ranges"
4. Update hlsUrl in TRAINING_VIDEOS array in brainiac-mastermind-training/index.html
5. Deploy to purebrain-staging
