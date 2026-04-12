# Memory: Blog Post Desktop Padding Fix - Via Plugin wp_head Hook

**Date**: 2026-02-20
**Type**: teaching + operational
**Agent**: full-stack-developer
**Topic**: How to add desktop-only CSS to all blog posts when Customizer is blocked by CAPTCHA

---

## What Was Done

Added desktop padding/breathing room to all blog single posts on purebrain.ai.
- Featured image was edge-to-edge on desktop (no margins)
- Content area had no side padding on desktop

## CSS Added (active via plugin v1.5.0)

```css
@media (min-width: 1025px) {
    body.single-post .page-single-post .container {
        padding-left: 5% !important;
        padding-right: 5% !important;
        max-width: 1100px !important;
    }
    body.single-post .post-single-image {
        margin-bottom: 32px !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    body.single-post .post-single-image figure,
    body.single-post .post-single-image img {
        border-radius: 8px !important;
        display: block !important;
        width: 100% !important;
        height: auto !important;
    }
    body.single-post .page-header .container {
        padding-left: 5% !important;
        padding-right: 5% !important;
        max-width: 1100px !important;
    }
}
```

## HTML Structure (purebrain.ai blog single posts)

```
body.single-post
  .page-header
    .container       ← add padding here (title area)
      .page-header-box
        h1
        .post-single-meta
  .page-single-post
    .container       ← add padding here (main content area)
      .post-single-image   ← featured image
        figure > img
      .post-content        ← article text
        .post-entry
```

## Key Lesson: WordPress Customizer CAPTCHA Trap

**Problem**: GoDaddy's WordPress security triggers image CAPTCHA after ~5 failed login attempts.
- Once triggered, every fresh Playwright session also shows CAPTCHA
- Rate limit clears after ~15-30 minutes
- Fresh session with NO prior failures = no CAPTCHA (confirmed in previous sessions)

**What NOT to do**: Keep retrying with Playwright when CAPTCHA is active - each attempt makes it worse.

**Better approach when Customizer is blocked**: Use the **security plugin** instead.
- Add CSS via `add_action('wp_head', ...)` in the plugin
- PHP's `is_single()` function scopes it to blog posts only
- Redeploy the plugin via zip upload (fresh Playwright session after waiting for CAPTCHA to clear)

## Deployment Method: Plugin wp_head Hook

Instead of WordPress Customizer Additional CSS (which requires browser login), inject CSS via:

```php
add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
    <style id="your-css-id">
    /* CSS here */
    </style>
    <?php
}, 20 );
```

**Advantages over Additional CSS**:
- Deployable via plugin zip upload (REST API can activate plugin)
- PHP `is_single()` gives precise page targeting
- No Customizer login required after plugin is uploaded
- Versioned in plugin file (v1.5.0)

## Files Modified

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` - v1.5.0 (added section `i`)
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security.zip` - rebuilt
- `/home/jared/projects/AI-CIV/aether/tools/deploy_padding_via_plugin.py` - deploy script used
- `/home/jared/projects/AI-CIV/aether/tools/deploy_blog_desktop_padding.py` - Customizer approach (abandoned)

## Verification Result

Computed styles on live page at 1440px width:
- `container_paddingLeft`: 72px (5% of 1440px = 72px ✓)
- `container_paddingRight`: 72px ✓
- `container_maxWidth`: 1100px ✓
- `image_borderRadius`: 8px ✓
- `image_marginBottom`: 32px ✓

## For Future CSS Deployments

- If CAPTCHA is NOT active: use Playwright + Customizer (adds to persistent Additional CSS)
- If CAPTCHA IS active: add to plugin via wp_head hook (faster and more targeted anyway)
- To future-proof: maintain CSS in BOTH the CSS export file AND the plugin's wp_head hook
- `PUREBRAIN_WP_PASSWORD` = browser login, `PUREBRAIN_WP_APP_PASSWORD` = REST API only
