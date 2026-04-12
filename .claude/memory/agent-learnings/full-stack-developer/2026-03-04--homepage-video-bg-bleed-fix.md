# Homepage Visual Bug Fix - 2026-03-04

## Type: gotcha + fix

## What Broke
PureBrain.ai homepage (page 11) had 3 visual bugs:
1. WATCH PUREBRAIN COME ALIVE video section showed blank/broken - only play button visible, no video player
2. Cosmic/nebula animated background bleeding through all sections
3. Footer area showing cosmic background instead of dark solid

## Root Cause Analysis

### Bug 1 - Video section broken
The `<section class="pb-demo-section">` HTML element existed, but ZERO CSS was defined for:
- `.pb-demo-section` - no padding, no background, no dimensions
- `.pb-demo-player` - critical: no `padding-top: 56.25%` for 16:9 aspect ratio
- `.pb-demo-player video` - no `position: absolute` to fill the container
- All the `__inner`, `__label`, `__heading`, `__sub`, `__cta` sub-classes

Result: The video container had 0 height. The video element rendered with 0x0 size. Only the overlay div (which had flex centering) showed the play button floating in a collapsed space.

### Bug 2+3 - Background bleed-through
The homepage uses `position: fixed` for:
- `.video-background` (z-index: -1) - the cosmic nebula video
- `.living-background` (z-index: 0) - canvas particles and gradient orbs

These are FIXED positioned, meaning they always cover the full viewport. Content sections with `background: transparent` literally show the fixed cosmic background through them. This is INTENTIONAL for the hero section (meant to look immersive), but problematic for:
- `.pb-demo-section` - had NO background at all
- `.footer` - had `background: transparent`

### Injection script NOT the cause
The `PB Levels Link Injection v1.0` script appended to the HTML widget was confirmed NOT causing these issues. It was correctly placed and unrelated.

## The Fix

### What was added
A new `<style>` block inserted immediately before `<!-- DEMO VIDEO EMBED SECTION v3 2026-03-01 -->` comment in the main HTML widget (id=292c72a):

```css
/* pb-demo-section complete CSS set - copied from sandbox-3 (page 1232) as reference */
.pb-demo-section {
    padding: 80px 20px;
    background: linear-gradient(180deg, rgba(8,10,18,0) 0%, rgba(8,10,18,1) 8%, rgba(8,10,18,1) 92%, rgba(8,10,18,0) 100%);
    position: relative;
    z-index: 1;
}
.pb-demo-player {
    position: relative;
    width: 100%;
    padding-top: 56.25%; /* 16:9 */
    /* ...etc */
}
.pb-demo-player video {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    /* ...etc */
}
/* + all other pb-demo-section__ classes */

/* Footer dark background */
.footer {
    background: rgba(5, 8, 15, 0.97) !important;
}
```

### Reference page used
Page 1232 (Pay Test Sandbox 3) had the complete working CSS. Used it as exact source.

### Background bleed for content sections
The `background: linear-gradient(180deg, rgba(8,10,18,0) 0%, rgba(8,10,18,1) 8%, rgba(8,10,18,1) 92%, rgba(8,10,18,0) 100%)` on `.pb-demo-section` creates a fade-in/fade-out effect that blocks the cosmic background in the middle 84% of the section while allowing a subtle transition at top/bottom edges. This is the correct design pattern.

Other sections that are transparent (`.section`, `.chat-section`, `.value-section`) are intentionally transparent to show the cosmic background - this is part of the design. Only the video player section and footer needed solid backgrounds.

## Files Changed
- Page 11 `_elementor_data` via WordPress REST API
- Specifically widget id=292c72a (main HTML widget, 256k chars)
- Added 3,731 chars of CSS

## Deployment Steps
1. Fetch current `_elementor_data` for page 11
2. Parse JSON, find widget id=292c72a
3. Insert CSS `<style>` block BEFORE the demo section comments
4. Re-serialize JSON
5. POST to `/wp/v2/pages/11` with updated `meta._elementor_data`
6. DELETE `/elementor/v1/cache` to force fresh render
7. Verify by re-fetching page and checking CSS present

## Video Source URLs (confirmed working 200 OK)
- Background video: `https://purebrain.ai/wp-content/uploads/2026/02/PureResearch.ai-1.mp4` (74MB)
- Demo video: `https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Demo-Video-real-compression-and-sizing.mp4` (90MB)

## Key Lessons
1. When adding new HTML sections to a page, ALWAYS include the CSS for those classes in the same widget or it will render broken
2. The `position: fixed` background system means sections need `background: rgba(...)` (not transparent) to block bleed-through
3. Video player containers MUST have `padding-top: 56.25%` + `position: relative` with `position: absolute; inset:0` on the video child for 16:9 aspect ratio
4. Always cross-reference with a working page (sandbox-3) before diagnosing CSS issues
5. The pb-levels-link injection script at end of HTML widget is safe and unrelated to visual bugs
