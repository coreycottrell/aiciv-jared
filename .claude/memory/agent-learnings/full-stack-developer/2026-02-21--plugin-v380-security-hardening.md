# Memory: Plugin v3.8.0 Security Hardening

**Date**: 2026-02-21
**Type**: operational
**Topic**: PureBrain Security Plugin v3.8.0 — three security fixes from security-engineer-tech review

---

## Summary

Built v3.8.0 of the PureBrain Security Plugin with three security fixes. NOT deployed yet —
code is ready and waiting for security review + QA before deploy (per engineering team workflow).

Plugin file: `tools/security/purebrain-security/purebrain-security-plugin.php`
Previous version: 3.7.0 (deployed to purebrain.ai; blocked on jareddsanborn.com due to admin password issue)

---

## Fixes Implemented

### MED-003: Brevo Fail-Closed on Missing API Key

**Finding**: When `BREVO_API_KEY` is not defined in wp-config.php, the endpoint should return
HTTP 503 with a clear, machine-readable error message.

**What changed**:
- Error message updated from "Subscription service is temporarily unavailable. Please try again later."
  to the spec-mandated: "Service unavailable - API key not configured"
- Error log message now explicitly states the endpoint is returning 503
- Error code: `configuration_error` (unchanged), HTTP 503 (unchanged)

**Note**: The fail-closed behavior (503 instead of fake success) was already present in v3.7.0.
This fix sharpened the error message to the exact wording security-engineer-tech specified,
and improved the log message for operator debugging clarity.

**Location in file**: `purebrain_brevo_subscribe()` function, ~line 697-705

---

### LOW-001: esc_html() Moved to Output Point (Transparency Section)

**Finding**: WordPress VIP best practice is to store raw values in PHP variables and apply
`esc_html()` only at the `echo` point. Escaping at assignment time can hide bugs and makes
the data unusable for non-HTML contexts.

**What changed**:
- Variables now store raw strings: `$week_of`, `$summary`, `$biggest_win`, `$cta_text`,
  `$stat_agents`, `$stat_domains`, `$stat_deliverables`, `$stat_hours`, `$cta_url`
- All `esc_html()` / `esc_url()` calls moved to the `echo` statement in the HTML template:
  - `echo esc_html( $week_of )`
  - `echo esc_html( $summary )`
  - `echo esc_html( $stat_agents )` (and stat_domains, stat_deliverables, stat_hours)
  - `echo esc_html( $biggest_win )`
  - `echo esc_html( $cta_text )`
  - `echo esc_url( $cta_url )`
- Table row breakdown cells were already correct (`echo esc_html(...)` inline) — left unchanged

**Security impact**: Same XSS protection, better code architecture.

**Location in file**: Transparency section render function, `wp_footer` action ~line 2739-2836

---

### LOW-002: Optional PUREBRAIN_BEHIND_CLOUDFLARE Constant

**Finding**: `purebrain_get_client_ip()` unconditionally trusted `HTTP_CF_CONNECTING_IP`.
An attacker hitting the origin server directly (bypassing Cloudflare) could spoof this header
and defeat the rate limiter by using a different IP per request.

**What changed**:
- `purebrain_get_client_ip()` now checks `defined('PUREBRAIN_BEHIND_CLOUDFLARE') && PUREBRAIN_BEHIND_CLOUDFLARE`
  before trusting `HTTP_CF_CONNECTING_IP`
- If constant is not defined, falls back directly to `$_SERVER['REMOTE_ADDR']`
- To enable Cloudflare trust, add to wp-config.php:
  `define( 'PUREBRAIN_BEHIND_CLOUDFLARE', true );`

**Migration note**: Both purebrain.ai and jareddsanborn.com ARE behind Cloudflare, so both
sites need `define( 'PUREBRAIN_BEHIND_CLOUDFLARE', true )` added to their wp-config.php
BEFORE deploying v3.8.0 — otherwise rate limiting will use REMOTE_ADDR (the Cloudflare edge
IP, not the real user IP) and rate limiting will be effectively broken.

**Location in file**: `purebrain_get_client_ip()` function, ~line 415-430

---

## Important Deployment Note

**Both sites need wp-config.php update before v3.8.0 deploys.**

Add to each site's wp-config.php:
```php
define( 'PUREBRAIN_BEHIND_CLOUDFLARE', true );
```

Without this, rate limiting breaks post-deploy (all requests hit the same Cloudflare edge IP,
the rate limiter counts them together and blocks legitimate users way too early).

---

## Files Modified

- `tools/security/purebrain-security/purebrain-security-plugin.php` (version 3.7.0 → 3.8.0)

## Files NOT Modified

- `tools/security/purebrain-security.zip` (stale, needs rebuild before deploy)
- Deploy scripts (unchanged, still work the same way)
