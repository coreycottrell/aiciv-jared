# CC: Team Chat + Task System Improvements
**Date**: 2026-03-22
**Type**: operational

## What Was Built

### Task System Improvements
- ALL team members can now add tasks (not just admin) via `POST /api/tasks/assign`
- `PUT /api/tasks/{id}` — assignees can update status + notes; admins can update everything
- `POST /api/tasks/{id}/complete` — marks complete with timestamp + actor tracking
- Three new columns added to tasks table: `completed_by`, `notes`, `history` (JSON audit trail)
- Task status workflow enforced: open → in_progress → done
- Filters extended: supports comma-separated status values, `department` filter
- History array logs every change with timestamp, actor, detail

### Team Chat
- New `api/chat.py` — WebSocket real-time messaging + REST fallback for AI members
- 6 default channels seeded: general, engineering, marketing, sales, product, operations
- DM support via channel naming convention: `dm_email1AT_email2`
- File uploads: `POST /api/chat/upload` → saved to `static/chat-uploads/`, max 25MB
- Presence via heartbeat: `POST /api/chat/presence/heartbeat` (every 30s)
- Read receipts: `POST /api/chat/channels/{id}/read`
- WS auth: uses same session cookie as HTTP
- AI members can post via REST using X-Aether-Key

### UI Additions (main.py injections)
- Chat tab added to desktop nav (INJECTION 2)
- Chat tab added to mobile sidebar nav
- Full Chat view div with two-column layout (sidebar + message area)
- Chat CSS injected via gateway_head_injection
- Chat JS injected via gateway_script (deferred switchView patch to avoid conflicts)
- "+ Add Task" button injected for non-admin users on tasks view

## Key Files
- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/api/chat.py` (NEW)
- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/api/tasks.py` (REWRITTEN)
- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/models.py` (EXTENDED)
- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/main.py` (EXTENDED)

## Patterns Learned
- SQLite ALTER TABLE migrations must check column existence first (SQLite doesn't support IF NOT EXISTS on ALTER)
- Python string escape: JS regexes with \w inside Python triple-quoted strings need to be \\w
- switchView patch must be deferred because hub's switchView is defined after gateway_script runs
- WebSocket auth via session cookie works transparently with FastAPI's Starlette session middleware
