# Customer Recovery: Failed Post-Payment Flow

**Date**: 2026-03-19
**Agent**: dept-systems-technology
**Type**: operational + teaching
**Topic**: Recovering a paying customer whose post-payment flow broke mid-session

---

## What Happened

Harrison Amit (HOVR, Canadian rideshare) paid $149/mo for the Awakened tier. The PayPal capture completed (0H160033H17201422) and the subscription was created (I-H6AC73U9HARH), but the page broke before the post-payment chatbox flow fired. No seed was sent to Witness, no container created, no magic link sent.

## Recovery Procedure (Repeatable)

### Step 1: Verify PayPal transaction
Get OAuth token with live credentials from .env (PAYPAL_CLIENT_ID / PAYPAL_SECRET).
Look up capture: GET /v2/payments/captures/{CAPTURE_ID}
Look up subscription for email/name: GET /v1/billing/subscriptions/{SUB_ID}

### Step 2: Find conversation in logs
grep/search purebrain_web_conversations.jsonl for customer name to get session_id.

### Step 3: Check clients.db
PayPal auto-sync (hourly) may have already added them. Check by email or subscription ID.
File: /home/jared/purebrain_portal/clients.db

### Step 4: Update missing fields
Auto-sync leaves ai_name, company, goes_by blank. Update manually with conversation data.

### Step 5: Send seed to Witness
Health check: GET http://178.156.229.207:8200/health
Send: POST http://178.156.229.207:8200/intake/seed
Auth: Bearer 03a3140abf7c914bac3d39dead043c0c4fde5b4af0f0c31bf1de46aafdc3bf36
Body: { partner: "acg-ai-civ-com", seed: { human_name, human_email, ai_name, tier, paypal_subscription_id, conversation[] } }
Response includes seed_id for tracking.

### Step 6: Notify Jared via Telegram

## Key Facts Discovered

- PayPal auto-sync runs hourly: It catches payment but WITHOUT chatbox data (ai_name, company)
- Witness seed endpoint at port 8200 — directly callable, works reliably
- AGENTMAIL_API_KEY is NOT in .env — send_agentmail.py will fail. Use HTTP endpoint instead.
- purebrain_payments.jsonl: orderId field is the I- subscription ID, but email/name are EMPTY when post-payment flow breaks

## Harrison Case Specifics

- Client ID: 30 in clients.db
- Email: Harrison@bisnce.com
- AI Name: MIA (chosen by Harrison in 23-message awakening conversation)
- Company: HOVR
- Subscription: I-H6AC73U9HARH (ACTIVE, $149/mo)
- Seed ID: acg-ai-civ-com-20260319-142401-36bc32 (queued with Witness)
- Container + magic link: pending Witness provisioning

## Root Cause of the Gap

The post-payment chatbox flow fires a pay_test_completion event to /api/pay-test-complete
which captures ai_name, email, company. When the page breaks, this event never fires.
PayPal sync catches the payment but has no chatbox data.

## Fix Recommendation

Log server should cross-reference conversation session against payment orderId when a
subscription is detected, and auto-extract ai_name/company from conversation logs.
This would prevent data gaps when post-payment flow breaks.
