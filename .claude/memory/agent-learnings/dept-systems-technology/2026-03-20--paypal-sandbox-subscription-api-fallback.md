# PayPal Sandbox Subscription API Fallback Pattern

**Date**: 2026-03-20
**Type**: teaching
**Agent**: dept-systems-technology
**File**: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`

## Problem

Sandbox subscriptions (pay-test-sandbox-3) produce I-* subscription IDs but the PayPal SDK onApprove callback for subscription flows only returns the subscriptionID. It does NOT include payerEmail, payerName, or amount. The previous code used an isSandbox flag to pick the API — but the verify-payment endpoint does NOT receive that flag from the frontend. Result: blank email/name and $0.00 amount in the log.

## Root Cause

The verifyPaymentServerSide() function on the page sends only { orderId, tier, payerInfo }. The payerInfo for subscription flows is the raw SDK data object (contains subscriptionID, facilitatorAccessToken — NOT email/name). No isSandbox flag reaches /api/verify-payment.

## Fix Applied

Replaced the single-API lookup with a three-step strategy:

1. Try LIVE API (https://api-m.paypal.com) with PAYPAL_CLIENT_ID / PAYPAL_SECRET
2. If live fails (any error/404), try SANDBOX API (https://api-m.sandbox.paypal.com) with PAYPAL_SANDBOX_CLIENT_ID / PAYPAL_SANDBOX_SECRET — both exist in .env
3. If both fail, fall back to page-supplied data: map tier to known price via _TIER_PRICES dict; mark email/name as (sandbox-sub) for identifiability

Used nested function pattern (_fetch_paypal_subscription, _apply_sub_data) with nonlocal for clean variable mutation inside the closure.

## Also Fixed

Sandbox seed notification text updated from "THIS IS A SEED TEST" to "THIS IS A SEED TEST FROM JARED OR PURE TECHNOLOGY" at line 1453.

## Key .env Variables

- PAYPAL_CLIENT_ID / PAYPAL_SECRET — live credentials
- PAYPAL_SANDBOX_CLIENT_ID / PAYPAL_SANDBOX_SECRET — sandbox credentials

## Tier Price Fallback Table

awakened: 149.00, bonded: 299.00, partnered: 499.00, unified: 999.00

## Lessons

- PayPal subscription onApprove does NOT give you payer data — always plan to call the API
- The isSandbox flag is set in send-seed payload but NOT in verify-payment payload — never assume it propagates
- When both APIs fail, a tier-based price fallback beats $0.00 in the log every time
- Mark fallback records clearly (sandbox-sub) so they are identifiable in the log vs truly missing data
