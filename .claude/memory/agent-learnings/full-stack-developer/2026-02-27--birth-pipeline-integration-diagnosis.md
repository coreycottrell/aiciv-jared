# Birth Pipeline Integration Diagnosis
**Date**: 2026-02-27
**Type**: operational
**Topic**: PureBrain birth pipeline — gaps between payment/OAuth/chat-complete and Witness seed data delivery

## Summary
Full audit of the 3 trigger points where data should fire to Witness/AICIV. Found 4 confirmed gaps and 1 architectural issue.

## Key File Paths
- JS flow: `exports/pay-test-script-chat-flow-v4.js`
- Log server: `tools/purebrain_log_server.py`
- Proxy host: `https://89.167.19.20:8443` (self-signed cert)
- Witness: `http://104.248.239.98:8099`

## Confirmed Gaps

### GAP 1: PayPal payment → NO seed data fires to Witness
`verify_payment()` in log_server on SUCCESS does:
- Increments invitation spots counter
- Fires Telegram notification to Jared
- Sends Brevo confirmation email to buyer
- Does NOT call Witness at all. Zero. Nothing.

### GAP 2: /birth/start proxy strips/ignores seed data passthrough
The JS sends `{name, email, human_name, tier}` to `/api/birth/start`.
The proxy (`proxy_birth_start()`) parses the body and passes it through raw to Witness.
This part IS working — the body IS forwarded. But Witness's response must include `container` or the flow fails.

### GAP 3: /birth/code proxy — no seed data in code call
The JS POSTs `{container, auth_code}` to `/api/birth/code`. No name/email/tier included.
If Witness needs to associate the OAuth completion with the full user profile, it's not getting it at this step.

### GAP 4: flow:complete fires `logPayTestData()` — not `log_pay_test`
`runCompletion()` fires: `await logPayTestData({ ...payTestData, event: 'flow:complete' })`
`logPayTestData()` sends to TWO endpoints: `/api/log-pay-test` AND `/api/log-conversation`.
BUT: it does NOT set `flowCompleted: true` in the payload. The `log_pay_test` handler triggers Brevo emails ONLY when `data.get('flowCompleted') == True`. Since `logPayTestData()` never sets this flag, Brevo emails do NOT fire on flow completion.

### GAP 5: `log_pay_test` does NOT trigger any Witness call on flow:complete
Even if `flowCompleted=true` arrived correctly, the handler only triggers Brevo email sequence. There is ZERO Witness notification on flow completion.

## What IS Working
- Proxy endpoints exist and route to Witness: `/api/birth/start`, `/api/birth/code`, `/api/birth/portal-status`
- CORS headers are set: `Access-Control-Allow-Origin: https://purebrain.ai`
- Birth/start logs show 200 OK in Feb-26 test (aiciv-06)
- Birth/code logs show 200 OK in Feb-26 test
- log-conversation forwarding to A-C-Gee IS working (forward_to_acgee)
- log-conversation forwarding to hub IS working (forward_to_hub)

## The Architectural Gap
Seed data for Witness (name, email, tier, chat history) gets split across 3 different places:
1. `/api/birth/start` — gets name+email+tier (at OAuth init time)
2. `/api/birth/code` — gets container+auth_code only (no user data)
3. `flow:complete` — full data exists in payTestData but nothing pushes it to Witness

Witness needs a "seed complete" call after all data is collected. This doesn't exist.

## Fix Required
Add a `/api/seed` (or `/api/birth/seed`) endpoint that:
- Accepts full user profile (name, email, tier, aiName, company, role, primaryGoal, conversationHistory)
- Proxies it to Witness so they can load the AiCIV's memory
- Called from `runCompletion()` or from `log_pay_test` on `flowCompleted=true`
