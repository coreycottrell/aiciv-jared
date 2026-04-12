# Memory: Zoom → R2 → Brainiac Training Pipeline Build
**Date**: 2026-03-12
**Type**: build record + patterns + blocker
**Agent**: dept-systems-technology

---

## What Was Built

Full 7-step automated pipeline: Zoom Cloud Recording → HLS Transcode → R2 → WP Page → AI Summary → Skill

**Files created**:
- `tools/zoom_api.py` — Zoom API helper (token refresh, list recordings, download, transcript extraction)
- `tools/zoom_brainiac_pipeline.py` — 7-step pipeline orchestrator with retry + Telegram updates
- `exports/brainiac-training/modules/` — Per-session training module storage (JSON + MD)
- `.claude/skills/brainiac-training/SKILL.md` — Fleet skill for accessing training content

---

## Architecture Decisions

### Token refresh pattern
- Zoom access tokens expire in 1 hour
- `zoom_api.py` auto-refreshes on every call using `saved_at` + `expires_in` fields from token file
- 5-minute proactive buffer prevents mid-session expiry
- On 401 from API: force refresh and retry once
- Token file: `.credentials/zoom_tokens.json`

### Scope detection
- Zoom returns HTTP 400 (not 403!) with JSON body containing "scope" when scopes are missing
- Detection: `"scope" in body_text.lower() or "access token" in body_text.lower()`
- Exact required scopes (confirmed from API error message):
  - `cloud_recording:read:list_user_recordings`
  - `cloud_recording:read:list_user_recordings:admin`

### Download streaming
- Large video files streamed in 8MB chunks — never loaded to RAM
- Timeout set to 600s (10 min) for large recordings
- Token passed as query param `?access_token=` (not header) because download URLs redirect and headers don't follow

### VTT transcript parsing
- Zoom transcripts are WebVTT format
- `_vtt_to_text()` strips: WEBVTT header, cue numbers, timestamps, speaker tags `<v Name>`, inline timestamp tags `<00:01:23>`
- Returns plain text lines joined with \n

### HLS integration
- Uses existing `tools/video-pipeline/transcode.sh` (artifact-fixed version from 2026-03-01)
- R2 path convention: `brainiac/recordings/YYYY-MM-DD/`
- Poster URL: same path but `poster.jpg` instead of `master.m3u8`

### WP page pattern
- Page ID: 1115 (purebrain.ai/brainiac-mastermind-training/)
- Template: elementor_canvas (no WP chrome)
- Wrapped in `<!-- wp:html -->` block
- Video library: JS array `VIDEO_LIBRARY` at top of inline script
- Password gate: sessionStorage-based, password `brainiac2026`
- Modal player: hls.js@1.5.7 pinned, Safari native HLS fallback

### Training summary generation
- Tries `claude -p "..."` CLI first (if available)
- Falls back to pattern extraction from transcript text
- Module JSON schema: key_topics, action_items, frameworks_taught, tools_referenced, implementation_steps, key_quotes, skill_tags

---

## BLOCKER: Zoom OAuth Scope Missing

Current token does NOT have recording access scope.

**Status confirmed**: `python3 tools/zoom_api.py status` shows no recording scope.

**Fix required** (one-time, Jared must do this in browser):
1. https://marketplace.zoom.us/develop/apps → OAuth app → Scopes
2. Add: `cloud_recording:read:list_user_recordings`
3. Add: `cloud_recording:read:list_user_recordings:admin`
4. Re-authorize the app (new OAuth flow → new refresh token with recording scope)
5. New tokens save automatically to `.credentials/zoom_tokens.json`

**After fix**: Run `python3 tools/zoom_api.py list` to verify, then `--manual` the pipeline.

---

## Scheduling (Not Yet Configured)

Pipeline is designed to fire every Wednesday at 2:30pm ET.
Add to `.claude/scheduled-tasks-state.json`:
```json
{
  "id": "brainiac-zoom-pipeline",
  "name": "Brainiac Zoom Recording Pipeline",
  "schedule": "Wednesday 14:30 ET",
  "command": "python3 /home/jared/projects/AI-CIV/aether/tools/zoom_brainiac_pipeline.py",
  "retry_times": ["15:00", "15:30", "16:00"]
}
```

---

## Dry Run Verification

All 7 steps pass in dry run mode:
```
Step 1: DRY RUN mock recording returned
Step 2: DRY RUN download skipped
Step 3: DRY RUN transcode skipped
Step 4: DRY RUN mock R2 URL constructed
Step 6: Module JSON + MD saved to exports/brainiac-training/modules/
Step 5: DRY RUN page update skipped
Step 7: DRY RUN skill update skipped
```

---

## Key Commands

```bash
# Check token status and scope
python3 tools/zoom_api.py status

# List recordings (requires recording scope)
python3 tools/zoom_api.py list

# Find latest Brainiac recording
python3 tools/zoom_api.py find-brainiac

# Dry run full pipeline
python3 tools/zoom_brainiac_pipeline.py --dry-run --manual

# Run pipeline now (any day)
python3 tools/zoom_brainiac_pipeline.py --manual

# Run specific step only
python3 tools/zoom_brainiac_pipeline.py --step 1 --manual
```
