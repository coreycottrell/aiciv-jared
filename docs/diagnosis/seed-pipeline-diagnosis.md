# Seed Pipeline Diagnosis: pay-test-2 → Witness/AICIV

**Date**: 2026-02-27
**Agent**: full-stack-developer
**Scope**: Three trigger points — payment seed, OAuth seed, final seed

---

## Executive Summary

**The birth pipeline is broken due to Witness server downtime.** The Witness server at `104.248.239.98:8099` has been unreachable since 2026-02-25 23:49 UTC (last successful `birth:start:url_ready`). All attempts since 2026-02-26 return `birth:start:failed`. This is the root cause of seed data NOT reaching Witness/AICIV.

Additionally, there is a **separate structural bug**: the PayPal `orderId` is never passed to `initPayTestFlow`, meaning `payTestData.orderId` is always `null` even when a real payment occurs.

---

## Infrastructure Health Check

| Component | Status | Details |
|-----------|--------|---------|
| Log server (89.167.19.20:8443) | **RUNNING** | `{"status":"ok"}` confirmed |
| `/api/health` endpoint | **OK** | Returns 200 |
| `/api/log-conversation` | **WORKING** | Receiving entries |
| `/api/log-pay-test` | **WORKING** | Receiving entries |
| `/api/birth/start` proxy | **FAILING** | Returns 504 — upstream Witness unreachable |
| Witness server (104.248.239.98:8099) | **DOWN** | Connection refused on all tests |
| Last successful `birth:start:url_ready` | **2026-02-25 23:49 UTC** | ~42 hours ago |

---

## Trigger Point 1: Payment Completion (Post-Payment Seed)

### What SHOULD happen

1. User clicks PayPal button → PayPal SDK fires `onApprove`
2. `onApprove` calls `verifyPaymentServerSide(tier, orderId, payerInfo)`
3. `verifyPaymentServerSide` POSTs to `https://api.purebrain.ai/api/verify-payment` with `{orderId, tier, payerInfo}`
4. On success → calls `handlePaymentSuccess(tier, orderId, payerInfo)`
5. `handlePaymentSuccess` sets `window.paymentOrderId = orderId` and calls `window.onPaymentComplete(tier, orderId, payerInfo)`
6. `onPaymentComplete` (integration glue) snapshots pre-purchase chat history and calls `launchPostPaymentFlow(tier)`
7. `launchPostPaymentFlow` calls `window.initPayTestFlow(chatContainer, aiName, tier)` — **NOTE: orderId is NOT passed here**
8. `initPayTestFlow` receives `orderId = undefined`, sets `payTestData.orderId = null`

### What IS happening

- The PayPal payment flow works correctly up through `handlePaymentSuccess`
- `window.paymentOrderId` is set correctly on the window object
- **Bug: `launchPostPaymentFlow` calls `initPayTestFlow(chatContainer, aiName, tier)` — orderId argument is missing**
- `initPayTestFlow` signature is `(chatContainer, aiName, tierPaid, orderId)` — 4th param is orderId
- Result: `payTestData.orderId = null` for ALL post-payment logging

### Data flowing at Trigger 1

The log server DOES receive data at this trigger point via `logPayTestData()`:
- Event: `questionnaire:name`, `questionnaire:email`, `questionnaire:company`, `questionnaire:role`
- These fire to `/api/log-pay-test` AND `/api/log-conversation`
- Both reach the log server successfully
- The data is logged and forwarded to A-C-Gee/hub

**BUT**: `orderId` is `null` in ALL these payloads. The payment order ID is never linked to the user data.

---

## Trigger Point 2: OAuth via Chatbox (Birth Init Seed to Witness)

### What SHOULD happen

After Q4 (role), `runQuestionnaire` calls `runBirthInit(dom, aiName, firstName)` automatically (v4.5 change: auto-fire).

`runBirthInit` sends the seed to Witness via:
```javascript
fetch(`${WITNESS_WEBHOOK_HOST}/api/birth/start`, {
  method: 'POST',
  body: JSON.stringify({
    name: payTestData.name,
    email: payTestData.email,
    human_name: payTestData.name,
    tier: payTestData.tierPaid || 'awakened',
  })
})
```

