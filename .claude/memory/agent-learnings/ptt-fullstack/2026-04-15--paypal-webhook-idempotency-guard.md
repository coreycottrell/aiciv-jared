# PayPal Webhook Idempotency Guard

**Date**: 2026-04-15
**Type**: teaching
**Topic**: Prevent duplicate tracker rows from PayPal webhook retries

## Problem
PayPal retries the SAME webhook (same `PAYPAL-TRANSMISSION-ID`) when our
response is slow or flagged. Original `handle_webhook` in
`tools/paypal_auto_split.py` had NO dedup — produced 4 rows for 2 real
payments today.

## Solution
File-based dedup at `logs/paypal_webhook_processed.jsonl`:

- **Helpers** added at module level (around lines 92-181):
  `_processed_webhook_ids()`, `_append_processed_webhook()`,
  `_is_duplicate_transmission()`. All fail-open.
- **Guard** injected at top of `handle_webhook` (lines ~860-888):
  Read `PAYPAL-TRANSMISSION-ID` header, check log, short-circuit with
  `200 duplicate_skipped` if seen. Optimistic lock via 'processing'
  entry written BEFORE work, terminal entry after.
- **10MB rotation** to `.jsonl.1`.
- **Returns 200 on duplicates** so PayPal stops retrying.

## Key Design Choice
Write 'processing' entry BEFORE calling `add_payment()`. Any concurrent
retry in-flight sees the tid in the log and skips. Same tid appearing
twice in the log is harmless (set membership check).

## Deploy
- Backup: `tools/paypal_auto_split.py.bak-2026-04-15-idempotency`
- Killed PID 3238420, respawned with `setsid nohup`, new PID 11875 (actual
  worker child 11900 bound to :8960)
- Health endpoint returns `{"status":"ok"}` on `GET /paypal/webhook`

## Test
Flask test_client: 2 calls with same transmission_id → first `recorded`,
second `duplicate_skipped`. Third call with different tid → `recorded`.
Passed.

## Gotcha
Flask normalizes headers; checked both uppercase and title-case variants
plus lowercase for belt-and-suspenders.
