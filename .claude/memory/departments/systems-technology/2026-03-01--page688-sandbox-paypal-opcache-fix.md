# Page 688 Sandbox PayPal Fix — OPcache + Self-Sufficient Strategy

**Date**: 2026-03-01
**Type**: gotcha + pattern
**Agent**: dept-systems-technology

---

## What Was Fixed

Page 688 (pay-test-sandbox-2) had a PayPal conflict:
- Black overlay showed but no PayPal modal appeared
- Root cause: Plugin's n4 section (pb-sandbox-override) conflicted with page's own SDK loading
- n4 called `delete window.paypal` (clearing pre-loaded sandbox SDK) then reloaded it
- Race condition caused button render failure

## What We Did

### Step 1: Plugin fix (is_page(0) to disable n4)
- Local file `exports/purebrain-security-plugin-v473-bypass-fix.php` already had `is_page(0)`
- Same as `exports/purebrain-security-plugin-v473.php` (in sync)
- Deployed via `tools/security/deploy_rollback_v473.py` (Playwright)
- Deploy reported SUCCESS but OPcache served old bytecode

### Step 2: OPcache issue — critical learning
- GoDaddy has `opcache.validate_timestamps = Off` (or very long revalidation)
- Plugin file correct on disk and in WP editor textarea but old bytecode ran
- Deactivate/reactivate via REST API did NOT invalidate OPcache immediately
- PATCH endpoint (`/wp/v2/plugins/{slug}`) with `source` field returned 200 but no effect
- WP login CAPTCHA triggered (429) after multiple Playwright login attempts — blocks for ~15 min
- `wpaas/v1/flush-cache` returns 403 for app password auth (requires admin session)
- **Solution**: Multiple deactivate/reactivate cycles + waiting ~15 min for OPcache TTL to expire

### Step 3: Page 688 self-sufficient fix (elementor_data)
- Verified: page 688 already had sandbox SDK URL and blank PLAN_IDS in _elementor_data
- Added `window.paypal.__sandboxLoaded = true` in `script.onload` handler
- This prevents n4 from clearing the pre-loaded SDK: `if (window.paypal && window.paypal.__sandboxLoaded) { return resolve(); }`
- Change: `script.onload = onLoad;` → `script.onload = function() { if(window.paypal) { window.paypal.__sandboxLoaded = true; } onLoad(); }; /* pb-sandbox-compat */`
- PUT to WP REST API `/wp/v2/pages/688` with `meta._elementor_data`
- Cleared Elementor cache after

## Key Technical Learnings

### GoDaddy OPcache
- `opcache.validate_timestamps` may be Off — file changes don't take effect immediately
- File writes succeed (textarea confirms), but PHP runs old bytecode
- Multiple deactivate/reactivate cycles + time is the fix
- `wpaas/v1/flush-cache` exists but requires admin session auth (not app password)

### n4 Plugin Override Conflict Pattern
- When plugin wp_footer script AND page widget both load the same SDK, race condition occurs
- n4's `loadSandboxSDK()` deletes `window.paypal` if `__sandboxLoaded` is not set
- Fix: set `window.paypal.__sandboxLoaded = true` in the page's SDK onload callback

### Page 688 Password Protection
- Page 688 is password-protected (`PureBrain.ai253443$$$`)
- Must submit password via `POST /wp-login.php?action=postpass` to get cookie
- Without cookie, Elementor renders only the password form (132K chars instead of 606K)
- Verification must include password cookie for correct results

### Elementor Cache
- `DELETE /wp-json/elementor/v1/cache` works with app password auth
- After clearing, pages re-render from `_elementor_data` on next request
- Elementor renders even password-protected content to authenticated users

## Files Modified
- `exports/purebrain-security-plugin-v473-bypass-fix.php` — is_page(0) in n4 section (pre-existing)
- `exports/purebrain-security-plugin-v473.php` — identical (pre-existing)
- Page 688 `_elementor_data` — added `window.paypal.__sandboxLoaded = true` in SDK onload

## Verification Results
- Page 688 (with password): pb-sandbox-override GONE, sandbox SDK present, PLAN_IDS blank, pb-sandbox-compat fix present
- Page 689: pb-sandbox-override GONE, sandbox.paypal.com NOT present (production untouched)
- Homepage: pb-sandbox-override GONE, sandbox.paypal.com NOT present
