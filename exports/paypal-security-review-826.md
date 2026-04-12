# PayPal Security Review — Page 826 (/ai-website-execution/)

**Agent**: security-engineer-tech
**Domain**: Security Engineering
**Date**: 2026-02-23
**Reviewed URL**: https://purebrain.ai/ai-website-execution/
**Thank-You URL**: https://purebrain.ai/thank-you/
**Method**: Static analysis of live page HTML + HTTP response headers

---

## Executive Summary

| Severity | Count |
|----------|-------|
| HIGH | 3 |
| MEDIUM | 3 |
| LOW | 2 |
| INFO | 2 |

The PayPal integration is fundamentally sound — correct SDK source, LIVE mode confirmed, correct pricing amounts hardcoded. However, there are significant gaps in server-side payment verification, a client-side ID exposure that should be understood, and the CSP is in report-only mode (not enforced). These issues should be addressed before high-volume traffic hits this page.

---

## CHECK 1: PayPal SDK Source Verification

**Result: PASS**

The PayPal SDK is loaded from the official source:

```html
<script src="https://www.paypal.com/sdk/js?client-id=AWgWNlBQ...&currency=USD&intent=capture" defer></script>
```

- Source domain: `www.paypal.com` (official)
- Not a CDN mirror, not a third-party host
- `defer` attribute prevents render-blocking
- No subresource integrity (SRI) hash on this tag — see Finding [MED-002]

---

## CHECK 2: LIVE vs. Sandbox Mode

**Result: PASS**

The client-id prefix `AWg` is consistent with a PayPal production (LIVE) credential. Confirming indicators:

- No `?environment=sandbox` parameter in SDK URL
- No `sandbox.paypal.com` references in the SDK load
- The comment in HTML explicitly states: `<!-- PayPal SDK — LIVE MODE -->`
- The `connect-src` CSP policy does include `https://www.sandbox.paypal.com` as a permitted source, but this is a defense-in-depth allowance and does not indicate the page is actually using sandbox mode

**Conclusion**: The page is operating in LIVE mode. Real money will be captured.

---

## CHECK 3: Pricing Amounts vs. Displayed Prices

**Result: PASS**

The JavaScript `PRICES` object:

```javascript
const PRICES = {
  critical: { amount: '197.00', description: 'PureBrain AI Website Execution — Critical Fixes (48hr)' },
  complete:  { amount: '497.00', description: 'PureBrain AI Website Execution — Complete Implementation (5 days)' }
};
```

Displayed prices in HTML:
- `$197` for Critical Fixes — MATCHES
- `$497` for Complete Implementation — MATCHES

The amounts passed to `actions.order.create()` match displayed prices. No price manipulation risk from display vs. charge mismatch.

---

## CHECK 4: Exposed API Secrets

**Result: PASS (with note)**

No server-side secrets (API keys, secret keys, private tokens) are exposed in the client-side HTML. The PayPal `client-id` is intentionally public — this is by PayPal's design. The client ID alone cannot process refunds, access account details, or create unauthorized transactions. It only allows payment buttons to render.

**Note**: The client-id is now public knowledge for anyone who views page source. This is expected and acceptable for PayPal's JS SDK model.

---

## CHECK 5: HTTPS Enforcement

**Result: PASS**

- Page served over HTTP/2 via Cloudflare
- HSTS header present: `strict-transport-security: max-age=31536000; includeSubDomains`
- 365-day HSTS max-age — good
- `includeSubDomains` — good
- No `preload` directive — see Finding [LOW-001]
- PayPal SDK URL is `https://` — correct

---

## CHECK 6: XSS Vulnerabilities

**Result: MIXED — See [HIGH-001] for thank-you page**

**On /ai-website-execution/ (payment page):**

One `innerHTML` usage was found:

```javascript
// In brandFooterLogo() function
logoEl.innerHTML = '<span class="pb-logo-brand" style="...">' +
    '<span style="color:#2a93c1;">PUREBR</span>' + ...
```

This innerHTML is populated with a hardcoded string only — no user input flows into it. This is **safe** as written.

No other XSS vectors found on the payment page. The PayPal button rendering uses the official PayPal SDK iframe model, which isolates all payment input from the parent page DOM.

**On /thank-you/ (post-payment redirect target):**

The thank-you page reads URL parameters and inserts them into the DOM:

```javascript
var params = new URLSearchParams(window.location.search);
var name = params.get('name') ? params.get('name').trim() : '';
var ai   = params.get('ai')   ? params.get('ai').trim()   : '';

if (name) {
  var heading = document.getElementById('ty-heading');
  if (heading) heading.textContent = 'Welcome to the Family, ' + name + '!';
}
```

**The good news**: `textContent` is used (not `innerHTML`), which means HTML tags in the URL parameter are rendered as plain text, not executed. This is the correct approach and prevents XSS.

