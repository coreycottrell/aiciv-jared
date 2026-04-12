# Critical Payment Flow: Two Bugs Fixed 2026-03-20

**Type**: operational + teaching
**Topic**: PayPal subscription payer info extraction + magic link endpoint 404

---

## Incident Summary

Every customer payment since at least 2026-03-18 was logging blank payer details
and the post-payment chatbox was stuck polling a 404 endpoint for the magic link.
Affected: Harrison Amit, Vishal, and Jared's tests.

---

## BUG 1: PayPal Payer Info Always Empty

**Root Cause**: PayPal subscription onApprove callback only returns subscriptionID.
Payer email, name, and amount are NOT in the SDK data for subscription flows.
Frontend sent empty fields because the SDK literally does not provide them.

**Fix**: In verify_payment(), added PayPal API call when I- ID present and payer empty:
1. POST /v1/oauth2/token to get Bearer token
2. GET /v1/billing/subscriptions/{id} to fetch subscriber details
3. Extract subscriber.email_address, subscriber.name, billing_info.last_payment.amount

Verified: Harrison I-H6AC73U9HARH returns Harrison@bisnce.com, Harrison Amit, $149.00

**Also**: Added .env loading to main() so PayPal creds available under systemd.

---

## BUG 2: Magic Link Endpoint 404

**Root Cause**: /api/magic-link/<uuid> route did not exist in purebrain_log_server.py.
The storage system (agentmail_monitor.py -> .magic-links.json) was working correctly.

**Fix**: Added GET /api/magic-link/<path:session_uuid> endpoint:
- Reads .magic-links.json
- Looks up by UUID key, falls back to email match
- Returns {status: ready, magic_link: ...} or {status: pending}

Verified: Returns 200 now. Frontend polling getting proper responses.

---

## Files Modified

- /home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py
  - Lines ~529-601: PayPal subscription API fetch in verify_payment()
  - Lines ~724-782: New get_magic_link() route  
  - Lines ~1276-1291: .env loading in main()
- Backup: purebrain_log_server.py.bak-payment-fix-20260320

---

## Key Facts

- Magic links stored: .magic-links.json (keyed by session UUID)
- PayPal live creds: PAYPAL_CLIENT_ID, PAYPAL_SECRET in .env
- PayPal subscription onApprove NEVER returns payer details (by design)
- Sandbox: pass isSandbox:true to use api-m.sandbox.paypal.com
