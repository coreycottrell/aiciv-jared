# Memory: Plugin v4.6.7 Deployment - WAF Blocked, Manual Deploy Required

**Date**: 2026-02-27
**Type**: teaching + operational
**Topic**: GoDaddy WAF reCAPTCHA gate blocks automated wp-login.php from server IP

---

## Situation

Tried to deploy purebrain-security plugin v4.6.7 via Playwright browser automation.
Goal: fix brain video visibility (homepage/pay-test/invitation pages).

## What Happened

1. **GoDaddy WAF blocks our server IP (89.167.19.20)** from wp-login.php with reCAPTCHA
2. **Not a password issue** - both `PUREBRAIN_WP_APP_PASSWORD` and `PUREBRAIN_WP_PASSWORD` work for REST API but wp-login.php shows "Invalid credentials" (actually WAF rejection disguised)
3. **HTTP 429 on all wp-admin paths** from our server IP
4. **REST API (wp-json) remains fully functional** - confirmed with App Password

## Full Diagnostic Result

| Endpoint | Status from Server IP | Notes |
|----------|----------------------|-------|
| wp-login.php | 429 + reCAPTCHA | WAF rate-limited |
| wp-admin/ | 302 → 429 | Redirects to blocked wp-login |
| wp-json/wp/v2/plugins | 200 | Working perfectly |
| xmlrpc.php | 403 | WAF blocked |
| admin-ajax.php | 400 | Returns "0" (no valid session) |

## Root Cause

Previous automation sessions (from other deployments) triggered GoDaddy's rate limiter.
Threshold: 3+ failed login attempts → reCAPTCHA gate → manual human verification required.
Recovery: 15-20+ minutes, or requires human CAPTCHA solve.

## Solution: Manual Deploy

When WAF blocks automated deployment:

1. **Create ZIP**: `exports/purebrain-security-v467.zip` (already created)
2. **Send to Jared**: `./tools/tg_send.sh --file exports/purebrain-security-v467.zip "caption"`
3. **Jared deploys from his browser** (his IP is not rate-limited):
   - Go to: https://purebrain.ai/wp-admin/plugins.php
   - Click "Add New" > "Upload Plugin"
   - Upload the ZIP
   - WordPress replaces the plugin files and keeps it active

## Alternative: REST API Plugin Upload (Doesn't Work for Local ZIPs)

The WP REST API `/wp-json/wp/v2/plugins` endpoint POST method tries to install from wordpress.org repository, NOT from a local ZIP. The `pluginzip` multipart approach doesn't work - it requires a `slug` parameter that maps to wordpress.org.

## When to Use This Pattern

Whenever you need to deploy plugin updates and automated browser login is blocked:
1. Create plugin ZIP with proper folder structure: `plugin-slug/plugin-file.php`
2. Send ZIP to Jared via Telegram
3. Ask Jared to manually upload via wp-admin

## Files

- Plugin PHP: `exports/purebrain-security-plugin-v466.php` (contains v4.6.7)
- Plugin ZIP: `exports/purebrain-security-v467.zip` (44.1 KB, ready to upload)
- Deployment script: `scripts/deploy_plugin_v467.py` (for future reference)

**Tags**: purebrain, plugin-deployment, godaddy-waf, rate-limit, recaptcha, manual-deploy, wp-rest-api
