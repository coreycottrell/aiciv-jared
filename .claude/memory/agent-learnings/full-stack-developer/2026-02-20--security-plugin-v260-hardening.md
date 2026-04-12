# Memory: PureBrain Security Plugin v2.6.0 Hardening

**Date**: 2026-02-20
**Type**: teaching + operational
**Agent**: full-stack-developer

## What Was Done

Four security hardening changes applied to `tools/security/purebrain-security-plugin.php` (local file only, no deployment).

### 1. Proxy Endpoints: Raw IP -> Cloudflare Tunnel
- **Before**: `https://89.167.19.20:8443/api/log-conversation` and `/api/verify-payment`
- **After**: `https://api.purebrain.ai/api/log-conversation` and `/api/verify-payment`
- Cloudflare Tunnel `api.purebrain.ai` was already deployed (Tunnel ID: fa55839c-e753-4a96-935c-cc58cf24b4b8)
- Affects: `purebrain_proxy_log_server` and `purebrain_proxy_verify_payment`

### 2. sslverify: false -> true
- Both wp_remote_post calls had `'sslverify' => false` to tolerate self-signed cert on raw IP
- Switching to Cloudflare Tunnel means valid TLS — sslverify can now be `true`
- Updated comments to explain the rationale

### 3. Rate Limiting (WordPress transients)
- Added `purebrain_check_rate_limit( $key, $max_requests, $window_seconds )` function
- Uses WordPress transients — zero extra DB tables, no dependencies
- Transient key format: `pb_rl_` + md5(endpoint_key + client_ip) — keeps it under 40 char WP limit
- Applied to all three REST callbacks:
  - `purebrain_proxy_acgee_logging`: 30 req/min (key: `acgee_logging`)
  - `purebrain_proxy_log_server`: 30 req/min (key: `log_server`)
  - `purebrain_proxy_verify_payment`: 10 req/min (key: `verify_payment`) — stricter for payment
- Returns HTTP 429 WP_Error on limit exceeded
- Also added 64KB body size cap (HTTP 413) to all three

### 4. Inline Event Handlers -> CSS Hover
- Removed `onmouseover` and `onmouseout` from privacy policy and terms of service links
- Added a `wp_head` hook that injects `<style id="purebrain-legal-footer-css">` with CSS `:hover` rules
- Links now use class `pb-legal-link` instead of inline handlers
- CSS targets: `#purebrain-legal-footer .pb-legal-link:hover` and `:focus` for accessibility

### 5. Version Bumped to 2.6.0
- Plugin header version updated from 2.5.0 to 2.6.0
- Changelog entry added summarizing all four changes

## Key Technical Patterns Learned

### WordPress Transient Rate Limiter Pattern
```php
function purebrain_check_rate_limit( $key, $max_requests = 30, $window_seconds = 60 ) {
    $client_ip     = isset( $_SERVER['REMOTE_ADDR'] ) ? $_SERVER['REMOTE_ADDR'] : 'unknown';
    $transient_key = 'pb_rl_' . md5( $key . '_' . $client_ip );
    $count         = (int) get_transient( $transient_key );
    if ( $count >= $max_requests ) { return false; }
    set_transient( $transient_key, $count + 1, $window_seconds );
    return true;
}
```
- `get_transient` returns `false` (not 0) when expired/missing — cast to `(int)` gives 0, which is correct
- Transient TTL is the sliding window. Each request resets the TTL for that IP+endpoint combo
- WP transient keys max 40 chars — use md5 to hash long keys safely

### Inline Handler to CSS Refactor Pattern (WordPress echo context)
- Add a separate `wp_head` hook to inject `<style>` CSS for hover states
- Give links a class instead of inline handlers
- Include `:focus` alongside `:hover` for keyboard accessibility

## Files Modified
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` — local only, not yet deployed
