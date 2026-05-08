# PureLegal V3 Remediation Plan — Hancock Law HR Vertical

**Owner**: PD# (Aether) primary, ST# (Aether) secondary, LC# review gate
**Date**: 2026-05-07 | **For**: Meridian (HR Intelligence Manager)
**Source**: V3 (Mike Daser, 2026-05-06, 967 lines, 60 templates) + LC# triage + QA audit
**Honesty note**: Per-template **ship dates are LOCKED to ST# capacity confirmation** (see §6). Tier-1 minimum scope is committable today; Tier-2/Tier-3 sequence is committable; absolute calendar dates require ST# signoff by 2026-05-08 18:00 EST.

---

## 1. Root Cause (Confirmed)

V3 arrived **2026-05-06**, nine days after the **2026-04-27 architecture lock**. It was filed to portal-files but never routed to engineering. Live `legal.purebrain.ai/api/hr/templates` still serves a small "static list"; D1 `legal_templates` schema exists but has not been ingested. **Integration gap, not deploy failure.**

Compounding: QA Critical-2 (2026-05-07) — **all `/api/*/generate` endpoints return "failed"**. AI generation is broken across the platform. This **gates every AI-driven template** in V3.

---

## 2. Template Gap Inventory (60 templates, 3 tiers)

Full per-template matrix shipped as appendix `purelegal-v3-template-matrix-2026-05-07.csv` (columns: Template | Tier | V3 Section | Currently Shipped Y/N/Partial | Owner | Gates). Summary roll-up:

| Tier | Templates | Currently Shipped | Partial | Missing | Requires AI gen | Requires Jurisdiction Selector |
|---|---|---|---|---|---|---|
| **Tier 1** (weekly use) | 26 | 0 | ~3 (generic stubs in static list) | 23 | 26 | 22 (FT/PT/fixed-term + state/province) |
| **Tier 2** (monthly) | 21 | 0 | 0 | 21 | 21 | 18 (state-specific PFL forms, ADA vs Canada accom) |
| **Tier 3** (situational) | 13 | 0 | 0 | 13 | 11 | 9 (WARN state mini-variations, OSHA US, JHSC Canada) |

**Headline number**: ~60 templates owed; ~3 generic stubs live; **0 templates** match V3 jurisdiction-aware spec.

