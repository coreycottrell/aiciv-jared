# Memory: Video Portal Team Usability Improvements

**Date**: 2026-03-01
**Type**: feature | pattern | product-decision
**Product**: video.purebrain.ai

---

## What Was Done

Self-diagnosed and implemented Priority 1 team usability improvements to the video.purebrain.ai portal after Jared confirmed the core pipeline "WORKS GREAT."

## Key Findings from Audit

### Current Stack (what exists)
- FastAPI backend (server.py, 979 lines before changes) at `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/gui/`
- Single-page frontend (index.html, 1176 lines before changes)
- Jobs persisted to `work/jobs.json` — survive restarts
- API routes: upload, transcode, upload-r2, mux, jobs CRUD, library, embed, storage, retranscode, tags, description, rename, bulk-delete

### Critical Gaps Found
1. No one-click pipeline (transcode + R2 required two manual steps with waiting)
2. Transcoding showed only a spinner — no progress %, team didn't know if stuck
3. No direct URL copy — only full embed code, had to manually extract URL
4. Library delete silently failed for R2-only videos (no local job match)
5. Storage header showed only local bytes, not R2 total

## What Was Implemented (Priority 1)

### Backend (server.py — 979 → 1254 lines)
1. **`POST /api/pipeline/{job_id}`** — chains `_run_transcode` then `_run_r2_upload` automatically
2. **`GET /api/jobs/{job_id}/log`** — returns last 50 lines of FFmpeg output (transcode_log field)
3. **`POST /api/jobs/{job_id}/poster`** — accepts image upload, resizes with Pillow, uploads to R2
4. **`DELETE /api/library`** — deletes R2 prefix directly (works without local job)
5. **Progress tracking** — `_run_transcode` now streams stdout line-by-line, parses `time=HH:MM:SS` via regex, writes `progress_pct: 0-100` to job state every few seconds
6. **R2 storage** — `/api/storage` now sums R2 object sizes via paginator, returns `total_r2_bytes`
7. **`POST /api/transcode/{job_id}`** — now accepts optional JSON body with `preset` field (was URL-only before)
8. Added `import re` and `import io` to top-level imports

### Frontend (index.html — 1176 → 1282 lines)
1. **"Run Pipeline" button** — orange gradient, appears for uploaded/failed jobs, calls `/api/pipeline/`
2. **Progress bar** — thin gradient bar (blue to orange) under transcoding badge, shows `47%` label
3. **"Copy URL" button** — appears on Ready job rows and in detail tab next to master URL
4. **R2 storage in header** — shows "| 2.3 GB R2" next to local storage
5. **Poster upload zone** — click/drop image in detail tab for Ready jobs, calls `/api/jobs/{job_id}/poster`
6. **Log viewer** — "View FFmpeg Log" button on failed jobs expands monospace log (last 50 lines)
7. **Library delete fix** — falls back to `deleteLibraryVideoByPrefix()` which calls `DELETE /api/library`
8. **`progressBarHtml(job)` function** — renders progress bar for transcoding/uploading states
9. **Updated `handleAction`** — added `pipeline` and `copy-url` cases
10. **Updated `loadStorageStats`** — reads and displays `total_r2_bytes`

## Patterns Learned

- The index.html uses template literal syntax (`\`...\${}\``) extensively — Python string replacements of JS template strings must handle escaped backticks carefully
- The actual function signatures in index.html differ from README docs — always read the source, not the docs
- `buildQueueActions` uses array push pattern (`b.push(...); return b.join('')`), not string concatenation — regex pattern matching against README description would have failed
- FFmpeg progress parsing: `time=HH:MM:SS.ms` appears in stderr lines during encoding passes; need to capture process stdout (piped from stderr via `STDOUT`) line by line without `communicate()` to get streaming updates
- `asyncio.create_subprocess_exec` + `readline()` loop = correct approach for streaming FFmpeg output
- R2 storage sum via paginator is slow (network call) — acceptable for the storage endpoint which is polled infrequently; wrap in executor

## Files Changed
- `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/gui/server.py` (979 → 1254 lines)
- `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/gui/index.html` (1176 → 1282 lines)

## PRD Location
`/home/jared/projects/AI-CIV/aether/exports/departments/product-development/specs/2026-03-01--video-portal-team-usability-prd.md`

## Remaining Backlog (not implemented)
- Priority 2: Keyboard shortcuts, bulk embed export, category folders in library
- Pillow dependency must be installed for poster resize: `pip install pillow`
