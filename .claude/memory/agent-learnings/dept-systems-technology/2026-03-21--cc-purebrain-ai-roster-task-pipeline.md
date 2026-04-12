# cc.purebrain.ai: AI Roster + Bench Cleanup + Task Assignment Pipeline

**Date**: 2026-03-21
**Type**: operational
**Topic**: Three critical fixes to Command Center - AI team members, bench cleanup, task API

## What Was Done

### Fix 1: AI Team Members Added to Roster

Added 11 AI team members to both config.py and the hub HTML source.

**Files changed**:
- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/config.py` — TEAM_ROSTER now has 61 members (was 49)
- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/purebrain-hub-source.html` — TEAM_ROSTER + TEAM_DATA + renderRoster

**AI members added**:
| AI | Human Partner | Contact |
|----|--------------|---------|
| Lyra | Nathan Olson | lyra@agentmail.to |
| Prodigy | Ahsen Awan | prodigy@agentmail.to |
| Meridian | Mike Daser | meridian-pt@agentmail.to |
| Flux | Alex Seant | flux.civ@agentmail.to |
| Anchor | John Smith | anchor@agentmail.to |
| Clarity | Phillip Bliss | clarity@agentmail.to |
| Tether | Melanie Salvador | tether@agentmail.to |
| Teddy | Robert Orlowski | teddy@agentmail.to |
| Metis | Michael Hancock | metis@agentmail.to |
| Parallax | Russell Korus | parallax@agentmail.to |
| Keel | Russell Korus | keel@agentmail.to |

AI members appear with orange-highlighted avatars and "AI" badge + human partner name in team view.
Profile view shows "AI Partner: [Name]" in the meta tags section.

### Fix 2: Bench People Removed from Task Assignments

**Hardcoded tasks in hub HTML** (aether-1 through aether-35) had bench assignees:
- Timothy DeVore (CTO) → Alex Seant (8 tasks)
- Charles Finkelstein (CPO) → Ahsen Awan (2 tasks)
- Alexander Logie → Mireille Dirany (2 tasks)

All 12 reassigned. Final unique assignees in hardcoded tasks:
- Aether, Ahsen Awan, Alex Seant, Jared Sanborn, Mireille Dirany, Nathan Olson, Phillip Bliss

**DB tasks**: No bench assignees existed in DB (tasks had no assigned_to column until this session).

**Bench cleanup API** at `DELETE /api/tasks/bench-cleanup` (admin/API key auth) - unassigns any future bench tasks.

### Fix 3: Task Assignment Pipeline

**DB migration**: Added 5 new columns to `tasks` table via ALTER TABLE (not breaking):
- `priority` TEXT DEFAULT 'medium'
- `assigned_to` TEXT (indexed)
- `ai_assignee` TEXT
- `mandala_segment` TEXT
- `created_by` TEXT

**New API endpoints** (`/home/jared/projects/AI-CIV/aether/tools/comms-gateway/api/tasks.py`):

```
POST /api/tasks/assign          — single task assignment
POST /api/tasks/assign/bulk     — bulk task assignment
GET  /api/tasks                 — list tasks (filterable)
DELETE /api/tasks/bench-cleanup — remove bench assignments (admin)
GET  /api/tasks/active-team     — get active whitelist
```

**Auth**: `X-API-Key: [AETHER_API_KEY]` header (same key as mandala endpoints).
API key value: in .env as GATEWAY_AETHER_API_KEY (default: aether-comms-api-key-2026-puretechnology)

**Sample call**:
```bash
curl -X POST http://localhost:8870/api/tasks/assign \
  -H "Content-Type: application/json" \
  -H "X-API-Key: aether-comms-api-key-2026-puretechnology" \
  -d '{
    "title": "Review Creator AI spec",
    "assignee": "Nathan Olson",
    "ai_assignee": "Lyra",
    "priority": "high",
    "mandala_segment": "Growth & Revenue",
    "due_date": "2026-03-22"
  }'
```

## Active Team Whitelist (17 humans + 12 AIs)

Humans: Nathan Olson, Ashley Tom, Natasha Carrasco, Ahsen Awan, Waqas Nasir, Shahbaz Ali, Zafeer Hassan, Mike Daser, Alex Seant, John Smith, Phillip Bliss, Melanie Salvador, Robert Orlowski, Michael Hancock, Russell Korus, Mireille Dirany, Jared Sanborn

AIs: Aether, Lyra, Prodigy, Meridian, Flux, Anchor, Clarity, Tether, Teddy, Metis, Parallax, Keel

## Gotchas

- API auth uses `X-API-Key` header (NOT `X-Aether-Key`)
- Roster endpoint `/api/roster` requires session auth (not API key) — by design
- Hub HTML TEAM_ROSTER and TEAM_DATA are separate arrays — both need updating
- mandala_segment field resolves partial matches (e.g. "Growth" matches "Growth & Revenue")
- DB migration was done via ALTER TABLE (safe for existing data)
- Natasha Carrasco is "Natasha Green" in some external docs — internal name is Natasha Carrasco

## Service

`aether-comms-gateway.service` on port 8870, tunneled via Cloudflare to cc.purebrain.ai
