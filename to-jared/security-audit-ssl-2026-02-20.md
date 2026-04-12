# PureBrain Security Audit: SSL / "Not Secure" Status
## Full Report - 2026-02-20

**Prepared by**: security-auditor agent (Aether team)
**Date**: 2026-02-20
**Scope**: Complete SSL and mixed-content audit of purebrain.ai

---

## Executive Summary

**The "Not Secure" browser warning is RESOLVED.**

The root cause was JavaScript calls to an internal server at `89.167.19.20:8443` that used a
self-signed SSL certificate. This caused Chrome (especially incognito) to block those calls and
show security indicators.

**That fix is live**: Both pay-test pages now call `https://api.purebrain.ai` (a Cloudflare
tunnel with a valid Google-issued certificate) and WordPress proxy endpoints instead of the raw
internal IP. No page on the site makes any HTTP or self-signed-cert calls.

**Two urgent items remain for Jared** (each takes about 10 minutes in the Cloudflare dashboard):
1. Deploy the secured Cloudflare Worker (anyone can currently use your Anthropic API for free)
2. Set minimum TLS to 1.2 (PCI compliance for payment pages)

---

## SSL Certificate Status

| Endpoint | Issuer | Status | Expires |
|----------|--------|--------|---------|
| purebrain.ai:443 | Google Trust Services (WE1) | VALID | May 12 2026 |
| api.purebrain.ai:443 | Google Trust Services (WE1) | VALID | May 12 2026 |
| 89.167.19.20:8443 | Self-signed | SELF-SIGNED | Feb 2027 |

**Key facts:**
- purebrain.ai has a valid, trusted SSL certificate. Visitors see the lock icon.
- api.purebrain.ai (the Cloudflare tunnel) has a valid certificate. Payment verification uses this.
- The internal server at 89.167.19.20:8443 still uses a self-signed certificate. However, no
  browser now connects to this IP directly. Traffic routes through the WP proxy and api.purebrain.ai.

---

## Mixed Content Scan Results

Mixed content (loading HTTP resources on an HTTPS page) is the number one cause of "Not Secure"
warnings. This audit scanned every page.

### Pages Checked

| Page | Status |
|------|--------|
| purebrain.ai/ (homepage) | CLEAN |
| purebrain.ai/blog/ | CLEAN |
| purebrain.ai/pay-test/ (ID 439) | CLEAN |
| purebrain.ai/pay-test-sandbox/ (ID 468) | CLEAN |
| purebrain.ai/purebrain-4/ (ID 383) | CLEAN |
| purebrain.ai/privacy-policy/ | CLEAN |
| purebrain.ai/terms-of-service/ | CLEAN |
| purebrain.ai/ai-partnership-guide/ | CLEAN |
| purebrain.ai/ai-readiness-assessment/ | CLEAN |
| purebrain.ai/thank-you/ | CLEAN |
| purebrain.ai/ai-partnership-assessment/ | CLEAN |
| purebrain.ai/living-avatar/ | CLEAN |
| All 7 recent blog posts | CLEAN |

### Elementor Data Scanned (raw JS/HTML inside page builders)

| Page ID | Elementor Data Size | Internal IP | http:// URLs |
|---------|---------------------|-------------|--------------|
| 11 (homepage) | 325,622 bytes | None | None |
| 383 (purebrain-4) | 166,246 bytes | None | None |
| 439 (pay-test) | 426,079 bytes | None | None |
| 468 (pay-test-sandbox) | 426,331 bytes | None | None |

**Result: Zero insecure resource loads across all pages and all Elementor widget code.**

---

## WordPress Settings Verification

| Setting | Value | Status |
|---------|-------|--------|
| siteurl | https://purebrain.ai | CORRECT |
| home | https://purebrain.ai | CORRECT |
| Aether user profile URL | https://purebrain.ai | FIXED TODAY (was http://) |

