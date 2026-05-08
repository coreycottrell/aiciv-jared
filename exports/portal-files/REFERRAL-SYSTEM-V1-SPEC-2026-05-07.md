# Referral System v1 — Comprehensive Sprint SPEC
**Date**: 2026-05-07 | **Author**: Aether (Co-CEO/Conductor) | **Status**: Pre-CTO-Review
**Cutover target**: `https://portal.purebrain.ai/admin/referrals`
**Build target**: `https://purebrain-staging.pages.dev/admin/referrals/`
**Public partner page**: `https://purebrain.ai/partners/` (PurePartner2026 — DO NOT TOUCH per Jared 5/7, except final wiring at end)

---

## 1. Goals

1. **Align the referral system with the public PurePartner2026 promises** (15-20% tiered recurring commission with retroactive recalc, 90-day cookie tracking, real-time dashboard, $50 min payout, Support Tier 25%).
2. **Make automatic commission attribution actually work end-to-end** — currently never has fired automatically.
3. **Close 3 critical security holes** introduced in the +1,382 LOC uncommitted Worker delta.
4. **Wire the existing /partners/ application form** to the real referral system as the FINAL step (no other page changes).
5. **Cut over to portal.purebrain.ai** with full git hygiene — no local deploys, no container persistence, all in CF Workers + D1 + CF Pages.

## 2. Non-goals (out of scope for v1)

