# Video Artifact Root Cause: R2 Path Mismatch + Source is MP4 Not HLS

**Date**: 2026-03-01
**Agent**: devops-engineer / dept-systems-technology
**Type**: gotcha + root-cause + fix
**Tags**: video, hls, r2, artifact, green-gray, purebrain, training-page

---

## Problem

Green/gray artifact at ~4:01-4:25 in Portal Demo video. Persisted after retranscode.

---

## Investigation Findings

### There are MULTIPLE video delivery systems on purebrain.ai

| Page | Video URL | Format |
|------|-----------|--------|
| purebrain.ai/ (homepage) | `wp-content/uploads/2026/02/Pure-Brain-Demo-Video-real-compression-and-sizing.mp4` | Direct WordPress MP4 |
| purebrain.ai/training/ | `videos/eaf39ae1_Portal_demo/master.m3u8` | R2 HLS |
| purebrain.ai/?p=688 (pay-test-sandbox-2) | Same WordPress MP4 | Direct MP4 |
| purebrain.ai/?p=689 (pay-test-2) | Same WordPress MP4 | Direct MP4 |
| purebrain.ai/video-test/ | `videos/demo/portal-enhanced-v1/master.m3u8` | R2 HLS |

### Root Cause of Artifact

The previous retranscode uploaded fixed HLS files to `videos/portal-demo/` on R2 but the LIVE training page used `videos/eaf39ae1_Portal_demo/master.m3u8`.

`eaf39ae1_Portal_demo` still had the OLD buggy HLS with:
- TARGETDURATION:10 (should be 6)
- Wildly inconsistent segment durations (2.6s, 4.8s, 10.0s, etc.)
- Different segment boundaries between 360p and 720p tiers
- When HLS.js switches renditions, it seeks to wrong keyframe → green/gray flash

### Why the Retranscode Did Not Fix It

The retranscode pipeline uploaded to a NEW path `videos/portal-demo/` instead of OVERWRITING the live path `videos/eaf39ae1_Portal_demo/`. The live training page was never updated to point to the new path.

---

## Fix Applied (2026-03-01)

Used Python boto3 to copy all 122 objects from `videos/portal-demo/` to `videos/eaf39ae1_Portal_demo/` in the `purebrain-video` R2 bucket.

```python
client.copy_object(
    Bucket='purebrain-video',
    CopySource={'Bucket': 'purebrain-video', 'Key': src_key},
    Key=dst_key
)
```

All 122 files copied with 0 errors.

---

## Verification

| Check | Before | After |
|-------|--------|-------|
| TARGETDURATION | 10 | 6 |
| 360p segment range | 2.6-10.0s | 4.977-6.020s |
| 720p segment range | 2.6-10.0s | 4.977-6.020s |
| Segment count match | Mismatched | 59 == 59 |
| Segment at 4:01 | Buggy | PASS (exists, correct duration) |

---

## Key Lesson: Always Check the Actual Live URL

When Jared reports a video artifact:
1. Intercept network requests to find the ACTUAL URL being loaded
2. Check `openVideoModal()` function and `window.pbDemoPlay` for the video src
3. The live URL may differ from what was retranscoded

## Source File Findings

- Homepage/pay-test pages use DIRECT WordPress MP4 (not HLS)
- MP4 source: `Pure-Brain-Demo-Video-real-compression-and-sizing.mp4` (316.5s, 86MB, H.264 bt709)
- The source MP4 has NO green artifact in the 4:01-4:25 range
- Green artifact is exclusively a HLS rendition-switch bug (segment boundary mismatch)

## R2 Path Map

| R2 Key Prefix | Video | Status |
|--------------|-------|--------|
| `videos/eaf39ae1_Portal_demo/` | Portal Demo (training page LIVE) | Fixed 2026-03-01 |
| `videos/portal-demo/` | Portal Demo (retranscode target, nobody points here) | Fixed, unused |
| `videos/c64e418d_purebrain-demo-video/` | Unknown/old | Untouched |
| `videos/75114256_Pure-Brain-Demo-Video/` | Full demo video | Untouched |
| `videos/demo/portal-enhanced-v1/` | Video test page | Untouched |
