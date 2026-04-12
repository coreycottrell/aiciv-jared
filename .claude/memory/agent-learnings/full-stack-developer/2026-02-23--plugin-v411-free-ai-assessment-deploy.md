# Plugin v4.1.1 Deploy — TEST 20 Free AI Assessment Nav Label

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: operational

## What Was Done

Deployed purebrain-security-plugin.php v4.1.1 to purebrain.ai.

TEST 20: Changed blog nav label "AI Assessment" → "Free AI Assessment" in the injected nav menu.

## Changes Made (Local File)

File: `tools/security/purebrain-security/purebrain-security-plugin.php`

1. Version bumped: `4.1.0` → `4.1.1`
2. Changelog entry added for TEST 20 (lines 17-21)
3. Plugin description updated: "Free AI Assessment" nav label
4. Comment line 1865: "AI Assessment" → "Free AI Assessment"
5. CSS comment line 1889: "AI Assessment" → "Free AI Assessment"
6. Nav JS line ~3293 was already "Free AI Assessment" (set in prior session)

Old v2.4.0 changelog entry kept as historical reference (fine to leave as-is).

## Deployment Result

- Playwright deploy: SUCCESS (GoDaddy SSO overlay handled, CodeMirror set)
- Elementor cache: HTTP 403 (expected with app password auth)
- Page cache bust: HTTP 403 (expected — WP REST API posts endpoint needs different auth)
- Live verification: 4/4 checks PASSED

## Verification Checks

- `https://purebrain.ai/the-ai-trust-gap/` → "Free AI Assessment" present
- `https://purebrain.ai/category/ai-strategy/` → "Free AI Assessment" present
- `https://purebrain.ai/blog/` → No nav injection (expected — not is_single/is_category)

## Key Pattern: 403 on App Password for Post Touch

The `bust_page_cache()` function using `POST /wp-json/wp/v2/posts/{id}` returns 403 with the Playwright auth (regular WP password). This is because the regular WP admin password used for Playwright is NOT the REST API app password. The app password (`PUREBRAIN_WP_APP_PASSWORD` in .env) is what works for REST API.

**Fix for future**: Use app password (from .env `PUREBRAIN_WP_APP_PASSWORD`) for REST API calls, NOT the WP admin password from the plugin editor login.

Despite the 403s, the live page showed the updated nav text immediately — likely because GoDaddy's cache respects the no-cache headers in the verification request.

## Deploy Script

`tools/security/deploy_plugin_v411_purebrain.py`

## Screenshots

- Deploy: `exports/screenshots/plugin_v411_purebrain_deploy.png`
- Verify: `exports/screenshots/plugin_v411_purebrain_verify.png`
