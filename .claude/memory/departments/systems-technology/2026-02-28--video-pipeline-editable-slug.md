# Video Pipeline GUI — Editable Filename/Slug Feature

**Date**: 2026-02-28
**Type**: pattern | feature-build
**Pipeline**: BUILD -> SECURITY -> QA -> SHIP (complete)

---

## What Was Built

Added editable slug/display-name to the video pipeline GUI at `video.purebrain.ai`.

### Files Modified
- `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/gui/server.py`
- `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/gui/index.html`

---

## Architecture

### Backend: `POST /api/jobs/{job_id}/rename`
- Body: `{ "slug": "url-safe-slug", "display_name": "Human Name" }`
- Validates: slug is URL-safe (lowercase, hyphens, alphanumeric only)
- Guards: rejects rename if `r2_uploaded == true` (409 Conflict)
- Persists to `work/jobs.json` via `update_job()`
- Inserted at line ~574 in server.py, before `/api/library`

### Frontend: Queue Card Rename UI
- Pencil icon (`&#x270E;`) next to filename on each queue card
- Click pencil → inline edit mode (input + Save + Cancel buttons)
- Live slug preview as user types (client-side slug computation)
- Enter key = save, Escape = cancel
- After R2 upload: lock icon shown, pencil disabled (slug frozen)
- Slug line shown below display name in the queue card

### Data Model
Jobs now have three name-related fields:
- `original_filename` — preserved from upload, never changed
- `display_name` — human-readable, editable until R2 upload
- `slug` — URL-safe, used in R2 paths, editable until R2 upload

---

## Key Decisions

1. **Slug locked after R2 upload** — once files are in R2 at `videos/{job_id}_{slug}/`, the slug is baked into all URLs and the embed code. Renaming after upload would break video playback.

2. **display_name vs slug**: Both are editable. The slug is auto-generated from the display name (spaces→hyphens, lowercase, strip specials). User sees both in the queue card.

3. **original_filename preserved** — the raw upload filename is always kept for reference in job detail.

4. **Client-side slug preview**: Slug is computed in real-time as user types in the input, giving instant feedback on what the R2 path will look like.

---

## Security Review Notes
- Input sanitized server-side: `re.sub(r"[^a-z0-9-]", "", slug)` after lowercasing
- Double sanitization: both client (JS) and server (Python regex) enforce URL-safe slugs
- No path traversal risk: slug only used as metadata field, not for filesystem ops
- R2 path uses `job_id` prefix too (`{job_id}_{slug}`) so even a slug collision is scoped to unique job IDs

---

## Test Results (All Pass)
- Rename pre-upload job: PASS
- Slug sanitization ("Pure Brain Demo Video" -> "pure-brain-demo-video"): PASS
- Rename blocked after R2 upload (409): PASS
- Missing slug returns 400: PASS
- Server restart after changes: PASS (PID confirmed)
