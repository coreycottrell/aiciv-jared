# Page 688 Latency Diagnosis
**Date**: 2026-02-28
**Page**: purebrain.ai/pay-test-sandbox-2 (WP ID 688)
**Type**: READ-ONLY investigation — no changes made

---

## ROOT CAUSE SUMMARY

Both performance regressions trace to a single upstream failure: **api.purebrain.ai (log server) is down**.

The server returns a 502 error after a **10-second timeout** on every request. This single failure cascades into both symptoms because the log server sits in the critical path for:
1. The PayPal verification call (which must complete before the post-payment chatbox opens)
2. Multiple `await logPayTestData(...)` calls inside the post-payment chat flow (which each await the failed server)

---

## ISSUE 1: PayPal Confirmation Box Stays on Screen Too Long

### Confirmed Root Cause

The PayPal success flow calls `verifyPaymentServerSide()` which does a blocking `fetch` to `https://api.purebrain.ai:8443/api/verify-payment`. That server is returning 502 after ~10 seconds. The `.catch()` handler does eventually call `handlePaymentSuccess()`, but only after the 10-second timeout fires.

### Exact Code Chain

**Step 1** — PayPal SDK `onApprove` fires (one-time payment path):
```javascript
// page content line ~7580
onApprove: function (data, actions) {
  return actions.order.capture().then(function (details) {
    var payerInfo = details.payer || {};
    verifyPaymentServerSide(tier, data.orderID, payerInfo);  // <-- blocking call
  });
},
```

**Step 2** — `verifyPaymentServerSide()` does a fetch with no timeout set:
```javascript
// page content line 7833
fetch(VERIFY_ENDPOINT, {        // VERIFY_ENDPOINT = 'https://api.purebrain.ai:8443/api/verify-payment'
  method:  'POST',
  headers: { 'Content-Type': 'application/json' },
  body:    payload,
})
  .then(function (response) {
    return response.json().then(function (data) {
      // ...
      handlePaymentSuccess(tier, orderId, payerInfo);  // only fires here, after server responds
    });
  })
  .catch(function (err) {
    // network/CORS error fallback
    handlePaymentSuccess(tier, orderId, payerInfo);    // or here, after timeout
  });
```
**Key**: No `AbortController` / no timeout on this fetch. Browser default TCP timeout applies — which is 10+ seconds when the server returns 502.

**Step 3** — `handlePaymentSuccess()` runs after the 10s delay (line 8122). Then adds MORE delays:
```javascript
// line 8136 — shows success banner
setTimeout(function () {
  banner.classList.remove('pb-visible');
}, 6000);  // auto-hides after 6 seconds (not blocking)

// line 8151 — fires onPaymentComplete callback
if (typeof window.onPaymentComplete === 'function') {
  window.onPaymentComplete(tier, orderId, payerInfo);
}

// line 8176 — scroll to #awakening
setTimeout(function () {
  window.location.hash = 'awakening';
  // ...
}, 800);  // 800ms delay
```

**Step 4** — `window.onPaymentComplete` (line 10712) adds another intentional delay:
```javascript
// line 10723
// Wait a beat, then launch the post-payment flow
setTimeout(function() {
  launchPostPaymentFlow(tier);
}, 1500);  // 1500ms intentional delay
```

### Total Delay Before Chatbox Appears

| Cause | Delay |
|-------|-------|
| `fetch(VERIFY_ENDPOINT)` — server 502 timeout | ~10,000ms |
| `setTimeout` in `handlePaymentSuccess` (scroll) | 800ms |
| `setTimeout` in `onPaymentComplete` (launch) | 1,500ms |
| **TOTAL** | **~12,300ms** |

**Previously** (when log server was working): verification call returned in ~200ms, total was ~2,500ms — felt instant.

---

## ISSUE 2: Post-Payment Chatbox is Extremely Slow (15+ seconds before thinking dots)

### Confirmed Root Cause

The `initPayTestFlow` function is `async` and uses `await logPayTestData(...)` in multiple places. `logPayTestData` itself uses `await Promise.allSettled([...])` to POST to `api.purebrain.ai`. Since that server is down and returning 502 after ~10 seconds, EACH `await logPayTestData(...)` call blocks the UI for ~10 seconds.

The very first call happens at the top of `initPayTestFlow`, before any UI is shown:

```javascript
// line ~427772 (inside initPayTestFlow)
if (window._pbPrePurchaseSession && window._pbPrePurchaseSession.conversationHistory.length > 0) {
  await logPayTestData({           // <-- BLOCKS HERE ~10 seconds
    ...payTestData,
    event: 'flow:start:pre-purchase-history',
    ...
  });
}
```

Then `runQuestionnaire` is called, which triggers more `await logPayTestData(...)` calls in sequence (one after each question answer).

