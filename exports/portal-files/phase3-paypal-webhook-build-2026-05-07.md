# Phase 3 BUILD: paypal-webhook Worker — Summary

**Date**: 2026-05-07
**Branch**: `referral-v1`
**Status**: CODE COMPLETE (NO DEPLOY)
**Agent**: coder (via Aether conductor)

---

## Commits Delivered

### 1. Service Binding Migration (A1 + CTO Edit #5)

**Commit**: `37cdf89`
**File**: `workers/paypal-webhook/wrangler.toml`

**Changes**:
- Added `[[services]]` binding for `REFERRALS_API` → `referrals-api`
- Eliminates cross-Worker HTTP + admin token authentication
- Constitutional pattern per CTO Edit #5

**Acceptance Criteria Satisfied**:
- ✅ A1: Remove hardcoded admin token fallback (achieved via Service Binding)
- ✅ CTO Edit #5: Service Binding migration bundled with A1

---

### 2. Real PayPal Webhook Signature Verification (A2)

**Commit**: `fa7a4da`
**File**: `workers/paypal-webhook/src/worker.js`
**Lines Changed**: +261, -20 (net: +241 LOC)

**Implementation**:

#### OAuth Token Caching
- In-memory cache per isolate, 5min TTL
- `getPayPalAccessToken(env)` function (lines 168-200)
- Supports both sandbox and live modes via `PAYPAL_MODE` env var

#### Signature Verification
- Replaces no-op stub (old lines 164-183)
- New `verifyWebhook(request, env, body)` (lines 202-265)
- Calls PayPal `/v1/notifications/verify-webhook-signature` API
- Validates:
  - `transmission_id`
  - `transmission_sig`
  - `transmission_time`
  - `cert_url`
  - `auth_algo` (SHA256withRSA)
  - `webhook_id`
  - Full event body

#### Security Fix
- **Before**: Always returned `true` — anyone could fake a PayPal payment
- **After**: Returns `401 Unauthorized` on signature failure
- Changed webhook handler line 476: `return Response.json({ status: "rejected", reason: "invalid_signature" }, { status: 401 });`

#### Required Secrets
- `WEBHOOK_ID` - from PayPal developer dashboard
- `PAYPAL_CLIENT_ID`
- `PAYPAL_CLIENT_SECRET`
- `PAYPAL_MODE` - "sandbox" or "live"

**Acceptance Criteria Satisfied**:
- ✅ A2: Real PayPal `verify-webhook-signature` API call implemented
- ✅ OAuth token acquisition + caching
- ✅ Signature verification returns 401 on failure (not 200 with warning)
- ✅ Reads WEBHOOK_ID from env (wrangler.toml comment already documented this)

---

### 3. BILLING.SUBSCRIPTION.UPDATED Handler

**Commit**: `fa7a4da` (same commit as A2)
**File**: `workers/paypal-webhook/src/worker.js`
**Lines**: 324-391

**Implementation**:

#### Plan Change Detection
- Compares `old_amount` (from `clients.monthly_amount`) vs `new_amount` (from webhook resource)
- Reads `previous_monthly_amount` + current amount from D1
- Extracts new amount from `resource.billing_info.last_payment.amount.value` or `resource.plan.billing_cycles`

#### Audit Trail
- Updates `clients` table:
  - `previous_monthly_amount` = old amount
  - `monthly_amount` = new amount
  - `plan_changed_at` = ISO timestamp
  - `last_active_at` = ISO timestamp

#### Commission Recalculation Trigger
- Calls `referrals-api` via Service Binding: `POST /internal/recalc-subscription`
- Request body:
  ```json
  {
    "subscription_id": "I-xxx",
    "old_amount": 149.00,
    "new_amount": 499.00,
    "changed_at": "2026-05-07T12:34:56.789Z"
  }
  ```
- Graceful degradation: logs warning if recalc fails, doesn't fail webhook
- **Note**: `wtt-fullstack` (parallel work on `referrals-api`) will implement the `/internal/recalc-subscription` endpoint

#### No-Change Path
- If amounts are equal or missing, updates tier metadata via `upsertClient()`

#### Race Condition Handling (CTO Q2)
- Reads amount-at-event-time from webhook resource (not from stale DB state)
- Stores `previous_monthly_amount` for audit trail
- CTO Q4: referrals-api endpoint will handle >500 row chunking

**Acceptance Criteria Satisfied**:
- ✅ Work Item #3: BILLING.SUBSCRIPTION.UPDATED handler exists
- ✅ Detects plan-amount change
- ✅ Triggers commission recalc via Service Binding
- ✅ CTO Q4: recalc logic deferred to referrals-api (>500 row chunking there)

