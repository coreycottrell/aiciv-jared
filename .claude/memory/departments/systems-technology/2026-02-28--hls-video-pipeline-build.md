# Memory: HLS Video Streaming Pipeline Build
**Date**: 2026-02-28
**Type**: pattern + build record
**Agent**: dept-systems-technology

---

## What Was Built

Self-hosted HLS video streaming pipeline for purebrain.ai on Cloudflare R2.
Zero recurring cost alternative to Mux/Vimeo/Cloudinary.

**Files**:
- `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/transcode.sh`
- `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/upload_r2.py`
- `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/player-embed.html`
- `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/README.md`

---

## Key Technical Decisions

### FFmpeg HLS encoding
- Three tiers: 360p/500kbps, 720p/2000kbps, 1080p/4500kbps
- Segment duration: 2 seconds (fast ABR switching)
- Codec: H.264 (libx264) + AAC — maximum device compatibility
- Pixel format: yuv420p — required for Safari/iOS
- Profile: main — broad compatibility without baseline limitations
- Preset: veryfast — good compression/speed tradeoff for server use
- Scale filter: `scale=W:-2,pad=W:H:...` — handles non-standard aspect ratios without black bars

### Cloudflare R2 upload
- boto3 S3-compatible client with `endpoint_url = https://{account_id}.r2.cloudflarestorage.com`
- Region: "auto" — R2 requirement, not a real AWS region
- Signature: s3v4 required
- Content-Type headers: .m3u8 = `application/vnd.apple.mpegurl`, .ts = `video/mp2t`
- Cache-Control: .ts segments get 1-year cache (immutable), .m3u8 playlists get 5-minute cache

### Player
- hls.js from CDN pinned to 1.5.7 (not @latest — stability)
- Safari detection: `video.canPlayType('application/vnd.apple.mpegurl')` — uses native HLS, no hls.js
- UNIQUE_ID pattern: allows multiple players per page without ID collision
- Autoplay: muted + loop + playsinline (Harvey.ai style for product demos)
- Error recovery: network errors → hls.startLoad(), media errors → hls.recoverMediaError()

---

## Environment State

- FFmpeg: NOT installed on this machine (server needs `sudo apt install -y ffmpeg`)
- Cloudflare R2 credentials: NOT in .env (CF_ACCOUNT_ID, R2_ACCESS_KEY, R2_SECRET_KEY needed)
- R2 bucket: `purebrain-video` (needs to be created in Cloudflare dashboard)
- R2 public access: must be enabled manually in R2 dashboard settings

---

## Security Review Findings (PASS)
- No hardcoded credentials — environment variable pattern only
- No shell injection — bash uses quoted variables + strict mode
- No eval/exec/system calls in Python
- No rm -rf patterns
- hls.js pinned to specific version, not floating latest

---

## Patterns for Future Use
- R2 key prefix convention: `videos/<type>/<slug>` (demo, testimonials, tutorials, hero, sales)
- .env loading pattern in upload_r2.py (load_dotenv function) is reusable for other R2 tools
- UNIQUE_ID player pattern should be used any time multiple video embeds appear on same WP page
