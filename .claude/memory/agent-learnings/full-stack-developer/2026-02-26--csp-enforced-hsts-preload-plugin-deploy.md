# Memory: CSP Enforced + HSTS Preload Plugin Deploy

**Date**: 2026-02-26
**Type**: teaching
**Agent**: full-stack-developer
**Topic**: Surgical plugin edits for security header upgrades

---

## What Was Done

Two surgical edits to the live PureBrain Security Plugin (v6.1.0):

1. **CSP enforced mode**: Changed `Content-Security-Policy-Report-Only` → `Content-Security-Policy`
   - File line 868 in `tools/security/purebrain-security/purebrain-security-plugin.php`

2. **HSTS preload**: Changed `max-age=31536000; includeSubDomains` → `max-age=31536000; includeSubDomains; preload`
   - File line 816 in same file

---

## Key Pattern: Surgical Edits vs Full Redeploy

When the task says "only change two lines", DON'T replace the entire plugin file.

1. Edit the local `.php` file directly (2 Edit tool calls)
2. Read the live version from Plugin Editor FIRST to confirm which version is deployed
3. The local `tools/security/purebrain-security/purebrain-security-plugin.php` IS the canonical source for what's deployed — keep it in sync

---

## Cloudflare Cache Gotcha

**Problem**: After successful deploy, `curl -sI https://purebrain.ai/` showed OLD headers.

**Root cause**: Cloudflare edge cache was serving cached responses (CF-Cache-Status: HIT).

**How to verify origin is correct despite CF cache**:
```python
import http.client, ssl, time
conn = http.client.HTTPSConnection("purebrain.ai", context=ssl.create_default_context())
conn.request("GET", f"/?nocache={int(time.time())}", headers={
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
})
```
When CF-Cache-Status shows DYNAMIC or MISS, that's the origin response.

**Resolution**: Cloudflare cache naturally expires (typically within minutes to hours). No action needed if origin is confirmed correct.

**GoDaddy "Flush Cache" link**: Available in WP admin toolbar at `/wp-admin/?wpaas_action=flush_cache&wpaas_nonce=[fresh_nonce]`. But must use the FRESH nonce from the current admin page — saved nonces expire. Use playwright `click()` on the link element directly.

---

## Verification Evidence

Plugin Editor confirmed both lines updated:
- Line 816: `header( 'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload' );`
- Line 868: `header( 'Content-Security-Policy: ' . $csp );`

Origin response (CF-Cache-Status: DYNAMIC):
- `content-security-policy: default-src 'self'; ...` ✓
- `strict-transport-security: max-age=31536000; includeSubDomains; preload` ✓

---

## Files

- Plugin: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`
- Deploy script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v462_csp_hsts_purebrain.py`
