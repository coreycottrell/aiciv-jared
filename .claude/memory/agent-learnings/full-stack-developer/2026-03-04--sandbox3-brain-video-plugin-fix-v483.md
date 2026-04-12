# Sandbox-3 Brain Video Background Fix (Plugin v4.8.3)

**Date**: 2026-03-04
**Agent**: full-stack-developer
**Type**: bugfix, plugin
**Tags**: sandbox3, video-background, plugin, z-index, page-1232, dark-bg

---

## Problem

The brain video background on pay-test-sandbox-3 (page 1232) was invisible.
The video element was present in the page HTML with correct z-index: -1 and body: transparent.
But the plugin (v4.8.2) was ALSO forcing body background to #080a12 via three layers of enforcement.

---

## Root Cause

Plugin v4.8.2 has three dark background enforcement layers:
1. **CSS Layer 1** (wp_head priority 1): `body { background: #080a12 !important }`
2. **CSS Layer 2** (wp_head priority 999): Same, with extra selectors
3. **JS Layer 3** (wp_head priority 999, JS): `document.body.style.setProperty('background', '#080a12', 'important')`

Pages with video backgrounds (688, 689, 987, homepage) were EXEMPTED.
Page 1232 (pay-test-sandbox-3, created 2026-03-03) was NOT in the exemption list.

So even though the page HTML had `body { background: transparent }`, the plugin OVERRODE it with opaque dark background, covering the z-index: -1 video.

---

## Fix (v4.8.3)

Added `body.page-id-1232` to the transparent-body exception in all three layers:

**Layer 1 CSS:**
```css
body.home,
body.page-id-11,
body.page-id-688,
body.page-id-689,
body.page-id-987,
body.page-id-1232 {    /* ADDED */
    background: transparent !important;
    background-color: transparent !important;
}
```

**Layer 2 CSS:** Same addition.

**Layer 3 PHP (JS skip condition):**
```php
if ( is_front_page() || is_page( array( 688, 689, 987, 1232 ) ) ) {
    return;
}
```

---

## Key Pattern

**EVERY TIME a new page with a video background is created**, it must be added to the plugin's exemption list. The current exemption pages are: 11 (homepage), 688, 689, 987, 1232.

If you clone a pay-test page and it shows a solid dark background instead of the video, the fix is always this: add the page ID to all three layers in the plugin.

---

## Verification

Live check on https://purebrain.ai/pay-test-sandbox-3/:
- Layer 1 CSS: `body.page-id-1232` in transparent exception ✅
- Layer 2 CSS: Same ✅  
- Layer 3 JS: NOT present (correctly skipped by PHP) ✅

---

## Deployment

- **Plugin**: v4.8.3 deployed via Playwright (deactivate → delete → upload zip → activate)
- **File**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v483.php`
- **Zip**: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security.zip`
- Confirmed active on plugins.php with version 4.8.3