---

### 4. 60-Second Deferred-Lookup Retry (CTO Edit #6)

**Commit**: `fa7a4da` (same commit as A2)
**File**: `workers/paypal-webhook/src/worker.js`
**Lines**: 286-322, 458-459

**Implementation**:

#### Race Condition Context
- PayPal webhook can arrive 1-30s before frontend POST creates pending referral row
- Without retry, commission silently lost

#### Retry Logic
- New function: `checkReferralAttribution(env, data, retryCount)` (lines 286-322)
- Called from `handleSubscriptionActivated` (line 458)
- On first attempt:
  - Calls `referrals-api` via Service Binding: `POST /internal/complete-by-email`
  - Body: `{ customer_email, subscription_id, payment_amount }`
- If `404 Not Found` (no referral row exists):
  - Schedules retry after 60 seconds via `env.ctx.waitUntil()` + Promise
  - Logs: "No referral found for {email}, scheduling retry in 60s"
- On retry (retryCount === 1):
  - Calls referrals-api again
  - If still `404`, writes to `paypal_webhook_log` with `event_type='no_referral_after_retry'`
  - Allows manual reconciliation

#### Execution Context Passing
- Updated `handleWebhook(request, env, ctx)` signature to receive `ctx` (line 511)
- Stores `ctx` in `env.ctx` for use in nested handlers (line 513)
- Main router passes `ctx` to `handleWebhook` (line 447)

#### Graceful Error Handling
- Service Binding errors logged but don't fail webhook
- `console.error("[paypal-webhook] Service binding error (attribution): ...")` (line 320)

**Acceptance Criteria Satisfied**:
- ✅ Work Item #4: 60-second retry for race condition
- ✅ CTO Edit #6: deferred-lookup retry on `no_referral`
- ✅ Manual reconciliation log for failed retries

---

## Service Binding Contract (for wtt-fullstack)

`wtt-fullstack` is building `referrals-api` in parallel. They need to implement these endpoints to satisfy the Service Binding calls:

### Endpoint 1: Attribution Completion

```
POST /internal/complete-by-email
Content-Type: application/json

Request Body:
{
  "customer_email": "user@example.com",
  "subscription_id": "I-XXXXXXXXXX",
  "payment_amount": 149.00
}

Response (200 OK):
{
  "referral_id": 123,
  "partner_id": "PB-1234",
  "commission_amount": 22.35,
  "status": "completed"
}

Response (404 Not Found):
{
  "error": "no_referral",
  "customer_email": "user@example.com"
}
```

### Endpoint 2: Commission Recalculation (Plan Upgrades)

```
POST /internal/recalc-subscription
Content-Type: application/json

Request Body:
{
  "subscription_id": "I-XXXXXXXXXX",
  "old_amount": 149.00,
  "new_amount": 499.00,
  "changed_at": "2026-05-07T12:34:56.789Z"
}

Response (200 OK):
{
  "affected_commission_count": 3,
  "total_dollars_recalculated": 52.50,
  "execution_time_ms": 45
}

Response (500 Internal Server Error):
{
  "error": "recalc_failed",
  "reason": "subscription_not_found"
}
```

**Notes**:
- Both endpoints are **internal-only** (not exposed to public)
- No explicit auth needed (Service Binding is internal CF communication)
- Endpoint 2: if >500 commission rows affected, chunk/queue per CTO Q4
- Endpoint 1: must lookup referral by `customer_email` OR `subscription_id`

---

## Acceptance Mapping

| Work Item | SPEC Requirement | Commits | Status |
|-----------|------------------|---------|--------|
| **A1** | Remove hardcoded admin token fallback at line 266 | `37cdf89` | ✅ COMPLETE (via Service Binding) |
| **CTO Edit #5** | Bundle Service Binding migration with A1 | `37cdf89` | ✅ COMPLETE |
| **A2** | Real PayPal webhook signature verification | `fa7a4da` | ✅ COMPLETE |
| **Work Item #3** | BILLING.SUBSCRIPTION.UPDATED handler | `fa7a4da` | ✅ COMPLETE |
| **CTO Edit #6** | 60-second deferred-lookup retry | `fa7a4da` | ✅ COMPLETE |

---

## NOT Included (Per SPEC Constraints)

