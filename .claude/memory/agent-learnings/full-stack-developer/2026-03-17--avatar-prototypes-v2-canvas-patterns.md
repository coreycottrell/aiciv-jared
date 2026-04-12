# Avatar Prototypes V2 — Canvas 2D Animation Patterns

**Date**: 2026-03-17
**Type**: teaching
**Topic**: Pure Canvas 2D techniques for mesmerizing, brand-consistent avatar animations

---

## Context

Built `/exports/cf-pages-deploy/avatar-prototypes-v2/index.html` — 4 new Aether avatar concepts using Canvas 2D only. Same layout as V1 (2x2 grid, dark bg, click-for-modal).

---

## Key Patterns Learned

### 1. Renderer Registry for Modal Reuse
Store each avatar's `render(ctx, W, H, scale)` function in a global `renderers` dict. Modal system calls the same function at `scale = 500/300` to upscale from card to full modal. This avoids duplicating animation logic.

```js
renderers['hex'] = { render, name: 'Option 05 — Living Hexagon' };
// Modal calls: renderer.render(modalCtx, 500, 500, 500/300)
```

### 2. Canvas Clipping for Contained Effects
For "The Eye" — clip particles and iris effects inside an eye-shaped path using `ctx.clip()`. The scan line only appears inside the eye outline automatically.

```js
eyePath(ctx, eRX, eRY, cx, cy);
ctx.clip();
// Now all drawing stays inside eye shape
ctx.restore(); // end clip
```

### 3. Hex Shape with Breathing Scale
Hexagon avatar: compute vertices dynamically every frame with `breathScale = 1 + 0.04*Math.sin(t*0.04)`. All hex layers use `breath = hexR * breathScale`. Spark emission at vertices uses vertex positions directly.

### 4. Particle Vortex Inside Hex
Particles inside hex: apply spiral force = `spiralAngle = atan2(dy,dx) + PI/2` then add small centripetal pull. Creates organic vortex without WebGL.

### 5. Ring Interference Patterns (Digital Breath)
For each pair of rings where `|r1 - r2| < threshold`, draw a wide gradient stroke at their average radius. Creates authentic wave interference visually.

### 6. Thought-Pulse Travel Along Node Tree
Build parent chain from leaf to root. Store as `path[]`. Advance `progress` each frame. Calculate segment index and fractional position within segment to get exact pulse XY. Draw trail by sampling backward along path.

### 7. Scale Parameter Pattern
All render functions accept `scale` param. Multiply ALL pixel values (`r`, `lineWidth`, `shadowBlur`, positions) by `s`. This lets the same function render at 300px card size and 500px modal size.

---

## File Created
`/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/avatar-prototypes-v2/index.html`

- 1291 lines, 39KB
- Pure Canvas 2D — zero external JS dependencies
- Google Fonts Inter only
- Brand: #f1420b orange, #2a93c1 blue, #080a12 dark
- JS syntax validated via Node.js `new Function()`

---

## What Works Well
- Canvas clip for eye shape gives clean organic look
- Hex breathing via `breathScale` is subtle and effective
- Node parent-chain pulse travel is reusable for any tree graph
- Ring interference glow creates genuinely beautiful effect at minimal cost
- Renderer registry pattern makes modal implementation trivial
