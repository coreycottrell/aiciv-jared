# Memory: Brainiac Transcript Extraction

**Date**: 2026-03-12
**Agent**: dept-systems-technology
**Task**: Extract transcripts from Brainiac Module 1 and Module 2 recordings

---

## What Was Done

### Module 2 (March 11, 2026)
- Zoom auto-generated VTT was already present at: `exports/brainiac-training/downloads/2026-03-11/...f469f241.vtt`
- 1,970 lines, 96KB — complete session transcript
- Converted to clean plain text: `exports/brainiac-training/transcripts/module-2-transcript.txt`

### Module 1 (March 4, 2026)
- No transcript in the downloads directory — only the .mp4
- Used `tools/zoom_api.py` to download the AUDIO_TRANSCRIPT file type via Zoom API
- Meeting ID: 81469491462 (found via `python3 tools/zoom_api.py list --from 2026-03-03 --to 2026-03-06`)
- Downloaded to: `exports/brainiac-training/transcripts/2026-03-04_...612f25db.vtt`
- 2,570 lines, 126KB
- Converted to clean plain text: `exports/brainiac-training/transcripts/module-1-transcript.txt`

### Conversion Script
VTT to plain text conversion done via inline Python. Parses speaker labels and timestamps from Zoom VTT format. Results in human-readable transcript with bold speaker labels and timestamps.

### Summary Updates
Both module summaries were fully rewritten with transcript content:
- `exports/brainiac-training/summaries/module-1-foundations.md` — 18.6KB
- `exports/brainiac-training/summaries/module-2-workflows.md` — 20KB
- Zero [NEEDS TRANSCRIPT] placeholders remain in either file

---

## Patterns Learned

### Zoom API Transcript Download
```bash
# List recordings for a date range
python3 tools/zoom_api.py list --from 2026-03-03 --to 2026-03-06

# Download only the transcript (not the full video)
python3 tools/zoom_api.py download <meeting_id> --out /path/to/dir --types TRANSCRIPT
```
- File type is `TRANSCRIPT` in the download command
- The API automatically refreshes the OAuth token from `.credentials/zoom_tokens.json`
- Tokens file location: `.credentials/zoom_tokens.json`

### Zoom VTT Format
- Zoom auto-generates VTT files with speaker names included in the cue text
- Format: `SpeakerName: transcript text`
- Speaker names include full titles (e.g., "Jared Sanborn | Pure Technology | CEO | NYC")
- 1 hour of meeting = approximately 500-650 VTT entries = ~70-90KB clean text

### Whisper Not Needed
- Whisper was not installed and would not have been needed anyway
- Zoom provides free auto-transcripts for all recorded meetings
- Zero CPU cost, much higher quality than local Whisper would have been

---

## File Paths

| File | Description |
|------|-------------|
| `exports/brainiac-training/transcripts/module-1-transcript.txt` | Module 1 clean plain text |
| `exports/brainiac-training/transcripts/module-2-transcript.txt` | Module 2 clean plain text |
| `exports/brainiac-training/transcripts/2026-03-04_...vtt` | Module 1 raw Zoom VTT |
| `exports/brainiac-training/summaries/module-1-foundations.md` | Module 1 AI-ready summary (complete) |
| `exports/brainiac-training/summaries/module-2-workflows.md` | Module 2 AI-ready summary (complete) |
