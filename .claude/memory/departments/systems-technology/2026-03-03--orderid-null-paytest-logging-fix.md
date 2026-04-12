# orderId=null Fix — pay_test.jsonl Logging

**Date**: 2026-03-03
**Type**: bug-fix
**Agent**: dept-systems-technology
**Pages Fixed**: 688 (pay-test-sandbox-2), 689 (pay-test-2)

---

## Root Cause

The integration glue script (`pay-test-integration-glue.js`) embedded in both pages had a
parameter propagation gap. The call chain was:

```
onPaymentComplete(tier, orderId, payerInfo)          <-- orderId received here
  -> launchPostPaymentFlow(tier)                     <-- orderId DROPPED here
       -> window.initPayTestFlow(chatContainer, aiName, tier)  <-- orderId never passed
            -> payTestData.orderId = orderId || null  <-- always null
                -> logPayTestData()                   <-- logs orderId: null
```

`orderId` was received correctly by `onPaymentComplete` (from PayPal SDK after
`verifyPaymentServerSide`) and stored in `window.payTestPaymentData.orderId`, but it was
never threaded through to `initPayTestFlow`.

## Fix Applied (4 changes per page)

1. **Function signature**: `function launchPostPaymentFlow(tier)` → `(tier, orderId)`
2. **onPaymentComplete setTimeout call**: `launchPostPaymentFlow(tier)` → `(tier, orderId)`
3. **initPayTestFlow call**: `window.initPayTestFlow(chatContainer, aiName, tier)` → `(tier, orderId)`
4. **URL return path**: `launchPostPaymentFlow(tier)` → `(tier, orderId)` (the `checkForPaymentReturn` function)

## Verification

All 4 fixes verified via read-back on both pages:
- `function launchPostPaymentFlow(tier, orderId)` — count 1 each
- `launchPostPaymentFlow(tier, orderId)` — count 3 each (3 call sites)
- `window.initPayTestFlow(chatContainer, aiName, tier, orderId)` — count 1 each
- Old bug string `launchPostPaymentFlow(tier);` — count 0 each

Elementor cache cleared after both deploys.

## Impact

- `pay_test.jsonl` entries will now have real `orderId` values (e.g. `1AB23456CD789012E`)
- `seed-watcher-filtered.sh` `orderId != null` check will now pass
- PayPal payment Telegram notifications will now fire correctly

## Related Files

- WP page 688: pay-test-sandbox-2 (sandbox PayPal, `AYTFob05DoSn...` client ID)
- WP page 689: pay-test-2 (production PayPal, real client ID)
- Log server: `tools/purebrain_log_server.py`
- Seed watcher: `tools/seed-watcher-filtered.sh`
- Log file: `logs/purebrain_pay_test.jsonl`

## Key Pattern

When chaining payment callbacks → flow launchers → flow initializers, ALL data from
the payment callback must be explicitly threaded through every intermediate function.
JavaScript function parameter lists are not implicitly inherited from outer scope when
crossing function boundaries.
