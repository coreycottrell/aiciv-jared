# Memory: Blog Desktop Padding v1.6.0 Deployment & CDN Fix

**Date**: 2026-02-20
**Type**: teaching + operational
**Agent**: full-stack-developer
**Topic**: Why v1.5.0 padding wasn't visible + how v1.6.0 fixed it

---

## Problem Diagnosed

- Plugin v1.5.0 was live on server with `padding-left: 5%` on `.container`
- Previous session verified 72px padding at 1440px (5% * 1440 = 72px)
- But Jared reported padding looked unchanged

## Root Cause: Server/CDN Version Mismatch

- Plugin v1.6.0 was written to LOCAL file but NEVER deployed to server
- Server was running v1.5.0 (old CSS with 5% approach)
- **The 5% approach was actually working** - but may have been visually subtle
- v1.6.0 uses much more direct approach: constrains `.post-content` and `.post-single-image` to `max-width: 820px` directly

## v1.6.0 CSS Changes (More Direct Approach)

```css
@media (min-width: 1025px) {
    /* Container: cap width */
    body.single-post .page-single-post .container {
        max-width: 1100px !important;
        padding-left: 40px !important;
        padding-right: 40px !important;
        box-sizing: border-box !important;
    }
    /* CRITICAL: Reset Bootstrap row negative margins */
    body.single-post .page-single-post .container > .row {
        margin-left: 0 !important;
        margin-right: 0 !important;
    }
    /* CRITICAL: Reset Bootstrap col gutters */
    body.single-post .page-single-post .container > .row > .col-md-12 {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    /* Directly constrain content to 820px */
    body.single-post .post-content {
        max-width: 820px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    body.single-post .post-single-image {
        max-width: 820px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        border-radius: 12px !important;
    }
}
```

**Key insight**: Directly constraining `.post-content` and `.post-single-image` is more visually obvious than constraining the parent container. Bootstrap's row/col gutter system was eating the container padding.

## Deployment Method: Plugin Editor via Playwright

- Script: `tools/security/deploy_plugin_v160.py`
- Login URL: `https://purebrain.ai/wp-login.php`
- Plugin editor: `https://purebrain.ai/wp-admin/plugin-editor.php?file=purebrain-security/purebrain-security-plugin.php&plugin=...`
- CodeMirror detection: `page.evaluate("() => !!document.querySelector('.CodeMirror')")`
- CodeMirror set: `page.evaluate("(content) => { document.querySelector('.CodeMirror').CodeMirror.setValue(content); }", content)`
- Wait: Use `domcontentloaded` NOT `networkidle` after save click (networkidle times out)

## CDN Cache Issue: TWO LAYERS

1. **GoDaddy gateway cache**: Shows `x-gateway-cache-status: MISS` (transparent)
2. **Cloudflare CDN**: Shows `cf-cache-status: HIT` (31-day cache!)

**Cache bypass**: `?nocache=TIMESTAMP` in URL bypasses Cloudflare and shows origin content.

**GoDaddy Flush Cache URL** (found in WP admin > Settings > General):
```
https://purebrain.ai/wp-admin/options-general.php?wpaas_action=flush_cache&wpaas_nonce=NONCE
```
Nonce is short-lived - must be obtained fresh per WP session. Found by:
```js
const links = Array.from(document.querySelectorAll('a'));
links.find(a => /flush.cache/i.test(a.textContent))
```

**After ~30-60 sec wait**: Cloudflare cache evicts naturally and serves fresh content.

## Verification Results (v1.6.0 live)

At 1440px viewport:
- Container max-width: 1100px ✓
- Container padding-left: 40px ✓
- Row margin-left: 0px ✓ (Bootstrap gutters reset)
- Post-content max-width: 820px ✓
- Post-content margin-left: 100px (auto-centered) ✓
- Post-single-image max-width: 820px ✓
- Post-single-image border-radius: 12px ✓

## Rate Limiting Warning

- WP login rate limit: GoDaddy blocks after ~3-4 rapid login attempts (429)
- After 429: wait 2-3 minutes before retrying
- Playwright sessions DO NOT persist cookies between runs
- Each Playwright run = fresh login attempt

## Files

- Plugin: `tools/security/purebrain-security-plugin.php` (v1.6.0)
- Plugin dir: `tools/security/purebrain-security/purebrain-security-plugin.php`
- Zip: `tools/security/purebrain-security.zip` (rebuilt with Python zipfile)
- Deploy script: `tools/security/deploy_plugin_v160.py`
- Screenshots: `exports/screenshots/blog_padding_FINAL.png`
