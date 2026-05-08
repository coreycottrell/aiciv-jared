# cto: Pre-Build Architectural Review — Referral System v1 Sprint

**Agent**: cto
**Domain**: Technology Strategy & Vision
**Date**: 2026-05-07
**Input SPEC**: `/home/jared/projects/AI-CIV/aether/exports/portal-files/REFERRAL-SYSTEM-V1-SPEC-2026-05-07.md`
**Verdict**: **GO-WITH-EDITS** (10 required changes, none architectural; mostly correctness + sequencing)

---

## Memory Search Results

- Searched `.claude/memory/agent-learnings/cto/` for "referral|payout|commission|webhook" — 8 prior memories.
- Most relevant: `2026-03-12--portal-voice-hmi-referral-sqlite-architecture.md` (proxy→D1 transition), `2026-03-06--referral-payout-phase3a-implementation.md` ($25 min + 30d cooldown, JSONL legacy), `2026-03-05--referral-system-phase2-architecture.md` (tier engine intent).
- Reused: parameterized SQL discipline, "if it ain't broke" principle for `paypal_auto_split.py`, separation of webhook (event) vs split (payout) concerns.
- Verified file claims by Read on `workers/paypal-webhook/src/worker.js` and Grep on `workers/`.

---

## 1. Architecture Soundness (data flow §4.1)

The flow is correct in shape. **Three race/ordering issues need handling:**

1. **Webhook fires before pending row exists.** If PayPal `onApprove` JS fires the `/referrals/complete` POST and the webhook arrives at paypal-webhook **before** the proxy POST lands in D1, the webhook's `complete-by-email` lookup returns `no_referral` and commission is silently lost. This is non-theoretical: PayPal webhook latency is typically 1-30s, but `onApprove` POSTs have been known to drop on slow connections. **Fix**: webhook handler must implement deferred lookup — on `no_referral`, queue a retry (Durable Object alarm or `paypal_webhook_log.pending_referral_lookup` flag) and re-check 60s later before declaring `no_referral` final.
2. **Plan-upgrade ordering.** `BILLING.SUBSCRIPTION.UPDATED` can arrive before the `PAYMENT.SALE.COMPLETED` for the new amount (or vice versa). Spec promise of "recalc at new rate" requires reading `clients.previous_monthly_amount` AND the timestamp of the upgrade vs the sale. **Fix**: commission writer must read the subscription's amount-at-event-time, not `clients.monthly_amount` (which may have been updated by a separate event in flight).
3. **Milestone recalc collision with concurrent commission writes.** If partner hits 100 refs and recalc-tier starts iterating `commission_payments` while a webhook is mid-INSERT, you get a row at the old rate that escapes recalc. **Fix**: recalc must either (a) `BEGIN IMMEDIATE` transaction, or (b) record `tier_at_write` on each commission row and use that as the source of truth, recalculating only rows where `tier_at_write != current_tier`. Recommend (b) — non-blocking, idempotent, audit-friendly.

---

## 2. D1 Schema Review (§4.2)

Sufficient in shape. **Required additions:**

- **Indexes**: `CREATE INDEX idx_partner_apps_status ON partner_applications(status)`, `idx_payout_requests_partner_status ON payout_requests(partner_id, status)`, `idx_rate_adj_partner ON rate_adjustments(partner_id)`. Without these, admin queue queries scan-table at scale.
- **Foreign keys**: D1/SQLite supports them with `PRAGMA foreign_keys=ON`. Add `partner_id REFERENCES partners(id)` on `rate_adjustments`, `payout_requests`. Worth the safety; D1 doesn't enforce FK by default but declaration makes intent explicit and migration safer.
- **`commission_source` granularity**: `'standard' | 'support_tier'` is fine for v1. Add `'plan_upgrade_recalc'` and `'milestone_recalc'` so audit trail distinguishes why a row exists. Single ENUM-as-TEXT is fine; use a CHECK constraint.
- **`tier_at_write` column on commission_payments** (per §1.3 above): `ALTER TABLE commission_payments ADD COLUMN tier_at_write TEXT;`. Critical for safe milestone recalc.
- **Migration sequencing**: ALTER TABLE on D1 is non-locking for ADD COLUMN with default — safe. Run migrations in order: new tables first (no dependents), then ALTERs, then indexes. Include a `schema_migrations` log table with applied timestamp to prevent re-runs.
- **`payout_requests.bank_details_encrypted`**: spec says encrypted but doesn't say with what key. **Fix**: define KMS source — `BANK_ENCRYPTION_KEY` Worker secret, AES-GCM via Web Crypto. v1 can defer bank by enforcing `payout_method='paypal'` only and dropping the bank column for now. Recommend the latter — ship narrower.

