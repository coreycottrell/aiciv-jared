# Portal Chat Image Upload Display Fix

**Date**: 2026-03-09
**Type**: teaching
**Topic**: Race condition between WS broadcast and REST upload callback causing images to not display

## Problem

When Jared uploads images in the portal chat, they only appeared after a hard page refresh.

## Root Cause (Race Condition)

The portal has two paths that render image uploads:
1. **REST callback** (`addFileImageMessage`): Called when `/api/chat/upload` responds
2. **WS broadcast** (`addMessage`): Called when the WS poll loop picks up the new portal-chat.jsonl entry

Both paths check `knownMsgIds.has(msgId)` to prevent duplicate rendering. The race:
- If WS fires FIRST (within 0.8s poll cycle): `addMessage` renders with `knownMsgIds.add(msgId)`. Then REST callback's `addFileImageMessage` sees ID already in `knownMsgIds` → returns immediately.
- The `addMessage` path rendered `[Image: stored_name]` as literal text in bubble PLUS the img element.
- On page refresh, `loadChatHistory` called `addMessage` → same rendering, image visible.

## Fixes Applied

### Fix 1: WS handler special case for image messages
In `chatWs.onmessage`, added check before falling through to `addMessage`:
- If `msg.role === 'user'` AND text matches `^\[Image: stored_name\]`, call `addFileImageMessage` instead
- This ensures clean rendering (image + caption bubble) regardless of timing
- Derives display name from stored name by stripping `{ms}_{hex}_` prefix

### Fix 2: Strip `[Image: stored_name]` from bubble text in `addMessage`
In `addMessage`, after stripping `[PORTAL_FILE:]` tags, also strip `[Image: ...]` prefix from user role messages. The img element is appended directly to the div, so only caption text needs to show in bubble.

### Fix 3: Image below bubble (PORTAL_CORE_UX_RULES compliance)
Moved `div.appendChild(_inlineImgEl)` to AFTER `div.appendChild(row)` so image renders below the text bubble, not above it.

### Fix 4: Optimistic rendering (UX improvement)
For image uploads, show image IMMEDIATELY using `blob: URL` before server responds:
- Creates local blob URL from File object
- Shows optimistic preview with 0.75 opacity ("uploading" state)
- On REST response: removes optimistic preview, renders final server-URL version
- On error: removes optimistic preview, shows error message
- Revokes blob URL on success/error to free memory

## Key Files Modified
- `/home/jared/purebrain_portal/portal-pb-styled.html` (production)
- `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/packages/purebrain-portal/portal-server/portal-pb-styled.html` (repo)

## Pattern: WS vs REST Race in Portal Chat
Any feature that:
1. Saves to portal-chat.jsonl (which WS polls)
2. AND calls a render function client-side via REST response

...is vulnerable to this race. The fix pattern:
- In WS handler, add special-case rendering for structured message formats
- Or: pre-register the msgId in `knownMsgIds` BEFORE the REST request, so WS is always blocked
