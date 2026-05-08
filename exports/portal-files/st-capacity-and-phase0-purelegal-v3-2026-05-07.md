# dept-systems-technology: ST# Capacity + Phase 0 — PureLegal V3

**Agent**: dept-systems-technology | **Date**: 2026-05-07 | **Deadline**: 2026-05-08 18:00 EST

---

## Track A — Capacity

### A.1 Hancock Law Worker — LOCATED (partial)

**Worker IS live**:
- Name: `hancock-law-api` (account `In0v8.admins@puretechnology.nyc`)
- Route: `legal.purebrain.ai` | Health: `{"service":"hancock-law-api","version":"0.1.0"}`
- Secrets present: `CLAUDE_API_KEY` + `JWT_SECRET` — **AI failure is NOT a missing-key issue**
- D1 backing: `hancock-law-staging` (uuid `54a8c619-...`, 285 MB — holds 301K-clause corpus)
- **10+ deploys TODAY** (5/7 12:42 → 15:17 UTC, all `Source: Upload`, author `jared@puretechnology.nyc`) — Chy/Morphe iterating live

**Source repo: STILL OFF-MACHINE.** Confirmed NOT in `/home/jared/projects/AI-CIV/aether/workers/`, `/home/jared/purebrain-site/`, `brainiac-purebrain`, or any wrangler.toml on disk. All deploys are direct API uploads, not Git-linked.

**ASK Jared**: Where is hancock-law-api source? (Chy/Morphe local + private GitHub likely.)

### A.2 ST# Capacity (engineer-days/wk)
- **5/7–5/13**: ~1 ed (CE SME Sprint 4 + referral-v1 + ce.purebrain.ai DNS consume rest) → Phase 0 only
- **5/14–5/20**: ~3–4 ed (CE SME lands)
- **5/21+ sustained**: ~5 ed/wk

### A.3 Tier Ship Windows (honest)

| Phase | Effort | Calendar |
|---|---|---|
| **Phase 0 unblock** | 2–4 ed | 5/13 |
| **Tier 1** (26 templates + Employment Agreement Builder UI + jurisdiction selector) | 10–15 ed | **2026-06-03 (≈4 wks)** |
| **Tier 2** (21 templates) | 8–12 ed | **2026-06-24 (≈7 wks)** |
| **Tier 3** (13 templates) | 6–8 ed | **2026-07-08 (≈9 wks)** |

**Recommend committing to Meridian: Tier 1 in 4 weeks.** 2 weeks impossible (would drop CE SME). 6 weeks slips. **4 weeks is the arithmetic.**

---

## Track B — Phase 0

### B.1 AI Gen Critical-2 Diagnosis

**ST# probes** (5/7 15:30 UTC):
- `/api/contract/generate` → `{"error":"not found"}`
- `/api/draft/generate` → `{"error":"not found"}`
- `/api/clause/generate` → `{"error":"not found"}`
- `/api/hr/generate` → `{"error":"unauthorized"}` (auth-gate-first)

**Hypothesis** (NOT confirmed without source):
- `CLAUDE_API_KEY` IS set — different bug from Chy's earlier AI key fix
- Failure is post-auth ("Generation failed" QA saw was authed)
- Most likely: Anthropic model name drift (deprecated model id) OR payload schema mismatch OR Anthropic credit/rate failure
- Less likely: KV/R2 binding (would 500, not "Generation failed")

**Action**: Need worker source + `wrangler tail hancock-law-api` to capture stack trace. **ST# cannot fix without source — ping Chy/Morphe.**

### B.2 V3 D1 Ingestion SQL — WRITTEN

**Schema discovery**: `legal_templates` table **DOES NOT EXIST** in `hancock-law-staging` (verified via `SELECT name FROM sqlite_master`). Architect memo 4/27 designed it; nobody created it. Live `/api/hr/templates` "static list" is hardcoded in worker code, not D1-backed.

**SQL written**: `/home/jared/projects/AI-CIV/aether/exports/sql/2026-05-07-purelegal-v3-legal-templates-migration.sql`
- `CREATE TABLE legal_templates` (id, name, tier, v3_section, jurisdictions JSON, employment_type, requires_ai_gen flag, requires_jurisdiction_selector flag, status, source_version, legal_reviewer, shipped_at, metadata JSON, timestamps)
- 3 indexes (tier, section, status)
- **74 V3 rows** mapping to V3's 60 headline templates (PFL counted as 1 row representing 13 state sub-templates at build time)
- Tier 1: 25 rows | Tier 2: 25 rows | Tier 3: 24 rows
- Jurisdiction metadata + special flags preserved (CA SB553, FTC non-compete ban states, Quebec Civil Code, OWBPA, ABC test, USERRA, etc.)
- Idempotent (`IF NOT EXISTS` + `INSERT OR REPLACE`)

**NOT APPLIED** per spec. Apply command (when Jared authorizes):
```
wrangler d1 execute hancock-law-staging --remote --file exports/sql/2026-05-07-purelegal-v3-legal-templates-migration.sql
```

**Commit pending**: File untracked on `referral-v1` branch. Recommend Aether commits to `main` or fresh `purelegal-v3` branch (don't pollute mid-build referral branch).

### B.3 Verification Path

After SQL applies AND worker code change to `SELECT FROM legal_templates`:
```
curl https://legal.purebrain.ai/api/hr/templates -H "Authorization: Bearer <session>" | jq 'length'  # expect 60-74
```
**WORKER CODE CHANGE BLOCKED** on source repo access — verification path can't close in Phase 0 without it.

---

## Critical-Path / Risks

| Item | Owner | Blocks |
|---|---|---|
| Hancock Law worker source repo location | Jared (ask Chy/Morphe) | AI gen fix + all Phase 1+ |
| Mike Daser review bandwidth (templates/wk) | LC# / HR# | Tier 1 ship date |
| Active iteration coordination (10+ deploys today by Chy/Morphe) | ST# coord | Avoid clobbering live work |
| Jared D1 schema apply auth | Jared | V3 ingestion go-live |
| Worker code → `/api/hr/templates` reads D1 | source-dependent | V3 inventory visibility |

## Files

- This deliverable: `/home/jared/projects/AI-CIV/aether/exports/portal-files/st-capacity-and-phase0-purelegal-v3-2026-05-07.md`
- SQL migration: `/home/jared/projects/AI-CIV/aether/exports/sql/2026-05-07-purelegal-v3-legal-templates-migration.sql`
- Memory: `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/systems-technology/2026-05-07--purelegal-v3-capacity-and-phase0.md`

## TL;DR for Aether → Meridian

> Worker located (`hancock-law-api`, live, iterating) but **source repo off-machine** — need Chy/Morphe to point us to it. ST# realistic windows: **Phase 0 by 5/13, Tier 1 by 6/3 (4 wks), Tier 2 by 6/24, Tier 3 by 7/8**. V3 D1 ingestion SQL written (74 rows, 60 V3 templates with jurisdiction metadata) — pending Jared sign-off to apply. AI gen Critical-2 NOT a missing-key issue (key set) — needs worker source for stack trace.