### A3: Commission Formula Reconciliation
**SPEC Error Caught by CTO Edit #1**: A3 targets `referrals-api/worker.js` lines 210 + 546, NOT `paypal-webhook`. The commission formula reconciliation is on the `referrals-api` side (wtt-fullstack's parallel work). paypal-webhook does NOT calculate commissions — it only writes subscription data and triggers recalc.

**No changes made to paypal-webhook for A3** — correctly scoped to referrals-api.

---

## Verification Steps (Post-Deploy)

**DO NOT DEPLOY YET** per Jared constraint. When deployment is authorized:

1. **Secrets Setup** (before deploy):
   ```bash
   cd workers/paypal-webhook
   echo "PROD_WEBHOOK_ID" | wrangler secret put WEBHOOK_ID
   echo "PROD_CLIENT_ID" | wrangler secret put PAYPAL_CLIENT_ID
   echo "PROD_CLIENT_SECRET" | wrangler secret put PAYPAL_CLIENT_SECRET
   echo "live" | wrangler secret put PAYPAL_MODE
   ```

2. **Deploy** (staging first):
   ```bash
   wrangler deploy
   ```

3. **Test Signature Verification**:
   - Send test webhook from PayPal dashboard
   - Check logs: `wrangler tail`
   - Verify: `[paypal-webhook] Signature verification: VALID`
   - Verify: OAuth token cached (no repeated token calls)

4. **Test SUBSCRIPTION.UPDATED**:
   - Upgrade a test subscription in PayPal
   - Check logs: `plan_changed` action
   - Verify D1: `SELECT previous_monthly_amount, monthly_amount, plan_changed_at FROM clients WHERE paypal_subscription_id = ?`
   - Verify referrals-api: commission recalc triggered (check referrals-api logs)

5. **Test 60-Second Retry**:
   - Subscribe WITHOUT referral cookie (no pb_ref)
   - Webhook fires → first attempt returns 404
   - Wait 60s → check logs for retry attempt
   - Verify: `paypal_webhook_log` has `event_type='no_referral_after_retry'` row

6. **Syntax Check** (already passed):
   ```bash
   node --check src/worker.js
   ```
   ✅ No errors

---

## File Modifications Summary

| File | Lines Added | Lines Removed | Net | Status |
|------|-------------|---------------|-----|--------|
| `wrangler.toml` | +4 | 0 | +4 | ✅ Committed |
| `src/worker.js` | +261 | -20 | +241 | ✅ Committed |

**Total**: +265 LOC, -20 LOC = **+245 net LOC**

---

## Constitutional Compliance

- ✅ **Code on `referral-v1` branch only** — no work on main
- ✅ **NO `wrangler deploy` executed** — code-only per Jared constraint
- ✅ **NO new D1 bindings added** — `purebrain-social` binding preserved (known violation, fixed in future sprint per domain isolation rule)
- ✅ **Service Binding as constitutional pattern** — replaces HTTP + token auth
- ✅ **No touching live paypal-webhook Worker** — all changes committed to branch only

---

## Next Steps (wtt-fullstack)

**wtt-fullstack** (parallel referrals-api work) must implement:

1. `POST /internal/complete-by-email` endpoint (contract above)
2. `POST /internal/recalc-subscription` endpoint (contract above)
3. Handle >500 row chunking in recalc (CTO Q4)
4. Return 404 when no referral found (triggers paypal-webhook's 60s retry)

**Coordination**: Both Workers must deploy in lockstep once referrals-api endpoints are ready. Service Binding will fail if referrals-api is not deployed.

---

## Git State

```bash
git log --oneline -3
fa7a4da feat(paypal-webhook): A2 — Real PayPal webhook signature verification
37cdf89 feat(paypal-webhook): A1 + CTO Edit #5 — Add Service Binding to referrals-api
b1c10a3 refactor(d1): split v1 sprint schema into 0002a (referrals-only, applyable now) + 0002b (clients additions, held pending extraction per domain isolation rule)
```

**Branch**: `referral-v1`
**Commits**: 2 new commits (A1/Edit#5 + A2/UPDATED/retry)
**Status**: Clean working tree (no uncommitted changes in paypal-webhook/)

---

## Memory Written

Path: `.claude/memory/agent-learnings/coder/2026-05-07--paypal-webhook-phase3-build.md`
Type: implementation
Topic: Service Binding pattern + PayPal signature verification + plan upgrade handling + 60s retry for race conditions

---

**Phase 3 BUILD: COMPLETE**

Ready for CTO SECURITY review when wtt-fullstack completes referrals-api endpoints.

---

*Generated by coder agent, 2026-05-07*
