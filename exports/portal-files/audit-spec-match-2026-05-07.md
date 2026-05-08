# pattern-detector: PurePartner2026 Spec vs Implementation Audit

**Date**: 2026-05-07
**Scope**: Public partner page (https://purebrain.ai/partners/) vs codebase
**Code refs**: `workers/referrals-api/src/worker.js`, `workers/paypal-webhook/src/worker.js`, `exports/cf-pages-deploy/partners/index.html`

---

## 11 Promises × Implementation Status

| # | Promise | Implemented? | Where (file:line) | Gap | Blocker? |
|---|---------|---|---|---|---|
| 1 | Tiered 15/17/20% rates | **PARTIAL — wrong default** | `referrals-api/src/worker.js:196-203` | Code defaults new signups to `partner_tier='standard'` = **5%** flat. The 15/17/20% only fires for `partner_tier='elite'`. Page promises 15% as STARTING rate to all approved partners. **Mismatch is fundamental.** | **YES — blocks launch** |
| 1b | Retroactive rate upgrades | **NO** | n/a | When `total_sales` crosses 100/1000, NEW commissions use new rate (line 200-201), but PRIOR `commission_payments` rows are not updated. "Retroactive to all clients" is unimplemented. | **YES** |
| 2 | 90-day cookie tracking | **YES** | `partners/index.html:42-87` | localStorage + cookie + `/api/referral/track` POST verified live | No |
| 3 | Recurring commission for "duration per referral" | **PARTIAL** | `paypal-webhook/src/worker.js:365-385` | `PAYMENT.SALE.COMPLETED` fires `completeReferralCommission` on each recurring payment — works as long as referral row stays attributed. NO end date / cap is enforced. Page never defines duration ("commission window" used vaguely line 1464). Spec ambiguity = legal risk. | Medium |
| 4 | Referrals get 10% off | **PARTIAL — disabled by default** | `referrals-api:244-245, 345-376, 962-979` | `discount_enabled=0` default, only Elite partners can enable (`worker.js:356`). Public lookup endpoint `/referrer-discount` exists but is **not wired into any payment page**. No checkout integration. **Page does NOT promise 10% off** — promise comes only from user prompt. Verify with Jared if still in scope. | Medium |
| 5 | Support Tier 25% commission | **NO** | n/a | Zero references to 25% / Support Tier in code or live page. May be deprecated from spec. **Confirm with Jared before building.** | No (verify scope first) |
| 6 | 30-day personal use required | **NO ENFORCEMENT** | `referrals-api:865-922` | `POST /partners/signup` creates immediately-active partner. No approval queue, no usage check, no admin gate. Application form (`partners/index.html:1709`) posts to **Brevo only** — not into any DB review table. Page promises "We review every application personally" — no mechanism exists. | **YES** |
| 7 | Real-time dashboard | **PARTIAL — page contradicts itself** | `referrals-api:1430-1599` | Dashboard endpoint `/dashboard?id=N` returns live D1 query (real-time). BUT page line 1229 says "updated **monthly**" and line 1434 says "verified monthly against **Stripe** subscription records" — page is wrong: it's PayPal, real-time, no monthly batch. Customer expectation mismatch. | Medium (page copy fix) |
| 8 | $50 min payout, no waiting | **PARTIAL** | `referrals-api:585-600, 1789-1800` | `payout_requests` table exists, admin can mark paid. **No `POST /payout/request` endpoint** for partner self-service. **No $50 min validation** anywhere. Page line 1444 says "Net-30 after first full billing cycle" — also unimplemented. | **YES** |
| 9 | Plan-upgrade auto-recalc | **PARTIAL** | `paypal-webhook:91-119, 365-385` | Per-payment `incrementTotalPaid` runs, and recurring commission uses the NEW `amount` from each PAYMENT.SALE event — so if PayPal sends new amount on plan change, it auto-applies. BUT: no explicit `BILLING.SUBSCRIPTION.UPDATED` handler (line 467-479 misses it). Untested edge case. | Medium |
| 10 | Certified Badge after 3 referrals | **YES** | `referrals-api:1559-1566, 1869-1912` | Auto-set at 3 completed, badge SVG URL returned, embed HTML provided. **`certified-partner-badge.svg` asset must exist** at purebrain.ai/assets/. | No (verify asset exists) |
| 11 | Monthly Partner Office Hours | **NO INFRASTRUCTURE** | n/a | Pure marketing claim. No calendar, no Zoom/booking link, no recurring event. Operational, not technical — but if no event ever happens, it's a broken promise. | Low (but operational blocker) |

---

## TOP 5 SPEC GAPS BLOCKING PRODUCTION CUTOVER

1. **5% vs 15% rate mismatch** (`worker.js:196-203`). New signups land at `standard`/5%. The public page promises 15% start. **Fix**: change default `partner_tier` to `'elite'` OR collapse tier system so 15/17/20% applies to all approved partners. Single-line code change + tier model rethink.

2. **No approval workflow / no 30-day check** (`worker.js:865-922`, `partners/index.html:1709`). Form goes to Brevo, signup creates active partner. Need: `partner_applications` table, admin approval UI, gated activation, 30-day usage trace via `clients.first_seen_at`.

3. **No retroactive rate recalc** (missing entirely). When partner crosses 100 → 17%, all existing `commission_payments` rows must be recalculated and a delta credit recorded. Page explicitly promises this.

4. **No partner-facing payout request endpoint + no $50 min** (`/admin/payouts` only). Need `POST /payouts/request` with balance check, `MIN(50)`, idempotency, status='requested'.

5. **Page copy lies** (3 instances): "updated monthly" (1229), "verified monthly against Stripe" (1434), "Net-30" (1444). System is real-time PayPal. **Either fix code to match page or fix page to match code.** Probably page — easier and more honest.

---

## TOP 3 NICE-TO-HAVES POST-LAUNCH

1. **Office Hours infrastructure** — Calendly + recurring Zoom + email reminder cron.
2. **Support Tier 25% rate** — confirm if still in scope; if so, add `addon_commissions` table with rate override per product line.
3. **Partner discount checkout integration** — wire `/referrer-discount` into `pay-*` pages so 10% applies automatically when `pb_ref` cookie present and partner has `discount_enabled=1`.

---

## D1 SCHEMA ADDITIONS NEEDED

```sql
-- 1. Partner application queue (replaces Brevo-only flow)
CREATE TABLE partner_applications (
  id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  email TEXT NOT NULL,
  full_name TEXT NOT NULL,
  website_url TEXT,
  role TEXT,
  audience_size TEXT,
  used_purebrain TEXT,
  why_partner TEXT,
  linkedin_url TEXT,
  client_profile TEXT,
  status TEXT DEFAULT 'pending', -- pending|approved|rejected
  usage_days_at_review INTEGER DEFAULT 0,
  reviewed_by TEXT,
  reviewed_at TEXT,
  rejection_reason TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(email)
);

-- 2. Payout requests (currently used by admin only, add partner-side fields)
ALTER TABLE payout_requests ADD COLUMN requested_amount REAL DEFAULT 0;
ALTER TABLE payout_requests ADD COLUMN payment_method TEXT DEFAULT 'paypal'; -- paypal|bank
ALTER TABLE payout_requests ADD COLUMN bank_details_encrypted TEXT;
-- (validate balance >= 50 in worker, not schema)

-- 3. Retroactive rate adjustments audit trail
CREATE TABLE rate_adjustments (
  id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  referrer_id INTEGER NOT NULL,
  old_rate REAL NOT NULL,
  new_rate REAL NOT NULL,
  trigger_total_sales INTEGER NOT NULL,
  payments_affected INTEGER DEFAULT 0,
  delta_credit REAL DEFAULT 0,
  applied_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (referrer_id) REFERENCES referrers(id)
);

-- 4. Plan-change tracking on clients (so commission can recalc)
ALTER TABLE clients ADD COLUMN previous_monthly_amount REAL DEFAULT 0;
ALTER TABLE clients ADD COLUMN plan_changed_at TEXT;
```

---

## Memory Written
Path: `.claude/memory/agent-learnings/pattern-detector/2026-05-07--purepartner-spec-gaps.md`
Type: pattern
Topic: 5 promise/implementation gaps in PurePartner2026 — default tier rate mismatch is highest-impact, page copy/code mismatch is easiest fix.
