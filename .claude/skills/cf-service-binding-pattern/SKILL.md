---
name: cf-service-binding-pattern
description: Constitutional pattern for cross-Worker calls in Cloudflare. Use Service Bindings (env.SERVICE.fetch) instead of HTTP+admin-token. Eliminates secrets in code, removes public exposure, simplifies auth. Apply ANY time one Worker needs to call another.
type: skill
domain: cloudflare-workers
contributed-by: aether (PureBrain)
date: 2026-05-07
source: workers/paypal-webhook → referrals-api integration (CTO Edit #5)
status: provisional
tick_count: 0
last_used: 2026-05-08
introduced: 2026-05-08
---

# Cloudflare Service Binding Pattern

**Status**: CONSTITUTIONAL — declared by CTO as the v1+ standard for cross-Worker calls. HTTP+token is a v0 hack only.

---

## The Anti-Pattern (don't do this)

```javascript
// HTTP + admin token — fragile, leaky, public exposure
const response = await fetch("https://referrals-api.in0v8.workers.dev/internal/recalc", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${env.REFERRALS_ADMIN_TOKEN || "purebrain-admin-2026"}`, // SECRET IN CODE
    "Content-Type": "application/json",
  },
  body: JSON.stringify(data),
});
```

Problems:
- Hardcoded fallback token = grep target
- Public HTTPS endpoint = every call traverses public internet
- Token rotation = coordinated deploys across N callers
- Auth complexity grows quadratically with Worker count

---

## The Pattern

### Step 1: Declare the binding in `wrangler.toml` of the **caller**

```toml
[[services]]
binding = "REFERRALS_API"     # name used in env.REFERRALS_API
service = "referrals-api"     # name of the deployed Worker
environment = "production"    # optional: pin to specific env
```

### Step 2: Call via `env.<BINDING>.fetch(request)`

```javascript
const request = new Request("https://referrals-api/internal/recalc", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data),
});
const response = await env.REFERRALS_API.fetch(request);
```

**Note**: The hostname `referrals-api` in the URL is a placeholder — CF routing ignores it when the binding is in use. Path + method + body matter; host does not.

### Step 3: Callee accepts requests as if HTTP

The receiving Worker doesn't need any code changes — it sees a normal `fetch` request. Add a path guard to mark internal endpoints:

```javascript
// referrals-api/src/worker.js
if (url.pathname.startsWith("/internal/")) {
  // Service Bindings ONLY — refuse if reached via public HTTPS
  // (CF doesn't expose Service Binding-only paths publicly when configured correctly,
  //  but defense-in-depth: check Cf-Connecting-IP or a shared header)
}
```

---

## Why It's Constitutional

| Concern | HTTP + token | Service Binding |
|---------|--------------|-----------------|
| Secrets in code | Yes (fallback tokens) | No |
| Public exposure | Yes (full HTTPS endpoint) | No (CF-internal routing) |
| Token rotation | Coordinated deploys | N/A |
| Latency | ~30-80ms (TLS + handshake) | ~1-5ms (in-CF call) |
| Failure mode | Network errors | Worker errors |
| Auth complexity | Per-caller | Zero |

---

## Deploy Order Gotcha

**Both Workers must exist when you deploy the caller.** First-time setup:

1. Deploy callee (referrals-api) WITHOUT any Service Binding referencing it
2. Deploy caller (paypal-webhook) with the `[[services]]` block
3. Subsequent updates can deploy in either order

Bootstrapping a brand-new pair? Deploy callee first, then caller.

---

## Graceful Degradation

If the bound service is down or returns an error, decide based on call semantics:

```javascript
try {
  const response = await env.REFERRALS_API.fetch(request);
  if (!response.ok) {
    console.warn("referrals-api returned", response.status);
    // For idempotent recalc: log + continue (caller succeeds)
    // For required lookup: return 502 to upstream caller
  }
} catch (err) {
  console.error("Service Binding call failed:", err);
  // Webhooks: return 200 to provider (so they don't retry forever)
  // User-facing: return 503 with retry hint
}
```

For PayPal/Stripe webhooks specifically: ALWAYS return 200 to the provider even if downstream Service Binding fails. Otherwise the provider retries infinitely.

---

## Contract-First Development

When two Workers will be Service-Bound, write the contract FIRST as a markdown spec:

```markdown
## POST /internal/complete-by-email

Request:
{ "customer_email": "...", "subscription_id": "...", "payment_amount": 149.00 }

Response (200):
{ "referral_id": 123, "commission_amount": 22.35 }

Response (404):
{ "error": "no_referral", "customer_email": "..." }
```

Both teams build against the contract in parallel. No blocking handoffs.

---

## When NOT to Use Service Bindings

- **Cross-account calls** — Service Bindings are per-account only
- **External API calls** (Stripe, PayPal, OpenAI) — these need real HTTPS
- **Public-facing endpoints** — anything a browser hits directly
- **One-off scripts / manual queries** — overkill

---

## Related Skills / Patterns

- Webhook signature verification (PayPal, Stripe) — separate concern, layered on top
- Idempotency keys (transmission_id, payment_id) — required for webhooks regardless of binding type
- D1 domain isolation — Service Bindings let you preserve isolation while still allowing controlled cross-domain calls

---

## Source

Built and validated 2026-05-07 in PureBrain's `paypal-webhook` → `referrals-api` integration. Replaced an admin-token HTTP call. CTO Edit #5 declared this the standard for v1+.

Files of reference:
- `workers/paypal-webhook/wrangler.toml` (caller binding)
- `workers/paypal-webhook/src/worker.js` (call site)
