# PayPal Webhook Phase 3 BUILD — Service Binding + Signature Verification

**Date**: 2026-05-07
**Agent**: coder
**Domain**: CloudFlare Workers, PayPal API integration, Service Bindings
**Context**: Referral System v1 Sprint — Phase 3 BUILD work item

---

## What Was Built

Implemented 4 work items for `workers/paypal-webhook` on `referral-v1` branch:

1. **A1 + CTO Edit #5**: Service Binding to referrals-api (replaces HTTP + admin token)
2. **A2**: Real PayPal webhook signature verification (replaces no-op stub)
3. **BILLING.SUBSCRIPTION.UPDATED**: Handler for plan upgrades → commission recalc
4. **CTO Edit #6**: 60-second deferred-lookup retry for race conditions

**Result**: +245 net LOC, 2 commits, zero deploy (code-only per Jared constraint)

---

## Key Learnings

### 1. Service Binding Pattern (Constitutional)

**What it is**: CloudFlare Service Bindings allow Worker-to-Worker calls without HTTP + tokens.

**Before** (HTTP + token anti-pattern):
```javascript
const response = await fetch("https://referrals-api.in0v8.workers.dev/internal/recalc", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${env.REFERRALS_ADMIN_TOKEN || "purebrain-admin-2026"}`, // VIOLATION
    "Content-Type": "application/json",
  },
  body: JSON.stringify(data),
});
```

**After** (Service Binding):
```javascript
// wrangler.toml
[[services]]
binding = "REFERRALS_API"
service = "referrals-api"

// worker.js
const request = new Request("https://referrals-api/internal/recalc", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data),
});
const response = await env.REFERRALS_API.fetch(request);
```

**Why it's constitutional**:
- No secrets in code (hardcoded token removed)
- No public HTTP exposure (internal CF routing)
- No cross-Worker auth complexity
- CTO declared this the standard pattern (Edit #5)

**When to use**: ANY time one of our Workers needs to call another. HTTP + token is v0 hack only.

---

### 2. PayPal Webhook Signature Verification

**The vulnerability**: Webhook stubs that always return `true` allow anyone to fake payments.

**Real verification flow**:
1. Get OAuth access token from PayPal (cache 5min in-memory)
2. Extract signature headers from webhook request:
   - `paypal-transmission-id`
   - `paypal-transmission-sig`
   - `paypal-transmission-time`
   - `paypal-cert-url`
   - `paypal-auth-algo` (SHA256withRSA)
3. Call PayPal `/v1/notifications/verify-webhook-signature` with:
   - All signature headers
   - `webhook_id` (from env)
   - Full event body (the thing being signed)
4. Return 401 if `verification_status !== "SUCCESS"`

**Gotcha**: Must pass **full event body as received** — PayPal signs the exact JSON. Don't parse and re-stringify.

**Token caching pattern**:
```javascript
let cachedAccessToken = null;
let tokenExpiry = 0;

async function getPayPalAccessToken(env) {
  const now = Date.now();
  if (cachedAccessToken && now < tokenExpiry) {
    return cachedAccessToken; // 5min TTL
  }
  // ... fetch new token, update cache
  tokenExpiry = now + (5 * 60 * 1000);
  return cachedAccessToken;
}
```

**Why cache matters**: OAuth call is slow (~200ms). Caching prevents repeated calls on burst webhooks.

---

### 3. BILLING.SUBSCRIPTION.UPDATED Handler

**Use case**: Customer upgrades Awakened ($149) → Partnered ($499). Commission should recalculate at new rate.

**Race condition** (CTO Q2): Webhook can arrive before OR after the `PAYMENT.SALE.COMPLETED` for the new amount. Don't trust `clients.monthly_amount` in DB — read from webhook resource.

**Audit trail**: Store `previous_monthly_amount` + `plan_changed_at` in clients table for legal/accounting.

**Recalc trigger via Service Binding**:
```javascript
const recalcRequest = new Request("https://referrals-api/internal/recalc-subscription", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    subscription_id: "I-xxx",
    old_amount: 149.00,
    new_amount: 499.00,
    changed_at: "2026-05-07T12:34:56.789Z",
  }),
});
const response = await env.REFERRALS_API.fetch(recalcRequest);
```

**Graceful degradation**: If recalc fails, log warning but don't fail webhook. Commissions can be fixed manually.

**Why**: PayPal will retry failed webhooks. If we return 500, we get infinite retries. Return 200 even if downstream fails.

---

### 4. 60-Second Retry for Race Conditions (CTO Edit #6)

**Problem**: PayPal webhook can arrive 1-30s BEFORE the frontend POST creates the pending referral row. Without retry, commission is silently lost.

**Solution**:
```javascript
async function checkReferralAttribution(env, data, retryCount) {
  const response = await env.REFERRALS_API.fetch(
    new Request("https://referrals-api/internal/complete-by-email", {
      method: "POST",
      body: JSON.stringify({ customer_email, subscription_id, payment_amount }),
    })
  );

  if (response.status === 404 && retryCount === 0) {
    // No referral row exists yet — schedule retry after 60s
    env.ctx.waitUntil(
      new Promise(resolve => setTimeout(resolve, 60000)).then(() => {
        checkReferralAttribution(env, data, 1); // Retry once
      })
    );
  } else if (response.status === 404) {
    // Still no referral after 60s — log for manual reconciliation
    await logNoReferral(env, data);
  }
}
```

**Critical**: Must pass `ctx` (execution context) down through handlers so `ctx.waitUntil()` is available. Updated function signatures:
- `handleWebhook(request, env, ctx)` — receives ctx
- `env.ctx = ctx` — stores for nested handlers
- Main router: `handleWebhook(request, env, ctx)` — passes ctx

**Why `waitUntil()`**: Allows async work to continue after response is sent. Without it, Worker terminates and retry never fires.

**Alternative**: Durable Object alarms for scheduled retries (more robust, but overkill for 1 retry).

---

## Patterns Worth Reusing

### Service Binding Contract Definition

When building cross-Worker calls, define the contract FIRST in a shared doc:

```markdown
## Endpoint: POST /internal/complete-by-email

