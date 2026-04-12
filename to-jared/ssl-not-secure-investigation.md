# SSL "Not Secure" Investigation: purebrain.ai/pay-test-sandbox/

**Date**: 2026-02-20
**Analyst**: security-auditor agent
**Page**: https://purebrain.ai/pay-test-sandbox/ (Page ID: 468)
**Triggered by**: Chrome incognito showing "Not Secure" warning

---

## Executive Summary

**Good news**: There is NO mixed content (HTTP resources on HTTPS page) and the main domain SSL certificate is valid. The purebrain.ai domain itself is fully secure.

**Root cause of "Not Secure" warning**: The self-signed SSL certificate on the backend server at `89.167.19.20:8443` is the primary trigger. When Chrome (especially incognito, where no certificate exceptions are stored) encounters JavaScript calls to a self-signed HTTPS endpoint, it displays security warnings.

**Secondary issue found**: An A-C-Gee API key is hardcoded in the public page HTML.

---

## SSL Certificate Status

| Endpoint | Certificate | Status | Expires |
|----------|-------------|--------|---------|
| purebrain.ai:443 | Google Trust Services (WE1) | VALID | May 12 2026 |
| 89.167.19.20:8443 | Self-signed (PureBrain/LogServer) | SELF-SIGNED | Feb 12 2027 |
| 89.167.19.20:8765 | Self-signed (PureBrain/LogServer) | SELF-SIGNED | Feb 12 2027 |
| api.puremarketing.ai | Google Trust Services | VALID | May 3 2026 |
| purebrain.workers.dev | Google Trust Services | VALID | May 5 2026 |
| www.paypal.com | DigiCert | VALID | Aug 4 2026 |
| sageandweaver-network.netlify.app | DigiCert (*.netlify.app) | VALID | Mar 19 2027 |
| cdn.by.wonderpush.com | Let's Encrypt | VALID | Good |
| res.cloudinary.com | GoDaddy G2 | VALID | May 26 2026 |

---

## Mixed Content Scan Results

**All static resources are HTTPS.** Comprehensive scan found:

- Zero `http://` script `src` attributes
- Zero `http://` image `src` attributes
- Zero `http://` CSS `href` attributes
- Zero `http://` video/audio `src` attributes
- Zero `ws://` (insecure WebSocket) connections
- Zero HTTP form `action` attributes
- Zero `http://` in dynamically injected resources

The W3C SVG namespace `http://www.w3.org/2000/svg` appears 3 times in Elementor data — these are **XML namespaces, not resource loads** and do not cause any browser warning.

---

## Root Cause: Self-Signed Certificate on Port 8443

The page JavaScript makes three `fetch()` calls to `89.167.19.20:8443`:

```javascript
const LOGGING_ENDPOINT = 'https://89.167.19.20:8443/api/log-conversation';
const VERIFY_ENDPOINT  = 'https://89.167.19.20:8443/api/verify-payment';
// Also: https://89.167.19.20:8443/api/log-pay-test
```

These calls use a **self-signed certificate** (issuer = CN=89.167.19.20, self-issued).

### Chrome's behavior with self-signed certs:
- **Regular Chrome**: If you have previously visited and accepted the cert warning at `https://89.167.19.20:8443`, Chrome stores that exception and doesn't warn again.
- **Chrome Incognito**: Does NOT inherit stored certificate exceptions. Every session starts fresh. When the page's JavaScript tries to call these endpoints, Chrome:
  1. **Blocks the fetch() request** with `net::ERR_CERT_AUTHORITY_INVALID`
  2. **Shows console errors** in DevTools
  3. For payment-related calls, Chrome may display the "Not Secure" indicator more prominently
  4. The payment verification call (`VERIFY_ENDPOINT`) has **no fallback** — the failure is hard

### Why this affects incognito specifically:
In incognito mode, Chrome:
- Has no stored cert exceptions
- Shows cert error overlay if navigated to directly
- Blocks fetch() silently but may trigger address bar indicators depending on Chrome version

**Note on Chrome version behavior**: Chrome 94-120+ changed how "Not Secure" appears. Some Chrome versions show the indicator for HTTPS pages that attempt payment operations to endpoints with invalid certificates, even via JavaScript.