---

## 3. Worker Route Changes (§4.3)

Routes are right. **Issues:**

- **Cross-Worker call auth (paypal-webhook → referrals-api)**: confirmed at `paypal-webhook/worker.js:264-286`. Currently uses `X-Admin-Token` over public HTTPS with hardcoded fallback (A1). After A1 rotation, replace with **CF Service Binding** (`env.REFERRALS_API.fetch(...)`) — internal, no token needed, no public exposure. This is the constitutionally correct fix; HTTP+token is a v0 hack.
- **Retry policy**: webhook → referrals-api currently throws away the call on non-2xx. Add: 3 retries with exponential backoff (200ms / 1s / 5s), and on final failure write a `failed_commission_writes` row for manual replay. Without this, transient referrals-api errors = lost commissions.
- **Idempotency for `/referrals/complete`**: spec doesn't mandate it. **Fix**: `(pb_ref, payment_id)` should be UNIQUE on `referrals` table; INSERT becomes `INSERT OR IGNORE`. Without this, B3's payment-page POST can double-fire (page reload, network retry) and create duplicate pending rows.
- **`/admin/applications/:id/approve` missing companion**: need `/reject` route too (with `rejection_reason`). Spec implies but doesn't list.

---

## 4. Engineering Flow Per Item (§6)

Two corrections:

- **D1 schema migrations** (currently implicit under B-items / C2 / E1) should be a **separate work item with its own gate**. They run ONCE, before any Worker that depends on the new columns deploys. Otherwise you ship a Worker that queries `is_support_tier` against a table that doesn't have it yet → CF 500 → outage.
- **D1 (host-gate)** marked "frontend-only, no SEC gate". **Wrong**: removing a host-gate is a security-relevant change (who can see the admin UI?). It needs SEC review even though no Worker code changes. Cheap review (5 min), but required.

---

## 5. Dispatch Plan (§7) — Inter-dependencies

Three serialization constraints the plan misses:

1. **Schema migrations MUST land before Worker BUILD finishes.** Make migrations a Phase 2a, before parallel Worker/Frontend work. (Or land migrations on day 1 of Phase 2 as a blocking sub-task.)
2. **B2 (pending row creation) blocks B3 (payment page POST) blocks E2E test.** Plan implies parallel; this is correct only if specialists agree on the contract first. **Fix**: write the `/referrals/complete` request/response contract as a sub-section of this SPEC (or a contract.json) and freeze it before BUILD starts. Then B2 and B3 can build in parallel against the contract; E2E waits for both.
3. **A1 (token rotation) blocks the cross-worker integration test.** When `REFERRALS_ADMIN_TOKEN` is rotated, both Workers must redeploy in lockstep. Service-binding fix (§3 above) eliminates this dependency entirely — recommend doing service binding migration as part of A1, not deferring.

Otherwise the 3-specialist split (Worker / Frontend / Schema) is sound.

---

## 6. Open Questions — Answers

- **Q1 (pending row location)**: At `/referrals/complete` POST time (payment-page onApprove). Aether's recommendation is correct. Click-track creates `referral_clicks` only — no pending `referrals` row. Pending row is created only when payment intent is real (PayPal approved). UNIQUE on `(pb_ref, payment_id)` prevents duplicates. Webhook joins on `customer_email` OR `payment_id` (use payment_id when available — more reliable than email).
- **Q2 (Support Tier indication)**: Use **PayPal Plan ID** matched against an env-configured allowlist (`SUPPORT_TIER_PLAN_IDS` secret, comma-separated). Plan ID is in the subscription event payload. Custom field is unreliable; metadata API requires extra call. Plan ID = one source of truth, easy to expand.
- **Q3 (30-day-use enforcement)**: Status = `needs_30d_use` with admin override. Auto-reject is too brittle for partner relationships (someone may have paid via different email). Admin queue with reason + override is correct. Add a `reviewer_override_reason` text field on `partner_applications`.
- **Q4 (retroactive recalc transactional safety)**: Use the `tier_at_write` approach (§1.3, §2) — recalc becomes idempotent and chunkable. For partners with >500 commission rows, paginate the recalc (LIMIT 200 per Worker invocation, queue continuation via Durable Object alarm). CF Worker free tier 30s CPU is plenty for ≤500 rows; chunk above that. Don't introduce queues for v1 unless real partner has >500 commissions today (D1 query will tell us — current top partner row count must be checked before BUILD).
- **Q5 (17-commit bundle)**: Cherry-pick referral-related commits onto a new `referral-v1` branch, push that. Defer non-referral commits to their own SHIP gates. Do NOT push the bundle as-is — mixing CE SME, social-api, blog-publisher into a referral-cutover deploy is a release-engineering anti-pattern (one rollback hits unrelated systems). Get a `git log --oneline -20` from G1 specialist with each commit tagged by subsystem before Jared auths the push path.

