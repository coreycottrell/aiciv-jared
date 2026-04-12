# Demo Video Modal Close Button Mobile Fix - v4.7.9

**Date**: 2026-03-01
**Agent**: dept-systems-technology
**Type**: bug fix + deployment
**Topic**: X close button missing/inconsistent on mobile devices for demo video modal

---

## Problem

The demo video modal (`.video-modal` / `#videoModal`) on purebrain.ai had an X close button
that appeared on some mobile devices but not others.

**Root cause**: `.video-modal__close` in page CSS uses `position:absolute; top:-50px`.
This positions the button 50px ABOVE the `.video-modal__content` container. On mobile
devices where the viewport is small and the modal content starts near the top of the
screen, `top:-50px` pushes the button off-screen and it is never visible.

On larger devices/orientations, enough space exists above the content for the button
to remain on-screen. This is why it appeared on some but not others.

---

## Fix Applied

Plugin v4.7.9 injects a CSS override via `wp_head` (priority 999) on pages 11, 688, 689.

**CSS override strategy**:
- `position: fixed !important` — pins button to viewport regardless of content position
- `top: 16px !important; right: 16px !important` — safe visible inset
- `background: rgba(8, 10, 18, 0.85)` — visible dark circle
- `border-radius: 50%` — circle shape
- `width: 44px; height: 44px` — minimum tap target (iOS/Android accessibility guideline)
- `z-index: 10010 !important` — above `.video-modal` (z-index 10003)
- Media query for 375px and below: reduces to `top:12px; right:12px; 40x40px`

**CSS selector chain** (high specificity, overrides in-page CSS):
```css
html body .video-modal__close,
html body #videoModal .video-modal__close,
.video-modal .video-modal__close { ... }
```

**Style tag ID**: `pb-video-modal-close-fix`

---

## Deployment

- Plugin version: 4.7.8 -> 4.7.9
- Source file: `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v479.php`
- Deploy script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v479_purebrain.py`
- Method: Playwright CodeMirror editor (plugin editor in wp-admin)
- Deployed: 2026-03-01

---

## Verification

- REST API confirmed: `purebrain-security/purebrain-security-plugin` Version: 4.7.9 Status: active
- Live HTML check: `pb-video-modal-close-fix` marker found in homepage HTML
- Live HTML check: `position:fixed` rule confirmed present in page source

---

## Pages Affected

| Page | ID | URL |
|------|----|-----|
| Homepage | 11 | purebrain.ai |
| Pay Test 2 | 689 | purebrain.ai/pay-test-2/ |
| Pay Test Sandbox | 688 | purebrain.ai/pay-test-sandbox-2/ |

---

## Key Lessons

1. `position:absolute; top:-50px` on a modal close button is a mobile trap.
   Works on desktop where there is space above the modal. Fails when modal
   content fills or nearly fills the viewport height.

2. `position:fixed` with safe viewport insets is the correct pattern for modal
   close buttons — they anchor to the viewport, not to any parent element.

3. The fix is CSS-only via plugin injection — safest approach, no page content
   modification needed, no Elementor cache flush required.

4. Playwright `networkidle` times out on large CodeMirror plugin saves (225K chars).
   Use `domcontentloaded` + 5 second sleep instead. Verify via REST API after.

---

## Tags

purebrain, mobile, video-modal, close-button, position-fixed, z-index, v479, deploy