---

## Architecture Issue: Full Homepage Embedded in Elementor Widget

A significant architectural finding: The **entire pay-test-sandbox page** is implemented as a **single Elementor Custom HTML widget** containing a full 404KB HTML document (including `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>` tags).

The widget content includes:
- The complete homepage layout (navbar, hero, video backgrounds, testimonials)
- The PayPal SDK integration
- The AI chat interface
- All CSS and JavaScript

**Implications**:
1. The inner `<html>`, `<head>`, `<body>` tags are stripped by the browser (they're invalid inside another HTML document)
2. The JavaScript IS executed as inline scripts within the outer WordPress page
3. The browser sees all fetch() calls from this embedded JS
4. Any security scan of the page will find the self-signed cert calls

---

## Additional Security Findings

### Finding 1: MEDIUM — A-C-Gee API Key Exposed in Public Page

**Location**: Elementor widget JavaScript (publicly visible in page source)
**Exposed key**: `os3ctWW0CAQSVPnM-WeNZr75SKTlrvliGTTvkdanYbc`
**Used for**: Sending conversation logs to `https://sageandweaver-network.netlify.app/api/capture-proxy`

**Risk**: Anyone can use this key to spam the Netlify logging endpoint. The endpoint accepts POST requests with this key.

**Fix**: Use a server-side proxy instead of calling the Netlify endpoint directly from client JavaScript, or rotate the key and use a per-request signed token.

### Finding 2: LOW — Missing HTTP Security Headers

None of the following headers are set on any purebrain.ai pages:

| Header | Purpose |
|--------|---------|
| `Strict-Transport-Security` | Enforce HTTPS, prevent downgrade attacks |
| `Content-Security-Policy` | Prevent XSS, restrict resource origins |
| `X-Frame-Options` | Prevent clickjacking |
| `X-Content-Type-Options` | Prevent MIME sniffing |
| `Referrer-Policy` | Control referrer information leakage |

### Finding 3: INFORMATIONAL — PayPal Plan IDs Mismatch

The `pay-test-sandbox` page (468) uses different PayPal Plan IDs than what's stored in `config/paypal_plans.json`:

- **In page 468**: `P-9KA28683EF7622051NGLUFJY`, `P-1JL98851AU229172RNGLUFJY`, etc.
- **In config**: `P-1AG936074F0953120NGLTFKY`, `P-2SA65600MT088594TNGLTFKY`, etc.

The page 468 correctly uses `PAYPAL_SANDBOX_CLIENT_ID` (`AYTFob05...`), so the sandbox plan IDs are likely the correct ones for testing. This is informational only.

---

## Does This Affect ALL Pages or Just pay-test-sandbox?

**Only pay-test-sandbox/ and pay-test/ are affected by the self-signed cert issue.** Both pages (ID 439 and 468) contain the same JavaScript that calls `89.167.19.20:8443`. No other pages on purebrain.ai contain these calls.

The homepage and all other pages use:
- The AI chat via `api.puremarketing.ai` (valid cert)
- Cloudinary for videos (valid cert)
- Standard WordPress resources (all on purebrain.ai HTTPS)

---

## Recommended Fixes (Priority Order)

### Fix 1 (CRITICAL — Resolves "Not Secure"): Replace Self-Signed Cert with CA-Signed Cert

The self-signed certificate on `89.167.19.20:8443` is the core issue. Replace it with a certificate from a trusted CA.

**Option A: Free Let's Encrypt cert** (requires a domain pointing to 89.167.19.20):
```bash
# Point a subdomain to 89.167.19.20, e.g., api.purebrain.ai
# Then issue cert:
certbot certonly --standalone -d api.purebrain.ai
# Start server with new cert:
uvicorn app:app --ssl-certfile /etc/letsencrypt/live/api.purebrain.ai/fullchain.pem \
    --ssl-keyfile /etc/letsencrypt/live/api.purebrain.ai/privkey.pem --port 8443
```

**Option B: Add a subdomain and update page JavaScript** (change endpoint URLs):
```javascript
// Change this:
const LOGGING_ENDPOINT = 'https://89.167.19.20:8443/api/log-conversation';
const VERIFY_ENDPOINT  = 'https://89.167.19.20:8443/api/verify-payment';

// To this (after pointing api.purebrain.ai to 89.167.19.20 and getting cert):
const LOGGING_ENDPOINT = 'https://api.purebrain.ai/api/log-conversation';
const VERIFY_ENDPOINT  = 'https://api.purebrain.ai/api/verify-payment';
```

**Option C: Add Cloudflare Tunnel** (simplest, no cert management):
```bash
# Install cloudflared on the 89.167.19.20 server
# Create tunnel pointing purebrain-api.purebrain.ai -> localhost:8443
# Cloudflare handles the cert automatically
# Cost: Free
```

### Fix 2 (HIGH — Security hygiene): Route Self-Signed Calls Through WordPress Proxy

If Option C above isn't implemented, add a WordPress proxy endpoint that Chrome trusts:

```php
// In a WordPress plugin or functions.php:
add_action('rest_api_init', function() {
    register_rest_route('purebrain/v1', '/log-conversation', [
        'methods' => 'POST',
        'callback' => function($request) {
            // Forward to local server (no SSL verification needed - same network)
            $response = wp_remote_post('https://127.0.0.1:8443/api/log-conversation', [
                'body' => $request->get_body(),
                'sslverify' => false,  // OK because this is server-to-server on same host
            ]);
            return rest_ensure_response(json_decode(wp_remote_retrieve_body($response)));
        },
        'permission_callback' => '__return_true',
    ]);
});
```

Then update the page JavaScript to use `/wp-json/purebrain/v1/log-conversation`.

### Fix 3 (MEDIUM — Security hygiene): Remove Exposed A-C-Gee API Key

Replace the hardcoded API key with a server-side proxy:

```javascript
// Instead of directly calling Netlify with exposed API key:
const logFallback = async (payload) => {
    // Call WordPress endpoint that proxies the request server-side
    await fetch('/wp-json/purebrain/v1/log-fallback', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
};
```

The WordPress endpoint holds the API key server-side (in `wp-config.php` or `.env`).

### Fix 4 (LOW — Security hardening): Add HSTS and Basic Security Headers

Add to GoDaddy's `.htaccess` or WordPress `functions.php`:

```php
// In WordPress functions.php or a plugin:
add_action('send_headers', function() {
    header('Strict-Transport-Security: max-age=31536000; includeSubDomains');
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: SAMEORIGIN');
    header('Referrer-Policy: strict-origin-when-cross-origin');
});
```

---

## Quick Fix vs Long-Term Fix

| Timeline | Action |
|----------|--------|
| **Today (30 min)** | Add domain alias `api.purebrain.ai` → `89.167.19.20` in DNS, get Let's Encrypt cert, update 2 URL constants in Elementor widget |
| **This week** | Route self-signed calls through WordPress proxy, rotate A-C-Gee API key |
| **This month** | Add HSTS and security headers to all pages |

---

## Files Examined

- `https://purebrain.ai/pay-test-sandbox/` — Live page (ID 468, Elementor)
- `https://purebrain.ai/pay-test/` — Live page (ID 439, Elementor)
- `/home/jared/projects/AI-CIV/aether/tools/avatar_chat_server.py` — Avatar server (port 8765)
- `https://89.167.19.20:8443` — Backend API server (self-signed cert)
- `config/paypal_plans.json` — PayPal plan configuration

---

## Conclusion

The "Not Secure" Chrome warning on `purebrain.ai/pay-test-sandbox/` in incognito mode is caused by **JavaScript fetch() calls to `89.167.19.20:8443`** which uses a self-signed SSL certificate. Chrome's incognito mode has no stored cert exceptions, so these calls fail with `ERR_CERT_AUTHORITY_INVALID`.

The fix is straightforward: point `api.purebrain.ai` (or similar subdomain) to `89.167.19.20`, get a free Let's Encrypt certificate, and update the two endpoint constants in the Elementor widget JavaScript.

The main `purebrain.ai` domain is fully secure and all other pages are unaffected.

