# Referral System Audit — March 29, 2026

**Audited by**: dept-systems-technology
**Files examined**: `referrals.db`, `portal_server.py`, `referral-tracker.js`, CF Pages payment pages, `admin-referrals.html`

---

## Executive Summary

The referral system has solid architecture but **one critical gap**: no one is calling the commission recording endpoint when recurring payments happen. As a result, **every affiliate shows $0.00 earned** even though some have completed referrals with paying members.

---

## Question 1: Is the referral system working end-to-end?

**PARTIALLY.** Here is what works and what does not:

### WORKING

| Component | Status | Evidence |
|-----------|--------|----------|
| Referrer registration | OK | 18 registered affiliates in DB (IDs 1-36) |
| Referral code generation | OK | Unique PB-XXXX codes assigned to each |
| Referral link tracking (`?ref=CODE`) | OK | 56 tracked clicks across 11 different codes |
| Cookie/localStorage persistence | OK | `referral-tracker.js` sets 90-day `pb_ref` cookie + localStorage |
| Referral completion on payment | OK | Browser JS on `/awakened/`, `/live/`, `/partnered/`, `/unified/` calls `/api/referral/complete` after PayPal payment |
| Affiliate login/dashboard | OK | Session-based auth, password reset, dashboard endpoint all functional |
| Admin dashboard at `/admin/referrals` | OK | Shows affiliates, clicks, referrals, has payout management |
| Payout request system | OK | Endpoint exists, PayPal payout execution code exists |

### BROKEN / MISSING

| Component | Status | Impact |
|-----------|--------|--------|
| **Commission calculation on payments** | **NOT WIRED** | `commission_payments` table is EMPTY. Nobody earns anything. |
| **PayPal webhook -> commission trigger** | **MISSING** | No PayPal webhook calls `/api/referral/commission`. The endpoint exists but nothing invokes it. |
| **Rewards table** | **EMPTY** | Zero entries. Commissions never recorded = no rewards. |

---

## Question 2: Are people able to get payouts?

**NO.** The payout request endpoint (`/api/referral/payout-request`) and approval endpoint (`/api/referral/payout-approve`) both exist and are coded correctly. However:

- Payout amounts are calculated from the `rewards` table
- The `rewards` table has **zero rows**
- Therefore every affiliate's "Available Balance" = $0.00
- No one can request a payout because there is nothing to pay out

The PayPal payout execution code (`_execute_paypal_payout`) is fully implemented and would work if there were amounts to pay.

---

## Question 3: Why are there no calculated amounts next to anyone's names?

**ROOT CAUSE**: The `/api/referral/commission` endpoint is never called.

Here is the intended flow vs what actually happens:

### Intended Flow
```
1. Visitor clicks referral link (purebrain.ai?ref=PB-XXXX)
2. Cookie/localStorage stores PB-XXXX                       [WORKS]
3. Visitor pays via PayPal                                   [WORKS]
4. Browser JS calls /api/referral/complete                   [WORKS]
5. Referral marked "completed" in DB                         [WORKS]
6. On each subsequent payment, something calls
   POST /api/referral/commission with payer_email,
   order_id, amount, tier                                    [NEVER HAPPENS]
7. Commission (5% of payment) recorded in
   commission_payments + rewards tables                      [NEVER HAPPENS]
8. Affiliate sees earnings on dashboard                      [SHOWS $0]
```

### The Missing Link (Step 6)

The `/api/referral/commission` endpoint expects to be called by "purebrain_log_server when a payment is verified" (per its docstring). But:

- No `purebrain_log_server` module exists separately
- The `_paypal_subscription_sync_loop` in portal_server.py syncs subscription **status** to `clients.db` but does NOT call the commission endpoint
- The `_collect_payments` function in the client import logic reads payment logs but never triggers commission recording
- No PayPal webhook handler exists that would fire on `PAYMENT.SALE.COMPLETED` events

