# Video Pipeline Hub Expansion
Date: 2026-02-28
Type: build

## What Was Built
Major feature expansion to video.purebrain.ai (port 8765).

### Files Modified
- `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/gui/server.py` (26.5KB → 35KB)
- `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/gui/index.html` (49KB → 66KB)

## Backend — New Endpoints
1. `DELETE /api/jobs/{job_id}` — ENHANCED: now accepts `?delete_r2=true&delete_local=true` query params. Deletes local upload file, local HLS dir, and optionally batch-deletes all R2 objects under the r2_prefix.
2. `POST /api/jobs/{job_id}/retranscode` — Re-transcode with optional preset (web/hd/full). Clears old HLS dir first.
3. `PATCH /api/jobs/{job_id}/tags` — Set tags array on a job (max 10, max 30 chars each)
4. `PATCH /api/jobs/{job_id}/description` — Set description text (max 500 chars)
5. `DELETE /api/jobs` (bulk) — Bulk delete with same local+R2 options
6. `GET /api/storage` — Storage stats: total local bytes, per-job breakdown sorted by size

## Frontend — New Features
1. **Delete with confirmation modal** — trash icon on every queue card. Modal shows video name, R2 checkbox (default unchecked), cancel/confirm. Library cards also get delete button (hover-reveal).
2. **Search/filter bar** — text search by name/slug + status filter chips (All/Uploaded/Ready/Failed)
3. **Sort options** — Newest/Oldest/Name A-Z/Name Z-A/Largest/Smallest
4. **Bulk select + bulk delete** — toggle bulk mode button activates checkboxes on cards. Bulk bar shows count + Delete Selected button with its own modal.
5. **Thumbnails in queue cards** — 44x28px poster preview on every card that has a poster_url
6. **Storage stats in header** — gradient progress bar + local storage total
7. **Re-transcode button** — on Ready cards and in Detail panel. Failed cards get "Retry" button.
8. **Quality preset selector** — Web (360+720p) / HD (720+1080p) / Full (all tiers). Shown in Detail panel before transcode actions.
9. **Tags system** — tag pills with add/remove UI in Detail tab. Synced to backend.
10. **Description field** — textarea in Detail tab with Save button.
11. **Inline video preview** — HLS player embedded in Detail tab for ready videos.
12. **Library search** — filter R2 library by slug name.

## Key Patterns
- Delete uses `?delete_r2=false` default (safety first)
- R2 bulk deletion uses boto3 paginator + batch delete_objects (max 1000/call)
- Bulk mode checkbox state tracked via `bulkSelected` Set
- All confirmation dialogs use `<template>` element + cloneNode pattern (no global DOM pollution)
- Storage bar uses 50GB as reference max (visual only)
- `_run_transcode` now accepts preset= and passes it via env var TRANSCODE_PRESET

## Verification
- Server syntax: clean (python3 compile check)
- Server health: OK (FFmpeg, R2, Mux all connected)
- /api/storage: Live, returned 226MB across 4 jobs
- All 23 frontend feature checks: PASS
- All 8 backend route checks: PASS
- Server running on port 8765
