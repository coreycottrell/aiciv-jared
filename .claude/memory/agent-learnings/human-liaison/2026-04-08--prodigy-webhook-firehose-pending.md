# Prodigy/Ahsen Payment Data Thread — Webhook Firehose Pending

**Date**: 2026-04-08 (checked 2026-04-09 17:05 UTC)
**Type**: operational
**Status**: PENDING PRODIGY REPLY

## Context
Ahsen's AI "Prodigy" (prodigy@agentmail.to) requested access to PureBrain payment data for a real-time SaaS growth dashboard (saas-dashboard-rho-sandy.vercel.app, Supabase backend). Initial email 2026-04-09 16:42 UTC to aethergottaeat@agentmail.to.

## Aether's Reply (16:54 UTC)
Sent 4-option menu:
- **Option A (recommended)**: Webhook firehose — POST every payment event to Prodigy's endpoint with HMAC shared secret
- Option B: Read-only REST poll endpoint `GET /api/payments/recent?since=`
- Option C: Google Sheets viewer
- Option D: SSH log access (not recommended)

Included sample event JSON schema (tier, amount, customer_email, order_id, subscription_id, referral_code, source_page).

## 5 Scoping Questions Asked Prodigy
1. Scope: payments only, or also customers/MRR/churn/referral?
2. Real-time webhook vs batch polling?
3. Consumer: AI, humans, or both?
4. Tech stack of receiving endpoint?
5. PII handling — raw emails or hashed?

## Jared Status
✅ **Approved Option A (webhook firehose)** the same day

## What's Built
- Webhook firehose code is BUILT and tested
- Just needs Prodigy's receiving endpoint URL dropped into config
- Flip `enabled:true` → live in ~10 min

## What's Blocking
Prodigy has NOT yet replied as of 2026-04-09 17:05 UTC (~11 min after our reply). Waiting on:
- Their endpoint URL
- Answers to Q1–Q5

## Data Locations Shared With Prodigy
- `/logs/purebrain_payments.jsonl` — production PayPal webhook events
- `/logs/purebrain_pay_test.jsonl` — test mode
- Sheets: `1bmmO2FVxZdAcYewPFNu6DbHZzh9AAojHUsWgofv6tqQ` (PayPal Auto-Split Tracker)
- portal.purebrain.ai/admin dashboards

## Next Actions for Next Session
1. Re-check aethergottaeat@agentmail.to for Prodigy reply
2. If URL present → delegate ST# to update webhook firehose config + flip enabled:true
3. If silent >2 hours → send polite bump email
4. Once live, verify first event lands in their Supabase

## Related Files
- Webhook firehose code: (location TBD — delegate ST# to locate)
- Sent email thread ID: `<0100019d732a89e6-b2d23987-2e0f-4f0c-a2fa-caea0c5cc20e-000000@email.amazonses.com>`
- Prodigy original: `<0100019d731fff6b-175b3152-0616-4fd4-9968-7905fdcb1274-000000@email.amazonses.com>`
