# Memory: Portal Demo Video Pipeline — Enhanced v1

**Date**: 2026-02-28
**Type**: pattern + operational
**Agent**: dept-systems-technology
**Topic**: Headless Playwright video recording of PureBrain portal with chatbox interaction + R2/Mux delivery

---

## What Was Built

Full automated video recording pipeline for portal demo videos. Records a real Playwright session against the PureBrain pay-test-sandbox-2 page with actual chatbox interactions.

### Recording Script
- **File**: `tools/video-pipeline/record_portal_demo.py`
- **Purpose**: Headless Playwright recording of portal with chatbox + payment flow
- **Output**: WebM → MP4 → HLS → R2 + Mux

---

## Architecture

```
WP REST API (page 688)
    |
    v
Local HTTP server (Python, port 9878)
    |
    v
Playwright (Chromium headless, record_video_dir)
    |
    v
.webm file (Playwright native format)
    |
    v
ffmpeg → MP4 (H.264, 1440x900)
    |
    v
Custom HLS transcode (720p + 1080p tiers)
    |
    v
R2 upload (upload_r2.py)
    |
    v
Mux direct upload (MP4 PUT)
```

---

## Video URLs (First Recording, 2026-02-28)

- **R2 HLS**: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/demo/portal-enhanced-v1/master.m3u8`
- **R2 Poster**: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/demo/portal-enhanced-v1/poster.jpg`
- **Mux Playback ID**: `XieKa12DScxH01Qt01w5BrGtD01GfCjjk02qB7wREYGGCjE`
- **Mux Stream**: `https://stream.mux.com/XieKa12DScxH01Qt01w5BrGtD01GfCjjk02qB7wREYGGCjE.m3u8`
- **Mux Asset ID**: `JCCVgSf5koCE3lkmmOvA900cNfCSroVMuEgzy00dzJf1k`
- **R2 Key**: `videos/demo/portal-enhanced-v1`
- **Duration**: 132.96 seconds

---

## Key Patterns and Gotchas

### 1. WP REST API Auth — Load from .env Directly
- `os.environ.get()` fails if shell has stale/empty env vars
- Always use `_dotenv.get("KEY") or ""` to read from .env file directly
- Use `urllib.request.build_opener()` not bare `urlopen()` — handles redirects correctly

### 2. Page Structure: pay-test-sandbox-2 (page 688) vs pay-test-2 (page 689)
- Page 688 = sandbox-2 = has SANDBOX MODE banner, sandbox PayPal client ID
- Page 689 = production pay-test-2 = no sandbox bypass button
- `pb-full-bypass` bypass code and `#pb-sandbox-bypass-btn` were in OLDER versions (pre-2026-02-27)
- Current page 688 uses WAITLIST MODAL when "Activate Now" is clicked
- Selector for "Activate Now": `#proCta` (visible after scrolling)

### 3. HLS Transcode — Aspect Ratio Handling
- Source is 1440x900 (1.6:1 ratio) — NOT standard 16:9 (1280:720)
- transcode.sh's 360p tier (640x360) fails with `Error reinitializing filters!` on 1440:900
- Solution: custom HLS transcode using scale with `force_original_aspect_ratio=decrease` + `pad` filter
- Only use 720p and 1080p tiers for 1440:900 source

```bash
# Correct scale filter for non-standard aspect ratios:
scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black
```

### 4. Mux — Direct Upload Flow
- DO NOT use `mp4_support: 'standard'` in new_asset_settings — deprecated, returns 400
- DO NOT pass HLS m3u8 URL as input — Mux rejects HLS files as "not a valid video"
- CORRECT flow: create upload → GET upload URL → PUT mp4 file → poll upload.asset_id → get playback_id
- Mux processes in ~10-15 seconds for a 9MB MP4

### 5. Playwright Video Recording
- Use `record_video_dir` + `record_video_size` in `new_context()` — automatic .webm capture
- Video only finalizes when `context.close()` is called — must close context before reading .webm
- `bypass_csp=True` is required for locally-served pages to call external APIs (Worker proxy)
- `#proCta` is hidden (CSS `display:none`) until pricing section is visible — use JS click fallback

### 6. WAF-Safe Strategy (Still Valid)
- WP REST API with Basic auth (user: Aether, PUREBRAIN_WP_APP_PASSWORD)
- Serve locally on localhost — no WAF, no password form submission
- All chatbox JS calls external Worker proxy — works from localhost with bypass_csp=True

---

## Current Flow Recorded

1. Page load — hero with video background
2. Begin Awakening — chatbox opens
3. AI awakening messages (Claude via Worker proxy)
4. User types "My name is Alex" — AI responds
5. Scroll to pricing section
6. "Activate Now" clicked — waitlist modal opens
7. Form filled — name, email, rating buttons
8. Form submitted — success state shown

---

## Files

| File | Description |
|------|-------------|
| `tools/video-pipeline/record_portal_demo.py` | Main recording script |
| `tools/video-pipeline/upload_r2.py` | R2 HLS uploader |
| `tools/video-pipeline/transcode.sh` | transcode.sh (has 360p aspect ratio bug with 1440:900) |
| `/tmp/portal-demo-enhanced.mp4` | Latest MP4 (9.1 MB, 132s) |
| `/tmp/hls/portal-demo-enhanced-v1/` | HLS segments (720p + 1080p) |
| `/tmp/portal-demo-raw/*.png` | 7 screenshots from recording |
| `/tmp/portal-demo-results.json` | URLs and metadata |

---

## Re-running

To re-record:
```bash
python3 tools/video-pipeline/record_portal_demo.py
```

To upload a new version without re-recording:
```bash
# Transcode existing MP4
bash tools/video-pipeline/transcode.sh /tmp/portal-demo-enhanced.mp4 /tmp/hls/portal-demo-v2

# Upload to R2 with new key
python3 tools/video-pipeline/upload_r2.py \
  --dir /tmp/hls/portal-demo-v2 \
  --key videos/demo/portal-enhanced-v2
```

**Tags**: purebrain, video, playwright, r2, mux, hls, chatbox, portal-demo, recording, pipeline
