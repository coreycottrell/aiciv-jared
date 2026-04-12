# PureBrain Security Plugin - Deployment Instructions

**Plugin file**: `purebrain-security-plugin.php`
**Date**: 2026-02-20
**Author**: Aether (AI) for Pure Technology

---

## What This Plugin Does

| Feature | Details |
|---------|---------|
| Block user enumeration (REST) | Removes `/wp/v2/users` endpoints |
| Block `?author=` enumeration | Redirects to homepage with 301 |
| Security headers | HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy |
| ACGEE logging proxy | `/wp-json/purebrain/v1/log-conversation-fallback` |
| Log server proxy | `/wp-json/purebrain/v1/log-conversation` |
| Payment verification proxy | `/wp-json/purebrain/v1/verify-payment` |

---

## Step 1: Upload and Activate the Plugin

### Option A: WP Admin Upload (Recommended)

1. Log in to **purebrain.ai/wp-admin**
2. Go to **Plugins > Add New**
3. Click **Upload Plugin** (button at the top)
4. Click **Choose File** and select `purebrain-security-plugin.php`

   **Note**: WordPress expects a `.zip` file. Zip it first:
   ```bash
   cd /home/jared/projects/AI-CIV/aether/tools/security/
   mkdir -p purebrain-security
   cp purebrain-security-plugin.php purebrain-security/
   zip -r purebrain-security.zip purebrain-security/
   ```
   Then upload `purebrain-security.zip`.

5. Click **Install Now**
6. Click **Activate Plugin**

### Option B: FTP/SFTP Direct Upload

1. Upload `purebrain-security-plugin.php` to:
   `/wp-content/plugins/purebrain-security/purebrain-security-plugin.php`
2. Go to **WP Admin > Plugins** and activate **PureBrain Security**

---

## Step 2: Add ACGEE_API_KEY to wp-config.php

The A-C-Gee API key must be defined as a PHP constant in `wp-config.php` so it's never exposed in client-side JavaScript.

### How to Edit wp-config.php

**Via GoDaddy cPanel File Manager:**
1. Log in to GoDaddy > My Products > Web Hosting > Manage
2. Open **cPanel** > **File Manager**
3. Navigate to the WordPress root (usually `public_html/` or the domain folder)
4. Find `wp-config.php`, right-click > **Edit**
5. Add the line below **before** the line that says `/* That's all, stop editing! */`:

```php
// PureBrain API Keys (server-side only - never expose to client)
define( 'ACGEE_API_KEY', 'os3ctWW0CAQSVPnM-WeNZr75SKTlrvliGTTvkdanYbc' );
```

**Via SSH (if available):**
```bash
# Find wp-config.php
find /path/to/wordpress -name wp-config.php -maxdepth 2

# Add the constant before the "stop editing" line
# (Use nano, vim, or your preferred editor)
nano /path/to/wordpress/wp-config.php
```

### Verification

After adding the constant, verify via WP Admin > Plugins that PureBrain Security is active, then test the proxy endpoint:

```bash
curl -X POST https://purebrain.ai/wp-json/purebrain/v1/log-conversation-fallback \
  -H "Content-Type: application/json" \
  -d '{"source":"test","messages":[],"metadata":{"event_type":"test"},"session_id":"test_123"}'
```

Expected response: `{"status":"ok"}` or the upstream A-C-Gee response.

---

## Step 3: Verify Security Headers

After activating, check headers are present:

```bash
curl -I https://purebrain.ai | grep -E "(Strict-Transport|X-Content|X-Frame|Referrer)"
```

Expected output:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
```

---

## Step 4: Verify User Enumeration is Blocked

```bash
# Should return 404 or empty
curl https://purebrain.ai/wp-json/wp/v2/users

# Should redirect to homepage
curl -I "https://purebrain.ai/?author=1"
```

---

## Proxy Endpoint Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/wp-json/purebrain/v1/log-conversation-fallback` | POST | Proxies to A-C-Gee capture-proxy with API key |
| `/wp-json/purebrain/v1/log-conversation` | POST | Proxies to internal log server (89.167.19.20:8443) |
| `/wp-json/purebrain/v1/verify-payment` | POST | Proxies to internal payment verification |

---

## Rollback Instructions

If the plugin causes any issues:
1. Go to **WP Admin > Plugins**
2. Find **PureBrain Security** and click **Deactivate**
3. The site returns to its previous state immediately

---

## What Was Changed on the Live Pages

As part of the 2026-02-20 security audit, these changes were applied directly to Elementor page content:

| Page | Change |
|------|--------|
| Homepage (ID 11) | Removed developer backdoor from system prompt; moved API key to WP proxy |
| Pay-test (ID 439) | Removed developer backdoor from system prompt; moved API key to WP proxy |
| Pay-test sandbox (ID 468) | Removed developer backdoor from system prompt; moved API key to WP proxy |

The client-side JS now calls `/wp-json/purebrain/v1/log-conversation-fallback` instead of directly calling the A-C-Gee API with a hardcoded key.
