# Plugin v2.9.0 + Additional CSS Fix Deployment

**Date**: 2026-02-21
**Type**: operational
**Topic**: Subscribe button hover fix deployment - plugin v2.9.0 + Additional CSS narrowing

## What Was Deployed

### Plugin v2.9.0 (`tools/security/purebrain-security-plugin.php`)
- Added `initSubscribeLinks()` JS function that tags subscribe/newsletter links with `data-pb-subscribe="1"` attribute
- Added high-specificity CSS rule targeting `[data-pb-subscribe]` on hover
  - Specificity 0,5,3 vs conflicting rule's 0,3,3 - wins definitively
  - Orange box-shadow: `rgba(241, 66, 11, 0.3)` (not blue glow)
  - `transform: none !important` (no translateY lift)
- Root cause of the bug: Additional CSS (`wp-custom-css`) loads AFTER plugin CSS in `<head>`, so broad `body.single-post .blog-cta-block a:hover` rule won at equal specificity

### Additional CSS Fix (`tools/security/deploy_additional_css_fix.py`)
- Narrowed the `body.single-post .blog-cta-block a:hover` rule to `a[href*="awakening"]:hover` only
- The broad rule was matching BOTH the CTA button AND subscribe links
- Now CTA button gets blue glow, subscribe link gets orange (plugin CSS)

## Issues Encountered

### Issue 1: fetch_current_css() returned 403
- Script used `no-cache` / `Pragma: no-cache` headers
- Cloudflare's bot protection blocks requests with those headers
- Fix: Use browser-like `User-Agent` + `Accept` headers instead
- The `Cache-Control: no-cache` header triggered Cloudflare WAF 403

### Issue 2: Playwright screenshot timeout on Customizer
- WordPress Customizer is heavy - fonts take >30 seconds to load
- `page.screenshot()` default timeout is 30000ms - not enough
- Fix: Wrap screenshots in try/except, pass `timeout=60000`
- The actual CSS save succeeded - screenshot was just for documentation

## Key Files
- Plugin: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php`
- Plugin deployer: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v290.py`
- CSS deployer: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_additional_css_fix.py`

## Verification Results (Both Passed)
- Plugin: 17/17 content checks, 8/8 live page checks
- Additional CSS: 5/5 validation checks, 4/4 live verification checks
- Live URL: https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/

## Pattern: Two-Layer CSS Fix
When a plugin CSS rule is being beaten by Additional CSS at equal specificity:
1. Belt: Add JS attribute + high-specificity attribute selector in plugin CSS
2. Suspenders: Narrow the Additional CSS rule to not match the element you're fixing
Both together = bulletproof - neither can be overridden by the other anymore.
