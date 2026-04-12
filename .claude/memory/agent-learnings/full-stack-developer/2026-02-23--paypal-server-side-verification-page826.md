# PayPal Server-Side Verification - Page 826 (ai-website-execution)

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: Adding server-side PayPal verification + webhook to page 826 (/ai-website-execution/)

---

## What Was Already There (Before This Task)

The `purebrain_log_server.py` ALREADY had both endpoints implemented (added on 2026-02-23 earlier):
- `POST /api/verify-payment` — live PayPal order lookup + Telegram notification + Brevo email
- `POST /api/paypal-webhook` — PayPal webhook receiver for PAYMENT.CAPTURE.COMPLETED

The endpoints were ALREADY complete and working. The only missing piece was:
1. Page 826 JavaScript not calling verify-payment
2. `PAYPAL_WEBHOOK_ID` not set in .env
3. Log server had accumulated ~100+ CLOSE_WAIT connections (was overwhelmed)

---

## What Was Done

### 1. Updated Page 826 JavaScript (WordPress REST API)
- Changed the `onApprove` callback to call `https://api.purebrain.ai/api/verify-payment`
- Uses `Promise.race` with 8-second timeout (server slowness NEVER blocks the redirect)
- ALWAYS redirects to thank-you page (verified or not - purchase proceeds regardless)
- Adds `&verified=1|0` to redirect URL for thank-you page logging

```javascript
onApprove: function(data, actions) {
  return actions.order.capture().then(function(details) {
    const name = ...;
    const orderID = data.orderID;

    const verifyTimeout = new Promise(resolve => setTimeout(() => resolve({verified:false,timeout:true}), 8000));
    const verifyFetch = fetch('https://api.purebrain.ai/api/verify-payment', {...})
      .then(res => res.json()).catch(() => ({verified:false,error:true}));

    Promise.race([verifyFetch, verifyTimeout]).then(result => {
      window.location.href = 'https://purebrain.ai/thank-you/?tier='+tier+'&order='+orderID+...;
    });
  });
}
```

### 2. Added PAYPAL_WEBHOOK_ID to .env
- Added placeholder with instructions for Jared to fill in
- Must register webhook URL in PayPal Developer Dashboard manually
- URL: `https://api.purebrain.ai/api/paypal-webhook`

### 3. Restarted Log Server
- Old instance (PID 5963) had ~100+ CLOSE_WAIT connections from prior requests
- This caused timeout for all new connections (Cloudflare tunnel was returning 502)
- New instance (PID 349156) healthy immediately
- LESSON: When log server returns 502 via Cloudflare, restart it first

---

## Key Diagnostic Pattern

When `api.purebrain.ai` returns 502 or times out:
1. Check `ss -tlnp | grep 8443` — is port bound?
2. Check `/proc/net/tcp | grep 20FB` — are there many CLOSE_WAIT connections?
3. If yes: `kill $(pgrep -f purebrain_log_server) && nohup python3 tools/purebrain_log_server.py >> logs/purebrain_log_server.log 2>&1 &`
4. Wait 3 seconds then test health: `curl --insecure https://localhost:8443/api/health`

Root cause: Flask's threaded mode eventually accumulates hung connections, particularly under SSL, when clients disconnect without reading the full response.

---

## Remaining Action for Jared

**Manual Step Required**: Register webhook in PayPal Developer Dashboard
1. Go to https://developer.paypal.com/dashboard/applications/live
2. Click on the live app
3. Click "Add Webhook"
4. URL: `https://api.purebrain.ai/api/paypal-webhook`
5. Events: Check `PAYMENT.CAPTURE.COMPLETED`
6. Save → copy the Webhook ID
7. Add to `.env`: `PAYPAL_WEBHOOK_ID=<id from PayPal>`
8. Restart log server to pick up new env var

Until this is done, webhook events will still be processed but signature verification is skipped (logged as `sig_verified=false`).

---

## File Paths

- Log server: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`
- Payments log: `/home/jared/projects/AI-CIV/aether/logs/purebrain_payments.jsonl`
- Env file: `/home/jared/projects/AI-CIV/aether/.env`
- WordPress page: https://purebrain.ai/ai-website-execution/ (Page ID: 826)

---

**End of Memory**
