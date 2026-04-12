# Memory: PureBrain Hub Merge Architecture Brief

**Date**: 2026-03-01
**Agent**: cto
**Type**: synthesis + teaching
**Topic**: Full architecture analysis of Hub repo vs cc.purebrain.ai — what overlaps, what conflicts, and the complete merge plan with Jared's decisions locked in

---

## Context

Jared sent a full repo (`purebrain-hub-full-repo/`) containing the Hub MVP and dashboard versions to be merged into cc.purebrain.ai. Produced comprehensive architecture brief at `exports/purebrain-hub-architecture-brief.md`.

**Updated 2026-03-01**: Jared answered all 5 open architecture questions. Decisions documented at top of brief in Section 0.

---

## Jared's Locked Decisions (2026-03-01)

| # | Decision | Status |
|---|----------|--------|
| 1 | Stay at cc.purebrain.ai — no domain migration | LOCKED |
| 2 | GDrive only — no local disk file storage | LOCKED |
| 3 | Team credentials after more is built — Sprint 3+ | LOCKED |
| 4 | Multi-user OAuth — each of 50 team members connects their own Microsoft AND Google accounts | LOCKED |
| 5 | Cross-AI endpoint — pending Jared's yes/no | PENDING |

---

## What the Decisions Changed

### Decision 2 — GDrive Only

Eliminates local file storage entirely. New file upload flow:
- Browser multipart -> FastAPI in memory -> gdrive_manager.py -> GDrive -> return URL
- `hub_files` table stores `gdrive_file_id` + `gdrive_url` only, no local path column
- Sprint 2 simplified: no upload directory provisioning, no sync jobs, no retry logic
- Risk: gdrive_manager.py must accept in-memory byte streams (not file path strings)

### Decision 4 — Multi-user OAuth (biggest change)

The single `MicrosoftToken` row becomes a `user_oauth_tokens` table:
- Compound unique key: `(user_id, provider)` where provider = 'microsoft' | 'google'
- OAuth callbacks must carry signed `state` JWT encoding user_id to know WHICH user is completing the flow
- Background sync loop must iterate over all users with connected tokens
- `calendar_events` and `email_messages` tables need `user_id` column
- Tokens must be encrypted at rest (Fernet, key from env) — 50 users' email/calendar access in one table requires it

This required adding Sprint 0.5 — auth layer rewrite — as a prerequisite before Calendar/Email views can ship.

### Decision 3 — Credentials Later

Sprints 1 and 2 built and tested with Jared's account only. Team rollout is Sprint 3.

---

## Key Findings (Original)

### The Four Systems

1. **Hub MVP** (Node.js + React + Express + sql.js) — posts feed, wins board, file upload, GDrive sync, 3D login canvas
2. **cc.purebrain.ai** (Python + FastAPI + SQLAlchemy + SQLite) — calendar, email, 50-person roster, Microsoft Graph, Google Calendar
3. **Dashboard v4** (self-contained HTML) — task CRUD, status machine, A/B/C delegation, team roster view — NOT yet in any live system
4. **Portal shell** (HTML) — visual design reference for merged UI

### Critical Architecture Decisions

- **FastAPI wins** over Express backend (it's live, it's Python, it has real users)
- **Gateway session auth wins** over Hub MVP token system (50 real users vs 4 demo)
- **SQLite additive migration** — new `hub_posts`, `hub_reactions`, `hub_files`, `hub_tasks` tables added to comms.db
- **React served by FastAPI StaticFiles** — removes Netlify dependency for hub
- **No Supabase** — v4 references it but merged system does not need it
- **No local disk** — GDrive only per Decision 2

### The Most Important Missing Piece

`author_type` field — without it you cannot distinguish Jared posts from agent posts. The feed is not an audit trail without this. Added to schema spec.

### Static Data Risk

Dashboard.jsx contains hardcoded contributor names and "Last sync: just now" / "Files synced: 24" strings. This is a credibility problem before wider team rollout. Fix = `GET /api/hub/stats` live endpoint.

### File Paths

- Architecture brief: `/home/jared/projects/AI-CIV/aether/exports/purebrain-hub-architecture-brief.md`
- Hub MVP source: `/home/jared/projects/AI-CIV/aether/tools/purebrain-hub-repo/purebrain-hub-full-repo/purebrain-hub-mvp/`
- Gateway source: `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/`
- Existing Hub (same as MVP): `/home/jared/projects/AI-CIV/aether/tools/purebrain_hub/`

## When to Apply This Pattern

When two systems need to merge: build a feature inventory matrix first (what's in A only, what's in B only, what's in neither). Then make auth and database decisions — those cascade everything else.

When founder decisions come in after the initial brief: document them at the TOP of the brief in their own section (Section 0), explain the implications in plain English, update the sprint plan and risk register to reflect what changed. The engineering team needs to see decisions and implications in one place.
