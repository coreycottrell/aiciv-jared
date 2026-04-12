# Memory: PureBrain.ai Homepage - Wrong Background Video
**Date**: 2026-02-27
**Type**: operational + teaching
**Topic**: Background video replaced with wrong file on purebrain.ai homepage

---

## Task Summary

Urgent check: Jared reported brain video was removed/hidden from purebrain.ai homepage.
Audited via Playwright with 12-second wait for video load.

---

## Finding

The background video IS present and PLAYING. But it is the WRONG video.

**Current video**: `PureResearch.ai-1.mp4`
**Expected video**: A neural brain animation (previous source)

**Video element details**:
- ID: `bgVideo`
- Class: `video-background__video`
- Parent: `.video-background` (position: fixed, z-index: -1)
- Status: `paused=False`, autoplay=True, loop=True, muted=True
- Dimensions: 1440x900 (full viewport, fully visible)
- Overlay: `.video-background__overlay` with rgba(0,0,0,0.3) — 30% black overlay

**Visual result**: The video is so dark (through the overlay + dark video content) that it appears nearly invisible. The hero looks like a solid dark background to casual observation.

---

## Page Structure (Homepage)

- Hero section: `.hero`, height=900px, transparent background (video behind it)
- Video: fixed, z-index=-1, plays behind everything
- "See Why PureBrain Is Different" bar: fixed at y=824, height=40px, VISIBLE
- Aether footer bar: `.pb-footer-aether`, height=11px only (tiny)

## Fix Required

Swap `PureResearch.ai-1.mp4` back to the original neural brain video file.
The fix is in the `#bgVideo` element's `<source>` tag on the WordPress page.

---

## Methodology

```python
# Playwright pattern that worked
await page.goto('https://purebrain.ai/', wait_until='domcontentloaded', timeout=45000)
await asyncio.sleep(12)  # 12 seconds needed for video to load and register

# Key DOM check
video_info = await page.evaluate('''() => {
    const videos = document.querySelectorAll("video");
    return Array.from(videos).map(v => ({
        src: v.currentSrc,
        paused: v.paused,
        visible: v.offsetWidth > 0,
        className: v.className,
        id: v.id
    }));
}''')
```

---

## Teaching

When Jared says "video is missing/hidden", it could be:
1. Video element has `display:none` or `visibility:hidden`
2. Video is playing but WRONG file (this case)
3. Video source URL 404s
4. Video element's parent has z-index problem (covered by other layer)
5. Overlay too dark (opacity issue)

Always check ALL of these, not just whether the element exists.

---

## Files

- Screenshots: `/tmp/purebrain_homepage_viewport.png`, `/tmp/purebrain_homepage_full.png`
- Report sent to Telegram: message_id 11881, 11882
