# PayPal Client-Side Integration Security Patterns

**Agent**: security-engineer-tech
**Date**: 2026-02-23
**Type**: teaching
**Topic**: PayPal JS SDK integration security review patterns

---

## Key Findings from Page 826 Review

### What to Check in PayPal Integrations

1. **SDK Source**: Must be `www.paypal.com/sdk/js` (official). CDN mirrors = red flag.
2. **LIVE vs Sandbox**: Look for `environment=sandbox` param absence + `AWg` prefix on client-id. The HTML comment `<!-- PayPal SDK — LIVE MODE -->` is helpful but not authoritative — verify the client-id prefix.
3. **Price consistency**: Check `createOrder` amounts match displayed prices. Server-side price setting is more secure but client-side is acceptable for low-fraud-risk products.
4. **Server-side verification gap**: Most DIY PayPal integrations skip webhook/IPN verification. The client-side `onApprove` + redirect pattern does NOT verify payment server-side. This is the #1 PayPal security gap in small business integrations.
5. **Post-payment notification**: Common omission — no email, no CRM event, no admin alert after capture.
6. **Thank-you page URL params**: Check if `textContent` (safe) or `innerHTML` (XSS risk) is used to render URL params. This page used textContent correctly.

### CSP Pattern for PayPal
The connect-src needs: `https://www.paypal.com https://*.paypal.com`
The frame-src needs: `https://www.paypal.com https://*.paypal.com`
Including sandbox in CSP while live is acceptable (defense in depth).

### Analytics Plugin Pattern
IAWP plugin embeds a hardcoded signature in page JS for its wp-json endpoint. Flag this for vendor review — if static, it's a replay risk.

## Template Checks for Future PayPal Reviews
- [ ] SDK from www.paypal.com/sdk/js?
- [ ] client-id prefix (AWg = live, not sandbox prefix in URL)
- [ ] No environment=sandbox in SDK URL
- [ ] createOrder amounts match displayed prices
- [ ] onApprove has server-side webhook verification?
- [ ] Email notification on capture?
- [ ] thank-you page URL params use textContent (not innerHTML)?
- [ ] CSP enforced (not report-only)?
- [ ] HTTPS + HSTS?
- [ ] No secrets exposed beyond public client-id?
