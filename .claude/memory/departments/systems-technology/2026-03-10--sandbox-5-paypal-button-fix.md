# sandbox-5 PayPal Button Fix
**Date**: 2026-03-10
**Pages**: pay-test-5 (1527) and pay-test-sandbox-5 (1528)

## Problem
Buttons on sandbox-5 called `openPayPalModal()` but that function was undefined on the page.
pay-test-5 (cloned from same source) worked fine.

## Root Cause
sandbox-5 was cloned from an EARLIER version of the source page, before the "PayPal Alias Fix"
script was embedded. That script is the bridge:

  window.openPayPalModal = window.openWaitlistModal

The PayPal IIFE sets up `openWaitlistModal` (and `openPayPalCheckout`) as the actual checkout
function. Without the alias, `openPayPalModal` is never defined, so buttons do nothing silently.

pay-test-5 had this fix embedded in its Elementor data + post_content.
sandbox-5 had empty `_elementor_data` (cloned without Elementor) and the fix was never present.

## What Was NOT the Issue
- No plugin was blocking sandbox-5 specifically
- All active plugins checked: Elementor, PureBrain Security v6.2.2, pb-content-gate,
  pb-lead-capture, WP File Manager — none targeted page 1528
- Security plugin PayPal routing only covered pages 688, 689, 11

## Fix Applied
Appended PayPal alias fix as `<!-- wp:html -->` block to sandbox-5 post_content via WP REST API
using Python requests (shell variable approach fails for 800KB+ payloads).

Script ID: `pb-paypal-alias-fix-1528`
Logic: 100ms delayed alias — if openWaitlistModal exists, alias it to openPayPalModal.
Fallback to openPayPalCheckout if needed.

## Verification
- WP REST API: Modified 2026-03-10T17:04:59, fix confirmed in rendered content
- Live page: CF-Cache-Status MISS, fix present in page source

## Security Plugin v6.2.8 (local only, not deployed)
Also updated local security plugin at:
  tools/security/purebrain-security/purebrain-security-plugin.php

Added wp_footer hook for pages 1527+1528 as a server-side safety net.
Could not deploy via REST API (WP plugin REST endpoint only works for wordpress.org plugins).
Needs manual SFTP/SSH deploy when available.

## Key Patterns
- WP REST API for large content: use Python requests, not curl shell variables
- Cloned pages may miss embedded JS fixes if cloned from pre-fix source
- Cloudflare cache can serve stale even after REST API update — check CF-Cache-Status
- `_elementor_data` empty + `_elementor_edit_mode` not 'builder' = page renders from post_content only
- NEVER set `_elementor_edit_mode: 'builder'` without valid `_elementor_data` (breaks page)
