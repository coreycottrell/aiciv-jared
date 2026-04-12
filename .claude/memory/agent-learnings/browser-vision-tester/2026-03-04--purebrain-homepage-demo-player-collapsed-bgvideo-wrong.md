# Memory: PureBrain Homepage - Demo Player Collapsed + Background Video Still Wrong

**Date**: 2026-03-04
**Type**: gotcha + pattern + teaching
**Topic**: Two critical homepage bugs: collapsed demo video player, wrong background video file still live

---

## Context

Full homepage audit requested by Jared. "Something wrong with this whole video section" + "brain video not functioning properly / other background showing through".

---

## Bug 1: Demo Video Player (pb-demo-player) Is Collapsed

### The Bug
`.pb-demo-player` container renders at only **150-214px tall** (should be ~640px for 16:9 at 1140px wide). The `<video>` element inside has `height:100%` but the container has no proper height definition.

**Current computed CSS**:
```
height: 214px    ← wrong
aspect-ratio: auto  ← should be 16/9
```

### What Works
- `pbDemoPlay()` function IS correctly defined
- On click: `video.src = MP4` is set, video loads (readyState=1), plays (paused=false)
- Duration = 316.5 seconds - file is valid
- MP4 URL: `https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Demo-Video-real-compression-and-sizing.mp4`

### Fix
```css
.pb-demo-player {
    position: relative !important;
    aspect-ratio: 16 / 9 !important;
    min-height: 300px !important;
    background: #080a12 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}
.pb-demo-player video {
    position: absolute !important;
    inset: 0 !important;
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
}
.pb-demo-player__overlay {
    position: absolute !important;
    inset: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
```

---

## Bug 2: Background Video Still Wrong File

**Confirmed again** (same as 2026-02-27 memory): `#bgVideo` is still playing `PureResearch.ai-1.mp4`.

HTML in WP page ID 11 (inside `_elementor_data`):
```html
<source src="https://purebrain.ai/wp-content/uploads/2026/02/PureResearch.ai-1.mp4" type="video/mp4">
```

This bug was identified on 2026-02-27 and apparently not fixed. Jared still complaining about it.

Fix: Swap `PureResearch.ai-1.mp4` to the correct brain animation filename. Requires `_elementor_data` update + cache clear.

---

## Page Architecture Notes (Updated)

Background layer system:
```
z-index: -1  .video-background (fixed) — bgVideo plays here
z-index:  0  .living-background (fixed) — canvas particle system + gradient orbs
z-index: 1+  All content sections
```

Video overlay darkens from 30% (hero) to 75% (scrolled) intentionally:
```javascript
const overlayOpacity = 0.3 + (scrollRatio * 0.45);
```

This means screenshots at y=2000+ look very dark — expected behavior, not a bug.

## Footer

Footer logo uses `loading="lazy"`. URL is valid (HTTP 200, 1MB PNG). Not broken.

The footer (with logo) is inside `pb-alt-footer-section` Elementor HTML widget at `offsetTop: 8701`.

---

## Demo Player HTML Structure

```html
<section class="pb-demo-section" id="pb-demo-section" aria-label="Product Demo">
  <div class="pb-demo-section__inner">
    <div class="pb-demo-section__label">Live Demo</div>
    <h2>WATCH PUREBRAIN COME ALIVE</h2>
    <p>See your AI awaken...</p>
    <div class="pb-demo-player" id="pbDemoPlayer" onclick="pbDemoPlay(this)">
      <video id="pbDemoVideo" playsinline preload="none"
             style="width:100%;height:100%;display:block;background:#080a12"></video>
      <div class="pb-demo-player__overlay" id="pbDemoOverlay">
        <!-- Play button SVG -->
      </div>
    </div>
  </div>
</section>
```

Section at `offsetTop: 2162`, height: 358px.

---

## Teaching

1. **When demo player looks "broken"**: Check container height first. A collapsed container (wrong CSS height) is different from a broken video source.

2. **`preload="none"` + no `<source>` is intentional**: The `pbDemoPlay()` function sets `video.src = MP4` on first click. This is a valid lazy-load pattern.

3. **Background video wrong-file is a recurring bug**: This was first reported 2026-02-27. If it comes up again, it means the WP page wasn't fixed after the previous audit.

4. **ERR_ABORTED on video URLs in Playwright**: Normal. Headless aborts streaming video after headers. Does NOT mean file is missing.

---

## Files

- Report: `/home/jared/projects/AI-CIV/aether/exports/screenshots/homepage-qa-20260304/HOMEPAGE-BUG-REPORT.md`
- Screenshots: `/home/jared/projects/AI-CIV/aether/exports/screenshots/homepage-qa-20260304/`
