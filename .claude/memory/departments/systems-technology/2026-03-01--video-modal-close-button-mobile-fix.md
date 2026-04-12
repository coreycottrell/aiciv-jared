# Video Modal Close Button Mobile Fix

**Date**: 2026-03-01
**Agent**: dept-systems-technology
**Type**: gotcha + fix
**Topic**: Video demo popup X close button not visible on all mobile devices

---

## Problem

The `.video-modal__close` button on purebrain.ai was using:
```css
position: absolute;
top: -50px;
right: 0;
z-index: 10;
```

This places the button 50px ABOVE the `.video-modal__content` container. On desktop (large viewport with padding), this works because there's space above the content box. On small phones (iPhone), the modal content fills most of the screen height and the `-50px` offset puts the button above the visible viewport area or clipped by the overlay container. Result: button invisible, user cannot close the video.

## Fix Applied

Changed to `position: fixed` anchored to viewport:
```css
.video-modal__close {
    position: fixed;
    top: 16px;
    right: 16px;
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--white);
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    line-height: 1;
    transition: color 0.2s ease, transform 0.2s ease, background 0.2s ease;
    z-index: 99999;
}
```

Key improvements:
- `position: fixed` - viewport-relative, NEVER goes off screen
- `top: 16px; right: 16px` - always 16px from top-right corner of viewport
- Visible circle background (rgba white) - easier to spot and tap on mobile
- `z-index: 99999` - beats everything (modal was 10003)
- `width/height: 44px` - meets Apple's minimum tap target guideline

## Pages Affected

- Page 11 (purebrain.ai homepage) - content raw + elementor_data both fixed
- Page 688 (pay-test-sandbox-2) - content raw + elementor_data both fixed
- Page 689 (pay-test-2) - content raw + elementor_data both fixed

## Deployment Method

1. Read raw content from WP REST API (`context=edit`)
2. String replace old CSS with new CSS in `content.raw`
3. POST back to WP REST API
4. Repeat for `meta._elementor_data` (JSON-escaped `\\n` patterns)
5. DELETE `/wp-json/elementor/v1/cache` to clear Elementor cache

## Pattern for Finding Elementor Data CSS

Elementor stores CSS with literal `\\n` (double-backslash n) in the JSON string:
```
'.video-modal__close {\\n            position: absolute;\\n ...'
```
Not newlines - actual escaped backslash-n sequences. Match accordingly.

## Root Cause Lesson

`position: absolute; top: -Npx` for modal close buttons ALWAYS risks mobile clipping.
The safe pattern is ALWAYS `position: fixed` for modal close/dismiss buttons that should
be viewport-visible regardless of content height.

## Verification

All 3 pages confirmed:
- `top: -50px` removed from content raw: True
- `position: fixed; top: 16px` present in content raw: True
- `top: -50px` removed from elementor data: True (all pages)
- `position: fixed; top: 16px` present in elementor data: True (all pages)
- Elementor cache cleared: HTTP 200
