# Portal Multi-Image Upload Race Condition Fix

**Date**: 2026-03-19
**Type**: bug fix / pattern
**Topic**: tmux injection race condition when multiple files uploaded simultaneously

## Root Cause

When Jared uploads multiple images at once via the portal, the frontend JS
fires parallel concurrent `fetch('/api/chat/upload')` calls — one per file —
with no serialization (`filesToSend.forEach` launches all fetches simultaneously).

Each upload handler in `portal_server.py:api_chat_upload` then fires tmux
`send-keys -l "\n{notification}"` immediately after saving the file.

When 6 requests all fire `send-keys -l` within milliseconds of each other,
tmux's literal paste buffer gets interleaved writes. The results:
- Messages overwrite each other in the paste buffer
- Only SOME of the 6 notifications make it into the Claude session
- The `_retry_enters()` coroutines from multiple uploads also compete,
  sending Enter at cross-purposes and further corrupting the queue

## Fix Applied

Added to `/home/jared/purebrain_portal/portal_server.py`:

1. `_tmux_inject_lock` — module-level `asyncio.Lock` (lazy-initialized)
2. `_get_tmux_inject_lock()` — lazy init helper (must be inside event loop)
3. `_inject_into_tmux_serialized(notification)` — acquires lock, injects,
   sleeps 1.5s INSIDE the lock, releases. This serializes all concurrent
   injections with 1.5-second spacing.

Changed `api_chat_upload` to:
- Build the notification string as before
- Fire `asyncio.ensure_future(_do_serialized_inject())` — background task
- Return the JSON response IMMEDIATELY (good UX, file is saved)
- Injection happens in lock-serialized queue order (1.5s apart)
- Removed the racing `_retry_enters()` pattern for upload injections

## Result

With 6 simultaneous uploads:
- All 6 files are saved immediately (no change there)
- Upload ACKs return immediately to frontend (no UX delay)
- Injections happen ~1.5s apart: file1 at t=0, file2 at t=1.5, file3 at t=3, etc.
- Total injection time for 6 files: ~7.5 seconds (acceptable — all get through)
- No more dropped injections, no more interleaved paste buffer corruption

## Key File

`/home/jared/purebrain_portal/portal_server.py`
- New helper: ~line 265-305 (`_inject_into_tmux_serialized`)
- Changed section: `api_chat_upload` tmux block (~line 1222-1240)

## Backup

`/home/jared/purebrain_portal/portal_server.py.bak-multi-image-upload-fix-20260319`

## Pattern

**asyncio.Lock as injection serializer**: When multiple concurrent async handlers
need to write to the same external resource (tmux, a file, a serial port), use
an asyncio.Lock with a sleep INSIDE the lock to both serialize and throttle.