**logPayTestData uses `await Promise.allSettled`** (line 8513):
```javascript
await Promise.allSettled([
  fetch('https://api.purebrain.ai/api/log-pay-test', { ... }).catch(...),
  fetch('https://api.purebrain.ai/api/log-conversation', { ... }).catch(...),
]);
```
This is `await`-ed, which means the caller blocks until BOTH fetches resolve — but since the server is returning 502 after 10 seconds, each `await logPayTestData()` takes ~10 seconds.

### Why Thinking Dots Don't Appear for 15+ Seconds

The chatbox UI (thinking dots) only renders after `initPayTestFlow` has progressed through its early `await logPayTestData` calls and started `runQuestionnaire`. The first `aiSay()` in the questionnaire is what shows the initial AI message + triggers visible activity. Each log call before that point blocks silently.

### Cloudflare Worker Timing (CONFIRMED FAST)

Direct test of the Cloudflare Worker returned in **1.63 seconds total, 1.63s TTFB** — this is normal and fast. The Worker itself is NOT the problem.

The `callClaude()` function (pre-purchase chatbox) correctly shows `showTyping()` before the fetch:
```javascript
// line 6411
showTyping();
const response = await callClaude(state.conversationHistory);
hideTyping();
```
This means the pre-purchase chatbox thinking dots work correctly. The post-payment chatbox (`initPayTestFlow`) blocks on logging before showing anything.

---

## SPECIFIC FIXES NEEDED

### Fix 1 — Add timeout to `verifyPaymentServerSide` fetch (Priority: CRITICAL)

**Location**: `verifyPaymentServerSide` function, around line 7833 of page content

**Current code**:
```javascript
fetch(VERIFY_ENDPOINT, {
  method:  'POST',
  headers: { 'Content-Type': 'application/json' },
  body:    payload,
})
```

**Fix**:
```javascript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 3000); // 3s max wait

fetch(VERIFY_ENDPOINT, {
  method:  'POST',
  headers: { 'Content-Type': 'application/json' },
  body:    payload,
  signal:  controller.signal,
})
  .then(function (response) {
    clearTimeout(timeoutId);
    return response.json().then(function (data) {
      // ... existing logic
      handlePaymentSuccess(tier, orderId, payerInfo);
    });
  })
  .catch(function (err) {
    clearTimeout(timeoutId);
    console.warn('[PB PayPal] Verification failed/timed out. Proceeding.', err.message);
    handlePaymentSuccess(tier, orderId, payerInfo);
  });
```

This caps the wait at 3 seconds instead of 10.

### Fix 2 — Make `logPayTestData` fire-and-forget, not blocking (Priority: CRITICAL)

**Location**: `logPayTestData` function, line 8513, and all `await logPayTestData(...)` call sites

**Current code** (logPayTestData):
```javascript
async function logPayTestData(data) {
  // ...
  await Promise.allSettled([   // <-- BLOCKS caller
    fetch('https://api.purebrain.ai/api/log-pay-test', ...),
    fetch('https://api.purebrain.ai/api/log-conversation', ...),
  ]);
}
```

**Fix** — Remove `async` and remove `await`:
```javascript
function logPayTestData(data) {  // Remove async
  // ...
  Promise.allSettled([           // Remove await — fire and forget
    fetch('https://api.purebrain.ai/api/log-pay-test', ...),
    fetch('https://api.purebrain.ai/api/log-conversation', ...),
  ]);
  // No return, no await — just fire
}
```

Then update ALL `await logPayTestData(...)` call sites to just `logPayTestData(...)` (remove `await`).

There are 15+ call sites throughout `initPayTestFlow`. All should have `await` removed.

### Fix 3 — Add timeout to logPayTestData fetches (Priority: HIGH)

Even after making it fire-and-forget, add a timeout so it doesn't hold open network connections:

```javascript
function logPayTestData(data) {
  const controller = new AbortController();
  setTimeout(() => controller.abort(), 4000); // 4s max, fire-and-forget

  Promise.allSettled([
    fetch('https://api.purebrain.ai/api/log-pay-test', {
      ...
      signal: controller.signal,
    }).catch((err) => console.warn('[pay-test] log-pay-test failed:', err.message)),
    fetch('https://api.purebrain.ai/api/log-conversation', {
      ...
      signal: controller.signal,
    }).catch((err) => console.warn('[pay-test] log-conversation failed:', err.message)),
  ]);
}
```

### Fix 4 — Restore log server (Priority: HIGH, separate track)

`api.purebrain.ai` / `localhost:8443` is returning 502 and timing out at ~10 seconds. Need to:
1. SSH into the server and check if `purebrain_log_server.py` is running
2. Check systemd service status
3. Restart if dead: `systemctl restart aether-log-server` or equivalent

This is the underlying cause of everything. Fixes 1-3 make the client resilient against the failure. Fix 4 actually fixes the server.

---

## NO CHANGES MADE

This is a read-only diagnosis. All findings above are from code analysis and direct API testing only.
