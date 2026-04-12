# PayPal Subscription Sync — 3 Client Manual Corrections

**Date**: 2026-03-19
**Type**: operational
**Agent**: dept-systems-technology

---

## Task

Jared flagged 3 clients whose payment records were wrong in clients.db. Required PayPal Live API sweep and database corrections.

## PayPal API Key Learnings

### What Works

- GET /v1/billing/subscriptions/{sub_id} - Direct lookup by subscription ID is accurate and reliable. Use this when you have a sub ID.
- Live credentials: PAYPAL_CLIENT_ID + PAYPAL_SECRET in .env
- Base URL: https://api-m.paypal.com
- Token endpoint: POST /v1/oauth2/token with Basic auth (base64 client_id:secret)

### What Does NOT Work

- GET /v1/billing/subscriptions?plan_id={plan_id} - plan_id filter is IGNORED. Returns paginated list of ALL subs.
- GET /v1/billing/subscriptions?subscriber_email={email} - also IGNORED. Same list for every email.
- GET /v1/reporting/transactions - Returns 403 Forbidden (scope not granted on this account).
- Rate limit: Rapid pagination hits 429. Add 1-2s sleeps between calls.

### Reliable Search Strategy

When you need to find a subscription for a specific customer:
1. Check clients.db for paypal_subscription_id - direct lookup is fast and accurate
2. Check logs/spots_state.json claimed_orders for I- prefixed order IDs
3. Check logs/portal_server.log for subscription activity
4. Direct lookup all I- IDs from logs using /v1/billing/subscriptions/{id}
5. The list API cannot be reliably used for email/plan filtering

## Plan ID Reference

- P-2SA65600MT088594TNGLTFKY = $149/mo "Awakened" plan
- P-8AU4270420374002JNGY3VYQ = $74.50/mo "Insiders" plan

Note: paypal_sync_subscriptions.py maps these wrong - it calls $149 "Bonded" and $74.50 "Awakened". Actual tier names: $149=Awakened, $74.50=Insiders.

## Outcome

- Hannah Khokhar: DB updated to Insiders/$74.50. No PayPal sub ID found yet.
- Carolina Gerding: Already correct (subscription_cancelled). Notes added.
- Tess Verneuil: DB updated to Insiders/$74.50. Old I-N2DV819PXT4Y still ACTIVE in PayPal at $149 - Jared needs to cancel it.

## Database Location

/home/jared/purebrain_portal/clients.db

## Portal Restart

sudo systemctl restart aether-portal.service
