# Referral Complete Fix — All 6 Payment Pages

**Date**: 2026-03-13
**Type**: bug-fix
**Severity**: Critical (revenue impact — referrers never earned rewards)

---

## Bug

`/api/referral/complete` was never called after payment success on any payment page.
Referrers shared links, people paid, but rewards were never issued.

## Root Cause (Two Issues)

### 1. Missing fetch() call in onPaymentComplete
`window.onPaymentComplete(tier, orderId, payerInfo)` existed on all 6 pages but had no
call to `https://app.purebrain.ai/api/referral/complete`.

### 2. URL param mismatch
Referral server generates links as `?code=PB-XXXX`
Payment pages captured `?ref=` from URL — so `getPbRef()` always returned null even if
a referral link was used.

## Fix Applied

### Pages fixed (all 6):
- `exports/cf-pages-deploy/pay-test-2/index.html`
- `exports/cf-pages-deploy/insiders/index.html`
- `exports/cf-pages-deploy/pay-test-awakened/index.html`
- `exports/cf-pages-deploy/pay-test-partnered/index.html`
- `exports/cf-pages-deploy/pay-test-unified/index.html`
- `exports/cf-pages-deploy/pay-test-sandbox-3/index.html`

### Fix 1 — Added referral fetch call in onPaymentComplete:
```javascript
(function() {
  var refCode = typeof window.getPbRef === 'function' ? window.getPbRef() : null;
  if (refCode) {
    var refEmail = (payerInfo && payerInfo.email_address) ? payerInfo.email_address : '';
    var refName  = (payerInfo && payerInfo.name)
      ? ((payerInfo.name.given_name || '') + ' ' + (payerInfo.name.surname || '')).trim()
      : '';
    fetch('https://app.purebrain.ai/api/referral/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ referral_code: refCode, referred_email: refEmail, referred_name: refName })
    })...
  }
})();
```

### Fix 2 — Updated URL param capture to support both ?ref= and ?code=:
```javascript
var ref = params.get('ref') || params.get('code');
```

## API Contract

Endpoint: `POST https://app.purebrain.ai/api/referral/complete`
Required params: `referral_code`, `referred_email`
Optional params: `referred_name`
Returns: `{"ok": true, "reward": 5.0}` or `{"ok": true, "message": "already completed"}`

## Deployment

- Deployed via wrangler to `purebrain-staging` CF Pages project
- CF cache purged for all 6 payment page URLs
- Verified live on staging: `https://e47e67b4.purebrain-staging.pages.dev/pay-test-2/`

## Database Schema

`/home/jared/purebrain_portal/referrals.db` — 4 tables: referrers, referrals, rewards, referral_clicks
`REWARD_PER_REFERRAL = $5.00` (set in portal_server.py line 66)
Double-completion prevention is built into the endpoint.
