# Footer Logo Brand Fix - v3.0.0

**Date**: 2026-02-21
**Type**: operational
**Topic**: Replacing "Pure Brain" plain text footer logo with color-coded PUREBRAIN.AI on all pages

---

## Problem

Footer of purebrain.ai showed "Pure Brain" in plain white text inside `div.footer-logo h4`.
This is a theme-level element (Artistics theme) that appears on every page.

## Root Cause

The footer logo text comes from the theme's footer template, rendered as:
```html
<div id="site-footer" class="footer" role="contentinfo">
  <div class="footer-main">
    <div class="container">
      <div class="col-lg-5">
        <div class="footer-logo">
          <h4>Pure Brain</h4>   <!-- TARGET -->
        </div>
```

The WordPress Site Title (`blogname`) is "Pure Brain" but this specific text is hardcoded in the theme template. We cannot change it directly without theme file editing (risky). The correct approach is JS injection.

## Solution

Added a new `wp_footer` action to purebrain-security-plugin.php (priority 30, no page conditional) that:
1. Fires on ALL pages site-wide
2. Finds `div.footer-logo h4` (with 3 fallback selectors for resilience)
3. Replaces innerHTML with color-coded spans
4. Guards against double-execution with `.pb-logo-brand` check

## Brand Color Rules (NON-NEGOTIABLE)

```
PUREBR = #2a93c1 (blue)
AI     = #f1420b (orange)
N      = #2a93c1 (blue)
.AI    = #ffffff (white on dark background)
```

## Implementation

In `tools/security/purebrain-security-plugin.php`:

```php
add_action( 'wp_footer', function () {
    ?>
<script id="purebrain-footer-logo-brand">
(function() {
    'use strict';
    function brandFooterLogo() {
        var logoEl = document.querySelector('.footer-logo h4, #site-footer .footer-logo h4, footer .footer-logo h4');
        if (!logoEl) return;
        if (logoEl.querySelector('.pb-logo-brand')) return;
        logoEl.innerHTML =
            '<span class="pb-logo-brand" style="font-size:inherit;font-weight:inherit;letter-spacing:inherit;">' +
            '<span style="color:#2a93c1;">PUREBR</span>' +
            '<span style="color:#f1420b;">AI</span>' +
            '<span style="color:#2a93c1;">N</span>' +
            '<span style="color:#ffffff;">.AI</span>' +
            '</span>';
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', brandFooterLogo);
    } else {
        brandFooterLogo();
    }
})();
</script>
    <?php
}, 30 );
```

## Deployment

- Plugin bumped from v2.9.0 to v3.0.0
- Deployed via: `tools/security/deploy_plugin_v300.py`
- All 19 validation checks passed
- All 3 live page types verified: blog post, homepage, blog index

## Key Files

- Plugin: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php`
- Deploy script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v300.py`
- Deploy screenshot: `exports/screenshots/plugin_v300_deploy.png`
- Verify screenshot: `exports/screenshots/plugin_v300_verify.png`

## Notes

- Priority 30 ensures it runs after all other footer hooks
- The `font-size:inherit; font-weight:inherit; letter-spacing:inherit;` on the parent span preserves the original h4 typography
- The selector triple-checks `'.footer-logo h4, #site-footer .footer-logo h4, footer .footer-logo h4'` for maximum resilience
- Works on ALL page types: homepage, blog index, single posts, archives, static pages

## Lesson

When theme-level text needs branded color coding, JS injection via the plugin's `wp_footer` hook with no page conditional is the right approach. CSS alone cannot change text colors for specific characters within a text node - JS DOM manipulation is required.
