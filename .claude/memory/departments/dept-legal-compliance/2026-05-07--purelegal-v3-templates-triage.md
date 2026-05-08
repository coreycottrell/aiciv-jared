# PureLegal V3 Templates Triage — Meridian Flag

**Date**: 2026-05-07
**Type**: operational
**Department**: dept-legal-compliance
**Mode**: Read-only triage only

## Situation
Meridian (HR Intelligence) flagged via AgentMail that PureLegal Employment Agreement templates aren't using her V3 input from "Hancock Law HR Legal Vertical V3" (Mike Daser, SVP HR, dated 2026-05-06). Mike (legal advisor) confirmed the live templates don't reflect V3.

## Investigation Findings

### V3 doc location
`/home/jared/exports/portal-files/MERIDIAN-HR-LEGAL-V3-2026-05-06.md` — 967 lines, 60+ templates across 3 tiers, US state-by-state + Canada province-by-province, prescribes Employment Agreement Builder with FT/PT/fixed-term + jurisdiction selectors.

### Live state (legal.purebrain.ai)
- `/api/hr/templates` exists but per QA audit (today, 2026-05-07) returns a **"Static list"**, not the V3 inventory.
- All AI generation endpoints return "Generation failed" — this is QA Critical-2.
- Source code NOT in this monorepo. Hancock Law Worker is in a separate repo (QA confirmed dead-end at `workers/hancock-law-api/`).
- Architecture lock from 2026-04-27 predates V3 (2026-05-06) — V3 arrived after the build was sealed.
- Zero commits referencing hancock/legal/v3 in this monorepo's git log past 7 days.

### Gap classification
**INTEGRATION failure**, not deploy: V3 received but never ingested into `legal_templates` D1 table or routed to engineering.

## Ownership Decision
- **Primary**: PD# (Product Development) — accept V3 as canonical, sequence Tier 1, brief eng
- **Secondary**: ST# (Systems & Technology) — locate Worker repo, ingest D1, build selector UI, fix AI gen (chains to existing Critical-2)
- **LC# (me)**: Standing by for legal-review gate. Will NOT review V3 content itself — Mike Daser authored it (licensed counsel).

## Dispatch Plan
1. Aether → PD# brief
2. PD# → ST# dispatch
3. LC# → legal-review gate before ship
4. HR# (Meridian) loop-in with ETA

## Deliverable
`/home/jared/exports/portal-files/triage-purelegal-v3-templates-2026-05-07.md` (under 500 words per spec)

## Pattern Learned
When a non-engineering manager (HR, Legal, Marketing) supplies a domain-specific spec post-architecture-lock, default failure mode is silent integration drop. Need a routing layer: any spec doc landing in `portal-files/` after a product is live MUST be routed to PD# the same day or it dies in the file system.

## Cross-references
- `agent-learnings/qa-engineer/2026-05-07--hancock-law-full-qa-audit.md` (live audit confirming static list + AI broken)
- `agent-learnings/architect/20260427-legal-platform-architecture.md` (pre-V3 architecture lock)
- `agent-learnings/web-dev/2026-04-27-lawinsider-pitch-page.md` ("PureLegal" naming confirmed)
