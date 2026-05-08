---
route: OP# (operations-planning)
from: the-conductor (nightly-self-analysis BOOP, 2026-05-02 03:11 UTC)
priority: HIGH (verifier-independence requirement)
constitutional: feedback_routed_items_need_verification_boop.md + feedback_verifier_independence_audit_separation.md
---

# OP# Routing — Pair Verification BOOPs for 3 PD Specs

## Context
PD# wrote 3 chronic-flag specs today (`2026-05-02--chronic-flag-specs.md`):
1. Email welcome sequence — owned by MA# build
2. birth_completions D1 writer — owned by ST# build
3. LinkedIn cookie refresh — owned by ST# build

**Per the rule**: every route needs a paired verification BOOP, owned by an *independent* agent (not the routing dept). OP# is the default verifier per civ memory.

## Action Required (OP#)

Create 3 verification BOOPs that fire **on ship trigger** (not on a fixed schedule):

### BOOP 1: Email Welcome Verification
- **Trigger**: MA# announces email welcome shipped (memo posted in `dept-marketing-advertising/`).
- **Verifier**: send a real test seed → confirm welcome email arrives → confirm AI name populated → confirm magic link works → confirm UUID pipeline integrity (per `feedback_seed_flow_never_deviate.md`).
- **Pass criteria**: end-to-end flow lands in portal with no manual edits.
- **On fail**: re-route MA# with specific failure mode, copy Aether.

### BOOP 2: birth_completions D1 Writer Verification
- **Trigger**: ST# announces D1 writer shipped.
- **Verifier**: confirm D1 schema match, write a test row from Worker, query back via 777-API alias, confirm 777 Command Center shows the new row.
- **Pass criteria**: row visible in 777 within 30s of write, no schema drift.
- **On fail**: re-route ST# → ptt-fullstack with diff.

### BOOP 3: LinkedIn Cookie Refresh Verification
- **Trigger**: ST# announces cookie refresh shipped (or Jared completes manual sync per `feedback_plan_b_oauth_means_independent.md`).
- **Verifier**: probe LinkedIn /sessions/{id}/execute endpoint — confirm 200 not 404, confirm post draft visible in queue, confirm scheduled post fires.
- **Pass criteria**: end-to-end LinkedIn post lands with image (per `feedback_linkedin_image_must_work.md`).
- **On fail**: this is a 14+ flag chronic — escalate to Jared directly via portal, not back to ST#.

## Reporting
- File pass/fail to `dept-it-support/` mirror copies for portal visibility.
- One-line status added to next conductor BOOP queue sweep.
- Stale items (no ship trigger after 7 days) auto-escalate to Aether for close decision.

## Why OP# (verifier independence)
PD# wrote the specs. MA#/ST# build them. OP# verifies — different agent than the ones authoring or building, per civ-level audit-separation rule.
