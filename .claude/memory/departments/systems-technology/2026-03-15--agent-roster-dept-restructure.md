# Agent Roster Department Restructure
**Date**: 2026-03-15
**Type**: infrastructure change
**Agent**: dept-systems-technology

## What Was Done

Restructured the portal agents.db from 8 legacy broad departments (AI & Strategy, Development, Meta & Governance, etc.) to the 23 official Pure Technology departments with trigger codes.

## Key Facts

- **77 agents** mapped across **23 departments**
- Every department has exactly **1 department manager as is_lead=1**
- All specialist agents assigned to exactly one department
- Backup created: `/home/jared/purebrain_portal/agents.db.bak-dept-restructure-20260315_181328`
- Migration script: `/home/jared/purebrain_portal/migrate_agents_departments.py`

## Department → Agent Count

| Department            | Agents | Notes                              |
|-----------------------|--------|------------------------------------|
| Systems & Technology  | 17     | Largest — CTO + 15 tech specialists |
| Marketing & Advertising | 11  | CMO + 9 marketing specialists      |
| Corporate & Organizational | 5 | COO + human liaison, naming, etc. |
| Pure Research         | 5      | PR# lead + data sci, ML, web research |
| Pure Technology       | 3      | PT# lead + conductor + strategy     |
| And 18 more depts     | 1–3 each |                                  |

## Files Changed

- `/home/jared/purebrain_portal/agents.db` — all agent department/lead fields updated
- `/home/jared/purebrain_portal/portal_server.py` — `dept_order` list updated to 23 PT departments
- `/home/jared/purebrain_portal/migrate_agents_departments.py` — migration script (keep for reference)

## Endpoints Verified

- `GET /api/agents/stats` → `{"total":77,"departments":23}`
- `GET /api/agents/orgchart` → all 23 departments, each with correct lead
- `GET /api/agents` → all 77 agents with correct department assignments

## Key Mapping Decisions

- `the-conductor` → PT# (Pure Technology) — orchestrates the whole org
- `strategy-specialist` → PT# — company-wide strategy
- `cto` → ST# (under dept-systems-technology, not leading it — dept manager is the lead)
- `marketing-automation-specialist` → MA# (not lead — dept-marketing-advertising is lead)
- `marketing-team` → PMG# (client-facing team agent)
- `trading-strategist` → PC# (Pure Capital)
- `data-scientist`, `ai-ml-engineer`, `web-researcher`, `pattern-detector` → PR#
- `collective-liaison`, `cross-civ-integrator` → ES# (External Share)
- `doc-synthesizer` → IS# (Internal Share)
- `tg-bridge`, `claude-code-expert` → IT# (IT Support)
- `ai-psychologist`, `health-auditor` → HR#
- `human-liaison`, `naming-consultant`, `conflict-resolver`, `genealogist` → CO#
- `task-decomposer`, `result-synthesizer` → OP#
