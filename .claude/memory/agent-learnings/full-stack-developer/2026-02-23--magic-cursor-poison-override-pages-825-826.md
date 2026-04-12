# Magic Cursor Poison Override - Pages 825 and 826

**Date**: 2026-02-23
**Type**: operational
**Topic**: WordPress Additional CSS [class*="magic"] poison fix for pages 825 and 826

## Root Cause

WordPress Additional CSS has a rule:
```css
[class*="magic"] {
    color: #f1420b !important;
    background-color: #f1420b !important;
}
```
The Artistics theme adds `tt-magic-cursor` to the `<body>` tag, so `[class*="magic"]` matches the body. This sets both text AND background to orange - rendering everything invisible.

## Two-Layer Fix Applied

### Layer 1: Inline CSS in Page Content (loads after Additional CSS)
Both pages 825 and 826 have a `<style id="magic-cursor-fix">` block at the TOP of their wp:html content with:
```css
html body {
  background-color: #0a0e1a !important;
  color: #e8edf5 !important;
}
```
Using `html body` (specificity 0,0,2) - lower than `[class*="magic"]` (0,1,0) BUT wins because !important with later load order. This style appears at position ~93000 in the page, after Additional CSS at position ~26000.

### Layer 2: Plugin Footer Override (v4.9.0)
The `purebrain-security` plugin at wp_footer priority 99 injects:
```css
body.page-id-825.tt-magic-cursor { background-color: #0a0e1a !important; }
body.page-id-826.tt-magic-cursor { background-color: #0a0e1a !important; }
```
Specificity 0,2,1 beats `[class*="magic"]` (0,1,0). Loads absolutely last.

## Plugin Deployment Incident

During this fix, the plugin was accidentally deleted via:
```
DELETE /wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin
```
The REST API allows deleting active plugins!

### Recovery Process
1. Updated v4.8.0 → v4.9.0 locally at `tools/security/purebrain-security/purebrain-security-plugin.php`
2. Created zip: `python3 -c "import zipfile; zf = zipfile.ZipFile('/tmp/plugin.zip', 'w'); zf.write(src, 'purebrain-security/purebrain-security-plugin.php')"`
3. IMPORTANT: WP REST PUT endpoint for plugin upload doesn't work for custom plugins
4. Used wp-admin cookie auth to upload: POST to `/wp-admin/update.php?action=upload-plugin`
5. Activated via: GET to `/wp-admin/plugins.php?action=activate&...&_wpnonce={fresh_nonce}`
6. The nonce in the success response is stale - must GET a fresh plugins.php page to get valid nonce

## Cloudflare Cache Issue

Cloudflare CDN caches pages for up to 31 days. After plugin updates:
- Regular requests serve stale cached HTML
- Bypass with query param: `?nocache=$(date +%s)` 
- Proper purge via wpaas/v1/flush-cache endpoint (requires cookie auth)

## Page 826 Content Note

Someone or a previous agent session updated page 826 content at 23:24:33 with a `html body` approach (more robust than page-id-specific body class selectors since elementor_canvas may sometimes strip body classes).

## Files Modified
- `tools/security/purebrain-security/purebrain-security-plugin.php` - v4.8.0 → v4.9.0

## Verification Commands
```bash
# Fresh page check (bypasses CF cache)
curl -s "https://purebrain.ai/ai-website-execution/?nocache=$(date +%s)" | grep -o 'pb-magic-cursor-body-override'
curl -s "https://purebrain.ai/ai-website-execution/?nocache=$(date +%s)" | grep -o 'page-id-826'
```
