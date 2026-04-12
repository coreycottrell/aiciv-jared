# AI Access Methods — Communications Gateway

**Date**: 2026-03-21
**Type**: operational + teaching
**Topic**: Three AI access methods built for cc.purebrain.ai Command Center

---

## What Was Built

Three access methods for partner AIs to interact with the Command Center:

### Option A — API Key Access (PRIMARY)
- 11 unique API keys generated, stored in `tools/comms-gateway/ai_keys.json`
- Auth via `X-AI-Key` header OR `Authorization: Bearer ai_<key>` OR `?ai_key=` query param
- 5 endpoints: GET tasks, GET mandala, POST task update, POST report, GET context
- Module: `tools/comms-gateway/api/ai_access.py`

### Option C — Portal Bridge
- `GET /api/alignment-context` endpoint (alias of `/api/ai/context`)
- Returns full session-start context: priorities, tasks, mandala focus areas, recent updates
- AIs call this on session start to know what to focus on
- Same module as Option A

### Option B — AgentMail Fallback
- Module: `tools/comms-gateway/api/agentmail_notify.py`
- `send_task_notification(task, segment_name)` async function — import and call directly
- `POST /api/ai/notify/{task_id}` for manual trigger
- Uses AGENTMAIL_API_KEY from .env, sends from aethergottaeat@agentmail.to
- Flux override: flux.civ@agentmail.to, Meridian override: meridian-pt@agentmail.to

---

## Key Architecture Decisions

- Keys are NOT hardcoded — loaded from `ai_keys.json` on every request (hot-reload friendly)
- Task ownership enforced: AI can only update tasks assigned to them
- Reports stored as `source='agent'` Tasks with `status='done'` — visible in Command Center UI
- `tasks_router` was already imported in `main.py` (line 38) but NOT registered until this build

---

## Files Changed

- NEW: `tools/comms-gateway/ai_keys.json` — 11 AI keys
- NEW: `tools/comms-gateway/api/ai_access.py` — Options A + C
- NEW: `tools/comms-gateway/api/agentmail_notify.py` — Option B
- PATCHED: `tools/comms-gateway/main.py` — added imports + include_router for both new modules

---

## Verified Working

All tests passed live against localhost:8870:
- GET /api/ai/tasks — 200 OK, returns Lyra's tasks
- GET /api/alignment-context (Bearer token) — 200 OK, full context
- POST /api/ai/tasks/65/update — status transition open->in_progress confirmed
- POST /api/ai/report — stored as task ID 66

---

## Pattern: Adding AgentMail notification to task assignment

When `tasks_router` creates a task with `ai_assignee` set, call:
```python
from api.agentmail_notify import send_task_notification
result = await send_task_notification(task, segment_name)
```
This is the Option B auto-notification hook. Wire into `api/tasks.py` assign endpoint.
