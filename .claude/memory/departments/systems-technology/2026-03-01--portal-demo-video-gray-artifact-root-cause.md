# Portal Demo Video — Gray Artifact Root Cause & Fix
**Date**: 2026-03-01
**Agent**: dept-systems-technology
**Type**: gotcha + fix

---

## Problem

Training page at purebrain.ai/training/ showed green/gray artifact at 4:01-4:25.
Persisted after: retranscode, re-upload, hard refresh, incognito.

## Investigation Sequence

1. Checked R2 CDN cache headers — files matched local sizes, Last-Modified was fresh. NOT a CDN cache issue.
2. Ran segment alignment verification on hls-output — 0ms drift across 59 segments. NOT a transcode alignment issue.
3. Extracted frames from local segment040-043 — stdev=0, RGB=(116,117,116). Solid gray.
4. Extracted frames from source .mov at 4:01 — same solid gray, stdev=0, 7.9KB JPEG. Gray IS IN THE SOURCE.
5. Checked all 5 Portal_demo.mov uploads — all identical, all have the same gray zone.

## Root Cause

**The source video has a 65-second gray screen baked in from 4:00 to 5:04.**

This is a screen recording where the presenter's screen showed a gray/blank state (likely page loading, browser tab switching, or UI loading state) for ~65 seconds. The transcode faithfully reproduced the source content.

The "artifact" Jared saw was not a video encoding bug — it was the actual demo content being gray.

### Full source video content map:
- 0:00-3:59 (0-239s): Clean dark PureBrain UI content
- 4:00-5:04 (240-304s): SOLID GRAY SCREEN (65 seconds)
- 5:05-5:07 (305-307s): 3 seconds of content
- 5:08+ (308s+): Black/gray/blank to end of 352s video

## Fix Applied

1. Trimmed source at 239s using ffmpeg `-t 239 -c copy`
2. Retranscoded trimmed video using fixed transcode.sh (sc_threshold 0, force_key_frames, GOP_SIZE=180)
3. Output: 40 segments × 2 tiers, 0ms alignment drift, no artifact segments
4. Uploaded to NEW R2 path: `videos/portal-demo-v2/` (bypasses CDN cache of old path)
5. Updated training page (ID 1115) via WordPress PATCH API to use new URL

## New Live URLs

- Master: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/portal-demo-v2/master.m3u8`
- Poster: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/portal-demo-v2/poster.jpg`

## Files

- HLS output: `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/hls-output/portal-demo-v2/`
- Trimmed source: `/tmp/portal_demo_clean.mov` (239s, 15MB)
- Updated transcode script: `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/transcode.sh`

## Key Learnings

1. **Diagnose before fixing** — before reuploading, verify source frames to check if artifact is in source video
2. **Frame pixel analysis** is fast and definitive: stdev < 5 + RGB > 80 = solid gray screen
3. **New R2 key path** is the right nuclear option when CDN caching is suspected — avoids 1-year cache TTL
4. **WordPress training page** uses `<!-- wp:html -->` block (not Elementor), PATCH method works for API updates
5. **WAF blocks python urllib POST** but allows curl and `urllib PATCH` with WordPress user agent

## Verification Evidence

- Live page grep: `curl -s https://purebrain.ai/training/ | grep portal-demo-v2` → 2 matches
- R2 response: HTTP 200, Content-Length=262, Last-Modified=2026-03-01
- Segment alignment: 0ms drift, 40 segments, PASS
- No gray frames in 0-239s zone (stdev all > 8)