**In short**: The commission recording endpoint is built and ready, but no part of the system ever calls it.

---

## Database State Snapshot

| Table | Rows | Notes |
|-------|------|-------|
| `referrers` | 18 | Active affiliates |
| `referrals` | 46 | 18 real referrals + 24 paypal-placeholder + 4 rejected |
| `referral_clicks` | 56 | Across 11 codes. Daniel Grand (PB-G8XP) has 25 clicks. |
| `rewards` | **0** | EMPTY — this is why $0 shows everywhere |
| `commission_payments` | **0** | EMPTY — commissions never recorded |
| `admin_tokens` | (not checked) | Admin auth tokens |

### Top Affiliates by Completed Referrals (data present but $0 earnings)

| Affiliate | Code | Completed Referrals | Earnings |
|-----------|------|---------------------|----------|
| MJ S (Jared) | JAREDSB0 | 8 real + several paypal-placeholder | $0.00 |
| Apex People | PB-AYXE | 3 | $0.00 |
| Michael Hancock | PB-3AUQ | 2 (+1 new: Pia Knudsen) | $0.00 |
| Alexander Logie | PB-K22P | 1 (Harrison Amit) | $0.00 |
| Joseph Ray Diosana | PB-JJ8N | 1 (Vishal Doddanna) | $0.00 |
| Donato LaSaracina | PB-N2GR | 1 (Daniel Grand) | $0.00 |
| Daniel Grand | PB-G8XP | 1 (paypal placeholder) | $0.00 |

---

## What Needs to Be Built

### Fix 1: Wire PayPal payments to commission recording (CRITICAL)

When a PayPal subscription payment is received (or synced), the system needs to call the existing `/api/referral/commission` endpoint internally. Two options:

**Option A — Add to PayPal subscription sync loop:**
In `paypal_sync_subscriptions.py`, after syncing payment data, check if the payer email exists in `referrals` table and call the commission endpoint.

**Option B — Add a PayPal webhook handler:**
Register a PayPal webhook for `PAYMENT.SALE.COMPLETED` events. On each event, extract payer_email + amount + order_id and POST to `/api/referral/commission`.

Option A is simpler and works with existing infrastructure. Option B is more real-time.

### Fix 2: Backfill existing commissions

For the ~18 completed referrals with real emails, cross-reference against actual payments in the payment logs and retroactively record commissions.

### Fix 3: Clean up paypal-placeholder referrals

24 referral records have `paypal_i-XXXXX@pending` as their email. These were created when the `/api/referral/complete` endpoint received an order_id but no payer email. These cannot be matched to actual payers for commission purposes and should either be:
- Cleaned up / resolved to real emails
- Or left as-is (they won't cause harm, just clutter)

---

## CF Pages Referral Link Handling

The `referral-tracker.js` file at the site root correctly:
1. Reads `?ref=`, `?code=`, or `?referral=` URL params
2. Sets a 90-day first-touch cookie (`pb_ref`)
3. Mirrors to localStorage
4. Fires a click-track POST to `app.purebrain.ai/api/referral/track`
5. Exposes `window.getPbRef()` for payment pages to read

Payment pages (`/awakened/`, `/live/`, `/partnered/`, `/unified/`) correctly call `getPbRef()` after PayPal approval and POST to `/api/referral/complete`.

**This part of the pipeline works correctly.** The break is server-side after initial referral completion.

---

## Files Examined

- `/home/jared/purebrain_portal/referrals.db` — SQLite database
- `/home/jared/purebrain_portal/portal_server.py` — All referral API endpoints (lines 3066-5000+)
- `/home/jared/purebrain_portal/admin-referrals.html` — Admin dashboard HTML
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/referral-tracker.js` — Client-side tracking
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/refer/index.html` — Affiliate portal page
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/awakened/index.html` — Payment page (referral complete call)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/live/index.html` — Payment page (referral complete call)
