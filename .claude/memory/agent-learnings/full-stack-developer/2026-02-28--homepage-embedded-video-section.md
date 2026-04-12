# Homepage Embedded Video Section Deployment

**Date**: 2026-02-28
**Type**: pattern + deployment
**Agent**: full-stack-developer

---

## What Was Built

Added a new "Demo Video Embed Section" to the purebrain.ai homepage (page 11), pay-test-2 (page 689), and pay-test-sandbox-2 (page 688).

The section:
- Appears in the page flow BETWEEN the hero section and the marquee section
- Shows the HLS demo video inline (not in a modal popup)
- Has a clickable poster-to-play experience: poster shows on load, click plays the video with sound
- Uses a dark PureBrain-styled section with "Live Demo" pill label, heading "Watch PureBrain Come Alive", and a call to action to begin awakening
- Element IDs use `pb-demo__` prefix to avoid collision with existing modal's `demoVideo`/`videoModal` IDs

## HLS Assets Used

- Video: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/master.m3u8`
- Poster: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/poster.jpg`
- HLS.js CDN: `https://cdn.jsdelivr.net/npm/hls.js@1.5.7/dist/hls.min.js`

## Injection Pattern (3 Places in the HTML)

The homepage widget is a single massive HTML document (~316K chars) stored in `_elementor_data`.

Injection requires updating 3 locations in that HTML:

1. **CSS injection**: Find last `</style>` before `</head>`, insert CSS block before it
2. **HTML section injection**: Find `Watch Demo` button text, then find the `</section>` that closes the hero, insert HTML section immediately after that `</section>`
3. **Script injection**: Find `function openVideoModal()`, then find its closing `</script>` tag, insert script block before it

## Key Landmarks

- Hero section HTML: `<section class="hero" id="hero" data-atmosphere="awakening">` at ~position 151813
- Watch Demo button: at ~position 154556 in the HTML
- Hero closing `</section>`: found via `html.find('</section>', watch_demo_pos)`
- After hero close: marquee comment `<!-- MARQUEE -->` then `<div class="marquee">`
- openVideoModal function: at ~position 291639

## Script Architecture

Uses an IIFE pattern with closure:
- `window.pbDemoPlay(playerEl)` - exposed as global for onclick handler
- `_pbDemoHls` - private HLS instance with destroy on re-play
- `_pbDemoLoaded` flag to avoid re-loading source on replay
- Lazy HLS.js loading: if `Hls` not defined globally, creates script tag at click time
- Auto-unmutes on play, falls back to muted if autoplay blocked
- Overlay (play button) hides on play via `classList.add('pb-playing')`, shows again on pause/end

## Deployment Results

- Homepage (page 11): VERIFIED live at purebrain.ai/
- Pay Test 2 (page 689): VERIFIED in Elementor data (page is password-protected, content renders after auth)
- Pay Test Sandbox 2 (page 688): VERIFIED in Elementor data (same, password-protected)

## Cache Note

Pay-test pages are password-protected. Cloudflare serves a password gate for unauthenticated users (106K). The actual video content renders post-authentication. Verified via REST API that `pb-demo-section` is stored in `_elementor_data` for both pages.

## Deployment Script

`/home/jared/projects/AI-CIV/aether/tools/deploy_homepage_video.py`

## Tags

purebrain, homepage, video, hls, elementor, demo, embed, page-11, page-689, page-688
