# Portal Task 1: Drag & Drop — Architecture Audit & Patch Decision
**Date**: 2026-03-05
**Type**: operational + teaching
**Agent**: cto

## Summary

Task 1 of 11 portal upgrade tasks: "Drag & drop files into chat like Telegram."

## Key Finding: Feature Already 80% Built

Before writing a single line of code, I audited what exists. This saved significant effort.

### What Was Already Complete

| Component | Location | Status |
|-----------|----------|--------|
| `/api/chat/upload` POST endpoint | `portal_server.py` lines 660-729 | Complete |
| `/api/chat/uploads/{filename}` serve | `portal_server.py` lines 732-743 | Complete |
| `UPLOADS_DIR = ~/portal_uploads` | `portal_server.py` line 42 | Complete |
| Drag & drop on #chat-messages | HTML lines 3594-3611 | Complete |
| `.drop-overlay` CSS + HTML | HTML lines 1364-1380, 2229 | Complete |
| `#attach-btn` paperclip button CSS | HTML lines 1256-1277 | Exists (wrong icon) |
| `#file-input` hidden file input | HTML line 2243 | Exists (wrong accept) |
| `pendingFiles` queue + preview bar | HTML lines 2908-2909 | Complete |
| `queueFile()` / preview helpers | HTML lines 3634-3681 | Exists (no size check) |
| `sendChat()` with upload path | HTML lines 3471-3548 | Complete |
| `addFileImageMessage()` | HTML lines 3721-3753 | Complete |

### What Was Missing / Needed Improvement

1. Drop zone did NOT cover the textarea/input-bar — only #chat-messages
2. Drop overlay used gold color — task spec wants PT Blue (#2a93c1)
3. Attach button used "+" text — needed proper SVG paperclip icon
4. File input `accept="*/*"` — needed restriction to images + docs
5. No client-side file size limit — task spec says 10MB max
6. Drop overlay text "Drop file here" — minor: updated to "Drop files here" with icon

## Architecture Decision: Patch Only (No Server Changes)

The server already has everything needed. Decision: HTML-only patch.

This is the right call because:
- Server endpoint handles 50MB max (more than enough for UI's 10MB limit)
- Files are saved to both `~/portal_uploads/` AND `~/docs/from-telegram/`
- tmux injection mirrors the Telegram bridge pattern exactly
- No new routes, no new dependencies

## Patch Script Pattern

Used string replacement approach (not regex) with exact whitespace matching.

**Critical lesson**: The HTML file uses 2-space indent for CSS blocks, 4-space for properties, 10-space for HTML inside the chat-input-bar. Always verify exact indentation before writing patch search strings.

**Verification pattern**: After writing patch, grep for each exact search string before declaring it ready. All 6 search strings confirmed present before handing off.

## Files

- Patch script: `/home/jared/purebrain_portal/apply_task1_dragdrop.py`
- Target file: `/home/jared/purebrain_portal/portal-pb-styled.html`
- No server changes: `/home/jared/purebrain_portal/portal_server.py` unchanged
