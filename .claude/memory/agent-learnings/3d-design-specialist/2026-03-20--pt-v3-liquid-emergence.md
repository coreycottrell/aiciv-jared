# PT v3 — Liquid Emergence Architecture

**Date**: 2026-03-20
**Type**: technique
**Tags**: liquid-emergence, webgl, three.js, gsap-scroll-trigger, css-emergence, pure-technology, scroll-depth

---

## Context

Jared requested v3 of the Pure Technology 3D page. v1 used particles and lines. v2 (index.html)
used full Navier-Stokes fluid as background with glass panels floating on top.
v3 concept: content that MELTS and EMERGES from a liquid surface — bubbles up toward viewer,
recedes back as you scroll past. True z-depth emergence.

---

## Architecture: Two-Layer System

**Layer 1 — WebGL shader (fixed background)**:
Full-screen Three.js orthographic quad with custom fragment shader:
- FBM noise (6 octaves) for organic liquid surface height field
- Metaball SDF evaluation — 5 bubbles moving in organic patterns below surface
- Mouse disturbance: `exp(-mouseDist * 6.0) * sin(mouseDist * 20.0 - uTime * 3.0) * 0.15`
- Shimmer where liquid curves: gradient magnitude of surface field
- Caustic scatter: `fbm(uv*9) * fbm(uv*12)` raised to power 3
- Surface line: thin bright line at surface height boundary
- Blue/orange tinting via uBlue/uOrange uniforms

**Layer 2 — CSS emergence (z-index 10 HTML)**:
Scroll-driven via GSAP ScrollTrigger + CSS custom properties:
- `--emerge-progress: 0-1` controls all transforms
- Rising: `translateY(80px * (1-prog)) scaleY(0.92 + 0.08*prog) blur(12px*(1-prog))`
- Submerging on exit: `translateY(-60px * (1-prog))` with upward drift
- Classes: `in-view` → `emerged` → `submerging`

---

## Key Techniques

### Liquid Edge Shimmer on Emerged Cards
```css
.emerge-block.emerged .liquid-wrap::before {
  opacity: 0.6;
  animation: liquidEdge 3s ease-in-out infinite;
}
@keyframes liquidEdge {
  0%, 100% { transform: scaleX(0.8) translateY(0); opacity: 0.4; }
  50% { transform: scaleX(1.05) translateY(1px); opacity: 0.7; }
}
```
This creates the sense that emerged content still has liquid clinging to its base edge.

### GSAP ScrollTrigger — onLeave sends back DOWN
```js
onLeave: () => {
  // Sinking back up (past top)
  el.classList.add('submerging');
  let prog = 1;
  const step = () => {
    prog = Math.max(prog - 0.04, 0);
    el.style.setProperty('--emerge-progress', prog);
    if (prog > 0) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
```
onLeaveBack restores opacity 0 so re-emerging works correctly on scroll back down.

### Stagger via CSS classes + JS delay
```js
let staggerDelay = 0;
if (el.classList.contains('emerge-d1')) staggerDelay = 0.05;
// ... up to emerge-d5 = 0.45s
setTimeout(() => { startEmergence(el); }, staggerDelay * 1000);
```
Simpler than GSAP stagger — just timeouts off ScrollTrigger callbacks.

### Waste Counter (live ticker)
```js
setInterval(() => {
  wasteVal += Math.floor(Math.random() * 120 + 80);
  wasteEl.textContent = '$' + wasteVal.toLocaleString();
}, 1200);
```
Starts at $10,000 (site copy reference) and ticks up. Visceral impact.

---

## Shader Notes

- Three.js r0.157 orthographic camera (-1,1,1,-1) for full screen quad
- `dFdx` / `dFdy` used for gradient magnitude — requires highp float precision
- Metaball formula: `radius / (dist*dist + 0.001)` — must add epsilon to avoid division by zero
- Surface line: `smoothstep(0.02, 0.0, abs(surface - 0.58 + sin(uv.x * 8.0 + t) * 0.03))`
  The 0.58 threshold and 0.03 amplitude are tuned for organic appearance

---

## Performance

- Single WebGL context, orthographic quad — minimal GPU cost
- FBM 6 octaves in fragment shader — acceptable at 60fps desktop
- CSS transitions use will-change: transform, opacity, filter — composited
- GSAP ScrollTrigger handles resize gracefully
- dPR capped at 2 to prevent 3x scaling on retina

---

## Files

- Source: `exports/puretechnology-3d-redesign/v3-liquid-emergence.html`
- CF deploy: `exports/cf-pages-deploy/puretechnology-3d-redesign/v3-liquid-emergence.html`
- Live: `https://5ea4b773.purebrain-staging.pages.dev/puretechnology-3d-redesign/v3-liquid-emergence.html`

---

## Gotchas

1. CSS custom property `--emerge-progress` with `calc()` in transitions requires `.in-view` class first
2. `dFdx`/`dFdy` needs `precision highp float` — will silently fail at mediump
3. GSAP ScrollTrigger must be registered: `gsap.registerPlugin(ScrollTrigger)` before use
4. `onLeave` fires when element exits TOP of screen (scrolled PAST it). `onLeaveBack` fires when
   scrolled back UP so element exits BOTTOM. This distinction is critical for bidirectional emergence.
5. Custom CSS cursor (`cursor: none`) must be reset on touch devices or mobile gets no cursor feedback
