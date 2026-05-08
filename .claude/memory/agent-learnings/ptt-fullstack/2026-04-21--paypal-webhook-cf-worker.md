# PayPal Webhook Cloudflare Worker

**Date**: 2026-04-21
**Type**: operational
**Topic**: CF Worker to receive PayPal webhooks and sync clients to D1

## What Was Built

`workers/paypal-webhook/` — standalone CF Worker that:
- Receives 5 PayPal subscription/payment webhook events
- Upserts/updates the `clients` table in `purebrain-social` D1
- Deduplicates via `paypal_webhook_log` table (transmission ID)
- Returns 200 to PayPal on ALL cases (prevents retries)

## Key Files
- `workers/paypal-webhook/src/worker.js` (438 lines)
- `workers/paypal-webhook/wrangler.toml` (D1 binding: `625dde70-0a60-45e7-bf81-e18e5ac4d854`)

## Events Handled
1. `BILLING.SUBSCRIPTION.ACTIVATED` — upsert client (INSERT ON CONFLICT UPDATE)
2. `BILLING.SUBSCRIPTION.CANCELLED` — set status/payment_status to cancelled
3. `BILLING.SUBSCRIPTION.SUSPENDED` — set payment_status to suspended
4. `BILLING.SUBSCRIPTION.RE-ACTIVATED` — set both back to active
5. `PAYMENT.SALE.COMPLETED` — increment total_paid, update last_active_at

## Plan-to-Tier Mapping
- "insider" or $74.50 -> Insiders
- "awakened"/"purebrain ai" or $149 -> Awakened
- $499 -> Partnered
- $999 -> Unified

## Idempotency Design
- In-memory Set (per isolate, max 500) for fast dedup
- D1 `paypal_webhook_log` table (auto-created) for durable dedup
- Optimistic lock: write 'processing' BEFORE handling, then 'processed' after
- INSERT OR IGNORE prevents race conditions on concurrent retries

## Integration Note
Needs a route added to portal proxy: `POST /paypal/webhook` -> this worker.
Existing PayPal webhook URL: `https://portal.purebrain.ai/paypal/webhook`
WEBHOOK_SECRET should be set via `wrangler secret put WEBHOOK_SECRET`.

## Gotchas
- PayPal header casing varies: checked both `paypal-transmission-id` and `PAYPAL-TRANSMISSION-ID`
- PAYMENT.SALE.COMPLETED uses `billing_agreement_id` not `id` for subscription lookup
- Always return 200 even on errors — PayPal retries aggressively on non-200
- `CREATE TABLE IF NOT EXISTS` for webhook log runs on first event — no migration needed