**Fix applied today**: The Aether user account had its website URL set to `http://purebrain.ai`.
This appeared in the Yoast schema.org JSON-LD on every blog post as `"sameAs":["http://purebrain.ai"]`.
While this is structured data and not a resource load, it was the only remaining `http://` reference
on the site. It has been updated to `https://purebrain.ai` via the WordPress REST API.

---

## Security Headers Status

All six security headers are present on every page.

| Header | Value | Status |
|--------|-------|--------|
| Strict-Transport-Security | max-age=31536000; includeSubDomains | ACTIVE |
| X-Content-Type-Options | nosniff | ACTIVE |
| X-Frame-Options | SAMEORIGIN | ACTIVE |
| Referrer-Policy | strict-origin-when-cross-origin | ACTIVE |
| Permissions-Policy | camera=(), microphone=(), geolocation=(), payment=(self) | ACTIVE |
| Content-Security-Policy | Report-only mode (monitoring, not blocking) | ACTIVE |

**HSTS note**: With `max-age=31536000; includeSubDomains`, browsers that visit the site will
enforce HTTPS for the next year, even if someone types `http://purebrain.ai`. This is the strongest
HSTS setting short of preloading.

---

## API Endpoint Security (Pay-Test Pages)

The pay-test pages (439 and 468) make JavaScript API calls. Here is the full inventory of what
they call and whether each is secure:

| Endpoint | Purpose | Protocol | Certificate | Status |
|----------|---------|----------|-------------|--------|
| https://api.purebrain.ai/api/verify-payment | Payment verification | HTTPS | Google Trust Services | SECURE |
| https://api.purebrain.ai/api/log-conversation | Conversation logging | HTTPS | Google Trust Services | SECURE |
| https://api.purebrain.ai/api/log-pay-test | Pay test logging | HTTPS | Google Trust Services | SECURE |
| https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages | AI chat (Cloudflare Worker) | HTTPS | Cloudflare | SECURE (see HIGH-001) |
| /wp-json/purebrain/v1/log-conversation-fallback | Fallback logging | HTTPS (relative) | Same as site | SECURE |
| /wp-json/purebrain/v1/log-conversation | Direct logging | HTTPS (relative) | Same as site | SECURE |
| https://www.paypal.com / https://*.paypal.com | PayPal SDK | HTTPS | DigiCert | SECURE |

**The internal IP address `89.167.19.20:8443` does NOT appear anywhere in any page.**

---

## Active Plugin: PureBrain Security v1.6.0

The plugin is running on WordPress and providing these protections:

| Protection | Status |
|-----------|--------|
| User enumeration (REST API) blocked | ACTIVE |
| Author URL enumeration blocked | ACTIVE |
| Security headers (6 total) | ACTIVE |
| Cookie flags (Secure, HttpOnly, SameSite) | ACTIVE |
| Login error message hardening | ACTIVE |
| Privacy/legal footer on all pages | ACTIVE |
| Staging pages noindex | ACTIVE |
| WP proxy endpoints registered | ACTIVE |

**Plugin version note**: Version 1.7.0 is built and ready at
`/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security.zip`. Live is 1.6.0. The
differences are cosmetic (CSS improvements for blog post layout) and do not affect security. No
urgent upgrade needed.

---

## Remaining Issues (Action Required)

### HIGH-001 CRITICAL: Cloudflare Worker Is Wide Open

**Severity**: HIGH (financial exposure)

**What was found**: The Cloudflare Worker at
`https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages` accepts unauthenticated
POST requests from any origin. This was confirmed live during this audit - a test request
received a full response from the Anthropic API using Jared's credentials.

**Risk**: Anyone who discovers this URL can:
- Use Jared's Anthropic API account to generate text at his expense
- Make unlimited requests (no rate limiting currently)
- Extract the AI system prompt by crafting specific requests

**The fix is ready**: A secured version of the worker is at
`/home/jared/projects/AI-CIV/aether/tools/security/cloudflare-worker-secured.js`

It adds: origin whitelist (only purebrain.ai), secret token header, per-IP rate limiting,
constant-time token comparison (prevents timing attacks), and full rejection logging.

