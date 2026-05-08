# 🛡️ security-auditor: Referral System Production Cutover Audit

**Agent**: security-auditor
**Domain**: Static security review — Cloudflare Workers (referrals-api, paypal-webhook)
**Date**: 2026-05-07
**Scope**: Local working-tree (uncommitted, +1382/+78 LOC vs HEAD post-5/1 audit)
**Targets**: `workers/referrals-api/src/worker.js` (1918 LOC), `workers/paypal-webhook/src/worker.js` (512 LOC)

---

## Executive Summary

| Severity | Count |
|---|---|
| Critical | **2** |
| High | **3** |
| Medium | **4** |
| Low | **3** |
| Info | 2 |

**Overall posture**: 🟡 **DO NOT CUT OVER until Critical-1 + Critical-2 + High-1 are fixed.** All five 5/1 fixes are still in place — no regressions. New surface is large (+1382 LOC) and introduces two showstoppers around money flow and admin token handling.

---

## TOP 3 BLOCKERS (must fix before production)

1. **CRITICAL-1**: Hardcoded admin token fallback in `paypal-webhook` — `"purebrain-admin-2026"` will leak into source/git/logs and unlocks every `/admin/*` write on referrals-api if `REFERRALS_ADMIN_TOKEN` ever unsets.
2. **CRITICAL-2**: PayPal webhook signature verification is **disabled** — `verifyWebhook()` always returns `true`, even on signature mismatch (comment: "allow through to avoid losing events"). Anyone who can POST to the webhook URL can mint subscriptions, mark referrals complete, and trigger commission payments.
3. **HIGH-1**: `commission_payments` insert path (POST `/commission_payments` line 546) computes commission as `(payment_amount - 35) * split.percentage` — **subtracts $35 ops fee from the base** before applying split %. Conflicts with `calculateCommission()` (line 210) which uses **full** `paymentAmount * rate`. Two code paths, two answers, real money. Pick one rule and remove the other.

---

## Findings

### 🔴 CRITICAL

