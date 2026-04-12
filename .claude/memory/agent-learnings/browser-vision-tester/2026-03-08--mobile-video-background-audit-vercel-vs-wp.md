# Memory: Mobile Video Background Audit - Vercel vs WordPress

**Date**: 2026-03-08
**Type**: operational + teaching
**Topic**: Mobile viewport (375x812) video background status on both purebrain-site.vercel.app and purebrain.ai

---

## Task

Jared asked: prove the video background is working (NOT showing hexagon/spiral static image) on mobile viewport for both Vercel and WordPress homepages.

---

## Findings

### Both Sites: Video IS Playing (Not a Static Image)

On BOTH sites:
- `#bgVideo` element exists with class `video-background__video`
- Dimensions: 375x812 (fills full mobile viewport)
- `paused=false` (actively playing)
- No static poster/hexagon image detected
- 0 images found above the fold (no static hexagon replacing video)

### But: WRONG VIDEO FILE on Both

`#bgVideo` source on both Vercel AND WordPress:
```
https://purebrain.ai/wp-content/uploads/2026/02/PureResearch.ai-1.mp4
```

This is NOT the intended brain animation. This is the PureResearch.ai video.

**Visual description from screenshots**: Cosmic galaxy/space scene with orange spiral nebula center. Very dark atmosphere with blue/purple swirls and bright star-like particles. NOT the hexagon spiral static image.

This same bug was documented:
- 2026-02-27 (first detection)
- 2026-03-04 (still not fixed)
- 2026-03-08 (still not fixed - 9 days unresolved)

### Vercel vs WordPress State

| Property | Vercel | WordPress |
|----------|--------|-----------|
| Video playing | Yes (paused=false) | Yes (paused=false) |
| readyState | 4 (fully loaded) | 2 (loading) |
| Video file | PureResearch.ai-1.mp4 | PureResearch.ai-1.mp4 |
| Static hexagon shown | No | No |
| Hero images above fold | 0 | 0 |

Vercel has readyState=4 because it's likely caching the video. WordPress had readyState=2 because it was still buffering at screenshot time.

---

## Visual Description

Both pages show:
- Deep dark navy/black background
- Vibrant cosmic video: orange spiral at center, radiating blue/purple nebula tendrils
- PUREBRAIN wordmark visible with correct brand colors (blue/orange/blue)
- Hero headline text clearly legible
- No hexagon, no static spiral graphic - it IS a live video

---

## What's NOT Wrong

- No static poster image replacing the video
- No hexagon/spiral SVG showing instead of video
- No display:none on the video element
- No z-index problem covering the video
- The background is dark and atmospheric as designed

---

## What IS Wrong

The video source file is wrong: `PureResearch.ai-1.mp4` instead of the brain animation.
This has been unfixed for 9 days.

Fix path: Update `_elementor_data` on WP page ID 11, swap the `<source src="...">` tag. Then clear Elementor cache. Then redeploy Vercel from the same WP source.

---

## Screenshot Files

- `/tmp/mobile-vercel-hero.png` (375x812 iPhone viewport, Vercel)
- `/tmp/mobile-wordpress-hero.png` (375x812 iPhone viewport, WordPress)

Both sent to Telegram (message_ids: 22127, 22128).

---

## Teaching

When testing "is video background working on mobile":
1. Check `video.paused` - if false, it's playing
2. Check `video.offsetWidth/offsetHeight` - if > 0, it's visible
3. Check `video.currentSrc` - what file is actually loading
4. Take a screenshot and look visually - static poster vs live video is immediately obvious
5. Check for img elements above fold - a static hexagon would appear as an `<img>` or CSS background-image

The Playwright 8-second wait is sufficient for mobile video to initialize on both Vercel and WP.
