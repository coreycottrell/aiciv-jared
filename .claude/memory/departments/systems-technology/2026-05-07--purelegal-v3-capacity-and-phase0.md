# PureLegal V3 — ST# Capacity Assessment + Phase 0 Unblock

**Date**: 2026-05-07
**Type**: operational
**Topic**: ST# capacity numbers + Phase 0 SQL migration for Hancock Law / PureLegal V3 remediation
**Trigger**: Aether ST# dispatch with 2026-05-08 18:00 EST capacity-lock deadline

## Key Findings

### Worker location (was unknown to QA + LC# triage)
- `hancock-law-api` IS deployed (CF account `In0v8.admins@puretechnology.nyc`)
- Live at `legal.purebrain.ai`, version 0.1.0, 10+ deployments TODAY (someone iterating, likely Chy/Morphe)
- Secrets `CLAUDE_API_KEY` + `JWT_SECRET` both set — AI failure NOT a missing-key issue
- D1 backing: `hancock-law-staging` (uuid `54a8c619-bdee-41a5-94d4-39de1e41fe2c`, 285 MB — holds 301K-clause corpus)
- **Source repo still off-machine** — all CF deployments are `Source: Upload`, no Git linkage. Chy/Morphe's local repo or private GitHub.

### D1 schema gap (was assumed by PD plan to "exist")
- `legal_templates` table **DOES NOT EXIST** in live D1 (verified via `SELECT name FROM sqlite_master`)
- Architect memo 2026-04-27 designed the table but nobody ever created it
- `/api/hr/templates` "static list" is hardcoded in worker code, not D1-backed
- **ST# Phase 0 = create the table + ingest V3 (74 rows after PFL split, mapping to 60 V3 templates)**

### Capacity numbers (engineer-days/wk)
- This week: ~1 ed (CE SME Sprint 4 + referral-v1 + ce.purebrain.ai DNS consume ~5/7)
- Next week: ~3–4 ed (CE SME Sprint 4 lands)
- Sustained from 5/21: ~5 ed/wk
- **Tier 1 = 4 weeks (ship 2026-06-03)** — honest number; not 2 weeks (impossible), not 6 weeks (slippage)
- Tier 2 ships ≈ 2026-06-24, Tier 3 ≈ 2026-07-08

## What Worked
- `wrangler deployments list --name hancock-law-api` returned full deployment history including author + version IDs — much faster than searching disk
- `wrangler d1 execute hancock-law-staging --remote --command "SELECT name FROM sqlite_master..."` enumerated full schema in <2s
- `wrangler secret list --name hancock-law-api` confirmed secrets without exposing values
- Probe sequence: `/api/health` → confirmed worker name; unauthenticated POST to generate routes → identified auth-gate-first vs route-not-found patterns

## What Didn't Work / Dead Ends
- `find /home -maxdepth 8 -type d -name "*hancock*"` returned only the cf-pages-deploy/hancock-law (frontend `index.html` only, NOT the worker source)
- No wrangler.toml on disk references `hancock-law-api` or `legal.purebrain.ai`
- `wrangler r2 bucket list` failed (token lacks R2 permission) — could not check for source backups in R2
- AI gen diagnosis impossible without source: `wrangler tail` would capture stack trace but fixing requires touching code we don't have

## Patterns

### Worker source location pattern
When CF Worker shows `Source: Upload` on every deployment AND no wrangler.toml references it locally, the source repo is on a teammate's machine, not in the monorepo. Don't waste time grepping — go directly to msg-chy.sh / direct ask.

### "Static list" smell
When QA reports "endpoint returns small static list" + architecture memo claims "D1 schema exists", verify D1 schema directly via wrangler before trusting the architect memo. Architect memos describe intent, not always live state.

### Multi-row-from-one-V3-row
V3 lists "State-Specific Paid Family Leave (13 states)" as 1 line item but it represents 13 sub-templates at build time. Headline counts (60 templates) and DB row counts (74) will diverge — flag this clearly so PD#/LC# don't double-count or miss the split.

### Honest dates require capacity floor
PD# asked "2 weeks, 4 weeks, or 6 weeks for Tier 1?" — the honest answer is the one that holds given current ST# load. Don't pick the middle out of false modesty; pick the number that matches the actual engineer-days arithmetic. 4 weeks IS the honest answer at 10–15 ed effort vs ~3–4 ed/wk available next week + ~5 ed/wk after.

## Critical-Path / Risks Documented

1. **Source repo location is THE blocker** for AI gen fix + Phase 1+ — must resolve via Chy/Morphe ask
2. **Active iteration risk**: 10+ deploys today by jared@puretechnology.nyc means Chy/Morphe shipping live; ST# changes must coordinate
3. **Mike Daser review bandwidth** is parallel risk — even fast ST# build doesn't ship without his per-batch sign-off

## Files

- Capacity + Phase 0 deliverable: `/home/jared/projects/AI-CIV/aether/exports/portal-files/st-capacity-and-phase0-purelegal-v3-2026-05-07.md`
- V3 D1 ingestion SQL: `/home/jared/projects/AI-CIV/aether/exports/sql/2026-05-07-purelegal-v3-legal-templates-migration.sql` (untracked on referral-v1 branch — recommend Aether commits to `main` or fresh `purelegal-v3` branch)

## Tags
purelegal, hancock-law, v3, capacity, d1-migration, integration-gap, phase-0, meridian, mike-daser