`WITNESS_WEBHOOK_HOST` = `https://89.167.19.20:8443` (our proxy)

This proxies to `http://104.248.239.98:8099/api/birth/start`.

Witness is expected to return:
```json
{"status": "url_ready", "oauth_url": "https://claude.ai/...", "container": "aiciv-XX"}
```

The seed data (name, email, tier) travels WITH the `/birth/start` call — this IS the seed arriving at Witness.

### What IS happening

**Witness server is DOWN.** Every attempt since 2026-02-26 returns:
```
{"error": "Birth service timeout", "details": "Upstream did not respond in time"}
```

The v4.7 retry logic fires 3 attempts at 45s timeout each (was 180s, reduced to 45s):
- Attempt 1 → `birth:start:failed` logged to `/api/log-conversation`
- Attempt 2 → `birth:start:failed` logged
- Attempt 3 → `birth:start:failed` logged
- Then shows error message with retry button to user

**All 3 Trigger 2 fires today (2026-02-27) have failed.**

The seed data DOES reach the log server (we see `birth:init:start` events logged) but NEVER reaches Witness because the proxy returns 504.

---

## Trigger Point 3: End of Post-Payment Chat (Final Seed)

### What SHOULD happen

After OAuth completes (`birth:authenticated`), the flow continues through:
- Phase 2: Behind the Curtain
- Phase 3: Primary Goal question
- Phase 4: Telegram question
- Phase 5: Thank You + Portal button

At the end of Phase 5, `logPayTestData({ ...payTestData, event: 'flow:complete', flowCompleted: true })` fires.

This sends the FULL accumulated data (name, email, company, role, primary goal, AI name, tier, containerName) to:
1. `/api/log-pay-test` — triggers Brevo email sequence if `flowCompleted: true` and email is present
2. `/api/log-conversation` — triggers A-C-Gee forwarding + hub forwarding

### What IS happening

**Trigger 3 is never reached.** Because Trigger 2 fails (Witness is down), `runBirthInit` shows an error and the flow stalls. The user never progresses past the birth init phase.

**No `flow:complete` events have been seen in logs today.**

The pay-test log shows `flowCompleted: false` on all recent entries — the flow never finishes.

---

## Complete Data Flow Map

```
USER PAYS (PayPal onApprove)
    ↓
verifyPaymentServerSide()
    → POST https://api.purebrain.ai/api/verify-payment {orderId, tier}
    → Log server verifies with PayPal API (for page 826 tiers only — Bonded/Partnered tiers pass-through)
    → handlePaymentSuccess()
        → window.paymentOrderId = orderId  [stored but NOT passed forward — BUG]
        → window.onPaymentComplete(tier, orderId, payerInfo)
            ↓
INTEGRATION GLUE (onPaymentComplete)
    → Snapshots pre-purchase chat history to window._pbPrePurchaseSession
    → launchPostPaymentFlow(tier)  [orderId NOT passed — BUG]
        → initPayTestFlow(container, aiName, tier)  [orderId missing — BUG]
            → payTestData.orderId = null  [ALWAYS null — BUG]
            ↓
QUESTIONNAIRE (Q1→Q4)
    → Each answer fires logPayTestData() → POST /api/log-pay-test + /api/log-conversation
    → Data reaches log server, stored in purebrain_web_conversations.jsonl
    → Forwarded to A-C-Gee (http://5.161.90.32:3001/api/landing-chat)
    → Forwarded to hub via hub_cli.py
    → orderId is null in ALL these payloads [BUG]
            ↓
BIRTH INIT (runBirthInit — auto-fires after Q4)
    → logPayTestData({event: 'birth:init:start'}) — reaches log server ✓
    → POST https://89.167.19.20:8443/api/birth/start  [proxy to Witness]
        → FAILS: Witness 104.248.239.98:8099 is DOWN [CRITICAL BUG]
        → Returns 504 timeout
    → Retries 3x, each logs 'birth:start:failed' to log server
    → Retry button shown to user
    → Flow STALLS here
            ↓
OAUTH (never reached — Witness down)
    → Would: show OAuth button for claude.ai authorization
    → Would: wait for user to authorize
    → Would: POST /api/birth/code with code
    → Would: log birth:authenticated
            ↓
FLOW COMPLETION (never reached — birth init failed)
    → Would: log flow:complete, flowCompleted: true
    → Would: trigger Brevo welcome email sequence
    → Would: log full data with container name
```

