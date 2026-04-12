# Mobile Vortex Background Fix - Root Cause Analysis
**Date**: 2026-03-08
**Type**: gotcha + pattern
**Agent**: dept-systems-technology

## Problem
purebrain.ai homepage showed spinning hexagon/vortex animation on mobile instead of video background.
Multiple fix attempts failed. Previous browser-vision-tester report showed `display: block` for `.vortex-ring` despite CSS having `display: none !important`.

## Root Cause Identified
The browser-vision-tester report that triggered this investigation was from **before pb-video-handler v1.4.0 was deployed**. The fix WAS already deployed and working.

**Confirmed via Playwright browser testing:**
- Chromium mobile (390x664 iPhone 12): ALL vortex rings hidden, video playing
- Chromium mobile (375x812): ALL vortex rings hidden, video playing
- Both viewports: `mq767=True, allHidden=True, pvHidden=True, videoPlaying=True`

## Key Architecture Finding
The purebrain.ai homepage is structured as:
1. **Outer WordPress page** with plugin CSS in `<head>`
2. **5 Elementor HTML widgets** embedded in the body
3. **Widget 1** (388kb) contains a complete `<!DOCTYPE html>` document with:
   - Its OWN `<style>` tags (no id) defining `.vortex-ring` base CSS
   - The `<div class="portal-vortex">` with 6 `.vortex-ring` children
   - The `<section class="hero">` (portal-vortex is INSIDE .hero, NOT inside .living-background)

**Important**: The portal-vortex is in `.hero` section, NOT in `.living-background`. So the rule `body.home .living-background * { display: none !important }` does NOT cover vortex rings. They are covered by the direct rule: `@media (max-width: 767px) { .portal-vortex, .vortex-ring { display: none !important } }`.

## CSS Rule Cascade (What Actually Works)
1. `pb-video-handler-css` (position 30615 in page): `@media (max-width: 767px) { .portal-vortex, .vortex-ring { display: none !important; visibility: hidden !important; } }` ← WORKS
2. `pb-video-modal-close-fix-v611` (position 102705): `@media (max-width: 767px) { .vortex-ring { display: none !important; } }` ← REDUNDANT BACKUP
3. Widget 1 inline style (position 185191): `.vortex-ring { position: absolute; ... }` ← NO display property, does NOT override our rule

## Gotcha: Double wp-custom-css Block
The page has TWO `<style id="wp-custom-css">` blocks. This is a WordPress/caching behavior where the Additional CSS loads twice. Not causing the vortex issue but worth noting.

## Verification Method
```python
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    iphone = p.devices["iPhone 12"]
    ctx = browser.new_context(**iphone)
    page = ctx.new_page()
    page.goto("https://purebrain.ai/", wait_until="networkidle", timeout=60000)
    time.sleep(5)
    result = page.evaluate("""() => ({
        ringCount: document.querySelectorAll('.vortex-ring').length,
        allHidden: Array.from(document.querySelectorAll('.vortex-ring')).every(r => r.offsetWidth === 0),
        videoPlaying: !document.getElementById('bgVideo').paused
    })""")
    # Expected: {ringCount: 6, allHidden: True, videoPlaying: True}
```

## Files Involved
- Plugin: `/home/jared/projects/AI-CIV/aether/tools/security/pb-video-handler/pb-video-handler.php` (v1.4.0)
- Deploy script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_pb_video_handler.py`

## Lesson
When browser-vision-tester reports a CSS issue, always:
1. Check Cloudflare cache-status header (can be HIT with 31+ min old content)
2. Run a fresh Playwright browser test to get current computed styles
3. Distinguish between "CSS not in page" vs "CSS in page but browser ignores it" vs "JS overriding CSS"
4. A `display: block` computed style on an element whose PARENT has `display: none` is normal - the child's own computed display value doesn't change, it's just not rendered.
