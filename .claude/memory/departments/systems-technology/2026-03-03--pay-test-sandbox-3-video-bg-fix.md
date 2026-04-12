# pay-test-sandbox-3: Brain Video Background Fix
**Date**: 2026-03-03
**Type**: bug-fix
**Agent**: dept-systems-technology
**Plugin**: purebrain-security v4.8.2

## Root Cause
The security plugin (3-layer dark background enforcement) had a hardcoded whitelist of pages
that should have `background: transparent` (to allow video/3D backgrounds to show through).

Page 1232 (pay-test-sandbox-3) was NOT in this whitelist. Result: body got `background: #080a12 !important`
which covered the video element at `z-index: -1`.

The video itself is correctly implemented (`position: fixed; inset: 0; z-index: -1`) — the bug
was purely in the plugin enforcement, not the video CSS.

## Fix Applied: v4.8.2
Added `body.page-id-1232` to all 3 enforcement layers:

**Layer 1 (CSS priority 1)**:
```css
body.page-id-987,
body.page-id-1232 {
    background: transparent !important;
    background-color: transparent !important;
}
```

**Layer 2 (CSS priority 999)**: Same as Layer 1

**Layer 3 (JS DOMContentLoaded)**:
```php
if ( is_front_page() || is_page( array( 688, 689, 987, 1232 ) ) ) {
    return; // Skip JS enforcement for video pages
}
```

## Whitelist Reference (current as of v4.8.2)
Pages with transparent body (video/3D backgrounds):
- `body.home` / `body.page-id-11` - Homepage
- `body.page-id-688` / `body.page-id-689` - Pay test pages
- `body.page-id-987` - Invite/landing page
- `body.page-id-1232` - Pay test sandbox 3 (NEW)

## Verification
- `body.page-id-1232` appears in CSS Layer 1 and Layer 2
- `pb-dark-bg-js` script NOT injected on page 1232
- No JS `#080a12` override on this page

## File
`exports/purebrain-security-plugin-v482.php`

## Pattern for Future
Any new page with a video/3D background that gets covered by the dark background needs
its page-id added to all 3 layers in the security plugin. Check by:
1. Loading the page
2. Checking if `pb-dark-bg-js` is present in source
3. Checking if `body.page-id-XXXX` is in the transparent whitelist CSS