---

## Bugs Identified

### BUG 1 (CRITICAL): Witness Server Down
**Severity**: P0 — entire birth pipeline blocked
**Location**: `http://104.248.239.98:8099`
**Symptom**: All `/api/birth/start` calls return 504 timeout since 2026-02-26
**Last working**: 2026-02-25 23:49 UTC
**Fix**: Witness team needs to restart the server. Once it's up, birth pipeline will auto-resume.

### BUG 2 (HIGH): orderId Never Passed to initPayTestFlow
**Severity**: P1 — payment order ID not linked to user data
**Location**: `pay-test-integration-glue.js` line 87
```javascript
// CURRENT (broken):
window.initPayTestFlow(chatContainer, aiName, tier);

// SHOULD BE:
var orderId = (window.payTestPaymentData && window.payTestPaymentData.orderId) || null;
window.initPayTestFlow(chatContainer, aiName, tier, orderId);
```
**Impact**: Every log entry has `orderId: null`. Cannot reconcile purchases with user sessions.
**Fix**: Pass `window.payTestPaymentData.orderId` as the 4th argument in `launchPostPaymentFlow`.

### BUG 3 (MEDIUM): No Direct Seed to Witness at Payment Time
**Severity**: P2 — architectural gap
**Current behavior**: The seed data (name, email, tier) is sent to Witness only when `runBirthInit` fires (after Q4 of questionnaire). There is no direct data push to Witness/AICIV at the moment of payment itself.
**What's missing**: A Trigger 1 webhook — immediately on payment, before the questionnaire, sending at minimum `{orderId, tier, timestamp}` to Witness.
**Fix**: Add a post-payment webhook call in `handlePaymentSuccess` or `onPaymentComplete` that fires immediately to `WITNESS_WEBHOOK_HOST/api/payment-notification` (Witness team would need to implement this endpoint).

### BUG 4 (LOW): verify-payment endpoint used for PureBrain tiers is wrong endpoint
**Severity**: P3 — wrong endpoint for PureBrain pay-test
**Current behavior**: The PayPal `VERIFY_ENDPOINT` in the PayPal script is `https://api.purebrain.ai/api/verify-payment`. This endpoint is designed for page 826 (ai-website-execution — Critical/Complete tiers at $197/$497). The PureBrain pay-test uses Bonded/Partnered/Awakened tiers — these don't match `TIER_AMOUNTS` in the server, so `amount_valid` is always `false`, and `verified` will be `false` for PureBrain purchases.
**Impact**: Server-side payment verification shows "not verified" for legitimate PureBrain payments.
**Fix**: Either extend `TIER_AMOUNTS` to include PureBrain tier amounts, or create a separate verification endpoint for PureBrain purchases.

---

## What IS Working

1. **Log server is healthy** — all endpoints responding, SSL valid
2. **Questionnaire data logging** — Q1-Q4 answers reach log server correctly
3. **A-C-Gee forwarding** — data is being forwarded to A-C-Gee shared DB
4. **Hub forwarding** — data reaches AICIV comms hub
5. **Brevo email infrastructure** — templates ready, would fire on `flow:complete`
6. **v4.7 retry logic** — correctly retries 3x and shows user feedback
7. **Pre-purchase chat history** — correctly snapshotted and included in post-payment payloads
8. **CORS configuration** — purebrain.ai origin accepted

---

## What Is NOT Working

1. **Witness server (104.248.239.98:8099)** — DOWN since 2026-02-26
2. **Birth init / OAuth** — blocked by Witness being down
3. **Container allocation** — never received, no container names in logs
4. **orderId propagation** — always null due to glue script bug
5. **flow:complete event** — never fires, so Brevo emails never send
6. **Portal polling** — never starts because birth init fails

