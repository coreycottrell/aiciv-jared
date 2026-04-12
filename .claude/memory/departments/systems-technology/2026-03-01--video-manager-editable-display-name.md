# Video Manager: Editable Display Name in Job Detail

**Date**: 2026-03-01
**Type**: feature pattern
**Files Modified**: tools/video-pipeline/gui/index.html

---

## What Was Done

Added inline editable video name to the Job Detail view in video.purebrain.ai manager GUI.

## Architecture

Single-file app (vanilla JS + HTML + CSS). No build step.
Backend: FastAPI at `tools/video-pipeline/gui/server.py`
Frontend: `tools/video-pipeline/gui/index.html`

## Key Finding

The rename backend endpoint already existed:
- `POST /api/jobs/{job_id}/rename` — body: `{ slug, display_name }`
- `saveRename(jobId, displayName)` function already existed in frontend
- Only the UX trigger was missing in the detail view

## Changes Made

### CSS Added (after `.meta-url` rule)
- `.detail-title-edit-btn` — pencil icon button next to title
- `.detail-name-input` — large input styled at 18px bold to match title
- `.meta-edit-btn` — small pencil button next to Display Name meta row
- `.meta-name-input` — small meta-sized input

### HTML Changed
- Wrapped `#detail-title` in `#detail-title-wrap` flex container
- Added `#detail-title-edit-btn` pencil button (hidden initially)

### JS Changes
1. `renderDetail()`: shows edit button, wires `onclick` to `startDetailRename(jobId)`
2. `fields.map()`: added 4th param `isEditable` to distinguish Display Name row
3. `meta render`: added `isEditable` branch that renders Display Name with pencil button
4. New `startDetailRename(jobId)`: replaces title wrap with inline input + Save/Cancel

## Gotcha: Backend Blocks Rename After R2 Upload
- `r2_uploaded == True` → 409 error
- Rename only works on pre-R2-upload jobs
- Frontend shows rename UI regardless — backend will reject gracefully with toast

## Pattern

For single-file app edits: use Python `str.replace()` in a script to make atomic changes.
The Edit tool requires its own Read tool to be invoked first — not usable with bash-read files.
