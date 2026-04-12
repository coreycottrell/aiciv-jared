# Brainiac Module 1 Zoom Download — 2026-03-12

**Type**: operations | download pipeline
**Agent**: dept-systems-technology

---

## What Was Done

Downloaded the Brainiac Mastermind Module 1 recording from Zoom API to VPS.

## Meeting Details

- **Topic**: 2103-Module 1 of Brainiac - Mastermind Training / Jared
- **Meeting ID**: 81469491462
- **Date**: 2026-03-04 (started 15:56 UTC)
- **Duration**: 83 minutes
- **File size on disk**: 332MB MP4

## File Location

```
/home/jared/projects/AI-CIV/aether/exports/brainiac-training/downloads/module-1-2026-03-04.mp4
```

## Pipeline Used

- `tools/zoom_api.py list --from 2026-03-01 --to 2026-03-07` — found the recording
- `tools/zoom_api.py download 81469491462 --out <dir> --types MP4` — downloaded MP4 only
- Renamed from verbose Zoom filename to clean `module-1-2026-03-04.mp4`

## Critical Rules Observed

- NO ffmpeg / transcoding on VPS (permanent rule)
- Downloaded MP4 only — transcoding to be done off-VPS
- Transcript and other file types NOT downloaded (not requested)

## Zoom API Notes

- Tokens file: `.credentials/zoom_tokens.json`
- Token was refreshed automatically (expired on load)
- Required scope for recordings: `cloud_recording:read:list_user_recordings` + `cloud_recording:read:list_recording_files` — both present
- API base URL: `https://api-us.zoom.us`
- Meeting type returned as `SHARED_SCREEN_WITH_SPEAKER_VIEW` (standard Zoom recording type for this meeting)

## Next Steps (not done here)

1. Transfer `module-1-2026-03-04.mp4` off-VPS for transcoding to HLS
2. Upload HLS segments to Cloudflare R2
3. Embed video on Brainiac training WP page (ID 1115)