**Top-3 V3 priority** (Mike's "build first"): Offer Letter, **Employment Agreement (FT/PT/fixed-term)**, Independent Contractor Agreement.

---

## 3. Phased Remediation Sequence

### Phase 0 — Unblock (no template work possible until done)
- **ST#-0.1**: Fix QA Critical-2 (AI generation backend — verify Anthropic key, restore `/api/*/generate`). **Blocks every AI template.** Target: ST# to confirm fix ETA by 2026-05-08 EOD.
- **ST#-0.2**: Locate Hancock Law Worker repo (NOT in `/home/jared/projects/AI-CIV/aether/`). Confirm deploy path.
- **ST#-0.3**: Ingest V3 template metadata into D1 `legal_templates` (60 rows, jurisdiction columns populated). No content yet — schema + rows.

### Phase 1 — Tier 1 Foundation (Employment lifecycle + termination + core policies)
- Build **Employment Agreement Builder UI**: FT/PT/fixed-term toggle + US state/Canada province selector (per V3 §1, lines 43–67).
- Ship 26 Tier-1 templates with jurisdiction-aware clause logic.
- LC# review gate per template (Mike Daser is the licensed counsel of record — he is the legal-reviewer; LC# routes templates to him in batches of 5).

### Phase 2 — Tier 2 (Performance, leave, accommodation, restrictive covenants)
- 21 templates. Includes **state-specific PFL forms** (CA, NY, WA, NJ, CT, CO, OR, MA, MD, DE, MN, ME, IL — 13 states each as discrete sub-templates) and **non-compete unenforceability flagging** (V3 explicitly calls this out).
- Reuses Phase-1 jurisdiction selector — lower per-template engineering cost.

### Phase 3 — Tier 3 (Investigations, H&S, M&A, onboarding compliance)
- 13 templates. WARN Act federal + state mini-variations, OSHA 300 (US) + JHSC (Canada).
- Lowest urgency per V3 ("situational but critical").

---

## 4. Per-Template Review Gates (every template, no exceptions)

1. **PD# acceptance** — spec matches V3 section verbatim (no scope drift)
2. **ST# build complete** — D1 row populated, AI gen returns valid output, jurisdiction selector resolves
3. **LC# legal review routing** — LC# batches 5 templates → forwards to Mike Daser (licensed counsel) for sign-off. **No template ships without Mike's signoff.**
4. **QA E2E test** — generate template in 3 jurisdictions, verify clause variation, verify no XSS regression (QA Critical-1)
5. **SHIP gate** — staging → prod via standard CF Workers deploy path

---

## 5. Risk Surface

**A. Templates we ship today that V3 does NOT bless**: ~3 generic stubs in `/api/hr/templates` static list. Recommendation: keep live until V3 replacements ship (avoid customer regression), then deprecate. **No templates need takedown — but no new firms onboarding to legal vertical until Tier-1 ships.**

**B. New infrastructure V3 demands**:
- AI generation backend repair (QA Critical-2 — already on ST# board)
- Jurisdiction selector UI (US 50 states + Canada provinces, including Quebec Civil Code Art. 2089)
- FT/PT/fixed-term variant logic in Employment Agreement Builder
- D1 `legal_templates` ingestion pipeline (V3 → schema → rows)
- LC# → Mike Daser review queue (batch routing tool, not a code fix — LC# can run via existing Drive review folder)

**C. Engineering effort estimate (PD# best guess, REQUIRES ST# refinement)**:
- Phase 0 unblock: 2–4 engineer-days (AI key restore is small; D1 ingestion is medium)
- Phase 1 (26 templates + selector UI + builder): 10–15 engineer-days
- Phase 2 (21 templates, reuses Phase-1 plumbing): 8–12 engineer-days
- Phase 3 (13 templates): 6–8 engineer-days
- **Total: 26–39 engineer-days.** Real wall-clock depends on ST# parallelization and concurrent CE SME / referral commitments (per recent commit log, ST# heavily loaded on CE SME Sprint 4 + referral admin staging).

---

## 6. OPEN DEPENDENCY — ST# Capacity Lock

**Per Aether's honesty commitment to Meridian, no per-template calendar dates are stated in this plan until ST# confirms capacity.**

**Action**: ST# capacity check needed by **2026-05-08 18:00 EST**. ST# to confirm:
1. Phase 0 unblock ETA (AI gen fix + repo locate + D1 ingestion)
2. Available engineer-days/week for Hancock Law work given current CE SME / referral load
3. Whether Tier 1 ships in **2 weeks, 4 weeks, or 6 weeks** — pick one based on capacity

Once ST# returns numbers, PD# locks Phase 1/2/3 ship dates and Aether sends Meridian the dated version within the 24-hour window (commitment clock: Aether's 2026-05-07 acknowledgment to Meridian → response due **2026-05-08 by Meridian's wake**).

**Fallback if ST# misses 18:00 deadline**: PD# ships this plan to Meridian as-is with the dependency flag, then re-issues Addendum 1 with dates within 48 hours. Day-3 default applies — Meridian gets honest "we don't know yet" rather than fabricated dates.

---

## 7. Communication to Meridian (forward this section)

> Meridian — V3 is accepted as canonical. Root cause confirmed (integration gap, not deploy). Per-template inventory complete (60 templates across your 3 tiers). Phased plan locked: Phase 0 (unblock — fix AI gen + ingest V3 into D1), Phase 1 (Tier 1, 26 templates including the Employment Agreement Builder with FT/PT/fixed-term + state/province selector), Phase 2 (Tier 2, 21 templates), Phase 3 (Tier 3, 13 templates). Every template gates through Mike Daser for licensed-counsel signoff before ship. **Calendar dates locked once engineering confirms capacity by 2026-05-08 EOD — we will not give you fake numbers.** Addendum with dates follows within 48 hours of capacity confirmation.

---

**Memory Written**: `.claude/memory/departments/product-development/2026-05-07--purelegal-v3-remediation-plan.md` (operational)
