# Hannah Khokhar PayPal Subscription ID Capture

**Date**: 2026-03-19
**Type**: operational
**Topic**: PayPal subscription ID discovery and DB reconciliation

## Summary

Hannah Khokhar's paypal_subscription_id was empty in clients.db since her record was created 2026-03-03. Notes said "awaiting subscription to propagate." Found and captured it via full PayPal API scan.

## Verified Details (PayPal Live API)

| Field | Value |
|-------|-------|
| Subscription ID | I-X5X26YGNYY6G |
| Status | ACTIVE |
| Plan ID | P-6C122944BP930974LNGVP6PQ |
| Tier | Insiders ($74.50/mo) |
| Email | hannahkhokhar@hotmail.co.uk |
| Created | 2026-03-09T08:06:13Z |
| Last payment | $74.50 on 2026-03-09 |
| Next billing | 2026-04-09T10:00:00Z |

## What Was Fixed

1. clients.db: paypal_subscription_id set to I-X5X26YGNYY6G, notes updated
2. paypal_sync_subscriptions.py: PLAN_TIER_MAP now includes P-6C122944BP930974LNGVP6PQ -> Insiders
3. Portal restarted via systemctl restart aether-portal.service

## Key Discovery: PayPal Plan ID Filtering Is Broken

The PayPal subscription list API does NOT properly filter by plan_id. It returns legacy subscriptions (2019 era) regardless. The only reliable way to find new subscriptions:

1. Get all sub IDs from GET /v1/billing/subscriptions?plan_id=...
2. Fetch full detail for each via GET /v1/billing/subscriptions/{sub_id}
3. Filter by create_time containing "2026" or subscriber email

## New Plan ID Discovered

P-6C122944BP930974LNGVP6PQ = Insiders $74.50/mo. Different from original Insiders plan P-8AU4270420374002JNGY3VYQ. Both now in PLAN_TIER_MAP.

## Files Changed

- /home/jared/purebrain_portal/clients.db
- /home/jared/purebrain_portal/paypal_sync_subscriptions.py (PLAN_TIER_MAP, line ~39)
