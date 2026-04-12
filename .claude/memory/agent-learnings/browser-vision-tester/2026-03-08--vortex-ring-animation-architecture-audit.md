# Memory: Vortex Ring Animation Architecture on purebrain.ai

**Date**: 2026-03-08
**Type**: operational + teaching
**Agent**: browser-vision-tester
**Topic**: Full anatomy of the spinning hexagon vortex animation covering the video background on mobile

---

## What Are the Vortex Rings?

The spinning vortex/hexagon animation is NOT the video background. It is a set of **6 pure CSS-animated `<div>` elements** with class `.vortex-ring`, all contained inside `.portal-vortex`.

### HTML Structure

```html
<section class="hero" id="hero">
  <!-- ... -->
  <div class="portal-vortex">
    <div class="vortex-ring"></div>   <!-- 150x150px -->
    <div class="vortex-ring"></div>   <!-- 280x280px -->
    <div class="vortex-ring"></div>   <!-- 420x420px -->
    <div class="vortex-ring"></div>   <!-- 580x580px -->
    <div class="vortex-ring"></div>   <!-- 750x750px -->
    <div class="vortex-ring"></div>   <!-- 920x920px -->
  </div>
  <!-- ... -->
</section>
```

### CSS Rules (from inline stylesheet)

```css
.portal-vortex {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 1000px;
  height: 1000px;
  pointer-events: none;
}

.vortex-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 1px solid transparent;
  animation: 20s linear 0s infinite normal none running vortexSpin;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

/* Each ring is a different size, color, and speed */
.vortex-ring:nth-child(1) { width: 150px; height: 150px; border-color: rgba(241, 66, 11, 0.2); animation-duration: 12s; box-shadow: rgba(241, 66, 11, 0.1) 0px 0px 30px; }
.vortex-ring:nth-child(2) { width: 280px; height: 280px; border-color: rgba(42, 147, 193, 0.15); animation-duration: 18s; animation-direction: reverse; }
.vortex-ring:nth-child(3) { width: 420px; height: 420px; border-color: rgba(241, 66, 11, 0.1); animation-duration: 24s; }
.vortex-ring:nth-child(4) { width: 580px; height: 580px; border-color: rgba(42, 147, 193, 0.07); animation-duration: 30s; animation-direction: reverse; }
.vortex-ring:nth-child(5) { width: 750px; height: 750px; border-color: rgba(58, 96, 171, 0.05); animation-duration: 36s; }
.vortex-ring:nth-child(6) { width: 920px; height: 920px; border-color: rgba(241, 66, 11, 0.03); animation-duration: 42s; animation-direction: reverse; }

@keyframes vortexSpin {
  0%   { transform: translate(-50%, -50%) rotate(0deg); }
  100% { transform: translate(-50%, -50%) rotate(360deg); }
}
```

### The Hexagon Shape

The hexagon shape is created by `clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)` applied to each ring. This clips a circular border into a hexagon.

---

## Z-Index Stacking Stack (Full Page)

```
z=-1  .living-background (display:none — not active)
z=0   .video-background (fixed, 375x812) — bgVideo plays here
z=2   .hero section (relative)
  z=2   .hero__background (absolute)
  z=auto .hero-pulse (absolute, 300x300)
  z=auto .portal-vortex (absolute, 1000x1000) — CONTAINS VORTEX RINGS
  z=auto .hero__particles (absolute)
  z=10  .hero__content (relative) — TEXT ON TOP
```

### Key Finding: The Vortex IS Between the Video and the Text

`.portal-vortex` is:
- `position: absolute` inside `.hero` (which is `z=2`)
- Centered via `transform: translate(-50%, -50%)` from `top: 50%; left: 50%`
- **1000x1000px on a 375px mobile screen** — extends 312.5px off left edge, 688px off right edge
- `pointer-events: none` — doesn't block clicks
- `z-index: auto` — stacks with document flow, visually sits above the video

The rings are visible/active: all have `display:block`, `visibility:visible`, `opacity:1`.

---

## Why It "Covers" the Video

The vortex rings sit at `z=2` (inherited from .hero's stacking context) vs the video at `z=0`. On mobile, the 920px outermost ring extends far beyond the 375px viewport. The rings are very low opacity (0.03 to 0.2) so they create a subtle but visible overlay effect over the video.

---

## Where the CSS Lives

The vortex CSS is in an **inline `<style>` element** in the page (not a separate stylesheet with a URL). `document.styleSheets` shows `href: null` (inline). This means it's embedded directly in the WordPress page HTML, likely in the plugin's injected CSS or Elementor HTML widget.

---

## The Living Background (Separate System — Currently Hidden)

`.living-background` is a completely separate animation system:
- `display: none` / `visibility: hidden` / `opacity: 0`
- Contains a canvas (`#livingCanvas`), 5 gradient orbs, 3 wave layers, noise overlay
- This system is **not active** — probably disabled intentionally

The vortex rings are the ACTIVE animation. The living-background is dormant.

---

## Teaching

1. **"Spinning vortex/hexagon" = `.portal-vortex` div with 6 `.vortex-ring` children**
2. **Hexagon shape = `clip-path: polygon(...)` on circular divs** — not SVG, not canvas
3. **CSS source = inline `<style>` tag** — modifying requires plugin CSS or Additional CSS
4. **To hide/remove**: target `.portal-vortex { display: none !important; }` or lower opacity
5. **The rings are pure CSS** — no JavaScript involved in creating them
6. **They sit BETWEEN the video (z=0) and the text (z=10)** in the hero section
