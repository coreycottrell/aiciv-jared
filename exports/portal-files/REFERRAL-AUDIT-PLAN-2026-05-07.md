# Referral System: Test + Full Audit + Production Cutover Plan
**Date**: 2026-05-07 | **Owner**: Aether (Co-CEO/Conductor) | **Target**: PurePartner2026 program at https://purebrain.ai/partners/

---

## 🚨 PRE-FLIGHT BLOCKER (must clear before prod cutover)

`workers/referrals-api/src/worker.js` has **+1,382 LOC uncommitted** vs HEAD.
`workers/paypal-webhook/src/worker.js` has **+78 LOC uncommitted**.

This means: **what's running in production right now is not what's in git.** You said "NOTHING local, everything in git with CF" — that requirement is already broken on the most expensive paths in the system (referrals + PayPal split). This must be triaged FIRST:

- Who edited these? (likely from the 5/1 security audit cycle)
- Are these the deployed versions or local experimental edits?
- Commit + SEC + QA gate, or revert and redeploy from git.

This is non-negotiable for production cutover.

---

## ✅ STEP 1 — TEST THE 3 STAGING FIXES TOGETHER (YOU + ME, ~5 MIN)

Today's commit `b98235f` shipped 3 frontend-only fixes to `exports/cf-pages-deploy/admin/referrals/index.html`. **Staging admin is live (HTTP 200 verified).**

### Setup
1. Open **private/incognito tab**: https://staging.purebrain.ai/admin/referrals/
2. Open DevTools → Console + Network tabs
3. Login with admin token (whatever you use for staging)

### Test 1 — Bug 1: Autocomplete CORS fallback
- Click any partner row to open detail panel
- In the client/affiliate autocomplete field, start typing 1-2 letters
- **Expected console output (one of):**
  - `[ensureClientsLoaded] Loaded N clients from admin-api` (admin-api worked, no CORS issue)
  - `[ensureClientsLoaded] admin-api failed (likely CORS on staging): ...` followed by `[ensureClientsLoaded] Fallback: loaded N from referrals-api affiliates` (CORS blocked, fallback ran, dropdown still populated)
- **PASS**: Dropdown shows clients regardless of which path fired
- **FAIL**: Empty dropdown OR `Fallback also failed:` in console

### Test 2 — Bug 2: Split row persistence
- In a partner detail panel, click "Add Split"
- Fill the new split row with a name + percentage
- Click "Add Split" AGAIN to add a second row
- **PASS**: First row's name + % is still populated (not blanked)
- **FAIL**: First row went empty when second row was added

### Test 3 — Bug 3: Save with PUT/PATCH fallback
- Fill 2-3 split rows with valid splits (must total 100%)
- Click Save / Update Splits button
- **Network tab — expected sequence:**
  - PATCH request → if 200, done (PASS)
  - If PATCH 404/405 → automatic PUT /splits → if 200, done (PASS)
  - If PUT /splits 404 → automatic PUT /partners/:id → if 200, done (PASS)
- **PASS**: One of the three requests returns 200 + UI confirms saved
- **FAIL**: All three return error, OR DOM values typed in disappear after save

### Tell me which tests pass/fail and any console errors. I'll correlate to Worker logs.

---

## 🔍 STEP 2 — FULL AUDIT (RUNNING IN PARALLEL NOW, BACKGROUND)

Four specialists dispatched in background. Each has a focused brief:

| Specialist | Brief |
|------------|-------|
| **payment-flow-qa** | End-to-end referral attribution: 90-day cookie capture on `/partners/` → ref code persists through payment pages → PayPal webhook fires → D1 write attributes commission to correct partner. Verify the DB split (referrals-api uses `purebrain-referrals`, paypal-webhook uses `purebrain-social` — different DBs, must verify cross-DB writes are correct). |
| **security-auditor** | PayPal auto-split integrity ($35 ops fee → 5% referral → 60% Corey / 40% Pure Tech). Admin auth (post-5/1 bcrypt fix). Webhook signature verification. Rate limiting on `/track`. Re-audit the +1382 LOC uncommitted referrals-api delta. |
| **pattern-detector** | Match PurePartner2026 spec promises against what exists. Tiered commission (15% start → 17% at 100 refs → 20% at 1000 refs, **RETROACTIVE**), 90-day cookie, recurring duration, 10% referral discount, **Support Tier 25% commission**, real-time dashboard, $50 min payout, plan-upgrade auto-recalc, Certified Partner Badge after 3 active refs, monthly office hours. Output: feature gap list. |
| **browser-vision-tester** | Live UI test on https://staging.purebrain.ai/admin/referrals/ — runs the same 3 tests you're running, in parallel, with screenshots. Cross-checks your manual test. |

