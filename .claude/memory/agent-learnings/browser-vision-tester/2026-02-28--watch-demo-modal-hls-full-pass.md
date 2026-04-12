# Watch Demo Modal + HLS Video - Full Pass Audit - purebrain.ai

**Date**: 2026-02-28
**Agent**: browser-vision-tester
**Type**: teaching + operational
**Topic**: Watch Demo button, video modal, HLS.js streaming from Cloudflare R2 on purebrain.ai homepage

---

## Context

Audited the "Watch Demo" button on the purebrain.ai homepage. This is an HLS video
(eaf39ae1_Portal_demo) served from Cloudflare R2 via blob: URL (MSE buffer), loaded by
HLS.js on the page. The video modal opened, video played, and close worked. Full PASS.

---

## Results: All 5 Criteria

1. **Watch Demo button exists and clickable**: PASS
   - Tag: `<button class="btn btn--secondary">`
   - Position: right of "Awaken Your PURE BRAIN" CTA, inside `.hero__cta`
   - onclick handler: `openVideoModal()` - JavaScript function, NOT a link
   - Visible at y=746 in 900px viewport (near bottom of hero fold)

2. **Clicking opens a modal**: PASS
   - Modal ID: `#videoModal`, class `video-modal`
   - Adds class `active` on click -> CSS switches display from `none` to `flex`
   - Full opacity: `rgba(0,0,0,0.95)` overlay
   - z-index: 10003 (above everything including waitlist modal at 10002)
   - CSS animation: content transitions from opacity 0 to 1

3. **Video loads and plays (HLS.js streaming)**: PASS
   - HLS.js NOT exposed as global `Hls` (loaded via plugin/encapsulated)
   - Video uses MSE (Media Source Extensions) -> `currentSrc` = `blob:https://purebrain.ai/...`
   - `readyState: 4` (HAVE_ENOUGH_DATA) - fully buffered
   - `paused: false` - actively playing
   - `currentTime` advances over time (11.7s -> 16.9s over 5s wait - confirmed live play)
   - Duration: 352.9s (~5 min 52s)
   - Resolution: 1280x720 (HD)
   - NOT muted, volume=1 (sound enabled - user must click play or browser may autoplay)
   - R2 URL: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/master.m3u8`
   - Previous CORS block on /video-test/ page is NOT present here (video plays fine)

4. **Poster image visible before play**: PASS (infrastructure only)
   - Poster URL: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/poster.jpg`
   - Poster attribute confirmed on `#demoVideo` element
   - NOTE: In Playwright headless, video autoplays before screenshot can capture poster state

5. **Closing the modal works**: PASS
   - Close button: `.video-modal__close` at top-right corner (x=1181, y=115 in 1440px viewport)
   - Visible: `true`, clickable
   - onclick: `closeVideoModal()`
   - After close: modal class = `['video-modal']` (active removed), display = `none`
   - Homepage restored correctly behind the modal

---

## Visual Observations

- Hero section: Dark space background with particle/brain animation
- Watch Demo button: Play triangle icon + "Watch Demo" text, muted/secondary style
- Modal: Near-black overlay (rgba 0,0,0,0.95), video centered 1000x562.5px (16:9)
- Video content: Shows PureBrain portal chat interface (dark UI with typing animation)
- Close button: White "×" top right, clearly visible
- After close: Returns cleanly to hero page

---

## Known Issue: Orange Background on Full Page

- `document.body` background: `rgb(241, 66, 11)` (orange) - visible in full page scroll
- Plugin v4.6.6 dark enforcement not covering body fully on homepage
- Separate from the Watch Demo flow, which works correctly
- Hero section covers this with its own dark background

---

## Known Issue: Background Video (PureResearch.ai-1.mp4) Fails

- Network failures: `net::ERR_ABORTED` for `PureResearch.ai-1.mp4` (multiple failures)
- This is the homepage background video, not the demo video
- Separate upload/CDN issue; does not affect Watch Demo functionality

---

## Gotchas for Future Testing

1. **HLS.js not exposed globally** - `typeof Hls === 'undefined'` in console eval, but video still plays
   via MSE. Check `currentSrc.startsWith('blob:')` to confirm HLS is active.

2. **Video autoplays in Playwright** - Cannot capture poster-only state without muting autoplay
   in page JS. To test poster: intercept `play()` calls or check poster attribute directly.

3. **Button is near viewport bottom** - At 1440x900, button at y=746 is in view but only ~154px
   from bottom. Mobile viewports will push button below fold.

4. **`openVideoModal()` is pure JS** - No href, no page navigation. Must use button tag selector
   or `onclick` content search.

5. **Modal z-index: 10003** - Beats waitlist modal (10002) and all other overlays.

6. **Click timing** - 2 second wait after click sufficient for modal CSS animation to complete.

---

## When to Apply

- Any test of Watch Demo on purebrain.ai homepage
- HLS video in modal patterns on WordPress/Elementor sites
- Verifying R2 CORS is working (blob: URL in currentSrc = CORS resolved)
