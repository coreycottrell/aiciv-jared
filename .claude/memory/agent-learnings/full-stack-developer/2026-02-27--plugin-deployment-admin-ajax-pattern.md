# Plugin Deployment via admin-ajax.php Pattern
**Date**: 2026-02-27
**Type**: operational-critical
**Agent**: conductor (discovered during deployment)

## Problem
WordPress App Passwords work for REST API but NOT for wp-admin login.
GoDaddy adds SSO overlay ("Log in with GoDaddy") that breaks Playwright.
Rate limiting on wp-login.php triggers 429 + reCAPTCHA.

## Solution: Two-Step Cookie + AJAX Pattern

### Step 1: Get cookies via curl POST to wp-login.php
```bash
WP_USER=$(grep PUREBRAIN_WP_USER .env | head -1 | cut -d'=' -f2-)
WP_PASS=$(grep PUREBRAIN_WP_PASSWORD .env | head -1 | cut -d'=' -f2-)

curl -s -c /tmp/wp_cookies.txt -b /tmp/wp_cookies.txt \
  -X POST "https://purebrain.ai/wp-login.php" \
  -d "log=${WP_USER}&pwd=${WP_PASS}&wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1"
```

### Step 2: POST plugin update via admin-ajax.php
```bash
# Get nonce from plugin editor page
NONCE=$(curl -s -b /tmp/wp_cookies.txt \
  "https://purebrain.ai/wp-admin/plugin-editor.php?plugin=purebrain-security%2Fpurebrain-security-plugin.php&Submit=Select" \
  | grep -oP 'name="nonce" value="\K[^"]+')

# POST the update
curl -s -b /tmp/wp_cookies.txt \
  -X POST "https://purebrain.ai/wp-admin/admin-ajax.php" \
  -F "action=edit-theme-plugin-file" \
  -F "nonce=${NONCE}" \
  -F "plugin=purebrain-security/purebrain-security-plugin.php" \
  -F "file=purebrain-security/purebrain-security-plugin.php" \
  -F "newcontent=<${PLUGIN_FILE}"
```

### Key Notes
- `PUREBRAIN_WP_PASSWORD` = actual admin password (for wp-login.php form)
- `PUREBRAIN_WP_APP_PASSWORD` = app password (for REST API Basic Auth only)
- Cookies from wp-login.php include `wordpress_sec_*` and `wordpress_logged_in_*`
- These cookies work for admin-ajax.php endpoints
- The nonce field is `name="nonce"` (NOT `name="_wpnonce"`)
- Response: `{"success":true,"data":{"message":"File edited successfully."}}`
- After deployment, Cloudflare may cache old output. Use `?nocache=` param or purge.

## Caching
- After plugin update, Cloudflare serves cached HTML for ~minutes
- `?nocache=$(date +%s)` query param may bypass GoDaddy/Cloudflare page cache
- Hard refresh (Ctrl+Shift+R) needed on client side
