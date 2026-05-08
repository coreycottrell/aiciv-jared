# Production Cutover Audit — Referral Payment Flow (E2E)
**Date**: 2026-05-07
**Auditor**: payment-flow-qa-engineer
**Scope**: READ-ONLY, local source (workers + cf-pages-deploy)
**Verdict**: 🔴 **NOT READY FOR PRODUCTION CUTOVER**

---

## Architecture (current local source)

- `/api/referral/*` → portal-proxy → `referrals-api.in0v8.workers.dev` (D1 `purebrain-referrals`)
- PayPal webhook → `paypal-webhook` Worker (D1 `purebrain-social`)
- `purebrain-social` writes clients; calls `referrals-api/referrals/complete-by-email` over HTTP for commissions

---

## Critical Questions — Verdict Per Question

### Q1. Webhook writes to correct DB? ✅ (mostly)
- `paypal-webhook/src/worker.js:91` writes clients into `env.DB` = `purebrain-social`.
- Commissions are NOT written cross-DB directly. Webhook calls referrals-api over HTTP at `worker.js:272-286` which writes commissions into `purebrain-referrals`. Boundary is clean.
- Auth uses hardcoded fallback `"purebrain-admin-2026"` (`worker.js:266`) — works only if `REFERRALS_ADMIN_TOKEN` secret matches `ADMIN_TOKENS` on referrals-api. Verify both are set.

### Q2. Does pb_ref persist across all payment pages? 🔴 **NO**
| Page | tracker.js loaded | `getPbRef()` callsite | Fires `/api/referral/complete` |
|------|---|---|---|
| `/` (homepage) | ✓ | ✓ | ✅ `index.html:16094` |
| `/awakened/` | ✓ | ✗ | ❌ |
| `/insiders/` | ✓ | ✗ | ❌ |
| `/partnered/` | ✓ | ✗ | ❌ |
| `/unified/` | ✓ | ✗ | ❌ |
| `/home-test*` (3 variants) | ✓ | ✓ | ✅ |
| `/pay-test-*` (3 variants) | ✓ | ✓ | ✅ |
| `/insiders/awakened/` | meta-refresh redirect (search preserved) | n/a | n/a |

Cookie/localStorage capture works on all 10 pages. But the **canonical production payment pages (`/awakened/`, `/insiders/`, `/partnered/`, `/unified/`) never call any referral attribution endpoint**.

### Q3. `BILLING.SUBSCRIPTION.ACTIVATED` writes? ⚠️ partial
- Upserts `clients` row in `purebrain-social` (`worker.js:311-317`).
- Calls `completeReferralCommission()` → `referrals-api /referrals/complete-by-email` (`worker.js:264-298`).
- 🔴 **complete-by-email requires a pre-existing `pending` referral row** (`referrals-api/worker.js:729-734` — `WHERE r.status = 'pending'`). Nothing in the live flow creates that pending row. The only INSERTs into `referrals` are from admin endpoints (`/admin/referral/assign` line 693; `/admin/payments/manual` line 832). Result: webhook always gets `{action: "no_referral"}`. **Commissions never write automatically.**

### Q4. `PAYMENT.SALE.COMPLETED` recurring commission? ❌
- `incrementTotalPaid()` updates client total (`worker.js:148-154`).
- Recurring referral commission call at `worker.js:374-379` — same `complete-by-email` path. Same blocker as Q3 (no pending row → no commission).
- Even if it worked: `complete-by-email` flips status to `completed` on first payment, so months 2-N would also return `no_referral`. **Only first month would attribute, never the 15-20% MRR promise.**

### Q5. `BILLING.SUBSCRIPTION.UPDATED` (plan change) recalc? ❌
- `paypal-webhook/src/worker.js:466-490` switch statement has NO case for `BILLING.SUBSCRIPTION.UPDATED`. Falls through to `default: ignored`. Plan upgrades are silently dropped. Tier in `clients.tier` never updates. Commission rate never recalcs. Spec promise ($297→$597 auto-recalc) **NOT IMPLEMENTED**.

### Q6. `BILLING.SUBSCRIPTION.CANCELLED` stops accrual? ✅ (de facto)
- `worker.js:333-338` flips `status='cancelled'`. PayPal stops sending `PAYMENT.SALE.COMPLETED` after cancellation, so accrual stops by upstream. No explicit guard against late-arriving sales though.

