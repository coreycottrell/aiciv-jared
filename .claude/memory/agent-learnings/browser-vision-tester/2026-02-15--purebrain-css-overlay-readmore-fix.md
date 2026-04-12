# PureBrain CSS Fix: Video Overlay and Read More Buttons

**Date**: 2026-02-15
**Type**: operational
**Agent**: browser-vision-tester

## Context

Jared reported two issues with purebrain.ai:
1. Video background too grainy/dark (overlay too heavy)
2. Read more buttons inconsistent across blog posts

## Solution Applied

### Issue 1: Video Overlay Fix

The previous CSS had multiple layers of dark overlays:
- `body.page-id-95 [class*="overlay"]` with `opacity: 0.15`
- Additional gradient overlays in UX fixes file with `rgba(0,0,0,0.15)` to `rgba(0,0,0,0.18)`
- Combined effect made video look grainy/dark

**Fix applied**:
```css
.video-overlay,
.elementor-background-overlay,
[class*="background-overlay"],
body.page-id-95 .elementor-background-overlay,
body.page-id-95 [class*="overlay"]:not(.elementor-post):not(.blog-card) {
    background: transparent !important;
    opacity: 0 !important;
}
```

Key insight: Used `:not()` selector to exclude blog cards from the overlay removal.

### Issue 2: Read More Buttons

Added aggressive force-visibility rules:
```css
.elementor-post__read-more,
a.elementor-post__read-more,
.wp-block-latest-posts__read-more,
.read-more,
a.read-more {
    display: inline-block !important;
    visibility: visible !important;
    opacity: 1 !important;
    /* Plus full styling for orange gradient button */
}
```

Also added container overflow fix:
```css
.elementor-post__text,
.elementor-post .elementor-widget-container {
    overflow: visible !important;
}
```

## Technical Details

- **Updated file**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css`
- **Tool used**: `tools/wp_css_updater.py` (Playwright-based WordPress Customizer automation)
- **WordPress location**: Appearance > Customize > Additional CSS
- **Screenshots**: `/home/jared/projects/AI-CIV/aether/sandbox/wp-screenshots/`

## Verification

- CSS successfully pushed to WordPress at 12:40 UTC
- Live site confirmed receiving new CSS via curl check
- Comments in CSS clearly mark the two critical fixes

## Pattern Learned

For Elementor-based WordPress sites:
1. Overlay removal needs `:not()` exclusions to avoid breaking card designs
2. "Read more" buttons may be hidden by parent `overflow: hidden` - need to force container overflow
3. Multiple CSS files may contain conflicting overlay rules - need to consolidate and use `!important`

## Files Changed

- `/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css`
