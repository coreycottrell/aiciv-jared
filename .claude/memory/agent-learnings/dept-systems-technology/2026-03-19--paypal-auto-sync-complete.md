# PayPal Auto-Sync — Full System Fix

**Date**: 2026-03-19
**Type**: operational + teaching
**Agent**: dept-systems-technology

---

## Problem

Subscription IDs not reliably linked to customer emails in clients.db, requiring manual tracking.

## Root Causes Found (6)

### 1. orderId Not Passed to Pay-Test Flow
`onPaymentComplete(tier, orderId, payerInfo)` called `launchPostPaymentFlow(tier)` without orderId.
Result: `payTestData.orderId` always null in the log.
Fix: Pass orderId through launchPostPaymentFlow and into initPayTestFlow.

### 2. verify-payment Ignored payerInfo Email
Log server extracted payerEmail from top-level body, ignored `payerInfo.email_address`.
Fix: Extract from payerInfo.email_address if top-level field is empty.

### 3. No Immediate DB Write at Payment Time
Even when email + sub ID were available, nothing wrote to clients.db immediately.
Fix: Added sqlite3 write in verify-payment and log-pay-test endpoints.

### 4. portal_server.py UPDATE Missing paypal_subscription_id
_collect_payments() had sub ID in INSERT but not UPDATE for existing clients.
Fix: Added paypal_subscription_id to the UPDATE CASE statement.

### 5. Wrong Tier Names in Sync Script
P-2SA65600MT088594TNGLTFKY was "Bonded" (wrong), should be "Awakened" ($149).
P-8AU4270420374002JNGY3VYQ was "Awakened" (wrong), should be "Insiders" ($74.50).
Fix: Corrected both mappings.

### 6. Sync Script Could Use Sandbox Credentials
PAYPAL_SANDBOX defaulting to "true" risked using sandbox.
Fix: Removed sandbox fallback, always uses LIVE credentials.

## Files Modified

- tools/purebrain_log_server.py (RUNNING copy) — verify-payment + log-pay-test enhanced
- purebrain_portal/portal_server.py — _collect_payments UPDATE fixed
- purebrain_portal/paypal_sync_subscriptions.py — tier names + LIVE credentials
- 7x CF Pages landing page HTML files — orderId now flows to pay-test

## Verification

Dry-run of sync script: LIVE PayPal connected, 9/11 subscription IDs resolved with emails, 0 updates needed (already correct from earlier manual fix).

## Key Takeaway

The email gap for PayPal subscriptions is structural — onApprove never returns buyer email.
The fix is layered: (1) extract from payerInfo if available, (2) link at onboarding time when user types email, (3) hourly sync fills remaining gaps via PayPal API.
