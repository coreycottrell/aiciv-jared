# Memory: Portal Demo Video Recording — Enhanced v1

**Date**: 2026-02-28
**Type**: operational + teaching
**Topic**: Headless Playwright recording of portal chatbox interaction, R2 + Mux delivery

---

## Summary

Built and executed a full automated video recording pipeline for the PureBrain portal demo.
Records real AI chatbox interactions, payment/conversion flow, success state.
Delivers to both Cloudflare R2 (HLS) and Mux.

---

## Key Outputs

- **R2 HLS**: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/demo/portal-enhanced-v1/master.m3u8`
- **Mux Playback ID**: `XieKa12DScxH01Qt01w5BrGtD01GfCjjk02qB7wREYGGCjE`
- **Mux Stream**: `https://stream.mux.com/XieKa12DScxH01Qt01w5BrGtD01GfCjjk02qB7wREYGGCjE.m3u8`
- **Duration**: 2 min 12 sec, 9.1 MB MP4

---

## Critical Learnings

### Page State (2026-02-28)
- Page 688 (pay-test-sandbox-2) NO LONGER has the PayPal bypass flow
- `pb-full-bypass` bypass code REMOVED
- `#pb-sandbox-bypass-btn` REMOVED
- Current conversion CTA: Waitlist modal (not PayPal)
- "Activate Now" (`#proCta`) → `openWaitlistModal('Bonded')` → `#waitlistModal`

### WP REST API Auth
- Always read credentials directly from `.env` file via custom `load_dotenv()`
- Never trust `os.environ.get()` — shell may have stale/empty values
- Use `urllib.request.build_opener()` not `urllib.request.urlopen()` — handles redirects

### HLS 1440x900 Transcode
- transcode.sh's 360p tier breaks with `Error reinitializing filters!` on non-16:9 sources
- Fix: `scale=W:H:force_original_aspect_ratio=decrease,pad=W:H:(ow-iw)/2:(oh-ih)/2:black`

### Mux API (2026-02-28 Current)
- `mp4_support: 'standard'` is DEPRECATED — returns 400 Bad Request
- Use direct upload (POST /video/v1/uploads) then PUT the MP4 file
- Mux CANNOT ingest HLS/m3u8 — must send raw MP4
- Processing time: ~10-15 seconds for a 9MB file

---

**Tags**: playwright, video, recording, r2, mux, hls, portal, chatbox, pay-test-sandbox-2
