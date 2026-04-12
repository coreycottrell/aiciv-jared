# Speed Optimization: purebrain.ai Homepage (2026-03-04)

## Summary
Identified and fixed major speed issues on purebrain.ai. Key pattern: self-referential Elementor widget embedding.

## Root Cause Found
Elementor HTML widget `292c72a` on homepage (page ID 11) contained the ENTIRE rendered WordPress page as HTML (328KB) embedded inside itself. This created:
- 3 nested DOCTYPE documents
- 14 duplicate script IDs
- 29 script tags instead of 16

## Fixes Deployed
1. **Plugin v4.8.2**: Added preconnect + dns-prefetch hints for 6 external domains (Google Fonts, PayPal, WonderPush, CDN, APIs). Priority 2 wp_head hook.
2. **Widget cleanup**: Replaced 328KB self-referential widget with 245KB clean chatbox HTML.

## Results
- Page: 490KB → 408KB (17% smaller)
- DOCTYPEs: 3 → 1
- Script duplicates: 14 → 0
- Preconnect hints: 0 → 6
- All functionality preserved

## Deployment Method
- Plugin: Playwright browser automation via `deploy_plugin_v480_purebrain.py` pattern (login → plugin editor → CodeMirror setValue → submit)
- Elementor data: `PUT /wp-json/wp/v2/pages/11` with updated `_elementor_data` meta, then `DELETE /wp-json/elementor/v1/cache`

## Files
- Plugin: `exports/purebrain-security-plugin-v482.php`
- Widget backup: `exports/widget-292c72a-original-backup.html`
- Clean widget: `exports/widget-292c72a-clean-v2.html`
- Report: `exports/speed-optimization-audit-2026-03-04.md`

## Remaining Recommendations (Need Jared Approval)
- WP caching plugin (no caching plugin active at all!)
- Image WebP conversion
- Defer Brevo/WonderPush scripts
- Evaluate if Independent Analytics overlaps with GA4
