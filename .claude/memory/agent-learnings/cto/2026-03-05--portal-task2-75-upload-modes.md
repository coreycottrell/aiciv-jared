# Portal Task 2.75 — Dual Upload Modes Architecture

**Date**: 2026-03-05
**Type**: teaching
**Topic**: Modal-gated file upload flow with client-side image/text compression

---

## What Was Built

A dual-mode upload interceptor for `portal.purebrain.ai/pb` (self-contained HTML portal).

**Patch script**: `/home/jared/purebrain_portal/apply_task2_75_upload_modes.py`
**Target file**: `/home/jared/purebrain_portal/portal-pb-styled.html`

---

## Key Architecture Decisions

### 1. Single Interception Point: queueFile()
The entire upload flow funnels through `queueFile(file)`. This was the correct
and only place to intercept — not the drag handlers, not the file input change
event (which both call queueFile). Intercepting here means no duplication.

### 2. Debounce Batching (60ms)
When a user drops 3 files at once, each file triggers `queueFile` separately
in rapid succession. Without batching, you'd show 3 modals back-to-back.
Solution: 60ms setTimeout debounce that collects all files from a single
drop/select into one batch, shows ONE modal. One choice = applies to all.

### 3. Client-Side Compression
No server round-trip needed:
- **Images**: `HTMLCanvasElement.toBlob()` with JPEG quality 0.7, max 1920px wide
- **Text/code**: FileReader reads as text, trims trailing whitespace per line, writes back as Blob
- **Other types**: Pass-through (no compression, button disabled with explanation)
- All async via Promise chains — non-blocking UI

### 4. Modal Pattern
- Overlay with `pointer-events: none` + `opacity: 0` by default
- `.visible` class toggles both — clean CSS transition
- Click outside modal = treat as "Original" (safe fallback)
- Size estimate shown BEFORE user chooses (important UX: show value of compression upfront)

### 5. Size Estimation Without Compressing
Rather than actually compressing to show the size chip (expensive), we estimate:
- Images: ~55% of original (JPEG quality 0.7 typical result)
- Text: ~97% (whitespace trim is minimal)
This is honest enough — labeled as estimate, not exact.

---

## Patch Strategy (Learned)

For self-contained HTML files with no build system:
1. Find the single function to replace — use grep to get exact indentation
2. Copy the EXACT string including all whitespace into the OLD_* anchor variable
3. Replace entire function body with new version
4. CSS: inject before the last `</style>` before first `<script`
5. HTML: inject before `</body>`
6. Always create .bak backup before writing

The `rfind('</style>', 0, html.find('<script'))` pattern is robust for
finding the main stylesheet closing tag in self-contained HTML portals.

---

## Files
- Patch: `/home/jared/purebrain_portal/apply_task2_75_upload_modes.py`
- Target: `/home/jared/purebrain_portal/portal-pb-styled.html`
- Backup created by script: `portal-pb-styled.html.bak-task2_75`
