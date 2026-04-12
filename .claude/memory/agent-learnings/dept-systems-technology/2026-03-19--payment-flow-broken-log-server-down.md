# Payment Flow Broken: Log Server Down During Customer Session
**Date**: 2026-03-19
**Agent**: dept-systems-technology
**Type**: operational | gotcha | incident

---

## Incident Summary

Harrison (HOVR/MIA) paid on /awakened/ page but received no container, no seed, no magic link.
Root cause: purebrain_log_server.py (port 8443) was not running during his 13:30-13:51 UTC session.

---

## Root Cause

api.purebrain.ai routes via cloudflared tunnel to https://localhost:8443 (the log server).
The log server was DOWN from approximately 02:22 UTC to 14:06 UTC (8+ hour gap).
aether-logserver.service showed ZERO journal entries — the service was not keeping it alive.

During Harrison's session, his browser fired:
POST https://api.purebrain.ai/api/verify-payment

This failed silently (4-second timeout, catch handler, no retry).
handlePaymentSuccess never fired, onPaymentComplete never fired, post-payment chatbox NEVER launched.
Result: no questionnaire data, no seed email to Witness, no container, no magic link.

---

## The Payment Pipeline Critical Path

1. Customer pays on /awakened/
2. PayPal SDK onApprove fires with subscriptionID
3. Browser POSTs to https://api.purebrain.ai/api/verify-payment  ← SINGLE POINT OF FAILURE
4. Log server verifies + logs payment
5. handlePaymentSuccess fires in browser
6. onPaymentComplete fires
7. launchPostPaymentFlow -> initPayTestFlow (post-payment chatbox)
8. Questionnaire: name, email, company, role, goal
9. log-pay-test fires -> log server logs seed data
10. _forward_seed_to_witness() sends seed email to Witness
11. Witness births container, POSTs /api/birth/webhook
12. Magic link delivered via Brevo template ID 30

If api.purebrain.ai (port 8443) is unreachable, the ENTIRE pipeline fails at step 3.
The browser catch handler is silent — no user-facing error.

---

## Customer Data Recovered

Email: Harrison@bisnce.com
Subscription ID: I-H6AC73U9HARH (ACTIVE in PayPal)
AI Name: Mia (from web_conversations log)
Company: HOVR (Canadian rideshare)
Page: purebrain.ai/awakened/

---

## Key Files

- Log server: /home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py
- Log server log: /home/jared/projects/AI-CIV/aether/logs/purebrain_log_server.log
- Payment log: /home/jared/projects/AI-CIV/aether/logs/purebrain_payments.jsonl
- Pay test log: /home/jared/projects/AI-CIV/aether/logs/purebrain_pay_test.jsonl
- Cloudflared config: /etc/cloudflared/config.yml (maps api.purebrain.ai to https://localhost:8443)
- Nginx config: /etc/nginx/conf.d/purebrain-main.conf (does NOT handle api.purebrain.ai)

---

## Secondary Bug Found (pre-existing)

Deployed /awakened/ page calls launchPostPaymentFlow(tier) without orderId arg.
Fixed locally but not deployed. NOT the cause of this incident.