### Q7. 5% / 60% Corey / 40% PT auto-split intact? ❌
- `tools/paypal_auto_split.py` is a **manual Python CLI**, not wired into Worker pipeline. There is zero integration between `paypal-webhook` and `paypal_auto_split.py`. Constitutional split is **manual every payment**.

### Q8. Click-but-no-attribution path? 🔴 YES (this is the dominant path)
- Click `/r/PB-XXX` or `/?ref=PB-XXX` → tracker.js sets cookie + POSTs `/api/referral/track` → recorded in `referral_clicks`.
- Customer lands on `/awakened/` directly → no attribution call at payment.
- Even on homepage (which DOES fire), the call goes to `/api/referral/complete`. Portal-proxy strips `/api/referral` prefix → forwards to `referrals-api/complete`. **No `/complete` route exists** in referrals-api (only `/referrals/complete` and `/referrals/complete-by-email`). All homepage attribution calls return 404. (`purebrain-portal-proxy/src/worker.js:194` strips prefix; `referrals-api/src/worker.js:463` requires `/referrals/complete`.)

---

## TOP 3 BLOCKERS (must fix before cutover)

1. **No path creates a `pending` referral row at customer arrival/checkout.** Webhook commissioning logic depends on it. Either: (a) homepage/payment pages POST to `/admin/referral/assign` with status=pending at email-capture time, or (b) `complete-by-email` should fall back to lookup-by-cookie/email and create-or-find. Without this, **0% of organic referrals ever pay commission**.
2. **Path mismatch between portal-proxy and referrals-api.** Homepage fires `/api/referral/complete` → proxied to `referrals-api/complete` (404). Either fix route to `/referrals/complete` OR add a `/complete` alias in referrals-api. (`exports/cf-pages-deploy/index.html:16094`, `workers/purebrain-portal-proxy/src/worker.js:194`)
3. **Production payment pages (`/awakened/`, `/insiders/`, `/partnered/`, `/unified/`) have ZERO referral-attribution wiring.** They capture cookie via tracker.js but never call attribution at PayPal `onApprove`. Only homepage and home-test/pay-test variants fire attribution. (`exports/cf-pages-deploy/awakened/index.html:5072` `onApprove` → `verifyPaymentServerSide` → `handlePaymentSuccess`, no referral fetch in either.)

## TOP 3 NICE-TO-HAVES (post-cutover OK)

1. Add `BILLING.SUBSCRIPTION.UPDATED` handler to recompute tier + write commission delta. Required by public spec but no live customer is mid-tier-change yet.
2. Auto-apply referrer discount at PayPal createOrder: pages don't call `/referrer-discount` (`workers/referrals-api/src/worker.js:963`). Discount logic is dead code today.
3. Wire `paypal_auto_split.py` to fire from webhook on `PAYMENT.SALE.COMPLETED` so the constitutional 60/40 split is automated, not manual.

---

## Other Notes (informational)
- `paypal-webhook` returns 200 on errors to PayPal (`worker.js:495-505`) — correct, prevents retry storms. Idempotency via `paypal_webhook_log` table works.
- `verifyPaymentServerSide` (`awakened/index.html:5005`) timeouts at 3s and falls through to success — no referral attribution sneaks in here either.
- Min payout $50 promised in spec → not enforced anywhere in `referrals-api`. Today payouts are admin-marked-paid (`/admin/payout/mark-paid`); enforcement is human.
- "Support Tier 25%" promised in `/partners/` page → no `0.25` rate in `calculateCommission()` (`workers/referrals-api/src/worker.js:189-230`). Hard cap is 20%.

---

## Files Referenced (absolute paths)
- `/home/jared/projects/AI-CIV/aether/workers/referrals-api/src/worker.js`
- `/home/jared/projects/AI-CIV/aether/workers/paypal-webhook/src/worker.js`
- `/home/jared/projects/AI-CIV/aether/workers/purebrain-portal-proxy/src/worker.js`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/awakened/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/insiders/awakened/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/referral-tracker.js`
- `/home/jared/projects/AI-CIV/aether/tools/paypal_auto_split.py`
