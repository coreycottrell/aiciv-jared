# Portal Communication Feature Parity Audit
**Date**: 2026-03-08
**Agent**: dept-systems-technology
**Scope**: All 9 Telegram-equivalent features in PureBrain Portal

---

## Infrastructure Map

- **Live portal server**: `/home/jared/purebrain_portal/portal_server.py`
- **Live portal HTML**: `/home/jared/purebrain_portal/portal-pb-styled.html`
- **Process**: PID 3452400, running since Mar 7, port 8765
- **Package (reference)**: `aiciv-comms-hub-bootstrap/_comms_hub/packages/purebrain-portal/`
- **Dual-delivery script**: `tools/tg_send.sh` → `portal_send_file.sh`
- **Portal chat log**: `/home/jared/purebrain_portal/portal-chat.jsonl`
- **File storage**: `/home/jared/portal_uploads/`
- **Inbound from portal**: `/home/jared/portal_uploads/from-portal/` + `docs/from-telegram/`

---

## Feature Status Matrix

| # | Feature | Status | Implementation |
|---|---------|--------|----------------|
| 1 | Outbound text (Aether → Jared) | FIXED | tg_send.sh TEXT mode now dual-delivers via portal_send_file.sh --text |
| 2 | Outbound files (.md, .html, etc.) | WORKING | tg_send.sh --file → portal_send_file.sh → PORTAL_FILE tag in JSONL |
| 3 | Outbound images | WORKING | tg_send.sh --photo → portal_send_file.sh → inline render in portal |
| 4 | Inbound text | WORKING | api_chat_send: saves to JSONL + tmux inject |
| 5 | Inbound files | WORKING | api_chat_upload: portal_uploads/ + docs/from-telegram/ + tmux notify |
| 6 | Inbound images | WORKING | Same as files, renders inline via /api/chat/uploads/ endpoint |
| 7 | Reply context | WORKING* | Frontend prepends [replying to Sender: "text"] to full message |
| 8 | Thinking (white dots) | WORKING | _thinking_monitor_loop() tails JSONL, pushes via /ws/chat WebSocket |
| 9 | Drop files to Aether | WORKING | Drag-drop + attach button + upload modal + progress bar |

*Reply context works but is embedded as plain text prefix, not structured data.

---

## Fix Applied

**Gap**: `tg_send.sh` TEXT mode only logged to `agent_updates.log`. Text messages sent via
`./tools/tg_send.sh "message"` never appeared in the portal chat.

**Fix**: Added portal dual-delivery to TEXT mode branch in `tools/tg_send.sh`:
```bash
PORTAL_SEND="$(dirname "$0")/../aiciv-comms-hub-bootstrap/.../portal_send_file.sh"
if [[ -x "$PORTAL_SEND" ]]; then
    "$PORTAL_SEND" --text "$TEXT" 2>/dev/null || true
fi
```

**Verified**: Test message appeared in `/home/jared/purebrain_portal/portal-chat.jsonl`
within 2 seconds of send.

---

## Architecture Notes

- **Outbound text from Claude responses**: The portal reads from Claude's session JSONL files
  (`~/.claude/projects/.../*.jsonl`) via `_parse_all_messages()`. So full Claude Code responses
  appear in portal automatically — they don't need tg_send.sh. tg_send.sh is for explicit
  agent-triggered notifications (progress updates, background agent reports).

- **Thinking blocks**: Two monitors run independently:
  1. Portal `_thinking_monitor_loop()` pushes to portal WebSocket clients
  2. Telegram bridge `monitor_jsonl_thinking()` pushes to Telegram
  Both share the same JSONL source. No duplication because each tracks its own position/hashes.

- **File card rendering**: `[PORTAL_FILE:storedName:originalName]` tag in JSONL is parsed
  by portal-pb-styled.html JS and rendered as a styled download card with icon, name, size,
  download button, and copy-path button.

- **tg_send.sh dual-delivery paths**: Both photo and file modes already had dual-delivery
  before this audit. Only text mode was missing.
