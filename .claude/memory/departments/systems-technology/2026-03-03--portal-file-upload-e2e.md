# Portal File Upload - End-to-End Build

**Date**: 2026-03-03
**Type**: pattern
**Topic**: Portal file upload with tmux notification and docs/from-telegram/ mirroring

## What Was Built

End-to-end file upload for the PureBrain Portal that mirrors the Telegram bridge pattern.

## Files Modified

1. `/home/jared/purebrain_portal/portal_server.py` — `api_chat_upload` function enhanced
2. `/home/jared/purebrain_portal/portal-pb-styled.html` — frontend `filesToSend.forEach` block updated

## Backend Changes (portal_server.py)

### Modified: `api_chat_upload` function

Key additions:
- Reads `caption` from form data: `caption = str(form.get("caption", "")).strip()`
- Saves file copy to `docs/from-telegram/` with prefix `portal_YYYYMMDD_HHMMSS_filename`
- Injects tmux notification via `get_tmux_session()` + `subprocess.run(["tmux", "send-keys", ...])`
- Returns `aether_path` in response JSON alongside existing `path`

### Tmux notification format (mirrors Telegram bridge):
```
[Portal Upload from Jared]
File saved to: /home/jared/projects/AI-CIV/aether/docs/from-telegram/portal_YYYYMMDD_HHMMSS_filename
INSTRUCTIONS from Jared: {caption text if provided}
```

### Both files saved:
- `~/portal_uploads/{timestamp_ms}_{filename}` — portal serving path
- `~/projects/AI-CIV/aether/docs/from-telegram/portal_{timestamp}_{filename}` — Aether reads this

## Frontend Changes (portal-pb-styled.html)

### Modified: `filesToSend.forEach` upload block

Key changes:
- Adds `if (fullMsg) { fd.append('caption', fullMsg); }` to FormData before fetch
- After all uploads complete, shows user message in UI via `addMessage(fullMsg, 'user', ...)` directly
- Does NOT call `_dispatchChatMessage(combinedMsg)` — avoids double-injecting to tmux (upload already did it)

## Key Architecture Decision

The upload notification IS the message to Aether. No need to also dispatch text via `/api/chat/send`.
This prevents double tmux injection when user sends files with caption text.

## Dependency

`python-multipart` already installed (v0.0.22) — no additional install needed.

## Test Results

- Upload with caption: returns `{"ok":true, "aether_path":"...", ...}` — confirmed file in both locations
- Upload without caption: same, no INSTRUCTIONS line in tmux notification
- Python syntax: clean (`python3 -m py_compile` passes)
- JS syntax: clean (`node --check` passes on extracted scripts)
- Portal API status: returns 200 after restart

## Routes

No new route added. `api_chat_upload` already registered at:
`Route("/api/chat/upload", endpoint=api_chat_upload, methods=["POST"])`
