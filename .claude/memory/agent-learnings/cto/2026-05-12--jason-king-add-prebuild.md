# CTO Pre-Build — Jason King Client Insert (Couplify Duo 2 Mirror)

**Date**: 2026-05-12
**Type**: operational + teaching
**Status**: PRE-BUILD-APPROVED — handed to ptt-fullstack
**Time budget**: 5–10 min (achieved ~8 min including memory search + deliverable + portal)

---

## What was asked

Jared portal: register Jason King in `purebrain-clients.clients` as covered-seat under Sheila's sub. Witness already minted AI=`Resolve` and emitted magic link `https://resolve-jason.app.purebrain.ai/?token=...`. "Just like Amy Housand" pattern.

---

## What worked (reusable pattern)

### Memory-first paid off

The Amy Housand (May 10) pattern in `whitehurst-household-audit-2026-05-10.md` + `p1-3-row-reconcile-receipt-2026-05-10.md` had EVERYTHING needed:
- Exact 16-column INSERT shape for `purebrain-clients.clients`
- The duo-partner-seat signature: `payment_status=covered`, `paypal_subscription_id=''`, `total_paid=0`, `source=paypal`, `tier=Partnered`
- Constitutional gate: write to clients-DB ONLY (not social)
- The May 7 D1 STOP lesson (wrong-DB writes)
- Parameterized-query D1 REST API pattern

**No new architectural thinking required** — the household pattern was already battle-tested 2 days ago. CTO pre-build for "mirror an existing in-prod pattern" should be FAST and largely consist of mapping new values into known slots.

### Welcome email decision pattern

When Witness has already emitted the magic link, **NO welcome email from us**. Constitutional `feedback_seed_flow_never_deviate.md` is "ONE seed per client after email" — Witness owned that. Doubling = violation.

Test for "skip welcome": is there already a working magic-link URL in the customer ask? If YES → skip. If NO → seed flow fires.

### Couplify household now fully mapped

Pre-Jason: Duo 1 complete (Jay+Cai), Duo 2 half-empty (Sheila + [UNSET])
Post-Jason: BOTH duos complete. Whitehurst household audit memo should update to reflect this — Jason populates the previously-[UNSET] slot.

---

## What I flagged for ptt-fullstack

1. **Email NOT in Jared's ask** — Jared wrote "Jason King from couplify" but didn't specify the email. Likely `jason@couplify.com` mirroring `jay@`/`amy@`/`sheila@` — but ptt-fullstack MUST confirm before INSERT. Don't infer.
2. **Magic-link domain ALREADY rewritten** — Jared's URL is `.app.purebrain.ai` not `.ai-civ.com`. No domain rewrite needed our side — Witness handled it per `feedback_magic_link_pipeline_constitutional.md`.
3. **Backup-first** — May 7 STOP lesson (wrong-DB writes) → always backup before any D1 write.

---

## Teaching: CTO pre-build for "mirror pattern" tasks

When customer ask says "do X like we did Y for Z":

1. Memory-search Y immediately (don't reinvent)
2. Pull the deliverable + memory from Y
3. Map new values into known slots (table form)
4. Re-verify constitutional gates haven't shifted since Y shipped
5. Flag only the deltas (in this case: email TBD, household map update)

This is the cheapest CTO review possible — most of the architectural work is already paid for. Don't gold-plate.

---

## Anti-patterns I avoided

- Spec'ing a new schema migration (P2 `paid_by_email` column is already queued — don't conflate dispatches)
- Sending a welcome email (Witness already owned this — would duplicate)
- Suggesting a `purebrain-social` write (constitutional ban + Phase-9 DROP imminent)
- Inferring Jason's email from surname (S5 fuzzy ban)
- CTO review re-litigating the Amy precedent (it shipped clean — trust it)

---

## Files

- Deliverable: `/home/jared/exports/portal-files/cto-prebuild-jason-king-add-2026-05-12.md`
- Source pattern: `.claude/memory/agent-learnings/full-stack-developer/2026-05-10--whitehurst-household-audit.md`
- Source pattern: `exports/portal-files/whitehurst-household-audit-2026-05-10.md`
- Source pattern: `exports/portal-files/p1-3-row-reconcile-receipt-2026-05-10.md` (16-col INSERT shape)
- Source pattern: `.claude/memory/agent-learnings/ptt-fullstack/2026-05-07--d1-schema-migration-stop-clients-wrong-db.md` (which-DB lesson)

## Constitutional refs touched

- `feedback_purebrain_social_never_touches_referral_or_clients.md`
- `feedback_seed_flow_never_deviate.md`
- `feedback_magic_link_pipeline_constitutional.md`
- `feedback_s5_payername_fuzzy_fallback_banned.md`
- `feedback_every_feature_multi_tenant_for_customers.md`
- `feedback_cto_pre_build_architectural_review.md`
