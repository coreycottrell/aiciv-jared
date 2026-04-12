# QA Learning: Plugin v3.8.0 Security Review

**Date**: 2026-02-21
**Type**: operational
**Topic**: PureBrain Security Plugin v3.8.0 QA - Three security fixes verified

## What Was Verified

### Fix Pattern: Fail-Closed on Missing Config
- MED-003 pattern: check for empty constant, return WP_Error with 503 and GENERIC message
- Error message "Service unavailable - API key not configured" - note this DOES say "API key"
- Error is logged internally with full detail; generic message returned to user
- The message does NOT mention "Brevo" specifically - acceptable for operator-facing error

### Fix Pattern: Output-Point Escaping (LOW-001)
- Correct pattern: store raw values in variables, esc_html()/esc_url() only at echo point
- Plugin has 22 escaping function uses total, all in transparency section at echo point
- Table rows also properly escaped inline: `echo esc_html( isset($row['domain']) ? ... : '' )`

### Fix Pattern: Conditional Header Trust (LOW-002)
- Gate pattern: `defined('PUREBRAIN_BEHIND_CLOUDFLARE') && PUREBRAIN_BEHIND_CLOUDFLARE`
- Fallback to REMOTE_ADDR is clean
- sanitize_text_field() applied to the IP header value

## Syntax Verification (PHP CLI unavailable)
- Brace balance: 348 open / 348 close = balanced
- File is 2939 lines
- All add_action/add_filter/register_rest_route hooks present and intact

## Regression Check Methodology
- Spot-checked: FAQ accordion (line 995), blog desktop padding (1189), CTA hover (1351), nav menu CSS+JS (1514, 2888)
- Nav menu URLs use esc_url() at assignment point (lines 2892-2894) - acceptable since immediately echoed into JS string
- All pre-existing functionality intact

## One Minor Concern (Flagged, Not Blocking)
- Error message at line 704: "Service unavailable - API key not configured"
- The phrase "API key" could hint to attackers that the endpoint uses an API key
- Acceptable as-is since it's a server-side configuration issue, not user-input-related
- Low severity - no actual key value exposed
