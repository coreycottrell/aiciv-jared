# Memory: Blog Post Featured Image Padding Fix - v1.7.0 Final Solution

**Date**: 2026-02-20
**Type**: teaching + operational
**Agent**: full-stack-developer
**Topic**: Why previous CSS wasn't visible + how v1.7.0 fixed it for both sites

---

## Problem Summary

Jared reported: "Blog post featured images have NO padding on desktop. The image goes edge-to-edge."

Screenshot timestamp: 13:09 (photo_20260220_130932.jpg)

---

## Root Cause Analysis

### Why Previous Attempts Failed

1. **v1.5.0 CSS** (padding: 5%): Deployed to server but Cloudflare was caching an even older page
2. **v1.6.0 CSS** (max-width: 820px, padding: 40px): Written to LOCAL file but server still ran v1.5.0
3. **v1.7.0 CSS** (max-width: 760px, padding: 60px, box-shadow): Written to LOCAL file but NEVER DEPLOYED

**The plugin deployment chain was broken**: local file was updated but not deployed to server.

### What the CSS DOES on the Server

Before fix (v1.6.0 live):
- Container: max-width 1100px with 40px padding each side = 1020px inner width
- .post-single-image: max-width 820px, auto-centered
- At 1440px viewport: image left=310px from viewport edge
- Cloudflare was still serving old cached version (cf-cache-status: HIT)

After fix (v1.7.0 deployed):
- Container: max-width 1100px with 60px padding (80px at 1400px+) = 980px inner width
- .post-single-image: max-width 760px, auto-centered, box-shadow
- At 1440px viewport: image left=340px from viewport edge
- Cloudflare cache flushed (cf-cache-status: MISS)

---

## purebrain.ai Fix

### Method: Plugin Editor via Playwright (v1.7.0)

Script: `tools/security/deploy_plugin_v170.py`

1. Login to WP Admin
2. Open Plugin Editor at plugin-editor.php
3. Set plugin content via CodeMirror setValue()
4. Click Save
5. Navigate to Settings > General to get flush cache nonce
6. Execute GoDaddy cache flush URL
7. Verify via HTTP request (bypass CDN with no-cache headers)

### CSS Changes in v1.7.0

```css
@media (min-width: 1025px) {
    body.single-post .page-single-post {
        padding-top: 20px !important;
    }
    body.single-post .page-single-post .container {
        max-width: 1100px !important;
        padding-left: 60px !important;  /* was 40px in v1.6.0 */
        padding-right: 60px !important;
        box-sizing: border-box !important;
    }
    body.single-post .post-single-image {
        max-width: 760px !important;   /* was 820px */
        margin-left: auto !important;
        margin-right: auto !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        display: block !important;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.55), 0 0 0 1px rgba(255, 255, 255, 0.07) !important;
    }
}
@media (min-width: 1400px) {
    body.single-post .page-single-post .container {
        padding-left: 80px !important;
        padding-right: 80px !important;
    }
}
```

### Verification Results

At 1440px:
- Image left from viewport: 340px ✓
- Image right from viewport: 340px ✓
- Image max-width: 760px ✓
- Box-shadow: present ✓
- CSS version: v1.7.0 ✓
- Cloudflare cache: MISS (fresh) ✓

---

## jareddsanborn.com Fix

### Site Structure (Divi theme)

jareddsanborn.com uses **Divi theme** (NOT Artistics theme like purebrain.ai).

HTML structure:
```
article.et_pb_post
  .et_post_meta_wrapper
    h1.entry-title
    p.post-meta
    <img> ← bare img, NO wrapper div like .post-single-image!
  .entry-content
```

The featured image has NO `.post-single-image` wrapper - it's a bare `<img>` tag.

### Deployment Method: REST API Content Injection

Since jareddsanborn.com only has REST API Application Password (no browser login password stored), could NOT use Playwright Customizer approach.

**Solution**: Inject `<style>` block into each post's content via REST API.

```python
# Get posts with context=edit to access raw content
GET /wp-json/wp/v2/posts/{id}?context=edit
# Update with prepended <style> block
POST /wp-json/wp/v2/posts/{id}
  {"content": "<style>...</style>\n\n{existing_content}"}
```

CSS used:
```css
@media (min-width: 1025px) {
    body.single-post article.et_pb_post .et_post_meta_wrapper > img,
    body.single-post .et_post_meta_wrapper img.wp-post-image {
        max-width: 760px !important;
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
        margin-bottom: 40px !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4) !important;
    }
}
```

Updated 8 posts successfully.

### Verification Results at 1440px

- Image width: 760px (was 811px unconstrained)
- Border-radius: 16px ✓
- Box-shadow: present ✓
- Left margin from viewport: 205px (sidebar shifts it right)
- CSS block present in DOM: ✓

---

## Key Lessons

### 1. Plugin Update ≠ Plugin Deploy

Just writing the plugin file locally does NOT update the server.
Must run the deploy script to push to WP plugin editor.

**Always verify live CSS value matches local file after writing.**

### 2. Cloudflare Cache is 31-Day

After deploying the plugin, Cloudflare may serve a cached old version for UP TO 31 DAYS.
Must flush GoDaddy cache after every plugin/CSS update.

**Cache flush URL pattern**:
`/wp-admin/options-general.php?wpaas_action=flush_cache&wpaas_nonce=NONCE`
Nonce obtained from: `document.querySelectorAll('a')` → find "Flush Cache" link

### 3. Verify with Computed Styles, Not Just Source

Source check confirms CSS text is present. Computed styles confirm CSS is APPLIED.
Use `window.getComputedStyle(element)` and `getBoundingClientRect()` in Playwright.

### 4. jareddsanborn.com Has Different HTML Structure

- purebrain.ai (Artistics theme): `.post-single-image > figure > img`
- jareddsanborn.com (Divi theme): `.et_post_meta_wrapper > img` (bare img!)

CSS selectors must be different for each site.

### 5. jareddsanborn.com Authentication Limitation

WORDPRESS_APP_PASSWORD = REST API only (Application Password)
Browser login password = not stored in .env

For CSS that needs Customizer, inject via post content instead.

---

## Files

- Plugin: `tools/security/purebrain-security-plugin.php` (v1.7.0)
- Deploy script: `tools/security/deploy_plugin_v170.py`
- Jared deploy: `tools/deploy_jared_blog_padding.py` (CSS via content injection)
- Screenshots:
  - `exports/screenshots/plugin_v170_live.png` (purebrain.ai after fix)
  - `exports/screenshots/purebrain_blog_FIXED_1440px.png` (final purebrain.ai)
  - `exports/screenshots/jared_blog_FIXED_1440px.png` (final jareddsanborn.com)
