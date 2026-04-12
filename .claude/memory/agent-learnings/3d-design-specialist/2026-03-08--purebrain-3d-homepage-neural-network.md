# PureBrain 3D Homepage — Neural Network Particle System

**Date**: 2026-03-08
**Type**: technique
**Agent**: 3d-design-specialist
**Topic**: Full-page Three.js neural brain particle system for purebrain.ai homepage

---

## Context

Built a complete standalone HTML file for the PureBrain homepage redesign with an embedded Three.js neural network visualization as the full-page background. Single file, all CSS/JS inline, Three.js loaded from CDN.

Output: `/home/jared/projects/AI-CIV/aether/purebrain-site/public/index-3d.html`
Live URL: `https://purebrain-site.vercel.app/index-3d.html`

---

## Architecture

### Three.js Setup (No bundler, CDN only)

```
CDN: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
Canvas: fixed position, z-index: 0, pointer-events: none
Content: position: relative, z-index: 10
```

Three.js r128 is stable for CDN delivery. No import maps needed — just script tag.

### Particle System

- 560 particles on desktop, 280 on mobile (detect via `window.innerWidth < 768`)
- Positioned in biased sphere distribution (not uniform box) — creates organic brain shape
- Each particle has: position, velocity, pulse offset/speed, isOrange flag
- BufferGeometry with `position` and `color` attributes for vertex coloring
- PointsMaterial with `vertexColors: true` and `sizeAttenuation: true`

### Connection Lines

- Pre-allocated `MAX_CONNECTIONS * 6` Float32Array (2 verts * 3 coords per line)
- Use `lineGeo.setDrawRange(0, connCount * 2)` instead of rebuilding geometry each frame
- Distance threshold: 7.5 units (desktop), 6 units (mobile), increases with scroll
- Color alpha scales with proximity: `alpha = (1 - dist/maxDist) * 0.7`
- Rebuilding connections every frame is fine at these particle counts (<700 connections)

### Performance Pattern — Critical

```js
// FAST: Pre-allocated, set draw range
const linePosArray = new Float32Array(MAX_CONNECTIONS * 6);
lineGeo.setDrawRange(0, connCount * 2);
lineGeo.attributes.position.needsUpdate = true;

// SLOW: Creating new geometry or pushing to arrays each frame — avoid
```

### Camera Parallax

```js
// Mouse smooth follow
mouse.x += (mouse.tx - mouse.x) * 0.04;
// Apply to camera
camera.position.x += (camTargetX - camera.position.x) * 0.03;
camera.lookAt(0, 0, 0);
```

Lerp factor 0.03-0.04 gives smooth but responsive feel.

### Scroll-Driven Animation

```js
// Scroll progress 0-1
const maxScroll = document.body.scrollHeight - window.innerHeight;
scrollProgress = window.scrollY / maxScroll;

// Apply to connection density
const connDist = BASE_DIST + scrollProgress * 4;

// Apply to rotation
particleMesh.rotation.y = t * 0.04 + scrollProgress * 0.8;
```

Scroll increases connection density AND speeds up rotation — feels alive as user scrolls.

---

## CSS Patterns That Worked

### Glassmorphic Cards
```css
background: rgba(255,255,255,0.04);
border: 1px solid rgba(255,255,255,0.08);
border-radius: 18px;
backdrop-filter: blur(12px);
```
Top gradient line on hover (before pseudo-element) adds premium feel.

### Scroll Reveal
```js
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
```
Combined with CSS `opacity: 0; transform: translateY(32px)` → `opacity: 1; transform: none` transition.

### Marquee (CSS only, no JS)
```css
@keyframes marqueeScroll {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}
```
Duplicate items in HTML (2x) then animate -50%. No JS needed.

---

## Gotchas

1. **Soft particle boundaries**: Without boundary enforcement, particles drift off-screen over time. Solution: nudge vel back toward center when radius > threshold (not hard clamp, which creates jitter).

2. **Connection loop is O(n²)**: Acceptable at 560 particles, but would need spatial partitioning (octree) at 2000+. For web use, keep particles under 800.

3. **Canvas behind content needs `pointer-events: none`** — otherwise canvas intercepts all clicks.

4. **Color pulse via vertex color (not opacity)**: Pulsing particle opacity causes z-fighting visual artifacts. Better to pulse between bright and dim color values while keeping overall opacity constant.

5. **Mobile pixel ratio**: Cap at 1.5 on mobile to prevent GPU overload on retina phones.

---

## Brand Colors in Three.js

```js
const BLUE   = 0x2a93c1;   // PureBrain blue
const ORANGE = 0xf1420b;   // PureBrain orange
const BG     = 0x080a12;   // Dark bg

// For dim (unlit) particle state
const dimBlue   = new THREE.Color(0x1a5577);
const dimOrange = new THREE.Color(0x7a2106);
```

Ratio: 82% blue particles, 18% orange — keeps brand blue dominant, orange as accent.

---

## Deployment

- Single file to `/public/index-3d.html` in purebrain-site repo
- `npx vercel --prod --yes` from `/home/jared/projects/AI-CIV/aether/purebrain-site/`
- Live at: `https://purebrain-site.vercel.app/index-3d.html`
- Deploy takes ~15 seconds

---

## What I'd Improve Next

1. Add a subtle bloom-like effect using a second additive render pass (requires post-processing library or manual shader)
2. Animate the pyramid layers floating slightly (CSS 3D transform, no Three.js needed)
3. On mobile: replace 3D canvas with a CSS gradient animation to save GPU budget entirely
4. Add GSAP ScrollTrigger for smoother scroll-driven camera movements
