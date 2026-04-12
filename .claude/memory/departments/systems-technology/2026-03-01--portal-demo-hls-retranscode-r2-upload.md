# Portal Demo HLS Retranscode + R2 Upload
**Date**: 2026-03-01
**Type**: deployment | video-pipeline | artifact-fix

## What Was Done
Re-transcoded Portal demo video (`eaf39ae1_Portal_demo.mov`) using fixed `transcode.sh` (artifact fix 2026-03-01) and uploaded all HLS segments to Cloudflare R2.

## Source
- File: `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/gui/work/uploads/eaf39ae1_Portal_demo.mov`
- Resolution: 1440x900 (source is 900p — 1080p tier correctly skipped)
- Duration: ~353s (5m 53s)
- Frame rate: 299/12 (~24.9fps — treated as ~25fps by ffmpeg)

## Transcode Results
| Tier | Segments | TARGETDURATION | Status |
|------|----------|----------------|--------|
| 360p | 59 | 6s | PASS |
| 720p | 59 | 6s | PASS |
| 1080p | skipped | — | source 900p < 1080p |

**Alignment verification**: 0.0ms drift across all 59 segment boundaries (360p vs 720p). Perfect alignment — ABR switching will be artifact-free.

## The Fix (what transcode.sh.bak-2026-03-01-pre-artifact-fix lacked)
Three bugs fixed in transcode.sh:
1. `-sc_threshold 0` — disables scene-change I-frame injection that caused tier boundary drift
2. `-g GOP_SIZE` + `-keyint_min GOP_SIZE` — enforces strict GOP = 6s
3. `-force_key_frames "expr:gte(t,n_forced*6)"` — guarantees I-frame at EVERY segment boundary
4. `-flags +cgop` — closed GOPs, no cross-segment references
5. `HLS_SEGMENT_TIME=6` — industry-standard 6s VOD (was 2s before, which was being completely ignored)

## R2 Upload
- Bucket: `purebrain-video`
- Key prefix: `videos/portal-demo`
- Files uploaded: 122/122 (59 .ts + 59 .ts + 2 playlists + master + poster)
- All content-types set correctly (.ts = video/mp2t, .m3u8 = application/vnd.apple.mpegurl)

## Live URLs
- **Master playlist**: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/portal-demo/master.m3u8`
- **Poster image**: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/portal-demo/poster.jpg`

## Player Integration
Use master playlist URL in `player-embed.html` `<source>` tag:
```html
<source src="https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/portal-demo/master.m3u8" type="application/vnd.apple.mpegurl">
```

## Key Files
- Script: `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/transcode.sh`
- Old backup: `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/transcode.sh.bak-2026-03-01-pre-artifact-fix`
- Upload script: `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/upload_r2.py`
- Local HLS output: `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/hls-output/eaf39ae1_Portal_demo/`
- Player embed: `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/player-embed.html`

## Pattern: VFR Sources
Source is likely VFR (variable frame rate from screen recording). The `-force_key_frames` expr handles this correctly even with fractional FPS — but if artifacts appear on a different VFR source in future, pre-convert to CFR first:
```bash
ffmpeg -i source.mov -vf fps=30 source_cfr.mp4
```
