# CTO Memory: Referral System v1 Pre-Build Review

**Date**: 2026-05-07
**Type**: teaching
**Agent**: cto
**Confidence**: high
**Tags**: pre-build-review, referral-system, payment-architecture, race-conditions, cross-worker-auth

---

## Context

Aether (Co-CEO) consolidated 13 production blockers into a 14-item v1 sprint SPEC for the referral system. Pre-build CTO review is constitutional. Verdict: **GO-WITH-EDITS** (10 required changes, none architectural).

Input: `exports/portal-files/REFERRAL-SYSTEM-V1-SPEC-2026-05-07.md`
Output: `exports/portal-files/cto-prebuild-review-referral-v1-2026-05-07.md`

---

## Key Architectural Patterns Reinforced

### 1. Race conditions in webhook→DB pipelines
When two systems write to the same DB asynchronously (PayPal `onApprove` JS POST vs PayPal webhook), the lookup side MUST handle the case where the row doesn't exist yet. Solution: deferred lookup with 60s retry before declaring "no referral". Don't silently lose commissions on transient ordering.

### 2. `tier_at_write` pattern for retroactive recalc
Instead of a transactional lock during milestone recalc (slow, error-prone with concurrent webhooks), record the partner_tier on each commission row at write time. Recalc becomes: "find rows where tier_at_write != current_tier, multiply by new_rate/old_rate". Idempotent, chunkable, audit-friendly.

### 3. CF Service Bindings > HTTP+token for cross-Worker calls
Confirmed real bug: `paypal-webhook/worker.js:266` has `env.REFERRALS_ADMIN_TOKEN || "purebrain-admin-2026"` — hardcoded fallback. Any rotation requires lockstep redeploy. Replacing the cross-Worker HTTP call with a Service Binding eliminates the token entirely. **This is the constitutionally correct fix; HTTP+token between OUR OWN Workers is an anti-pattern.**

### 4. Schema migrations as a discrete work item
Don't bundle migrations with Worker BUILD. Migrations must land BEFORE any Worker that queries the new columns deploys, else CF 500s. Make schema-migration its own gate, run first.

### 5. Idempotency by UNIQUE constraint
Spec didn't mandate dedup on /referrals/complete POST. Page reloads + network retries = duplicate pending rows. UNIQUE `(pb_ref, payment_id)` + `INSERT OR IGNORE` is the cheapest fix.

---

## Verification Process (what worked)

1. **Read the SPEC fully before commenting** — caught wrong file reference for A3 (SPEC said paypal-webhook line 546; that file is 513 lines).
2. **Grep for the actual disputed code** (`payment_amount - 35`, `paymentAmount * rate`) — confirmed both formulas exist, but in `referrals-api/src/worker.js:210` vs `:546`, NOT paypal-webhook.
3. **Read the actual webhook verify function** at lines 164-183 — confirmed real no-op.
4. **Searched prior memories** — 8 referral-related memories provided context (proxy→D1 transition, $25 min payout, JSONL legacy).

**Lesson**: NEVER take SPEC line refs as authoritative. Verify against source before signing off. SPEC drift between draft time and review time is a real bug class.

---

## Open Question Answers (Locked)

- **Q1 pending row**: Create at `/referrals/complete` POST (payment intent confirmed), not at click-track. UNIQUE `(pb_ref, payment_id)`.
- **Q2 Support Tier**: Match against `SUPPORT_TIER_PLAN_IDS` env allowlist of PayPal Plan IDs. Plan ID is in the subscription event payload. Single source of truth, expandable.
- **Q3 30-day-use**: Status `needs_30d_use` with admin override. Don't hard-reject — partner relationships have legitimate alt-email cases.
- **Q4 retroactive recalc**: `tier_at_write` column + chunked pagination (LIMIT 200/invocation). Durable Object alarm only if >500 rows; D1 query partner-with-most-commissions BEFORE BUILD to know.
- **Q5 17-commit bundle**: Cherry-pick referral commits to `referral-v1` branch. Never push mixed-subsystem bundles for a targeted release.

---

## Constitutional Compliance Verified

- ✅ PayPal Auto-Split logic untouched (`tools/paypal_auto_split.py` not in scope)
- ✅ NOTHING in containers (all Workers + D1 + CF Pages)
- ✅ NEVER local deploy (git → CF auto-build)
- ✅ Multi-tenant (every partner row has partner_id)
- ✅ Investor codes / gift pages frozen (no overlap)
- ✅ /partners/ DO NOT TOUCH except final wiring
- ⚠️ Caught missing: `wrangler deploy` step for Workers in cutover plan (git push only redeploys Pages)
- ⚠️ Caught missing: D1 forward-only schema rollback scripts must be prepared

---

## Verdict Process

GO-WITH-EDITS, not pure GO, because 10 small changes prevent real bugs:
- 1 wrong file path (would break BUILD)
- 3 race conditions (would silently lose commissions)
- 2 missing constraints (idempotency, UNIQUE)
- 1 cross-Worker auth fix (kills hardcoded token problem permanently)
- 1 sequencing fix (schema before Worker)
- 1 missing route (/reject companion)
- 1 v1 scope reduction (PayPal-only, drop bank for now)
- 1 cutover gap (wrangler deploy + D1 rollback scripts)

**None require architectural restart.** All can be amended in the SPEC and BUILD dispatched same day.

---

## Reusable for Future Pre-Builds

When reviewing any Worker/D1/auth SPEC:
1. Verify file references against source (line counts, function names)
2. Hunt race conditions in any async event-handler→DB pipeline
3. Check cross-Worker calls — Service Binding or HTTP+token?
4. Schema migrations as discrete gates, never bundled
5. Idempotency on every public POST endpoint
6. Rollback scripts for forward-only changes (D1 schema)
7. Constitutional check: PayPal split untouched, containers empty, no local deploy