**[SEC-001] Hardcoded admin token fallback** — CVSS 9.1 (AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
- **File**: `workers/paypal-webhook/src/worker.js:266`
- **Code**: `const ADMIN_TOKEN = env.REFERRALS_ADMIN_TOKEN || "purebrain-admin-2026";`
- **Impact**: If the secret is ever unset (deploy mistake, env rotation gap), this string becomes a valid `X-Admin-Token` for `referrals-api`. It's now in git history regardless. Every `/admin/*` endpoint (including `/admin/affiliate/delete`, `/admin/payments/manual`, `/admin/payout/mark-paid`) accepts it.
- **Fix**: Remove the fallback. Throw if `env.REFERRALS_ADMIN_TOKEN` is missing. **Then rotate `ADMIN_TOKENS` on referrals-api** (assume current token compromised by virtue of being committable). Add `pre-deploy-credential-scan` skill to CI.

**[SEC-002] PayPal webhook signature verification is a no-op** — CVSS 9.3 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
- **File**: `workers/paypal-webhook/src/worker.js:164-183`
- **Evidence**: `verifyWebhook()` always returns `true`. Even when `WEBHOOK_SECRET` is set and the header mismatches, code logs and falls through (line 178-180).
- **Impact**: Forged `BILLING.SUBSCRIPTION.ACTIVATED` POST → `upsertClient()` writes a paying client → `completeReferralCommission()` calls referrals-api with the hardcoded admin token → commission rows inserted → real PayPal payouts triggered downstream by `tools/paypal_auto_split.py`. Replay also possible (no nonce check until D1 dedup, which only fires after the event is processed).
- **Fix**: Implement proper PayPal Webhook ID + transmission signature verification per PayPal docs (`https://api.paypal.com/v1/notifications/verify-webhook-signature`). Reject on `verification_status != "SUCCESS"`. Reject on missing `paypal-transmission-id`/`paypal-transmission-time`/`paypal-cert-url`/`paypal-auth-algo`/`paypal-transmission-sig`.

---

### 🟠 HIGH

**[SEC-003] Two conflicting commission formulas** — CVSS 7.5
- **Files**: `referrals-api/src/worker.js:210` (`commissionValue = paymentAmount * rate`) vs `worker.js:546` (`(payment_amount - 35) * split.percentage`).
- **Impact**: Inconsistent commission ledger; partner disputes; under/overpayments. POST `/commission_payments` is reachable from admin tooling.
- **Fix**: Single source of truth in `calculateCommission()`. Refactor `/commission_payments` to call it.

**[SEC-004] CORS `Access-Control-Allow-Origin: *` on admin endpoints** — CVSS 6.5
- **File**: `referrals-api/src/worker.js:67, 301`. The `json()` helper applies `*` to ALL responses, including `/admin/*`, login, and dashboard.
- **Impact**: Combined with `X-Admin-Token` header auth (no cookie), the admin token must never leak to a browser tab — but if any frontend/extension stores it, every domain on the web can read admin data via `fetch()`. Expanded blast radius if the token ever lands in a browser context.
- **Fix**: Allowlist origins for `/admin/*` and `/dashboard` (e.g. `https://purebrain.ai`, portal). Wildcard OK for fully-public endpoints (`/leaderboard`, `/referrer-discount`, `/track`).

**[SEC-005] `requireAdmin` uses non-constant-time compare** — CVSS 5.9 → with current attack model, **High** because token is shared static secret
- **File**: `referrals-api/src/worker.js:79-87`. `allow.includes(token)` short-circuits character by character.
- **Impact**: Theoretically extractable over many requests. Unlikely over CF edge jitter, but trivially fixable.
- **Fix**: Compare via `crypto.subtle.timingSafeEqual` after hashing both sides, or run all candidate tokens through equal-time compare.

---

### 🟡 MEDIUM

**[SEC-006] Admin token rotation is undocumented & shared static** — CVSS 5.4
- `ADMIN_TOKENS` is a comma-separated env list with no rotation log. There's no per-actor admin auth — every internal caller (portal, paypal-webhook, manual ops) uses the same token. Compromise = full takeover.
- **Fix**: Document rotation runbook. Move toward per-caller tokens with role scoping (e.g. `webhook-only` token can only hit `/referrals/complete-by-email`).

**[SEC-007] No rate limit on `/forgot-password`** — CVSS 5.3
- `referrals-api/src/worker.js:1071`. Returns generic message (good — no enumeration), but unbounded request rate could mailbomb a target via Brevo on `purebrain@puremarketing.ai` reputation.
- **Fix**: 5 reset-token issuances per email per hour, reuse `login_attempts` schema.

**[SEC-008] `/track` endpoint accepts arbitrary referral_code with no rate limit** — CVSS 5.3
- `referrals-api/src/worker.js:929`. Attackers can stuff `referral_clicks` rows to inflate dashboards / mask legitimate fraud.
- **Fix**: Per-IP throttle on `/track`. Reject codes that don't exist in `referrers`.

**[SEC-009] Webhook idempotency window vulnerable to race** — CVSS 4.8
- `paypal-webhook/src/worker.js:455-460`. `isDuplicate()` checks D1, then `recordTransmission()` writes — but two concurrent identical events both pass the check before either writes. `INSERT OR IGNORE` on the log saves the table, but `handleSubscriptionActivated` runs twice → double commission.
- **Fix**: Insert into `paypal_webhook_log` with `INSERT INTO ... ` BEFORE handling the event; if `result.meta.changes === 0`, skip handling (already processed).

---

### 🟢 LOW

**[SEC-010] Verbose error leaks** — CVSS 3.1. `worker.js:1915` and `:459` echo `e.message` to clients. Use generic 500 + log internally.
**[SEC-011] Sessions never invalidated on password reset** — CVSS 3.7. `/reset-password` (line 1138) updates the hash but doesn't `DELETE FROM sessions WHERE referrer_id = ?`. Stolen session token survives reset.
**[SEC-012] PayPal webhook returns 200 on unhandled errors** (`paypal-webhook/src/worker.js:500`) — operationally correct but masks ingestion failures from monitoring.

---

### ℹ️ INFO

- Dashboard auth (line 1475) correctly verifies session ownership; admin bypass is intentional and documented.
- Bcrypt-needs-reset path (line 1040) correctly returns 401 + logs failed attempt.

---

## Status of 5/1 Fixes

| 5/1 Fix | Status | Evidence |
|---|---|---|
| Bcrypt no-auto-accept | ✅ HOLDING | `worker.js:124-134, 1040-1045` |
| Dashboard requires auth | ✅ HOLDING | `worker.js:1481-1510` (admin bypass intentional) |
| Login rate limit (10/15min) | ✅ HOLDING | `worker.js:1010-1015` |
| Salted SHA-256 hashing | ✅ HOLDING | `worker.js:102-114` |
| `/track` endpoint exists | ✅ HOLDING | `worker.js:929-956` |

**No regressions.** All five fixes preserved through the +1382 LOC delta.

---

## PayPal Auto-Split Constitutional Check

**Verdict**: ⚠️ **Cannot fully verify in Workers — but the Workers don't violate it.**

- The constitutional split ($35 ops → 5% referral → 60% Corey @ `weaver.aiciv@gmail.com` / 40% Pure Tech) lives in `tools/paypal_auto_split.py` (lines 53, 281). **Not** in either Worker.
- Workers handle: (a) referral commission calculation (5%/15%/17%/20% by tier — capped at 20% line 208), (b) recording into `commission_payments`, (c) firing webhooks.
- The Corey/Pure Tech 60/40 split happens **offline** in `paypal_auto_split.py` reading from the spreadsheet `1bmmO2FVxZdAcYewPFNu6DbHZzh9AAojHUsWgofv6tqQ`. Workers do NOT compute or persist the 60/40 split.
- **Risk**: HIGH-1 (`(payment_amount - 35) * split.percentage` at line 546) suggests someone tried to bake the $35 ops fee into the Worker calc inconsistently. If `paypal_auto_split.py` ALSO subtracts $35, you double-deduct. Reconcile before cutover.
- **Recipients**: `weaver.aiciv@gmail.com` confirmed in `tools/paypal_auto_split.py:53`. No Corey email literal in either Worker (correct — the Workers are partner-facing only).
- **Approval gate**: Constitutional doc requires manual approval before payout. This is enforced by `paypal_auto_split.py` workflow, NOT by these Workers. Confirm gate still active before cutover.

**Recommendation**: Before production, run a single end-to-end test in PayPal sandbox with real $-amount, trace from webhook → referrals-api → spreadsheet → `paypal_auto_split.py`, and verify exactly one $1.75 referral commission row + correct Corey 60% / PT 40% disbursement on a $35 ops fee.

---

## Memory Written
**Path**: `.claude/memory/agent-learnings/security-auditor/2026-05-07--referral-cutover-audit.md`
**Type**: gotcha + pattern
**Topic**: 5/1 fixes held; new critical surface (hardcoded admin token, no-op webhook sig verify, dual commission formulas) introduced in +1382 LOC delta.

**Verification of this report**:
- Read full `referrals-api/src/worker.js` (1918 lines) and `paypal-webhook/src/worker.js` (512 lines) ✅
- Cross-referenced 5/1 audit memo and `feedback_paypal_auto_split_constitutional.md` ✅
- Confirmed git delta via `git diff --stat HEAD` ✅
- Searched for hardcoded creds, SQL injection, CORS issues ✅