---

## Recommended Fixes (Priority Order)

### Fix 1: Restart Witness Server (P0 — do immediately)
- Contact Witness team to restart `104.248.239.98:8099`
- Verify with: `curl http://104.248.239.98:8099/api/health`
- Once up, test full birth flow at pay-test-sandbox-2 with bypass button

### Fix 2: Pass orderId to initPayTestFlow (P1 — code fix)
In the live WordPress page (pay-test-2 HTML widget), in `launchPostPaymentFlow`:
```javascript
function launchPostPaymentFlow(tier) {
  // ... existing aiName logic ...
  var chatContainer = document.getElementById('pay-test-post-payment');
  // ... existing container creation ...

  if (typeof window.initPayTestFlow === 'function') {
    // FIX: pass orderId as 4th argument
    var orderId = (window.payTestPaymentData && window.payTestPaymentData.orderId) || null;
    window.initPayTestFlow(chatContainer, aiName, tier, orderId);
  }
}
```

### Fix 3: Add Immediate Payment Webhook (P2 — new feature)
In `handlePaymentSuccess`, before calling `onPaymentComplete`, fire an immediate notification:
```javascript
// Fire immediate payment notification to Witness
fetch(WITNESS_WEBHOOK_HOST + '/api/payment-notification', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({orderId, tier, timestamp: new Date().toISOString()})
}).catch(() => {}); // non-blocking, best-effort
```
NOTE: Witness team must implement the `/api/payment-notification` endpoint.

### Fix 4: Fix PureBrain Tier Verification (P3 — server fix)
In `purebrain_log_server.py`, extend `TIER_AMOUNTS`:
```python
TIER_AMOUNTS = {
    'critical': '197.00',
    'complete': '497.00',
    # PureBrain pay-test tiers:
    'awakened': '79.00',
    'bonded': '149.00',
    'partnered': '499.00',
    'unified': '999.00',
}
```

---

## Log Evidence

### birth:start:failed (today 2026-02-27 16:30-16:31 UTC)
```json
{
  "session_id": "pb-post-1772209858549",
  "metadata": {
    "event": "birth:start:failed",
    "orderId": null,
    "phase": "post-payment"
  },
  "aiName": "Keen",
  "userName": "js",
  "userTier": "Bonded"
}
```

### Last successful birth:start:url_ready (2026-02-25 23:49 UTC)
```json
{
  "session_id": "pb-post-1772063380485",
  "metadata": {
    "event": "birth:start:url_ready",
    "orderId": null,
    "phase": "post-payment"
  },
  "aiName": "Keen",
  "userName": "j s",
  "userTier": "Partnered"
}
```

Note: Even in the last successful case, `orderId` was null (Bug 2 predates Witness going down).

### pay_test_completion always has flowCompleted: false
```json
{
  "type": "pay_test_completion",
  "tier": "Bonded",
  "orderId": null,
  "aiName": "Keen",
  "name": "js",
  "email": "j@pt.com",
  "company": "pt",
  "role": "ceo",
  "flowCompleted": false
}
```

---

## Files Involved

| File | Role |
|------|------|
| `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` | Log server — all endpoints |
| `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js` | Post-payment chat flow v4.7 |
| `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-integration-glue.js` | Wires PayPal to chat flow |
| `/home/jared/projects/AI-CIV/aether/exports/extracted-script-9-paypal-integration.js` | PayPal onApprove handler |
| `/home/jared/projects/AI-CIV/aether/logs/purebrain_web_conversations.jsonl` | Conversation logs |
| `/home/jared/projects/AI-CIV/aether/logs/purebrain_pay_test.jsonl` | Pay-test completion logs |
| `/home/jared/projects/AI-CIV/aether/logs/purebrain_payments.jsonl` | Payment verification logs |

---

## Memory Written

Path: `.claude/memory/agent-learnings/full-stack-developer/2026-02-27--seed-pipeline-diagnosis-witness-down.md`
Type: operational
Topic: Birth pipeline failure diagnosis — Witness server down + orderId bug
