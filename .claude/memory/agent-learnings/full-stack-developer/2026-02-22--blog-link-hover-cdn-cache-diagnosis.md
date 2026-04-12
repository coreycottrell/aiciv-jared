# Blog In-Text Link Hover Fix: CDN Cache Root Cause Analysis

**Date**: 2026-02-22
**Type**: teaching
**Topic**: Why Jared saw orange-on-orange hover even though the fix was deployed; CDN cache anatomy

---

## Problem Summary

Jared reported blog post in-text links still showed orange text on orange background on hover
even after the v3.9.1/v3.9.2 fix was deployed via REST API content injection.

## Root Cause: Layered Cache System (3 Layers)

### Layer 1: WordPress/PHP (server) — FRESH, always correct
- The raw post content (`context=edit`) has `pb-link-hover-v392` in all 9/10 posts per site
- Fresh WordPress renders output the correct CSS
- Bypassing CDN via `?nocache=1` query string shows `CF=DYNAMIC` with the fix present

### Layer 2: Cloudflare CDN cache — STALE (this was the problem)
- `CF-Cache-Status: HIT` with `Age: 83` to `2040` seconds
- Serving HTML cached BEFORE the style block injection ran
- `Last-Modified: Sun, 22 Feb 2026 15:34:20 GMT` — the cached timestamp
- `Cache-Control: public, max-age=2678400` (31-day TTL)
- Cloudflare cache CANNOT be purged programmatically without API credentials (not in .env)
- GoDaddy's `/wp-json/wpaas/v1/flush-cache` needs wp-admin session nonce auth (not app password)

### Layer 3: Browser cache — STALE (this is what Jared sees)
- Jared's browser cached the CDN-cached version
- Even after CDN refreshes, browser holds it for up to 31 days
- Fix: hard refresh (`Cmd+Shift+R` Mac / `Ctrl+Shift+R` Win)

## What Approach 1 Actually Did

Elementor cache clear (`DELETE /wp-json/elementor/v1/cache`) returned HTTP 200.
This cleared Elementor's PHP rendering cache, but NOT Cloudflare's CDN HTML cache.
These are completely different cache layers.

## The v3.9.2 Fix (Already Deployed By Previous Session)

Previous agent session already upgraded from v3.9.1 to v3.9.2 with CORRECT selectors:
- v3.9.1 used `.entry-content` which does NOT exist in the rendered DOM for this theme
- v3.9.2 uses `.post-content` (the actual theme class) + `.entry-content` (fallback) + Elementor wrapper
- Also improved exclusion: `not([href*="awakening"])` instead of `not(.blog-cta-button)`

CSS that is deployed (v3.9.2):
```css
body.single-post .post-content a:not([href*="awakening"]):not([rel="tag"]):not(.aether-transparency__cta-btn):hover,
body.single-post .entry-content a:not([href*="awakening"]):not([rel="tag"]):not(.aether-transparency__cta-btn):hover,
body.single-post .elementor-widget-theme-post-content a:not([href*="awakening"]):not([rel="tag"]):not(.aether-transparency__cta-btn):hover {
    background-color: #f1420b !important;
    color: #ffffff !important;
    ...
}
```

## Verification Results (All 19 Posts)

**purebrain.ai (9 posts)**: ALL have v3.9.2 in raw content
**jareddsanborn.com (10 posts)**: ALL have v3.9.2 in raw content

CDN-bypassed verification (`?nocache=1`): ALL posts show correct CSS in rendered HTML.

## Resolution For Jared

The fix IS deployed server-side. Jared needs to:
1. **Hard refresh**: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows) on any blog post
2. OR open blog post in incognito/private window (always gets fresh copy)
3. OR wait ~30 minutes for CDN cache to expire naturally

For permanent CDN purge without manual process: Jared needs to log into Cloudflare dashboard
and go to Caching → Purge Everything. We don't have Cloudflare API credentials in .env.

## Plugin v3.9.1 Deploy Status

Plugin v3.7.0 is still live (couldn't update via Playwright — admin password changed/invalid,
CAPTCHA present, REST API doesn't support custom plugin file upload).

The REST API content injection approach (style block in post content) is the working method
and will continue to work since all posts have v3.9.2 injected.

## Key Diagnostic Commands

```bash
# Check if CDN is caching (HIT = stale, DYNAMIC = fresh from PHP)
curl -sI https://purebrain.ai/the-ai-trust-gap/ | grep -i 'CF-Cache-Status\|Age\|Last-Modified'

# Bypass CDN to get fresh PHP output
curl -s 'https://purebrain.ai/the-ai-trust-gap/?nocache=1' | grep 'pb-link-hover'

# Check raw post content (context=edit gives raw)
# GET /wp-json/wp/v2/posts/631?context=edit → content.raw
```

## Password Status (Feb 2026)

- `PUREBRAIN_WP_APP_PASSWORD` in .env: WORKS for REST API (200 OK)
- `PUREBRAIN_WP_PASSWORD` in .env: FAILS for wp-login.php (Invalid credentials)
- Admin password has changed. Need Jared to update `PUREBRAIN_WP_PASSWORD` in .env.
- CAPTCHA is also present on purebrain.ai login page (appears after SSO toggle click)

## Files

- Deploy script: `tools/security/deploy_plugin_v391.py` (created, covers both v391 and REST injection)
- Plugin file: `tools/security/purebrain-security/purebrain-security-plugin.php` (v3.9.1, ready for deploy)
- Style block ID in posts: `pb-link-hover-v392`