**The concern**: The `name` parameter in the redirect URL is populated from PayPal's returned `details.payer.name.given_name`. This data originates from PayPal's API response, not raw user input on your page. The risk is low but see [MED-001] for the URL parameter concern.

---

## FINDINGS

---

### [HIGH-001] No Server-Side Payment Verification

**Severity**: HIGH
**Category**: Broken Authentication / Payment Integrity
**CVSS Estimate**: 7.5

**Description**: Payment flow is entirely client-side. After `actions.order.capture()` resolves successfully, the code immediately redirects to `/thank-you/`. There is no server-side webhook or endpoint that independently verifies the PayPal order was genuinely captured before fulfillment begins.

**The attack**: A technically capable user could:
1. Intercept the `onApprove` callback
2. Trigger the redirect manually without completing payment
3. Arrive at `/thank-you/` appearing as a legitimate purchaser

More realistically: if the capture call fails silently or returns an unexpected state, the user could land on the thank-you page without a verified payment.

**Evidence**:
```javascript
onApprove: function(data, actions) {
  return actions.order.capture().then(function(details) {
    // No server-side verification here
    window.location.href = 'https://purebrain.ai/thank-you/?tier=' + tier +
      '&order=' + data.orderID +
      '&name=' + encodeURIComponent(name);
  });
},
```

**Recommendation**: Implement a PayPal webhook handler (IPN or Orders v2 webhook) on your server. When a payment completes, PayPal should POST to your endpoint, you verify the order ID with PayPal's API directly, then trigger fulfillment (email, Brevo tagging, service delivery). The client-side redirect should be a UX convenience only — not the fulfillment trigger.

PayPal webhook endpoint to configure: `https://api.purebrain.ai/paypal/webhook` (suggested).

---

### [HIGH-002] No Email Notification on Purchase

**Severity**: HIGH
**Category**: Business Logic / Incident Response
**CVSS Estimate**: N/A (business risk)

**Description**: There is no code in either the payment page or the thank-you page that sends any notification (email, Brevo event, Telegram, Slack, etc.) when a purchase completes. The `onApprove` handler captures the payment and redirects — nothing else.

This means:
- You will not know a purchase happened in real-time
- The customer receives no confirmation email
- No CRM record is created automatically
- No service delivery is triggered

**Evidence**: Searched both pages for `brevo`, `email`, `notify`, `fetch` (after payment), `webhook`, `sendEmail` — none found in the payment flow.

**Recommendation**: In the `onApprove` callback, after capture succeeds, POST the order details to a server endpoint that:
1. Sends customer confirmation email via Brevo
2. Sends admin alert to Jared (Telegram or email)
3. Creates/tags contact in Brevo with purchase data
4. Logs the transaction to your payment records

---

### [HIGH-003] URL Parameter Injection Risk on Thank-You Page (Open Redirect Adjacent)

**Severity**: HIGH
**Category**: Input Validation / Social Engineering Vector
**CVSS Estimate**: 6.1

**Description**: The thank-you page redirect URL is constructed client-side and includes `&name=` from PayPal's response. While `textContent` is used safely on the thank-you page, the URL itself can be crafted manually by anyone. Someone could construct a URL like:

```
https://purebrain.ai/thank-you/?tier=complete&order=FAKE123&name=<any+name>
```

And arrive at a thank-you page that shows their crafted name. This is a social engineering vector — attackers could share this URL to appear as if they purchased a service. It could also be used in phishing: send someone a "legitimate looking" purebrain.ai/thank-you URL.

More urgently: `tier` and `order` parameters are exposed in the URL. These are not validated server-side. Anyone can visit the thank-you page without paying.

**Recommendation**:
1. Generate a signed, one-time token server-side after webhook verification
2. Only the webhook completion triggers a valid thank-you token
3. Thank-you page validates the token before rendering success state
4. Alternatively: use a session/cookie set server-side after webhook verification, not URL params

---

### [MED-001] CSP in Report-Only Mode — Not Enforced

**Severity**: MEDIUM
**Category**: Security Misconfiguration
**CVSS Estimate**: 5.3

**Description**: The Content Security Policy is present but deployed as `Content-Security-Policy-Report-Only`. This means violations are logged but NOT blocked. The CSP provides zero protection in this state.

**Evidence**:
```
content-security-policy-report-only: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' ...
```

Additionally, the CSP allows `'unsafe-inline'` and `'unsafe-eval'` in `script-src`, which significantly reduces its protective value even if enforced.

**Recommendation**:
1. Switch to `Content-Security-Policy` (enforced) header
2. Remove `'unsafe-eval'` — audit what requires it (likely WordPress/Elementor)
3. Consider nonce-based CSP instead of `'unsafe-inline'`
4. Set up a `report-uri` endpoint to collect violation reports before enforcing

