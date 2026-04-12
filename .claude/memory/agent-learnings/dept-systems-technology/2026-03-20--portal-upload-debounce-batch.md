# Portal Upload Debounce Batch Fix

**Date**: 2026-03-20
**Type**: teaching
**Topic**: Multi-file upload debouncing in portal_server.py

## Problem

When Jared uploads multiple files in one action from the portal, each file
triggers a separate POST to /api/chat/upload. Previously each upload
immediately fired its own _do_serialized_inject() background task, resulting
in N separate [Portal Upload from Jared] messages injected into tmux — one
per file. This wastes token context and creates a noisy experience.

## Fix Applied

Added a debounce batch system to ~/purebrain_portal/portal_server.py.

New globals (after line ~316):
- _DEBOUNCE_WINDOW_S = 2.5 — window to collect files before flushing
- _upload_batch: list — accumulates items during window
- _upload_batch_task — asyncio Task for the pending flush

New functions:
- _flush_upload_batch() — waits 2.5s then injects ONE combined notification
- _schedule_upload_batch_item(original_name, portal_copy_path, is_image, caption) — adds to batch, cancels+restarts timer (true debounce)

Modified:
- api_chat_upload — replaced per-file ensure_future(_do_serialized_inject()) with _schedule_upload_batch_item()

## Notification Format

Single file (identical to old format):
[Portal Upload from Jared] File saved to: /path/file.md INSTRUCTIONS from Jared: ... [Image: ... USE Read tool...]

Multiple files (batched):
[Portal Upload from Jared] 5 files saved: file1.md, file2.md, file3.png INSTRUCTIONS from Jared: [shared caption] Images (2): /path/file2.md, /path/file3.png — USE Read tool on each path TO VIEW

## Key Behaviour Notes

- Ack messages in portal chat still appear immediately (one per file) — UX unaffected
- Timer resets on each new arrival (true debounce, not throttle)
- Single-file uploads fire after 2.5s window — functionally identical to before
- Backup at: ~/purebrain_portal/portal_server.py.bak-upload-debounce-20260320

## Prior Art

There was already a _tmux_inject_lock with 1.5s sleep that serialized injections
to prevent interleaved tmux buffer writes. The debounce layer sits ABOVE that —
it reduces N injections to 1 rather than just spacing them out.