---

## 7. Risks Not Called Out

- **The SPEC contains a wrong file reference (A3)**. SPEC says line 546 of `paypal-webhook/worker.js` has the `(payment_amount - 35) * split.percentage` formula. That file is 513 lines. The actual conflicting formula is in **`workers/referrals-api/src/worker.js:546`**, while line 210 of the same file has `paymentAmount * rate`. A3's edit target is the wrong worker. **Fix in SPEC before BUILD**: A3 must say `referrals-api/src/worker.js` lines 210 vs 546.
- **Verification gap on hardcoded token**: confirmed at `paypal-webhook/worker.js:266`. SPEC is correct that A1 is real.
- **`verifyWebhook` is a no-op**: confirmed (lines 164-183 always return true). SPEC is correct.
- **Cutover constitutional risk**: SPEC §8 step 4 says "git push triggers CF auto-build". This is correct for Pages, but Workers require `wrangler deploy` per the wrangler-pages-vs-workers rule. Add explicit step: "deploy each Worker via `wrangler deploy` in `workers/{name}/`" — git push alone won't redeploy Workers.
- **PayPal Auto-Split untouched** (§11) — verified intact. Constitutional preserved.
- **`/partners/` page DO NOT TOUCH** — final wiring is the only contact, last step. Honored.
- **Investor codes / gift pages frozen** — no scope overlap. Honored.
- **Rollback gap**: §9 says "Git revert tag for each Worker prepared before cutover". Fine, but D1 schema is forward-only — schema rollback requires manual ALTER TABLE DROP COLUMN scripts prepared in advance. Spec must include those.

---

## 8. Verdict

**GO-WITH-EDITS.**

Required SPEC edits (all small, none change shape):

1. Fix A3 file reference: target is `workers/referrals-api/src/worker.js`, not paypal-webhook.
2. Add `tier_at_write TEXT` column to `commission_payments` and use it in the recalc strategy.
3. Add indexes on partner_applications, payout_requests, rate_adjustments.
4. Add `INSERT OR IGNORE` + UNIQUE `(pb_ref, payment_id)` on referrals table.
5. Replace cross-Worker HTTP+token with CF Service Binding for paypal-webhook → referrals-api as part of A1.
6. Add deferred-lookup retry (60s) for webhook `no_referral` case.
7. Make D1 schema migrations a discrete work item with its own gate, run before Worker BUILD finishes.
8. Add `/admin/applications/:id/reject` companion route.
9. Drop `payout_method='bank'` for v1 (PayPal only) OR define BANK_ENCRYPTION_KEY mechanism.
10. Add explicit `wrangler deploy` step per Worker in §8 cutover plan; D1 rollback scripts prepared in §9.

Once Aether amends the SPEC with these 10 edits, **dispatch BUILD specialists per §7 with corrected sequencing (schema migrations first, contract frozen before B2/B3 parallel)**.

The architecture is sound. The decisions (Service Binding, tier_at_write, plan ID for Support Tier, $50 min via UNIQUE constraint, payment-time pending row, cherry-pick over bundle push) compound into a system that's honest about race conditions and observable when things go wrong. That's the bar.

---

## Memory Written
Path: `.claude/memory/agent-learnings/cto/2026-05-07--referral-v1-prebuild-review.md`
Type: teaching
Topic: Pre-build review pattern — race conditions + cross-worker auth + schema-first migrations for payment systems