- **/partners/ page copy edits** — Jared directive: don't touch the page except final form wiring. Page copy stays as-is even where it contradicts system reality (e.g., "Net-30", "verified monthly against Stripe"). System must align to page where possible; remaining mismatches accepted as Jared's risk.
- **Custom partner landing pages framework** (Jared answer #3) — architectural intent for v2. v1 must leave the door open by keeping attribution payment-system-agnostic, but no v1 build of a partner-page-builder.
- **`staging.purebrain.ai` custom domain repair** — stuck on stale deploy; doesn't block since builds happen on `*.pages.dev`. ST# follow-up.
- **Future payment systems beyond PayPal** — design for extensibility; build PayPal only.
- **Monthly Partner Office Hours infrastructure** — pure marketing claim with no system component needed.

## 3. Locked scope decisions (Jared 5/7)

| # | Decision | Locked answer |
|---|---|---|
| 1 | /partners/ page during sprint | KEEP LIVE, do not touch. Final wiring at end. |
| 2 | Support Tier 25% commission | SHIP IN V1. Extensible payment-source architecture. |
| 3 | 10% referral discount | NOT system-wide. Future: partners build custom pages with their own offers; system tracks ref+payment→attribution payment-system-agnostically. |
| 4 | Existing partners | Zero payout requests pending. Active count TBD via D1 query (ST# task). |

## 4. Architecture

### 4.1 Data flow (target state)

```
Partner gets unique URL: purebrain.ai/?ref=PB-XXXX (or /partners/?ref=PB-XXXX)
   ↓
Visitor lands on any page → partners/index.html script captures pb_ref
   → 90-day cookie + localStorage + POST to /api/referral/track
   → referrals-api INSERT INTO referral_clicks
   ↓
Visitor proceeds to ANY payment page (/awakened/, /insiders/, /partnered/, /unified/, home-test variants, homepage)
   → onApprove handler reads pb_ref from URL/localStorage/cookie
   → POST to portal-proxy /complete → forwards to referrals-api /referrals/complete
   → referrals-api INSERT INTO referrals (status='pending', pb_ref, payment_id, customer_email)
   ↓
PayPal fires webhook → paypal-webhook (D1: purebrain-social)
   → Verify PayPal signature (REAL, not no-op)
   → Idempotency check via paypal_webhook_log
   → Look up referral by customer_email or payment_id (cross-Worker HTTP call to referrals-api)
   → INSERT INTO commission_payments at partner's current rate
   → Trigger milestone check: if total_sales hits 100/1000, update partner_tier + retroactive recalc on commission_payments
   ↓
Partner dashboard reads commission_payments at any time → real-time view
Partner self-service: POST /payouts/request (min $50 check) → admin approval queue
   ↓
Manual paypal_auto_split.py run for approved payouts → 60% Corey / 40% Pure Tech / partner commission
```

### 4.2 D1 schema additions (`purebrain-referrals` DB)

```sql
-- Application + approval flow
CREATE TABLE partner_applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  audience_size INTEGER,
  application_data JSON,
  status TEXT NOT NULL DEFAULT 'pending', -- pending | approved | rejected | needs_30d_use
  applied_at INTEGER NOT NULL,
  reviewed_at INTEGER,
  reviewed_by TEXT,
  rejection_reason TEXT
);

-- Audit trail for retroactive rate changes (legal record)
CREATE TABLE rate_adjustments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  partner_id TEXT NOT NULL,
  old_rate REAL NOT NULL,
  new_rate REAL NOT NULL,
  trigger_event TEXT NOT NULL, -- '100_referrals' | '1000_referrals' | 'manual'
  affected_commission_count INTEGER NOT NULL,
  total_dollars_recalculated REAL NOT NULL,
  created_at INTEGER NOT NULL
);

-- Partner-self payout requests
CREATE TABLE payout_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  partner_id TEXT NOT NULL,
  amount REAL NOT NULL CHECK(amount >= 50),  -- $50 min
  payout_method TEXT NOT NULL, -- 'paypal' | 'bank'
  paypal_email TEXT,
  bank_details_encrypted TEXT,
  status TEXT NOT NULL DEFAULT 'requested', -- requested | approved | paid | rejected
  requested_at INTEGER NOT NULL,
  paid_at INTEGER,
  paid_via_split_id TEXT  -- references paypal_auto_split.py run
);

-- Plan-upgrade auto-recalc
ALTER TABLE clients ADD COLUMN previous_monthly_amount REAL;
ALTER TABLE clients ADD COLUMN plan_changed_at INTEGER;

-- Support Tier flag (Jared 5/7 #2)
ALTER TABLE clients ADD COLUMN is_support_tier INTEGER DEFAULT 0;
ALTER TABLE commission_payments ADD COLUMN commission_source TEXT DEFAULT 'standard';
  -- 'standard' (15-20% by partner_tier) | 'support_tier' (25%) | future expansion
```

### 4.3 Worker route changes

| Worker | Route | Change |
|---|---|---|
| `purebrain-portal-proxy` | `/complete` | Fix path forwarding to `/referrals/complete` (B1) |
| `referrals-api` | `POST /referrals/complete` | Accept `pb_ref` from any payment page, INSERT pending row (B2) |
| `referrals-api` | `GET /admin/affiliates` | Add `split_config` to response shape (D2 — fixes Save Splits) |
| `referrals-api` | `POST /partners/signup` | Default `partner_tier='silver'` (15%), not 'standard' (5%) (C1) |
| `referrals-api` | `POST /partners/apply` | NEW: replaces Brevo-only flow; creates partner_applications row (C2) |
| `referrals-api` | `POST /admin/applications/:id/approve` | NEW: admin approves, creates active partner row (C2) |
| `referrals-api` | `POST /payouts/request` | NEW: partner-self payout request, $50 min (C4) |
| `referrals-api` | `internal/recalc-tier` | NEW: triggered on milestone hit, recalculates commission_payments retroactively (C3) |
| `paypal-webhook` | `verifyWebhook()` | Replace no-op with real PayPal verify-webhook-signature API (A2) |
| `paypal-webhook` | `BILLING.SUBSCRIPTION.UPDATED` | NEW: handler for plan upgrades; recalculates commission at new rate (spec promise) |
| `paypal-webhook` | Commission write logic | Use single formula `paymentAmount * rate`; remove duplicate `(payment_amount - 35) * split.percentage` (A3) |

### 4.4 Frontend changes

| File | Change |
|---|---|
| `exports/cf-pages-deploy/admin/referrals/index.html:1336` | Remove host-gate on fallback; merge affiliates+clients on fallback (D1) |
| `exports/cf-pages-deploy/admin/referrals/index.html:1006` | Render splits from `split_config` once Worker returns it (D2) |
| `exports/cf-pages-deploy/awakened/index.html` | Add pb_ref POST in PayPal onApprove (B3) |
| `exports/cf-pages-deploy/insiders/index.html` | Add pb_ref POST in PayPal onApprove (B3) |
| `exports/cf-pages-deploy/partnered/index.html` | Add pb_ref POST in PayPal onApprove (B3) |
| `exports/cf-pages-deploy/unified/index.html` | Add pb_ref POST in PayPal onApprove (B3) |
| `exports/cf-pages-deploy/refer/index.html` (or partner dashboard) | Add payout-request UI ($50 min) (C4) |
| `exports/cf-pages-deploy/partners/index.html` (LAST step only) | Wire application form from Brevo to `/partners/apply` endpoint (C2 wiring) |

## 5. Work items (locked scope, sequenced)

### Tier A — Security blockers (3) — REQUIRED BEFORE ANY DEPLOY

- **A1**: Remove hardcoded `purebrain-admin-2026` token fallback at `paypal-webhook/worker.js:266`. Rotate `ADMIN_TOKENS` production secret. Constitutional credential-leak bug.
- **A2**: Implement real PayPal webhook signature verification at `paypal-webhook/worker.js:164-183`. Currently `verifyWebhook()` always returns `true` — anyone can fake a PayPal payment.
- **A3**: Reconcile two conflicting commission formulas. Pick `paymentAmount * rate` (line 210). Remove `(payment_amount - 35) * split.percentage` (line 546). $35 ops fee comes off in `tools/paypal_auto_split.py`, NOT in Worker.

### Tier B — Attribution pipeline blockers (3) — MAKES THE SYSTEM ACTUALLY WORK

- **B1**: Fix path mismatch — purebrain-portal-proxy forwards `/complete` but referrals-api only has `/referrals/complete`.
- **B2**: Create `pending` referral row at payment-page-load OR onApprove time, so webhook can find it to upgrade to `paid`.
- **B3**: Wire `/awakened/`, `/insiders/`, `/partnered/`, `/unified/` payment pages to POST `pb_ref` at PayPal `onApprove` (homepage and home-test variants already do this).

### Tier C — Spec match blockers (4 items, was 5)

- **C1**: Default `partner_tier` for new signups: change from `'standard'` (5%) to `'silver'` (15%). Audit existing partners via D1 query — any on `'standard'`? If yes, propose corrective tier update + audit trail in `rate_adjustments`.
- **C2**: Build approval flow. Replace Brevo-only application path with `/partners/apply` → `partner_applications` table → admin review queue → `/admin/applications/:id/approve` → activate partner. Enforce 30-day-use check (look up applicant email in clients table; if no client record OR < 30 days, reject with reason `needs_30d_use`).
- **C3**: Build retroactive rate recalc. On milestone hit (100 refs → 17%, 1000 refs → 20%), update `partner_tier` AND iterate `commission_payments` for that partner, multiplying by new_rate/old_rate, log to `rate_adjustments`.
- **C4**: Build partner-facing payout request endpoint. `POST /payouts/request` with $50 min check. Insert into `payout_requests`. Admin approval triggers `paypal_auto_split.py` run.
- **C5 (was page copy fixes)**: OUT OF SCOPE per Jared #1.

### Tier D — Admin UI fixes (2)

- **D1**: Frontend host-gate fix at `admin/referrals/index.html:1336`. No SEC/QA gate (frontend-only).
- **D2**: Worker `/admin/affiliates` API contract change — include `split_config` in response. CTO pre-build → BUILD → SEC → QA → SHIP.

### Tier E — Spec gaps from Jared answers (1)

- **E1**: Support Tier 25% commission. Add `is_support_tier` to clients table. Add `commission_source` to commission_payments. Webhook detects support-tier subscriptions (TBD: how does PayPal indicate this? Plan ID? Subscription metadata?). Apply 25% rate when `commission_source='support_tier'` overriding partner_tier.

### Tier G — Git hygiene (1) — PRE-CONDITION

- **G1**: Triage 17 unpushed commits + 49k LOC uncommitted Worker delta. CTO review of bundle. **REQUIRES JARED EXPLICIT AUTH FOR PUSH.** Then push, or revert+redeploy from git.

## 6. Engineering flow per item

| Item | SPEC | CTO Review | BUILD | SECURITY | QA | SHIP |
|---|---|---|---|---|---|---|
| A1 (rotate token) | ✓ this doc | Required | Required | Required | Required | Required |
| A2 (real webhook verify) | ✓ this doc | Required | Required | Required | Required | Required |
| A3 (commission formula) | ✓ this doc | Required | Required | Required | Required | Required |
| B1 (proxy path fix) | ✓ this doc | Required | Required | Required | Required | Required |
| B2 (pending row) | ✓ this doc | Required | Required | Required | Required | Required |
| B3 (payment page wiring) | ✓ this doc | Required | Required | Required | Required | Required |
| C1 (15% default + audit) | ✓ this doc | Required | Required | Required | Required | Required |
| C2 (approval flow) | ✓ this doc | Required | Required | Required | Required | Required |
| C3 (retroactive recalc) | ✓ this doc | Required | Required | Required | Required | Required |
| C4 (payout request) | ✓ this doc | Required | Required | Required | Required | Required |
| D1 (host-gate) | ✓ this doc | N/A (frontend-only) | Required | N/A | Required | Required |
| D2 (admin/affiliates shape) | ✓ this doc | Required | Required | Required | Required | Required |
| E1 (Support Tier 25%) | ✓ this doc | Required | Required | Required | Required | Required |
| G1 (git triage) | ✓ this doc | Required | N/A | Required (audit bundle) | N/A | Required (push) |

## 7. Dispatch plan (parallel where possible)

After CTO pre-build review approval:

**Phase 1 — Git triage (G1) — solo, blocking**
- ST# coder reviews each of 17 unpushed commits
- Identifies which are b98235f referral-related vs unrelated
- Recommends: clean-bundle push OR cherry-pick OR partial revert
- Jared explicit auth on path

**Phase 2 — BUILD parallel (after G1 cleared)**
- ST#/wtt-fullstack: Worker fixes (A1, A2, A3, B1, B2, D2, plus paypal-webhook BILLING.SUBSCRIPTION.UPDATED handler, C2 routes, C3 routes, C4 routes, E1)
- ST#/ptt-fullstack: Frontend fixes (D1, B3 across 4 pages, partner dashboard payout-request UI, partners/ form wiring at end)
- ST#/coder or wtt-fullstack: D1 schema migrations (partner_applications, rate_adjustments, payout_requests, ALTER TABLE clients/commission_payments)

**Phase 3 — SEC + QA parallel**
- security-auditor: re-audit Workers post-fix, verify A1/A2/A3 closed, no new findings
- qa-engineer or browser-vision-tester: end-to-end test on purebrain-staging.pages.dev
- payment-flow-qa: re-run E2E attribution flow audit; verify commissions actually fire

**Phase 4 — Cutover (after all gates pass)**
- Deploy to `purebrain-staging.pages.dev` from git (CF Pages auto-deploys on push)
- Final smoke test on staging
- Cutover to `portal.purebrain.ai/admin/referrals` (production target)
- Wire `/partners/` form last (C2 wiring)
- Monitor PayPal webhook + commission writes for 24h post-cutover

## 8. Cutover plan

1. All 14 work items pass SECURITY + QA gates on `purebrain-staging.pages.dev`
2. D1 backup snapshot taken
3. Worker secrets rotated (ADMIN_TOKENS) on production
4. Production deploy via git push (CF Pages auto-build)
5. DNS check on portal.purebrain.ai/admin/referrals
6. Smoke test: admin login, partner list loads, autocomplete works, save splits works, commission row writes
7. Wire `/partners/` form to `/partners/apply` endpoint as final step
8. 24h monitoring window before declaring SHIP complete

## 9. Rollback plan

- Git revert tag for each Worker prepared before cutover
- D1 backup pre-cutover; backup_id documented in this SPEC at deploy time
- DNS swap is last step — easily reversible
- If cutover fails: `wrangler deploy` to roll Worker to last-known-good version + restore D1 from backup
- `paypal_auto_split.py` continues working independently (manual payout fallback always available)

## 10. Realistic timeline

- **CTO pre-build review**: 1-2 hours (this doc → cto agent)
- **Phase 1 (G1 git triage)**: 4-8 hours (ST# specialist + Jared auth round-trip)
- **Phase 2 (BUILD parallel)**: 3-5 days (largest work block; 14 items across 3 specialists)
- **Phase 3 (SEC + QA)**: 1-2 days
- **Phase 4 (Cutover + monitoring)**: 1 day + 24h watch
- **Total**: ~7-10 working days realistic, ~14 days with buffer

## 11. Constitutional compliance

- ✅ Multi-tenant always (every partner row includes partner_id; no shared scope)
- ✅ NOTHING in containers (all Workers + D1 + CF Pages)
- ✅ NEVER local deploy (all via git push → CF auto-build)
- ✅ PayPal Auto-Split logic preserved ($35 ops → 5% referral → 60% Corey / 40% PT, in `tools/paypal_auto_split.py`)
- ✅ Investor codes / gift pages frozen (no modifications)
- ✅ Payment guard preserved on all 10 payment pages
- ✅ Pre-deploy credential scan run before each deploy
- ✅ CF Pages health checks use GET not HEAD

## 12. Open questions for CTO review

1. **B2 — Where to create the `pending` referral row?** At click-track time (every page view with ref code creates a pending row — risk of pending-row bloat) OR at payment-page-load time (closer to conversion, fewer rows but harder to attribute if user leaves and comes back). Recommend: at `/referrals/complete` POST time, with `customer_email` joined retroactively when webhook fires.

2. **E1 — How does PayPal indicate Support Tier subscriptions?** Plan ID lookup in webhook? Custom field? Subscription metadata? Need to verify with PayPal product config.

3. **C2 — 30-day-use enforcement**: How strict? Hard reject under 30 days, or "manual review" status with admin override? Recommend: status `needs_30d_use` with admin manual approval override for cases where applicant has paid relationship via other means.

4. **C3 — Retroactive recalc transactional safety**: If recalculating 1000+ commission_payments rows takes longer than CF Worker timeout, need queue-based execution. Recommend: trigger recalc as background Durable Object task or queue.

5. **G1 — 17-commit bundle**: Some are b98235f referral-related, others are CE SME, social-api, blog-publisher, etc. Recommend: cherry-pick only referral-related commits; defer others to their own SHIP gates.

---

*Generated by Aether for CTO pre-build review, 2026-05-07. Awaiting CTO GO/NO-GO before BUILD dispatch.*
