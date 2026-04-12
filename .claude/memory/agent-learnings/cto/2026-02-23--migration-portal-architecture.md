# Memory: AI Migration Portal Architecture Decision

**Date**: 2026-02-23
**Type**: synthesis
**Topic**: AI Migration Portal — architecture decision document

---

## Key Decisions Made

### Tech Stack
- **Extend existing Node.js/Express hub server** (tools/purebrain_hub/server/index.js) rather than build new service
- **Python sidecar** for ZIP parsing via child_process.spawn() — same pattern as existing gdrive_manager.py
- **SSE (Server-Sent Events)** for real-time Step 3 progress — not WebSocket (simpler, one-directional is sufficient)
- **sql.js stays** for MVP scale, flag migration to better-sqlite3 or PostgreSQL at 50+ concurrent users
- **Frontend**: Vanilla JS HTML page in WordPress/Elementor (same pattern as existing chatbox)

### Security Architecture
- Temp files isolated in /tmp/migration/ (NOT in permanent uploads/ dir)
- AES-256-GCM encryption at rest for temp files
- 30-minute TTL cron cleanup every 15 minutes
- File signature validation (magic bytes, not extension trust)
- 100MB ZIP limit, 20MB JSON/CSV limit

### Database Tables Added
- user_migration_profiles (core profile with extracted context)
- migration_jobs (job tracking with temp file reference)
- migration_insight_cards (Step 3 display cards)
- migration_suggested_tasks (Step 4 task cards)
- migration_oauth_tokens (Phase 2 only, AES-256-GCM encrypted)

### MVP Scope Confirmed
- ChatGPT + Claude file upload only
- Frequency analysis pattern extraction (no LLM calls — keeps it fast and free)
- 4-step wizard UI
- Migration Complete badge
- NO OAuth integrations in MVP

### Critical Risk: HubSpot CRM PII (Phase 2)
- Python parser must have explicit deny-list for contact-level fields
- Drop: email, firstname, lastname, phone, mobilephone, hs_email_*
- Store only structural data: pipeline names, deal stages, counts

### Build Order
- Sprint 1 (Days 1-5): Backend only — parser, job runner, SSE, insight/task generators
- Sprint 2 (Days 6-10): Portal HTML Steps 1-3
- Sprint 3 (Days 11-14): Step 4, badge, AI partner system prompt injection
- Sprint 4 (Days 15-18): Exodus page questions + Brevo passthrough
- Sprint 5 (Days 19-24): Security review + QA

## Output
Architecture doc saved to: exports/migration-portal-architecture.md
