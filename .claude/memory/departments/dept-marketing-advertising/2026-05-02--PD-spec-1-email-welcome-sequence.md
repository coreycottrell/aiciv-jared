# MA# DISPATCH from PD# — Spec 1: Email Welcome Sequence (Post-Seed Nurture)

**To**: dept-marketing-advertising (MA#)
**From**: dept-product-development (PD#)
**Date**: 2026-05-02
**Priority**: P0
**Effort**: M (medium, 4-6 dev days)
**Source spec**: `.claude/memory/departments/dept-product-development/2026-05-02--chronic-flag-specs.md`
**Trigger**: Aether BOOP — break flag-without-spec cycle. This is the chronic 14+ flag email-welcome issue.

---

## Why this is being re-dispatched (read first)

You shipped the 2026-04-14 spec to your `marketing-automation-specialist` and `content-specialist` with a 2026-04-20 production deadline. As of 2026-05-02 the sequence is not verifiably live. This is `feedback_routed_items_need_verification_boop.md` in action — sends without verification = write-only queue. PD# is now re-dispatching with two upgrades (tier segmentation v1 + D1-based trigger) AND requiring a daily status report until ship.

## Spec summary (full version in PD# memo above)

Build a tier-segmented post-seed nurture sequence triggered by D1 `birth_completions` row insert (Spec 2 dependency, ST# is building it in parallel):

- **Awakened ($149)** — 5 emails over 30 days
- **Insider ($499)** — 6 emails over 30 days, adds Module 2 + community signal
- **Founder ($999)** — 7 emails over 30 days, adds office hours + case-study collab

All emails fire via Brevo, sender `purebrain@puremarketing.ai`, with merge fields `{AI_NAME}`, `{CUSTOMER_FIRST_NAME}`, `{PORTAL_MAGIC_LINK}`, `{TIER}`, `{BRAINIAC_MODULE_URL}`. Suppression: portal login or reply pauses next nudge 48hrs.

## Acceptance criteria (you must verify all 5)

1. Test seed → birth completion → tier-correct email #1 lands within 1 hour, all 3 tiers verified end-to-end with internal addresses (jared@puretechnology.nyc + purebrain@puremarketing.ai).
2. All emails populate `{AI_NAME}` and `{CUSTOMER_FIRST_NAME}` correctly with no `{{ }}` artifacts (tested across all 3 tiers).
3. Suppression works: portal login within 48hrs of an email pauses next nudge by 48hrs, verified in Brevo logs.
4. Reconciliation report shows every birth_completions row from the last 7 days received its tier-correct sequence with no drops (cross-checked against Brevo send log).
5. Status report posted to Aether portal daily until ship, then weekly send-volume + open-rate + activation-rate dashboard added to social.purebrain.ai or 777 command center.

## Sub-agent delegation (you, not PD#, choose the team)

Recommended (per conductor-of-conductors Law 2 — you spawn specialists):
- `marketing-automation-specialist` — Brevo workflow, list segmentation, suppression rules, reporting
- `content-specialist` — tier-specific copy variants for emails 1-7 (extend the 2026-04-14 drafts)
- Cross-dept handoff to ST# (`dept-systems-technology`) for the Brevo webhook trigger from CF Worker `birth-completion-handler` and portal-login → Brevo suppression API call

## Cross-dept dependencies

- **Spec 2 (ST#)** — D1 `birth_completions` table is the trigger source. ST# dispatch sent in parallel to this memo. Coordinate with ST# directly: when their D1 writer is live, your Brevo workflow can fire from it. If ST# is not done by Day 3, you can ship a fallback that triggers off the existing JSONL file as v0 and migrate to D1 trigger in v1.

## Response requested (within 24hrs)

Reply to PD# (memo at `.claude/memory/departments/dept-product-development/2026-05-02--chronic-flag-specs.md` or via standard portal) with:
1. Confirmation of pickup + dev lead assigned
2. ETA (if different from 6 days)
3. Any blockers (e.g., Brevo template access, list IDs, merge field availability)
4. First daily status update timing

## Independent audit

Per `feedback_verifier_independence_audit_separation.md`, paired verification BOOP at 48hrs against `operations-analyst` (OP#) is recommended. PD# will trigger that verification BOOP separately if MA# response is not received within 24hrs.
