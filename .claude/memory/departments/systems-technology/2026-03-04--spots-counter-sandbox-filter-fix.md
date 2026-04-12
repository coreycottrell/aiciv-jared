# Spots Counter Sandbox Filter Fix

**Date**: 2026-03-04
**Agent**: dept-systems-technology
**Type**: bug-fix + data-correction
**Files Changed**:
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`
- `/home/jared/projects/AI-CIV/aether/logs/spots_state.json`

---

## Problem

The `/api/spots-status` endpoint was returning 19 instead of the correct 6.

Root cause: `/api/verify-payment` incremented spots_claimed for ALL payment events including:
- Sandbox test orders (`SANDBOX-TEST-*`)
- E2E automation orders (`E2E-*`)
- Manual test orders (`test-*`)
- PayPal subscription/billing agreement IDs (`I-*`)

All 19 entries in the payments log had `amount: "0.00"` and `client_ip: "127.0.0.1"` — none were real captured PayPal transactions.

## Fix Applied

### Code Fix (purebrain_log_server.py, ~line 662)

Added sandbox/test order filter before spots increment:

```python
order_id = data.get('orderId', '')
sandbox_prefixes = ('SANDBOX-TEST', 'E2E-', 'test-', 'I-')
is_sandbox_or_test = any(order_id.startswith(prefix) for prefix in sandbox_prefixes)
if is_sandbox_or_test:
    logger.info(f'Spots counter NOT incremented — sandbox/test order filtered out: {order_id}')
else:
    # ... increment logic
```

### Data Fix (spots_state.json)

Reset `spots_claimed` from 19 to 6 (per Jared's instruction).
Kept 3 manually-entered real customer records. Added 3 placeholder entries for the 3 unlogged real customers.

## Verification

- Sandbox order `SANDBOX-TEST-filter-test` → counter stayed at 6
- Subscription ID `I-SUBSCRIPTION123` → counter stayed at 6
- Real-format order `VERIFY-LOGIC-TEST-REAL-FORMAT` → counter incremented to 7 (then reset to 6)
- Live API: `https://api.purebrain.ai/api/spots-status` returns `{"spots_claimed":6,"spots_total":25}`

## Key Learnings

1. The `verify-payment` endpoint logs ALL payment attempts (correct) but should NOT increment the spots counter for sandbox/test orders.
2. PayPal sandbox order IDs have identifiable prefixes. Real PayPal one-time payment order IDs are uppercase alphanumeric (e.g., `4MA83119W1272721N`).
3. The `aether-logserver.service` systemd unit auto-restarts on kill — always use `systemctl restart` or just kill and it comes back with new code.
4. All entries in payments.jsonl showed `amount: "0.00"` — the payment verification endpoint does NOT currently verify actual amount with PayPal API. This is a future security improvement to consider.

## Future Improvement

Consider adding PayPal API verification — call PayPal's Orders API to confirm the order exists, is COMPLETED status, and has the expected amount. This would prevent any false increments even if someone sends a real-format fake order ID.
