# Spots Counter Fix: PayPal Subscription IDs Were Blocked

**Date**: 2026-03-13
**Type**: bug-fix | root-cause | pattern
**Impact**: Real customer payments not incrementing invitation page counter

---

## Root Cause

All real payment pages (pay-test-awakened, pay-test-partnered, pay-test-unified, pay-test-2)
use **PayPal subscription billing** (PLAN_IDS configured with `P-*` plan IDs).

When a customer subscribes, PayPal's `onApprove` callback returns `data.subscriptionID`
which has the format `I-XXXXXXXXXXXXXXXXX`.

The server sandbox filter included `I-` as a blocked prefix (it was assumed to be test
billing agreements). This blocked ALL real subscription payments from incrementing the
spots counter.

## Fixes Applied

### 1. purebrain_log_server.py — verify-payment endpoint
- Removed `I-` from sandbox prefix filter
- Added `isSandbox` flag check (for sandbox-3 page to send explicitly)
- Added order_id dedup check (same order can't increment counter twice)
- Moved `order_id = data.get('orderId', '')` before the Telegram notification block
  (it was mistakenly placed AFTER the block that referenced it, causing UnboundLocalError)

### 2. exports/cf-pages-deploy/pay-test-sandbox-3/index.html
- Added `isSandbox: true` to the `verifyPaymentServerSide()` payload
- This tells the server explicitly not to increment the counter for sandbox payments

### 3. logs/spots_state.json
- Backfilled 4 missed I-* payments from 2026-03-13
- Removed 3 manual placeholder entries that were double-counting those same customers
- Final counter: 15 (was 14 before fix)

## Test Results
- Real I-* order: counter increments (PASS)
- Same I-* order submitted twice: dedup blocks second increment (PASS)
- isSandbox:true order: counter NOT incremented (PASS)
- SANDBOX-TEST* prefix: counter NOT incremented (PASS)

## Key Lesson
PayPal subscription IDs start with `I-`. Never filter this prefix on a platform
that uses subscription billing. Use an explicit `isSandbox` flag in the payload
instead of trying to infer from the order ID format.

## Files Changed
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` (line ~1180-1260)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pay-test-sandbox-3/index.html` (line ~14092)
- `/home/jared/projects/AI-CIV/aether/logs/spots_state.json`
