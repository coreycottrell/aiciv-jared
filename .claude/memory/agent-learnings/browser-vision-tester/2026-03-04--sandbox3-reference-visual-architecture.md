# Sandbox-3 Reference Page Visual Architecture

**Date**: 2026-03-04
**Agent**: browser-vision-tester
**Type**: technique + architecture + pattern
**Tags**: sandbox3, brain-video, demo-video, footer, background, css-architecture, reference-audit

---

## Context

Performed reference audit of `https://purebrain.ai/pay-test-sandbox-3/` to document the CORRECT visual state of the page for comparison against the homepage (which may be broken).

---

## BRAIN VIDEO BACKGROUND

### Architecture
- Element: `#bgVideo` class `.video-background__video`
- Container: `.video-background` with `position: fixed; z-index: -1`
- Source: `https://purebrain.ai/wp-content/uploads/2026/02/PureResearch.ai-1.mp4`
- 4K resolution (3840x2160), autoplay, loop, muted
- Poster: `MA1.BI-1.2.4-002-211107-Icon-PT.png` (shown while loading)
- readyState 2 when screenshot taken (loading), no errors

### CSS z-index Stack
```
z=-1: .video-background (fixed, brain video - always behind everything)
z=auto: Elementor sections (on top of video)
z=10003: #videoModal
z=99999: .video-modal__close
```

### Key: The brain video bleeds through TRANSPARENT hero and section backgrounds
Body bg: `rgb(10, 14, 26)` (#0a0e1a)

---

## DEMO VIDEO PLAYER

### Two Systems
1. **`#pbDemoVideo`** - embedded player (960x540), NO src at page load (preload="none"), source set dynamically by `pbDemoPlay()` onclick
2. **`#demoVideo`** - modal player with src to MP4 but type declared as `application/vnd.apple.mpegurl` (HLS MIME type on MP4 URL)

### Demo Section CSS
```css
#pb-demo-section {
    background: linear-gradient(
        rgba(8, 10, 18, 0) 0%,
        rgb(8, 10, 18) 8%,
        rgb(8, 10, 18) 92%,
        rgba(8, 10, 18, 0) 100%
    );
}
```
This creates floating section effect - brain video bleeds through top/bottom 8%.

### Play Button Design
Frosted glass circle: `background: rgba(255,255,255,0.15); backdrop-filter: blur(8px); border: 2px solid rgba(255,255,255,0.3)`

---

## FOOTER

- Located at y=9,435px (page height 9,763px)
- Logo: Full side-by-side Pure Technology logo (NOT just icon)
- Logo file: `MA1.BI-1.2.6-001-211107-Side-by-Side-Main-Orange-PT-scaled.png`
- Copyright: "© 2026 Pure Technology Inc."
- Links: Privacy & Terms | Contact Us | Team (row 1), PureTechnology.ai | PureMarketing.ai | PureInfluence.ai (row 2)
- Height: 198px
- Container: Elementor section with class `pb-alt-footer-section`

---

## WHAT "CORRECT" LOOKS LIKE (for homepage comparison)

1. Hero: TRANSPARENT background - brain video visible behind it (cosmic/space with hexagonal geometry)
2. Demo section: Gradient dark background (#080a12), NOT solid orange/white
3. Footer: Full side-by-side logo, dark background
4. Body: `rgb(10, 14, 26)` (#0a0e1a) dark navy background
5. All sections: Dark themed, no light/orange backgrounds

## COMMON FAILURE PATTERNS (from past experience)
- Orange background = plugin CSS override setting `background-color: orange !important`
- Brain video not showing = z-index wrong or `position: fixed` removed
- Demo video broken = `pbDemoPlay()` function missing or source URL wrong
- Footer logo wrong = different file or CSS override hiding it

---

## Reference Files

- Screenshots: `/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-reference-20260304/`
- KEY shots: `A1-hero-brain-bg-desktop.png`, `A6-pb-demo-video-element.png`, `B2-page-bottom.png`
- Report: `REFERENCE-AUDIT-REPORT.md` in same directory
- Data: `css-full-analysis.json`, `video-elements.json`
