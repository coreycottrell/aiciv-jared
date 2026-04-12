# Security Plugin v2.6.0: Cloudflare Tunnel + Rate Limiting Hardening

**Date**: 2026-02-20
**Type**: operational + teaching
**Topic**: WordPress plugin deploy - Cloudflare Tunnel, sslverify, transient rate limiting

---

## What Was Done

Updated `tools/security/purebrain-security-plugin.php` from v2.5.0 to v2.6.0:

### 1. Raw IP → Cloudflare Tunnel
- Both proxy functions (`purebrain_proxy_log_server`, `purebrain_proxy_verify_payment`) now call `https://api.purebrain.ai/api/...` instead of `https://89.167.19.20:8443/api/...`
- Cloudflare Tunnel (ID: fa55839c-e753-4a96-935c-cc58cf24b4b8) provides valid TLS cert
- `sslverify: true` re-enabled (was previously false to avoid self-signed cert errors)

### 2. Transient-Based Rate Limiting (new function: `purebrain_check_rate_limit`)
- Log conversation proxy: 30 requests/minute per IP
- Payment verification proxy: 10 requests/minute per IP (stricter)
- Uses WordPress transients (`set_transient`/`get_transient`) - no extra DB tables
- Returns HTTP 429 when limit exceeded

### 3. 64KB Body Size Cap
- All three proxy endpoints check `strlen($request->get_body()) > 65536`
- Returns HTTP 413 Payload Too Large if exceeded
- Protects against oversized request attacks

### 4. CSS-Only Legal Footer Hover
- Replaced `onmouseover="this.style.color='#2a93c1'"` inline handlers
- New CSS class `.pb-legal-link:hover { color: #2a93c1 }` via `wp_head` style injection
- Eliminates inline JS event handlers (security best practice)

---

## Deploy Pattern Notes

### Validation Check Refinement
- **DO NOT** check `"89.167.19.20" not in new_content` - the IP appears in PHP docblock comments as historical reference ("Raw IP replaced in v2.6.0")
- **DO** check `"https://89.167.19.20" not in new_content` - only flag if it appears as a live URL
- Lesson: comments are fine, functional URLs are what matter

### Version String in HTML
- PHP plugin header comments (`* Version: 2.6.0`) do NOT render to HTML output
- The inline CSS blocks (purebrain-faq-accordion, purebrain-blog-desktop-padding, etc.) also don't echo the version
- Checking for version string in live HTML will fail - use functional CSS/class presence instead
- Better live checks: `pb-legal-link`, `pb-blog-nav`, `faq-accordion` CSS IDs

### CDN Cache Behavior
- WordPress "File edited successfully" = plugin saved to disk (authoritative)
- GoDaddy flush_cache works for object/PHP cache but Cloudflare CDN takes time
- CDN headers: `cache-control: public, max-age=2678400` (31 days)
- Cached HTML will show old version strings for minutes/hours until CDN expires
- This is expected and not a deployment failure

### Playwright Login
- GoDaddy SSO overlay appears first - always click `.wpaas-sso-login-toggle` to get username/password form
- Use `PUREBRAIN_WP_PASSWORD` env var (regular password), not `PUREBRAIN_WP_APP_PASSWORD`
- Plugin editor URL uses `purebrain-security/` directory (not `purebrain-security-plugin/`)

---

## Deployment Result

- All 13 pre-deploy validation checks passed
- WordPress reported: "File edited successfully"
- GoDaddy cache flushed via nonce URL
- Live verification: `pb-legal-link`, `pb-blog-nav`, FAQ accordion all confirmed present
- `api.purebrain.ai` not visible in HTML (correct - it's PHP server-side only)

---

## Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` (v2.6.0)
- `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v260.py` (new deploy script)

## Screenshots

- `exports/screenshots/plugin_v260_deploy.png` - Post-save confirmation
- `exports/screenshots/plugin_v260_verify.png` - Cache flush result
