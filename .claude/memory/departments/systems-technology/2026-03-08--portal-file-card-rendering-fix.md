# Portal File Card Rendering Fix - 2026-03-08

## Problem
Files sent to portal via `portal_send_file.sh` were invisible in the portal UI (app.purebrain.ai) even though they were correctly:
- Copied to `/home/jared/portal_uploads/`
- Written to `portal-chat.jsonl`
- Served by `/api/chat/uploads/{filename}`

## Root Causes Found

### Bug 1: Mode 3 regex in `parseAiFiles` intercepting PORTAL_FILE tags
`parseAiFiles()` has a "Mode 3" regex `/\[(?:FILE|PORTAL_FILE):\s*([^\]]+\.([a-zA-Z0-9]+))\s*\]/g` that matches `[PORTAL_FILE:storedName:originalName]` and creates a file card with `serverPath: "storedName:originalName"` (wrong - treats the whole tag content as a path).

### Bug 2: PORTAL_FILE card appended at wrong DOM position in `addMessage`
The `renderAiFileCards([portalFile], div)` call happened BEFORE `div.appendChild(row)`, so the file card was the FIRST child of `.msg.assistant` - visually mispositioned.

### Bug 3: Duplicate JSONL entries causing confusion
`portal_send_file.sh` wrote directly to `portal-chat.jsonl`. The WS polling loop then called `_mirror_to_portal_log()` to write the SAME message again with the SAME ID. While deduplication handled this, it created unnecessary complexity.

## Fixes Applied

### Fix 1: Strip PORTAL_FILE tags before `parseAiFiles` in `addMessage`
In `addMessage`, strip `[PORTAL_FILE:...]` from `displayText` before passing to `renderMarkdown` and `parseAiFiles`. The specific PORTAL_FILE handler below renders them correctly.

### Fix 2: Defer file card append to after row/meta/actionBar in `addMessage`
Store the PORTAL_FILE object in `_portalFileAM`, then call `renderAiFileCards([_portalFileAM], div)` AFTER `div.appendChild(row/meta/actionBar)` for correct DOM position.

### Fix 3: Strip PORTAL_FILE tags in streaming completion handler
Same strip applied in `startStreamingMessage` completion code.

### Fix 4: Duplicate prevention in in-place update path
Added `data-portal-stored` attribute check to prevent duplicate cards on repeated WS updates.

### Fix 5: Mode 3 regex updated to only match `[FILE: ...]` not `[PORTAL_FILE: ...]`
Changed regex from `/\[(?:FILE|PORTAL_FILE):...` to `/\[FILE:...` — PORTAL_FILE format is handled exclusively by the specific handlers.

### Fix 6: `portal_send_file.sh` rewritten to use `/api/deliverable` endpoint
Instead of writing directly to `portal-chat.jsonl`, the script now POSTs to `/api/deliverable` which handles:
- File copy to uploads directory
- JSONL write (single entry, no duplicates)
- Correct `PORTAL_FILE` message format

## Files Modified
- `/home/jared/purebrain_portal/portal-pb-styled.html` (production portal)
- `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/for-witness/portal-pb-styled.html` (for-witness)
- `/home/jared/purebrain_portal/portal_send_file.sh` (rewritten)

## Key API
- `/api/deliverable` POST — accepts `{path, name, message}`, copies file to uploads, writes PORTAL_FILE message
- `/api/chat/uploads/{filename}` GET — serves uploaded files with token auth

## Testing
Both files tested via `portal_send_file.sh` — API returns `{"ok":true}` and JSONL entries are single (no duplicates).
