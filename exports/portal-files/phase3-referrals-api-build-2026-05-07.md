# Phase 3 BUILD — referrals-api Worker — Deliverable Summary

**Date**: 2026-05-07
**Branch**: `referral-v1` (NOT deployed; staged for cutover)
**Builder**: wtt-fullstack
**Spec**: `exports/portal-files/REFERRAL-SYSTEM-V1-SPEC-2026-05-07.md`
**CTO Review**: `exports/portal-files/cto-prebuild-review-referral-v1-2026-05-07.md`
**Schema migration**: `workers/referrals-api/migrations/0002a-referrals-only-schema.sql` (already applied)

---

## Constraint compliance

- [x] **Code on `referral-v1` branch only** — verified `git branch --show-current = referral-v1`
- [x] **NO `wrangler deploy`** — zero deploy commands run
- [x] **NO touching of live referrals-api** — Worker not modified in production
- [x] **Pre-existing code reviewed** — clean 590-line baseline (no +1382 LOC delta present in HEAD; the historical delta was already absorbed by commits b1c10a3 / d8a0306 / parallel agent's 0e417f2)
- [x] **`node --check` passes after every commit**
- [x] **Each commit = one work item** with clear message citing the relevant SPEC item + CTO amendment

Final worker: 1255 lines, 23 routes, all 8 work items applied.

---

## Commits (ordered)

| # | Hash | Item | Subject |
|---|------|------|---------|
| 1 | `0021852` | A3 | feat(referrals-api): A3 — canonical commission formula + tier_at_write |
| 2 | `0873137` | B2 | feat(referrals-api): B2 — pending row on /referrals/complete (idempotent) |
| 3 | `3e97285` | C1 | feat(referrals-api): C1 — default partner_tier='silver' (15%) for new signups |
| 4 | `5d0df5e` | C2 | feat(referrals-api): C2 — partner application + approval flow |
| 5 | `8a61bfc` | C3 | feat(referrals-api): C3 — retroactive rate recalc with tier_at_write |
| 6 | `0f32a25` | C4 | feat(referrals-api): C4 — partner-facing payout request endpoint |
| 7 | `803e091` | D2 | feat(referrals-api): D2 — split_config + tier exposed in API responses |
| 8 | `04f519a` | E1 | feat(referrals-api): E1 — Support Tier 25% via SUPPORT_TIER_PLAN_IDS |

(A parallel-agent commit `e2be7e0` for frontend/portal-proxy build summary appears
between hashes 0873137 and 3e97285 — separate work stream, not part of this delivery.)

---

## Acceptance summary by work item

### Item 1 — A3: Reconcile commission formula  ✅
**Commit**: `0021852`
**SPEC**: §5 Tier A; CTO Edit #1
**What changed**:
- Added `TIER_RATES` const (silver=15%, gold=17%, platinum=20%; standard=5% legacy; elite=25% legacy)
- Added `computeCommission()` helper enforcing `paymentAmount * rate` formula
- `POST /commission_payments` now writes `tier_at_write` + `commission_source` on every INSERT
- Backwards-compat preserved: caller can still pass pre-computed `commission_value` (paypal-webhook unchanged) — Worker writes `tier_at_write` regardless
- `GET /commission_payments` exposes `tier_at_write` + `commission_source`

**Note on stale line numbers**: SPEC referenced "duplicate `(payment_amount - 35) * split.percentage` at line 546" but that formula does not exist in the current 590-line baseline. The line was from the historical +1382 LOC delta already absorbed into the codebase before Phase 3 started. Forward fix: enforce single-formula contract in code with a clear comment that the $35 ops fee is taken in `tools/paypal_auto_split.py` only.

**Acceptance criteria**:
- [x] Commission = paymentAmount × rate (no $35 deduction in Worker)
- [x] `tier_at_write` set on every commission_payments INSERT
- [x] CTO Edit #2 satisfied (audit trail preserved for safe recalc)

---

### Item 2 — B2: Pending row on /referrals/complete  ✅
**Commit**: `0873137`
**SPEC**: §5 Tier B / CTO Q1 / CTO Edit #4
**What changed**:
- `POST /referrals/complete` is now dual-mode:
  - **Admin mode** (legacy): `{ referral_id }` → mark existing row completed
  - **Public mode** (new): `{ pb_ref, payment_id, customer_email, ... }` → `INSERT OR IGNORE` pending row
- Public mode requires no admin token; idempotency comes from UNIQUE INDEX `uniq_referrals_pbref_payment` on `(pb_ref, payment_id)` (applied in migration 0002a)
- Returns `idempotent: true` when INSERT OR IGNORE collapses a duplicate (page reload, network retry, double-click)
- Unknown referral codes return 404 with structured error so paypal-webhook can fall back to customer_email lookup

**Acceptance criteria**:
- [x] Pending row created with `pb_ref` + `payment_id` + `customer_email`
- [x] `INSERT OR IGNORE` leverages UNIQUE constraint
- [x] Error handling for missing fields (400) + unknown ref code (404)
- [x] CTO Q1 answered: pending row at `/referrals/complete` POST time

---

### Item 3 — C1: Default partner_tier='silver' (15%)  ✅
**Commit**: `3e97285`
**SPEC**: §5 Tier C / CTO Edit #2
**What changed**:
- `POST /referrers/upsert` now defaults `partner_tier='silver'` on new rows (was implicitly 'standard' 5% via DB column default)
- Added `POST /partners/signup` for direct admin-provisioning at chosen tier (default 'silver'), validates against `TIER_RATES` allowlist
- `PUT /admin/affiliate/update` now accepts `partner_tier` (validated) and `split_config` (array or pre-stringified JSON)
- All inserts/updates expose `partner_tier` + `total_sales` in response
- `tier_at_write` snapshot enforced via Item 1 logic — admin can change tier and existing rows retain their original tier_at_write for safe recalc

**Acceptance criteria**:
- [x] New signups default to 'silver' (15%)
- [x] Tier-rate lookup table: silver=15%, gold=17%, platinum=20% (matches SPEC)
- [x] Audit log: every commission_payments INSERT records `tier_at_write` (Item 1)
- [x] Admin can override tier with validation

**Existing partners untouched**: legacy `'standard'` (5%) partners are NOT auto-migrated. Admin must explicitly migrate them via `PUT /admin/affiliate/update` followed by `POST /admin/recalc-tier` (Item 5) for retroactive recalc with audit trail.

---

### Item 4 — C2: Approval flow  ✅
**Commit**: `5d0df5e`
**SPEC**: §5 Tier C / CTO Edit #8
**What changed**:
- `POST /partners/apply` (PUBLIC): creates `partner_applications` row, captures application_data JSON (source, referral_url, notes, user_agent), default status='pending'. UNIQUE on email returns 409 on duplicate.
- `POST /admin/applications/:id/approve` (ADMIN): creates active referrer row at chosen tier (default 'silver'), stamps application approved with reviewed_at/by + reviewer_override_reason
- `POST /admin/applications/:id/reject` (ADMIN, CTO Edit #8 companion): stamps rejection_reason (500 char max)
- `GET /admin/applications` (ADMIN): list applications, optional `?status=` filter

**30-day-use enforcement** (CTO Q3): clients table currently lives in `purebrain-social` D1 under domain-isolation rule (May 7 constitutional). For v1, applications default to 'pending' and admin verifies 30d-use manually during review. `reviewer_override_reason` field allows admin override for partners who paid via different email (per CTO recommendation). Future: extract clients to purebrain-clients D1 + add real lookup that auto-stamps `'needs_30d_use'`.

**Acceptance criteria**:
- [x] `/partners/apply` creates `partner_applications` row
- [x] `/admin/applications/:id/approve` activates partner + creates referrer
- [x] `/admin/applications/:id/reject` companion route present (CTO Edit #8)
- [x] Existing X-Admin-Token auth pattern reused for admin routes

---

### Item 5 — C3: Retroactive rate recalc  ✅
**Commit**: `8a61bfc`
**SPEC**: §5 Tier C / CTO §1.3 / CTO Q4
**What changed**:
- `POST /admin/recalc-tier` (ADMIN): trigger retroactive rate recalc for a partner
  - Computes target tier (force_tier > milestoneTier(total_sales) > current)
  - Updates `referrers.partner_tier`
  - Recalculates `commission_payments` rows where `tier_at_write != target` AND `commission_source != 'support_tier'` (Support Tier locked at 25%)
  - Chunked at LIMIT 200 per call (CF Worker 30s CPU limit)
  - Returns `more=true` if rows still need recalc → caller re-invokes
- Audit log: every chunk that recalculated rows writes one `rate_adjustments` row (partner_id, old_rate, new_rate, trigger_event, affected_commission_count, total_dollars_recalculated, created_at)
- `trigger_event` allowlist: `'100_referrals' | '1000_referrals' | 'manual'`

**Per CTO Q4**: chunked sync recalc for v1 (no Durable Object queue). Top current partner has <500 commission rows so single-call usually suffices; chunking preserves safety at scale.

**Per CTO §1.3**: `tier_at_write` is the source of truth — recalc only touches rows where `tier_at_write != target`, making concurrent webhook INSERTs safe (new INSERTs use current tier_at_write; old rows get caught on next invocation).

**Acceptance criteria**:
- [x] Triggered on tier change (force_tier or milestone derivation)
- [x] Updates existing commission_payments using `tier_at_write` for safe recalc
- [x] Chunked pagination (LIMIT 200)
- [x] Logs to rate_adjustments (audit trail)
- [x] Idempotent (safe to retry)

---

### Item 6 — C4: Partner-facing payout request  ✅
**Commit**: `0f32a25`
**SPEC**: §5 Tier C / CTO Edit #9
**What changed**:
- `POST /payouts/request` (PUBLIC): partner-self payout request
  - Identity gate: `{ partner_id (referral_code), paypal_email }` must match referrer record (no spoofing — paypal_email_mismatch returns 403)
  - $50 min enforced by DB CHECK on `payout_requests_v2.amount >= 50`
  - v1 PayPal-only (DB CHECK `payout_method = 'paypal'` per CTO Edit #9)
  - Validates: partner exists, requested amount ≤ (sum commissions earned) − (sum approved/paid payouts)
- `GET /admin/payouts`: now merges legacy `payout_requests` + `payout_requests_v2` rows with `'source'` column ('legacy' | 'v2')
- `DELETE /admin/affiliate/delete`: cascade now cleans `payout_requests_v2`

**Admin approval flow**: admin reviews via `GET /admin/payouts`, then runs `tools/paypal_auto_split.py` manually for approved requests (per current architecture; auto-trigger held for v1.1).

**Per CTO Edit #9**: `bank_details` encryption deferred — v1 is PayPal-only.

**Acceptance criteria**:
- [x] `/payouts/request` accepts partner-self payout
- [x] $50 min enforced (DB CHECK + Worker validation)
- [x] Inserts into `payout_requests_v2` with status='requested'
- [x] Identity gate prevents spoofing
- [x] Available-balance check prevents over-request

---

### Item 7 — D2: split_config in /admin/affiliates  ✅
**Commit**: `803e091`
**SPEC**: §5 Tier D
**What changed**:
- `GET /admin/affiliates` response now includes per-affiliate `partner_tier`, `tier_rate`, `total_sales`, and `split_config` (parsed JSON array)
- `GET /dashboard` response now includes `partner_tier`, `tier_rate`, `total_sales` for partner-facing UI
- `parseSplit()` helper handles array, pre-stringified JSON, or null/empty → always returns array

Frontend `renderSplitRows()` in `admin/referrals/index.html` can now populate split rows directly from API response without separate fetch.

**Acceptance criteria**:
- [x] `/admin/affiliates` includes `split_config` per affiliate
- [x] Parsed to array (never string) for frontend
- [x] Tier info included for admin UI display

---

### Item 8 — E1: Support Tier 25%  ✅
**Commit**: `04f519a` (worker hookup was in commit `0021852`)
**SPEC**: §5 Tier E / CTO Q2
**What changed**:
- `wrangler.toml`: declares `SUPPORT_TIER_PLAN_IDS` env var (empty default; override via `wrangler secret put SUPPORT_TIER_PLAN_IDS` in prod)
- Worker docblock: full endpoint inventory + env var documentation + constitutional notes (formula, tier_at_write, $50 min, idempotency)
- Support Tier logic was wired in commit `0021852`:
  - `SUPPORT_TIER_RATE = 0.25`
  - `isSupportTierPlan(planId, env)`: allowlist match against `SUPPORT_TIER_PLAN_IDS`
  - `computeCommission()`: if planId matches, override rate to 0.25 and set `commission_source='support_tier'`
  - `POST /commission_payments`: writes `commission_source` on every INSERT; Support Tier rows skipped during `/admin/recalc-tier` (locked at 25% regardless of partner_tier change)

**Per CTO Q2**: PayPal Plan ID is the source of truth for Support Tier detection (plan_id is in subscription event payload; one source of truth, easy to expand).

**Note**: paypal-webhook is the actual writer in production. Integration point: webhook can pass `plan_id` in `/commission_payments` POST body; referrals-api detects + applies Support Tier rate. paypal-webhook update is a separate work item (out of scope for referrals-api Phase 3 BUILD).

**Acceptance criteria**:
- [x] `commission_source` detection in commission write
- [x] `SUPPORT_TIER_PLAN_IDS` env var declared in wrangler.toml
- [x] 25% rate override when plan_id matches allowlist
- [x] Support Tier rows skipped in recalc (locked at 25%)

---

## Routes inventory (final state)

23 routes (was 18 in baseline):

**Public (no auth)**:
- `GET /health`, `/referrers`, `/referrals`, `/commission_payments`, `/dashboard`, `/leaderboard`
- `POST /partners/apply`, `/referrals/complete` (public mode), `/payouts/request`

**Admin (X-Admin-Token)**:
- `GET /admin/emails`, `/admin/affiliates`, `/admin/payouts`, `/admin/applications`, `/admin/stats`
- `POST /referrers/upsert`, `/partners/signup`, `/commission_payments`, `/admin/payout/mark-paid`, `/admin/referral/assign`, `/admin/applications/:id/approve`, `/admin/applications/:id/reject`, `/admin/recalc-tier`, `/referrals/complete` (admin mode)
- `PUT /admin/affiliate/update`, `/admin/referral/update`
- `DELETE /admin/affiliate/delete`

---

## Outstanding — NOT in scope of Phase 3 BUILD (Worker only)

Per the work order, these items are explicitly out of scope and remain for other Phase 3 work streams:

- **B1** (purebrain-portal-proxy `/complete` path forwarding) — separate parallel agent (commit `e2be7e0` covers this)
- **B3** (frontend wiring for `/awakened/`, `/insiders/`, `/partnered/`, `/unified/`) — already done in commit `557f307` (parallel agent)
- **D1** (admin/referrals frontend host-gate fix) — already done in commit `0e417f2` (parallel agent)
- **A1** (rotate hardcoded `purebrain-admin-2026` token) — paypal-webhook scope, not referrals-api
- **A2** (real PayPal webhook signature verify) — paypal-webhook scope; already done in commit `fa7a4da`
- **paypal-webhook updates** for Support Tier plan_id forwarding + retry policy + Service Binding — separate work item
- **Cross-Worker Service Binding** (CTO §3) — recommended but deferred for cutover stage

---

## Cutover readiness

**This branch is ready for SEC + QA gates** (Phase 3 SEC + QA per SPEC §7).

When Jared signals "cut over", the deploy sequence is:
1. Verify schema migration `0002a-referrals-only-schema.sql` applied to prod `purebrain-referrals` D1 (already applied per migration file header)
2. `wrangler secret put ADMIN_TOKENS` (rotated value)
3. `wrangler secret put SUPPORT_TIER_PLAN_IDS` (comma-separated PayPal Plan IDs that map to 25% Support Tier)
4. `cd workers/referrals-api && wrangler deploy` (Workers do NOT auto-deploy on git push per `feedback_wrangler_workers_vs_pages_distinction.md`)
5. Smoke tests on each route (see SEC + QA gates)

---

## Memory Written

**Path**: `.claude/memory/agent-learnings/full-stack-developer/2026-05-07--phase3-referrals-api-build.md`
**Type**: operational
**Topic**: Phase 3 BUILD execution pattern — referrals-api Worker code-only on branch
