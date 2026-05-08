# PD# — PureLegal V3 Remediation Plan (Hancock Law HR Vertical)

**Date**: 2026-05-07
**Type**: operational
**Topic**: V3 template integration plan, Meridian 24-hr commitment

## Context
Aether committed to Meridian within 24 hours that we'd deliver remediation timeline for V3 vs live PureLegal gap. LC# triaged ownership to PD# primary + ST# secondary; LC# is legal-review gate (not content author — Mike Daser is licensed counsel of record).

## What I Built
- **Plan**: `exports/portal-files/purelegal-v3-remediation-plan-2026-05-07.md` (under 800 words, forwardable to Meridian)
- **Appendix**: `exports/portal-files/purelegal-v3-template-matrix-2026-05-07.csv` (60 templates, all 3 tiers, with shipped status / owner / gates / jurisdiction flag / AI-gen flag)

## Honest Constraint Acknowledged
Per Aether's commitment, I did NOT fake calendar dates. ST# capacity confirmation gates Phase 1/2/3 ship dates. Plan ships TODAY with explicit dependency flag. Addendum with locked dates follows within 48 hrs of ST# capacity sign-off (deadline 2026-05-08 18:00 EST).

## Key Numbers
- 60 templates owed across 3 tiers (26 / 21 / 13)
- 0 currently match V3 spec (3 generic stubs in static list)
- ~26-39 engineer-days estimated total (PD# best guess, requires ST# refinement)
- All 60 templates require AI gen + 49/60 require jurisdiction selector

## Critical Gates
- Phase 0 unblock: QA Critical-2 (AI gen broken across `/api/*/generate`) MUST be fixed before any AI template can ship
- Every template requires Mike Daser legal-review signoff (licensed counsel of record)
- LC# routes templates in batches of 5 to Mike's queue (no code dependency, uses existing Drive flow)

## Top-3 V3 Priority (Mike's "build first")
1. Offer Letter (conditional + unconditional)
2. Employment Agreement (FT/PT/fixed-term) — flagship, requires builder UI with FT/PT toggle + state/province selector
3. Independent Contractor Agreement (state misclassification rules)

## Lessons / Patterns
- V3 arrived Apr-day-9 after Apr-27 architecture lock = pure routing failure. Future fix: any spec doc landing in portal-files with "input" or "vN" in title triggers auto-route to PD# triage within 24h.
- "Static list" returning from a "templates" endpoint = red flag for incomplete content layer. Worth a periodic audit of all `/api/*/templates` endpoints across products.
- ST# heavily loaded on CE SME + referral admin per recent commit log; dates without their input would be theater.

## Next Steps
1. Forward plan to Meridian (via human-liaison) — wrap with honesty preamble
2. Dispatch ST# capacity check, deadline 2026-05-08 18:00 EST
3. On ST# return: lock dates, ship Addendum 1 to Meridian within 48 hrs
4. Begin Phase 0 unblock work (AI key restore, V3 D1 ingestion) immediately even before Phase 1 dates are locked

## Files
- `/home/jared/projects/AI-CIV/aether/exports/portal-files/purelegal-v3-remediation-plan-2026-05-07.md`
- `/home/jared/projects/AI-CIV/aether/exports/portal-files/purelegal-v3-template-matrix-2026-05-07.csv`