**Steps to deploy (10-15 minutes)**:
1. Log in to dash.cloudflare.com
2. Go to Workers and Pages
3. Find `pure-brain-dashboard-api` worker
4. Replace the code with contents of `tools/security/cloudflare-worker-secured.js`
5. Add two environment variables (encrypted):
   - `ANTHROPIC_API_KEY` - your existing key
   - `PB_AUTH_TOKEN` - generate with: `openssl rand -base64 24`
6. Create a KV namespace named `RATE_LIMIT_KV` and bind to the worker
7. Deploy

See `/home/jared/projects/AI-CIV/aether/tools/security/CLOUDFLARE-WORKER-DEPLOY.md` for detailed
instructions.

---

### LOW-003: TLS 1.0 and 1.1 Still Accepted

**Severity**: LOW (compliance issue, low practical risk)

The site accepts connections from browsers using TLS 1.0 (1999) and TLS 1.1 (2006). These are
deprecated protocols with known vulnerabilities. PCI DSS compliance (required for payment
processing) mandates TLS 1.2 minimum.

**Steps to fix (2 minutes)**:
1. Log in to dash.cloudflare.com
2. Select the purebrain.ai zone
3. Go to SSL/TLS then Edge Certificates
4. Change "Minimum TLS Version" from 1.0 to 1.2
5. Save

---

### CRIT-001: ACGEE_API_KEY Not in wp-config.php

**Severity**: MEDIUM (feature gap, not a security risk to users)

The WordPress proxy for A-C-Gee logging (`/wp-json/purebrain/v1/log-conversation-fallback`) is
live and routing correctly. However, the API key must be set in `wp-config.php`. Until it is,
conversation logging to A-C-Gee is silently skipped. Nothing breaks for users.

**Steps to fix (5 minutes)**:
1. Access `wp-config.php` via GoDaddy hosting file manager or SFTP
2. Add before the `/* That's all, stop editing! */` line:
   ```php
   define( 'ACGEE_API_KEY', 'os3ctWW0CAQSVPnM-WeNZr75SKTlrvliGTTvkdanYbc' );
   ```
3. Save

**Important**: After adding this, the key will no longer be in any browser-visible code. It will
only exist in the server-side `wp-config.php`.

---

### MEDIUM: WordPress Version Number Still Visible

**Severity**: LOW (informational disclosure, no direct exploit)

The WordPress generator meta tag (`WordPress 6.9.1`) still appears in the page HTML.

**Root cause analysis**: The plugin's `remove_action('wp_head', 'wp_generator')` is running
correctly. Blog posts and other pages show clean HTML with no WP generator tag. The homepage
currently shows the tag because Cloudflare has cached an older version of the page.

**Evidence**:
- Blog posts (Cloudflare cache: HIT, generated after plugin update): no ?ver= strings, no WP generator
- Homepage (Cloudflare cache: HIT, older cached version): has ?ver= strings and WP generator

**Resolution**: This will resolve automatically when the Cloudflare cache for the homepage expires
(typically 4 hours to 1 day). To force immediate resolution: log in to the Cloudflare dashboard
and purge cache for purebrain.ai.

**Elementor generator tag**: Elementor adds its own generator tag which the WordPress plugin
cannot remove (Elementor outputs it via its own hook). This is low risk - it reveals the
Elementor version but not the WordPress version. Elementor vulnerabilities are patched quickly
and the version number alone is not actionable for attackers.

---

## WordPress Plugin Proxy: Status Check

The PureBrain Security plugin registers three proxy endpoints. Here is their current status:

| Endpoint | Purpose | Test Result | Notes |
|----------|---------|-------------|-------|
| POST /wp-json/purebrain/v1/log-conversation-fallback | A-C-Gee logging | 200 (skipped - no API key) | Working, pending API key in wp-config.php |
| POST /wp-json/purebrain/v1/log-conversation | Internal server logging | 200 (passed through) | Working |
| POST /wp-json/purebrain/v1/verify-payment | Payment verification | 503 (upstream failed) | Dead code - pay-test pages use api.purebrain.ai directly |

