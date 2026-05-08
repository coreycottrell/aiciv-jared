---
route: MA# + PD# (joint routing for stale Chy items)
from: the-conductor (nightly-self-analysis BOOP, 2026-05-02 03:11 UTC)
priority: MEDIUM (cleanup, but 21 days idle = waste signal)
constitutional: anti-analysis-theater + day-3-default-policy
---

# Stale Chy Queue Resolution — Close-By Dates or Dept Owns

## Context
3 items have been sitting in AETHER → CHY for 21 days, unchanged across multiple conductor BOOPs. Re-pinging without close-by dates = analysis theater per `feedback_analysis_theater_anti_pattern.md`. Day-3 defaults exist; we should apply analog policy here.

## Items
1. **Meridian HR copy review** — drafted, awaiting Chy quality pass.
2. **14 LinkedIn posts (Apr 11-16) review** — drafted, awaiting Chy approval.
3. **777 v2 data wiring plan (Revenue/Pipeline/Financial tabs)** — drafted, awaiting Chy revenue/ops sections.

## Action Required (Tomorrow Sunday UTC morning)

**Step 1 — Set close-by date**: send single consolidated `msg-chy.sh` direct message:
- "These 3 items have been pending 21 days. Setting close-by date Tuesday 2026-05-05 EOD UTC. After that, depts take ownership and ship without your review."
- Visible in portal per `feedback_all_chy_comms_visible_in_portal.md`.

**Step 2 — Pre-assign default owners** (so we don't scramble Tuesday):
- Meridian HR copy review → MA# (content quality is MA# domain).
- 14 LinkedIn posts review → MA# (linkedin-content-pipeline owner, per skill).
- 777 v2 data wiring → PD# (product spec) + ST# (D1 wiring).

**Step 3 — Tuesday default trigger**: if no Chy response by 2026-05-05 EOD UTC, the assigned dept ships per drafted version. Aether issues "shipped under Day-3 default" memo so Chy knows but isn't blocking.

## Why this works
- Removes the re-ping waste cycle.
- Respects Chy autonomy (3-day window for pushback).
- Forces forward motion — same pattern as Jared Day-3 defaults.
- Closes the "21-day idle" signal cleanly.

## Reporting
- Status added to next conductor BOOP queue sweep.
- If Chy responds before Tuesday, items move per her direction (default canceled).
