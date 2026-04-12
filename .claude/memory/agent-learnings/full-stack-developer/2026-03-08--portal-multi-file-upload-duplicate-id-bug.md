# Portal Multi-File Upload: Duplicate ID Bug Fix

**Date**: 2026-03-08
**Type**: gotcha
**Agent**: full-stack-developer

## Problem

When Jared dropped 3 images simultaneously onto the portal chat, all 3 appeared
in the preview area but only 1 rendered in the chat after send.

## Root Cause

**Server-side**: `_save_portal_message()` in `/home/jared/purebrain_portal/portal_server.py`
generated message IDs using only millisecond timestamp:

```python
"id": f"portal-{int(time.time() * 1000)}",
```

When 3 simultaneous uploads triggered 3 calls to `_save_portal_message`, all 3
could execute within the same millisecond, producing identical IDs
(e.g., `portal-1741444800000` x3).

**Frontend**: `addFileImageMessage()` in `portal-pb-styled.html` (line 6890) checks:
```javascript
if (knownMsgIds.has(msgId)) return;
```

The second and third uploads returned IDs already in `knownMsgIds`, so their
`addFileImageMessage` calls returned early without rendering — silently dropping
images 2 and 3 from the chat display.

**Secondary issue**: `stored_name` for uploaded files also used only `timestamp_ms`,
meaning simultaneous uploads of same-named files could collide on disk.

## Fix

Two changes to `/home/jared/purebrain_portal/portal_server.py`:

1. **Unique message IDs** — appended `secrets.token_hex(4)` (8 random hex chars):
```python
"id": f"portal-{int(time.time() * 1000)}-{secrets.token_hex(4)}",
```

2. **Unique stored filenames** — inserted random token before filename:
```python
stored_name = f"{timestamp_ms}_{secrets.token_hex(4)}_{safe_name}"
```

`secrets` was already imported. No frontend changes needed.

## Key Pattern

**Any server-generated ID that could be produced by concurrent requests MUST
include entropy beyond a timestamp.** `time.time() * 1000` is not sufficient
for parallel async requests. Always add `secrets.token_hex(N)` or `uuid4()`.

## Files Changed

- `/home/jared/purebrain_portal/portal_server.py` (lines 486, 763)

## Verification

Portal server restarted (PID 4091263). Health check at `http://localhost:8097/`
returned 200. Old process (4063339) killed.