**Note on the 503**: The verify-payment proxy calls `89.167.19.20:8443` internally. Currently
the backend returns 400 (bad request) on test calls, which the proxy translates to 503. However,
both pay-test pages (439 and 468) have been updated to call `https://api.purebrain.ai/api/verify-payment`
directly instead of the WP proxy. The WP proxy for verify-payment is no longer in the critical
path. It can be updated at leisure to call `https://api.purebrain.ai/api/verify-payment` instead
of the internal IP.

---

## What Causes Chrome's "Not Secure" Warning: Analysis

For Jared's reference, here is exactly what Chrome does and does not flag:

| Condition | Chrome Shows | Status |
|-----------|-------------|--------|
| Valid HTTPS cert on domain | Lock icon | GOOD - present |
| Any http:// resource loaded on HTTPS page | "Not Secure" | GOOD - no http:// resources |
| JavaScript fetch() to self-signed cert endpoint | ERR_CERT_AUTHORITY_INVALID in console | RESOLVED - no self-signed calls |
| JavaScript fetch() to HTTP endpoint | Mixed content blocked | N/A - no HTTP API calls |
| WordPress siteurl set to http:// | Redirect issues | GOOD - both https:// |
| HSTS header present | Browser enforces HTTPS | GOOD - present |
| http:// in schema.org structured data | NOT a browser warning | FIXED anyway (was sameAs URL) |
| Version numbers in generator tags | NOT a browser warning | Low priority |

**Conclusion**: The browser lock icon should be present and fully green on all pages. The previous
"Not Secure" warning was caused by Chrome blocking JavaScript calls to `89.167.19.20:8443` (self-signed
cert). Those calls are now routed through trusted HTTPS endpoints.

---

## Quick Reference: Files and Locations

| Item | Path |
|------|------|
| Security plugin (deployed v1.6.0, local v1.7.0) | tools/security/purebrain-security-plugin.php |
| Security plugin zip (v1.7.0) | tools/security/purebrain-security.zip |
| Secured Cloudflare Worker (ready to deploy) | tools/security/cloudflare-worker-secured.js |
| Cloudflare deploy instructions | tools/security/CLOUDFLARE-WORKER-DEPLOY.md |
| Previous SSL investigation | to-jared/ssl-not-secure-investigation.md |
| Previous full audit + remediation proof | to-jared/security-audit-proof.md |

---

## Action Items for Jared (Priority Order)

| Priority | Action | Time | Effort |
|----------|--------|------|--------|
| 1 | Deploy secured Cloudflare Worker (HIGH-001) | Today | 15 min |
| 2 | Set TLS 1.2 minimum in Cloudflare dashboard | Today | 2 min |
| 3 | Add ACGEE_API_KEY to wp-config.php | This week | 5 min |
| 4 | Purge Cloudflare cache to clear generator tags | Optional | 2 min |

All code needed for actions 1, 2, and 3 is already written and ready.

---

## Security Score: Current State

| Category | Score | Notes |
|----------|-------|-------|
| SSL/TLS | 9/10 | Valid cert everywhere, TLS 1.0/1.1 still accepted (-1) |
| Mixed Content | 10/10 | Zero http:// resource loads on any page |
| Security Headers | 9/10 | All 6 present, CSP in report-only not enforcing (-1) |
| API Security | 6/10 | Cloudflare Worker unauthenticated (-4) |
| Authentication | 9/10 | User enumeration blocked, login errors generic, cookies secure |
| Data Privacy | 8/10 | Legal pages exist, ACGEE API key pending wp-config.php (-2) |
| **Overall** | **8.5/10** | One critical open item (Cloudflare Worker) |

---

*Report produced by security-auditor agent (Aether) - 2026-02-20*
*Actions applied during this audit: User profile URL corrected from http:// to https://*
