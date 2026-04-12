# Memory: Blog Color Fix — Magic Cursor Override Extended to Single Posts

**Date**: 2026-02-24
**Type**: teaching
**Topic**: Root cause + fix for blog color scheme issue after v5.0.1 rollback

---

## Problem Summary

Jared reported blog color scheme still wrong after v5.0.1 rollback (which removed the j5 CSS hook).
The v5.0.1 rollback DID successfully deploy (confirmed by page source inspection - no `purebrain-inline-cta-white-text-v501` in live HTML).

A second, deeper issue was discovered:

## Root Cause Found

**The Additional CSS (wp-custom-css) has this rule:**
```css
[class*="magic"] {
    color: #f1420b !important;
    background-color: #f1420b !important;
    border-color: #f1420b !important;
}
```

**The Artistics theme adds `tt-magic-cursor` class to `<body>` on ALL page types**, including single blog posts (template: `post-template-default`).

**CSS Specificity battle:**
- `[class*="magic"]` = attribute selector = (0,1,0,0) in CSS specificity
- `body.single-post` = class + element type = (0,0,1,1)

(0,1,0,0) is MORE SPECIFIC than (0,0,1,1)! So `[class*="magic"]` beats `body.single-post` rules, making the body background orange.

**Previous fix was incomplete:** The `pb-magic-cursor-body-override` CSS block ran via `wp_footer` at priority 99, but ONLY for `elementor_canvas` template pages:
```php
if ( ! is_page_template( 'elementor_canvas' ) ) {
    return;
}
```

Blog posts use `post-template-default`, NOT `elementor_canvas`. So the override NEVER ran for blog posts.

The content-level CSS (`body.single-post .entry-content`, `.site-content`, etc.) overrides the orange for specific content boxes, but the BODY ITSELF was orange, showing through in gaps between content sections.

## Fix Applied (v5.0.4)

1. Removed the `is_page_template('elementor_canvas')` guard from the override hook
2. Added `is_admin()` guard instead (skip on WP admin pages only)
3. Added page-type-specific rules:
   - `body.single-post.tt-magic-cursor { background: #0a0a0f !important; }`
   - `body.blog.tt-magic-cursor { background: #0a0a0f !important; }`
   - `body.category.tt-magic-cursor { background: #0a0a0a !important; }`
   - `body.archive.tt-magic-cursor { ... }`
   - `body.tag.tt-magic-cursor { ... }`

The override runs at `wp_footer` priority 99, AFTER Additional CSS loads, ensuring it always wins.

## Deployment Details

- Plugin version: 5.0.4
- Deploy script: `tools/security/deploy_plugin_v504_purebrain.py`
- All 15/15 pre-flight validation checks: PASS
- All 15/15 live verification checks (3 posts × 5 checks): PASS
- Cache busted on posts: 879, 606, 565, 631

## Verification Commands

```bash
# Check live page for the override
curl -s "https://purebrain.ai/your-next-direct-report-wont-be-human/" | grep "body.single-post.tt-magic-cursor"

# Confirm v5.0.1 broken CSS is absent
curl -s "https://purebrain.ai/your-next-direct-report-wont-be-human/" | grep "purebrain-inline-cta-white-text-v501"
# Should return NOTHING (empty)
```

## Key Lessons

1. **CSS attribute selectors have higher specificity than class selectors**: `[class*="magic"]` (0,1,0,0) beats `body.single-post` (0,0,1,1). Never assume class selectors win over attribute selectors.

2. **`wp_footer` hooks with page-template guards can miss non-Elementor pages**: If a fix runs only for `elementor_canvas`, it won't apply to standard WordPress templates (`post-template-default`, `page-template-blank.php`, etc.).

3. **Always check body classes**: The Artistics theme adds `tt-magic-cursor` to the body on ALL page types. Any CSS targeting `[class*="magic"]` will hit the body.

4. **Page source inspection is the correct debugging approach**: curl + grep for style IDs tells you exactly what CSS is running. Don't guess — inspect.

5. **Cloudflare CDN cache miss vs hit**: Even with CDN caching, the issue was not cache-related in this case. The fix was genuinely needed.