Request:
{
  "customer_email": "user@example.com",
  "subscription_id": "I-xxx",
  "payment_amount": 149.00
}

Response (200 OK):
{
  "referral_id": 123,
  "commission_amount": 22.35
}

Response (404 Not Found):
{
  "error": "no_referral",
  "customer_email": "user@example.com"
}
```

**Why**: Allows parallel development. Caller and callee can build against the contract without waiting for each other's code.

---

### Webhook Idempotency Pattern

Already existed in this Worker, but worth documenting:

```javascript
// In-memory cache (per isolate)
const seenTransmissions = new Set();

// D1 durable storage
async function isDuplicate(env, transmissionId) {
  if (seenTransmissions.has(transmissionId)) return true; // Fast path

  const row = await env.DB.prepare(
    "SELECT 1 FROM paypal_webhook_log WHERE transmission_id = ?"
  ).bind(transmissionId).first();

  if (row) {
    seenTransmissions.add(transmissionId); // Warm cache
    return true;
  }
  return false;
}
```

**Why 2 layers**:
- In-memory: Fast (no D1 query for repeated calls within same isolate)
- D1: Durable (survives cold starts, prevents duplicates across isolates)

**Eviction**: Keep last 500 in-memory (`Set` size check + delete oldest).

---

## Gotchas Avoided

1. **Signature verification needs full body**: Don't parse → modify → re-stringify. PayPal signs the exact bytes received.

2. **Service Binding URL**: Use fake domain (e.g., `https://referrals-api/path`). CF routing ignores the domain when Service Binding is used.

3. **`waitUntil()` requires ctx**: Must pass execution context from main router down through handlers. Forgetting this = retry never fires.

4. **OAuth token expiry**: Cache with TTL, not indefinitely. PayPal tokens expire after ~9 hours. 5min cache is safe.

5. **Graceful Service Binding errors**: Wrap in try/catch, log, don't throw. If referrals-api is down, webhook should still succeed (return 200 to PayPal).

---

## What NOT to Do

1. **Don't add D1 bindings to paypal-webhook**: It already violates domain isolation by binding `purebrain-social`. Don't make it worse. Wait for clients extraction sprint.

2. **Don't calculate commissions in paypal-webhook**: Commission logic belongs in `referrals-api`. paypal-webhook only writes subscription data and triggers recalc.

3. **Don't deploy without secrets**: `WEBHOOK_ID`, `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET` must be set via `wrangler secret put` BEFORE deploy. Skipping = CF 1042 error.

4. **Don't use HTTP + token for internal Worker calls**: Service Binding is the constitutional pattern. HTTP is v0 hack.

---

## Files Referenced

- `workers/paypal-webhook/wrangler.toml` — Service Binding declaration
- `workers/paypal-webhook/src/worker.js` — All 4 work items
- `exports/portal-files/REFERRAL-SYSTEM-V1-SPEC-2026-05-07.md` — Original SPEC
- `exports/portal-files/cto-prebuild-review-referral-v1-2026-05-07.md` — CTO amendments
- `exports/portal-files/phase3-paypal-webhook-build-2026-05-07.md` — Build summary

---

## Service Binding Contract (for referrals-api)

**Documented for wtt-fullstack** (parallel work):

### POST /internal/complete-by-email
- Lookup referral by `customer_email` or `subscription_id`
- Return 404 if no referral row exists (triggers 60s retry)
- Return 200 + commission details on success

### POST /internal/recalc-subscription
- Recalculate commission_payments for given subscription at new rate
- If >500 rows affected, chunk/queue per CTO Q4
- Return affected row count + dollars recalculated

---

## Next Time

**Pattern to propagate**:
- Service Binding for ALL cross-Worker calls (not just referrals)
- Signature verification pattern for webhooks (Stripe, other providers)
- 60-second retry with `waitUntil()` for race conditions

**Things to watch**:
- Service Binding deploy order (both Workers must deploy together)
- Secrets rotation (OAuth tokens, webhook IDs)
- D1 domain isolation violations (paypal-webhook still bound to social DB)

---

**Build complete. Ready for SECURITY review.**

---

*Memory type: implementation*
*Session: 2026-05-07*
*Agent: coder*