---

### [MED-002] No Subresource Integrity (SRI) on PayPal SDK

**Severity**: MEDIUM
**Category**: Supply Chain Security
**CVSS Estimate**: 5.3

**Description**: The PayPal SDK script tag lacks a `crossorigin` and `integrity` attribute. If PayPal's CDN were compromised (extremely unlikely but possible), malicious code could be injected into the payment flow without detection.

**Evidence**:
```html
<script src="https://www.paypal.com/sdk/js?client-id=...&currency=USD&intent=capture" defer></script>
```

**Note**: PayPal does not provide SRI hashes for their dynamic SDK (because it changes frequently and includes version/config parameters). The practical risk here is low given PayPal's infrastructure. However, the CSP `frame-src` and `connect-src` restrictions do provide compensating controls.

**Recommendation**: Ensure the CSP is enforced (see MED-001) and the `connect-src` directive restricts PayPal communication to `https://*.paypal.com` only (currently configured correctly in the CSP policy).

---

### [MED-003] IAWP Analytics Signature Exposed Client-Side

**Severity**: MEDIUM
**Category**: Information Disclosure
**CVSS Estimate**: 4.3

**Description**: The IAWP (analytics plugin) embeds a `signature` value in the page JavaScript:

```javascript
...{"payload":{"resource":"singular","singular_id":826,"page":1},"signature":"b0aeb41f4b5c9ae25db8b5a85c0e1233"}
```

This appears to be a request authentication signature for the analytics endpoint at `https://purebrain.ai/wp-json/iawp/search`. If this signature is static (hardcoded, not time-limited or user-specific), it could potentially be replayed or used to spam the analytics endpoint with fake pageview data.

**Recommendation**: Verify with the IAWP plugin documentation whether this signature is time-limited or nonce-based. If static, raise with the plugin vendor.

---

### [LOW-001] HSTS Missing Preload Directive

**Severity**: LOW
**Category**: Transport Security
**CVSS Estimate**: 2.6

**Description**: HSTS is configured correctly but lacks the `preload` directive. Without preload, first-time visitors connecting over HTTP could be redirected via a 301 before HSTS takes effect.

**Current header**:
```
strict-transport-security: max-age=31536000; includeSubDomains
```

**Recommended**:
```
strict-transport-security: max-age=31536000; includeSubDomains; preload
```

Then submit to the HSTS preload list at https://hstspreload.org/

---

### [LOW-002] WordPress xmlrpc.php Returns 403 (Acceptable)

**Severity**: LOW — Note only
**Category**: Attack Surface

XML-RPC endpoint returns HTTP 403 (access denied). This is correct behavior. No action needed beyond maintaining this block.

---

## INFORMATIONAL FINDINGS

### [INFO-001] WP REST API User Enumeration Blocked

The `/wp-json/wp/v2/users` endpoint returns 404 (not 200). User enumeration via REST API is blocked. This is correct.

### [INFO-002] WordPress REST API Link Exposed in HTTP Headers

The `link:` HTTP header exposes:
```
Link: <https://purebrain.ai/wp-json/wp/v2/pages/826>; rel="alternate"
```

This reveals page IDs and the WordPress REST API structure. Not a direct vulnerability (REST API access is controlled), but worth knowing an attacker can enumerate page IDs via headers. Low risk given current REST API lockdown.

---

## PRIORITY REMEDIATION ROADMAP

| Priority | Finding | Effort | Impact |
|----------|---------|--------|--------|
| P0 | [HIGH-002] Email/notification on purchase | Low | Critical — you're flying blind on sales |
| P0 | [HIGH-001] Server-side payment verification | Medium | Critical — payment integrity |
| P1 | [HIGH-003] Thank-you page URL param validation | Medium | High — social engineering / fraud |
| P2 | [MED-001] Enforce CSP (not report-only) | Medium | High — XSS protection |
| P3 | [MED-003] Investigate IAWP signature | Low | Medium — analytics integrity |
| P4 | [LOW-001] Add HSTS preload | Low | Low — transport hardening |

---

## OVERALL ASSESSMENT

The PayPal integration is correctly configured for LIVE mode, uses the official SDK, charges correct amounts, and serves over HTTPS. The foundation is solid.

The critical gap is operational: there is no server-side payment verification and no notification system. If a purchase happens right now, you would only discover it by logging into PayPal directly. This needs to be fixed before marketing this page aggressively.

The thank-you page parameter handling (textContent, not innerHTML) was done correctly — good defensive coding instinct. The URL manipulation concern (HIGH-003) is about the URL itself being forgeable, not about DOM injection.

---

*Security review completed by: security-engineer-tech*
*Scope: Static analysis of live page HTML + HTTP response headers. No active exploitation. No authenticated testing.*