**ETA**: 15-20 min for results. Will synthesize into go/no-go cutover decision.

---

## 📋 STEP 3 — PRODUCTION CUTOVER CHECKLIST (AFTER TESTING + AUDIT)

Before flipping the switch:

### Code & Git
- [ ] +1,382 LOC referrals-api delta → committed + SEC + QA gates passed (or reverted)
- [ ] +78 LOC paypal-webhook delta → committed + SEC + QA gates passed (or reverted)
- [ ] Both Workers deployed from git, NOT from local
- [ ] No `wrangler pages deploy` (banned per memory) — only CF Pages git deploys
- [ ] No local SQLite anywhere in the path (containers banned for prod)

### D1 + Data
- [ ] Referrals D1 (`purebrain-referrals`) schema matches all PurePartner2026 features
  - Tiering table (commission rate per partner, milestones)
  - Retroactive upgrade trigger (when partner hits 100/1000 refs, recalc historical commissions at new rate)
  - Click tracking table (90-day cookie attribution)
  - Payout requests + min $50 threshold
  - Certified Partner Badge state
  - Plan-upgrade auto-recalc when client upgrades subscription
- [ ] PayPal-webhook → D1 write path verified (which DB? cross-DB or wrong-DB write risk?)
- [ ] PayPal Auto-Split logic intact: $35 ops → 5% referral → 60% Corey / 40% PT (CONSTITUTIONAL per `feedback_paypal_auto_split_constitutional.md`)

### Frontend
- [ ] `https://purebrain.ai/partners/` referral capture script (90-day cookie) writes to D1 via `app.purebrain.ai/api/referral/track` (already running per page source)
- [ ] All 10 payment pages preserve `pb_ref` from URL/localStorage/cookie (not just `?ref=` on load)
- [ ] Partner dashboard live and updated daily (spec says "real-time" — verify)
- [ ] Admin /admin/referrals/ — all 3 staging fixes verified, then deployed to prod

### Auto-Update from PayPal
- [ ] PayPal webhook URL configured in PayPal Developer Dashboard → points to `paypal-webhook` Worker
- [ ] WEBHOOK_SECRET set in Worker secrets (matches PayPal webhook ID)
- [ ] On `BILLING.SUBSCRIPTION.ACTIVATED`: writes referral attribution + commission row
- [ ] On `PAYMENT.SALE.COMPLETED`: writes monthly recurring commission to D1
- [ ] On `BILLING.SUBSCRIPTION.UPDATED`: recalculates commission at new plan rate (PurePartner2026 promises this)
- [ ] On `BILLING.SUBSCRIPTION.CANCELLED`: stops commission accrual

### Constitutional Locks
- [ ] Investor codes/gift pages frozen — no modification
- [ ] Payment guard on all 10 pages preserved
- [ ] Pre-deploy credential scan run (no hardcoded creds in HTML/JS)
- [ ] CF Pages health check uses GET not HEAD

### Rollback Plan
- [ ] Git revert tag for both Workers ready
- [ ] D1 backup snapshot taken before cutover
- [ ] DNS/route swap is last step, easily reversible

---

## 🎯 PUREPARTNER2026 SPEC SUMMARY (extracted from live page)

Promised to partners:
- **15–20% monthly recurring commission** (tiered: 15% start → 17% at 100 refs → 20% at 1000 refs, **retroactive to ALL clients**)
- **90-day cookie tracking window**
- **Recurring duration** ("per referral" — likely lifetime while subscription active)
- **Referrals get 10% off** (partner discount)
- **Support Tier add-ons: 25% commission** (higher rate for Support Tier upsells)
- **30-day personal use** before partner approval
- **Real-time dashboard** showing clicks, active referrals, commission earned (page says "updated daily" — minor inconsistency)
- **Min payout $50**, PayPal or bank, no waiting period
- **Plan-upgrade auto-recalc**: if referral upgrades $297 → $597, commission increases automatically (15% → $44.55 → $89.55)
- **Certified Partner Badge** after 3 active referrals (LinkedIn-shareable)
- **Monthly Partner Office Hours** with Jared

This is the spec audit will measure existing system against.

---

## 📡 TRIO RELAY (Morphe just updated)
- **Hancock Law**: 301,522 clauses live; all 5 batches running; lawyers testing today (platform GO after Chy's AI key fix)
- **CE SME**: Investigating ce.purebrain.ai 530. Frontend fine on `purebrain-production-23b.pages.dev` (200). 530 = CF Pages custom domain SSL issue. Worker code being located. Full QA on 6 modules in progress.

---

*Generated by Aether for Jared, 2026-05-07. Audit specialists running in background; will deliver consolidated findings + go/no-go cutover decision when they return.*
