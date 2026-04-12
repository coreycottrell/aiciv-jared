# Blog Background Video Restoration — Plugin v4.7.4

**Date**: 2026-03-01
**Type**: bug-fix + deployment
**Agent**: dept-systems-technology
**Ticket**: ST# URGENT blog background video missing

## Problem

The `/blog/` page (purebrain.ai/blog/) lost its animated GIF background.

## Root Cause

**Plugin v4.6.6** introduced site-wide opaque body background (`body { background: #080a12 !important }`).
**Plugin v4.6.7** hotfix added transparent-body exceptions for video/3D pages but MISSED page ID 319 (the blog listing).

The blog page uses:
- `.pb-brain-bg` at `position: fixed; z-index: -2` — GIF background animation
- `.pb-overlay` at `position: fixed; z-index: -1` — dark gradient overlay
- GIF URL: `https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif`

Because these are at negative z-index, an opaque body covers them entirely.

## WordPress Blog Page Details

- **Page ID**: 319
- **Slug**: /blog/
- **Template**: elementor_canvas
- **Content**: Stored in post_content (NOT _elementor_data — that's empty)
- **Body class**: `page-id-319`

## Fix Applied

Added `body.page-id-319` to all three transparent-body enforcement layers in the plugin:

### Layer 1 (CSS priority 1, wp_head):
```css
body.home,
body.page-id-11,
body.page-id-319,   /* <-- ADDED */
body.page-id-688,
body.page-id-689,
body.page-id-987 {
    background: transparent !important;
    background-color: transparent !important;
}
```

### Layer 2 (CSS priority 999, wp_head):
Same rule added.

### Layer 3 (JS DOMContentLoaded):
```php
if ( is_front_page() || is_page( array( 319, 688, 689, 987 ) ) ) {
    return; // Skip dark bg enforcement
}
```

## Plugin Version

- **Before**: 4.7.3
- **After**: 4.7.4
- **File**: `exports/purebrain-security-plugin-v473-bypass-fix.php`

## Deployment Method

admin-ajax.php cookie-based pattern (documented in full-stack-developer memory):
1. `curl -c /tmp/wp_cookies.txt POST wp-login.php` with PUREBRAIN_WP_PASSWORD
2. Get nonce from plugin-editor.php page
3. `curl POST admin-ajax.php action=edit-theme-plugin-file newcontent=<file`
4. Response: `{"success":true,"data":{"message":"File edited successfully."}}`

## Verification

- `body.page-id-319` in body class: TRUE
- Layer 1 CSS transparent exception: TRUE (confirmed in live HTML)
- Layer 2 CSS transparent exception: TRUE (confirmed in live HTML)
- Layer 3 JS NOT injected: TRUE (correct — PHP condition skips it)
- GIF URL present in page: TRUE

## Video Pages Full List (Post-Fix)

Pages that need transparent body (all now covered):
- Page 11 (Homepage) — via `body.home` and `body.page-id-11`
- Page 319 (/blog/) — **ADDED IN v4.7.4**
- Page 688 (pay-test-sandbox-2)
- Page 689 (pay-test-2)
- Page 987 (invitation page)

## Key Teaching

When adding site-wide background enforcement to a plugin, ALWAYS audit ALL pages with
fixed-position background elements at z-index < 0 BEFORE deploying. The pattern:
fixed-bg at negative z-index REQUIRES transparent body to show through.
