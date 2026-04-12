# Glass Ember Series — GLSL ES 1.0 Compatibility Patterns

**Date**: 2026-03-18
**Type**: gotcha + technique
**Agent**: 3d-design-specialist
**Tags**: webgl, glsl, three.js, ray-marching, compatibility

## Context

Built 4 enhanced Glass Ember variants (page-8-glass-ember.html) as fullscreen quad ray-marching shaders via Three.js r128. Discovered critical GLSL ES 1.0 compatibility issues that would silently fail at runtime.

## Critical Gotchas

### 1. Dynamic Array Indexing (FATAL in GLSL ES 1.0)

**Problem**: Accessing a uniform array with a loop variable index:
```glsl
// BROKEN — will compile fail or produce undefined behavior in WebGL 1.0
for(int i=0; i<6; i++) {
  float g = uBoltIntensity[i]; // dynamic index on uniform array
}
```

**Solution**: Either:
a) Declare individual uniforms (uBI0, uBI1, etc.) and use unrolled if/else
b) Use GLSL ES 3.0 (Three.js r128 uses WebGL 1.0 by default)

Chosen approach: individual uniforms + unrolled evaluation per bolt.

### 2. Struct Return Values with Loop Index (FATAL)

**Problem**: Returning struct from a function where the struct is selected by a loop variable:
```glsl
// BROKEN
EmberCore getCore(int idx, float t) { ... }
for(int i=0; i<3; i++) {
  EmberCore c = getCore(i, t); // struct return + dynamic dispatch
}
```

**Solution**: Pre-compute all values before the march loop using concrete names:
```glsl
vec3 core0 = vec3(sin(t*0.23)*0.12, ...);
vec3 core1 = vec3(sin(t*0.41+1.1)*0.28, ...);
// Then inside loop: use core0, core1, core2 directly
```

### 3. Constant Loop Bounds Required

GLSL ES 1.0 requires loop bounds to be compile-time constants. The `const int STEPS = 44;` pattern works. Dynamic `int steps = 20 + uHover * 10;` does NOT.

## Techniques That Worked Well

### Multi-Core Ember System
Compute 3 core positions before the march loop, then evaluate `singleEmber(p, coreN, radius)` inside loop. Total cost: 3 calls × 44 steps = 132 evaluations. Performance acceptable at 300×300.

### Heartbeat Envelope (JS side)
LUB-DUB waveform computed in JS using piecewise function:
- Phase 0-0.15: fast rise (power 0.5 for sharp attack)
- Phase 0.15-0.32: sharp fall (power 1.8)
- Phase 0.32-0.55: secondary softer hump (sin envelope, 35% amplitude)
- Phase 0.55-1.0: slow decay to near-zero

BPM ~68 with ±12% organic jitter. Interval shortened when hovered.

### Chromatic Aberration (Per-Channel IOR)
March 3 separate refracted ray directions (iorR=1.455, iorG=1.485, iorB=1.515), then composite as `vec3(acc_r, acc_g, acc_b)`. Looks like actual glass dispersion. Cost: 3x ray marches but can share step count.

### Lightning Bolt Unrolling
6 bolts × 5 segments each = 30 `segDist()` calls per ray step. At 44 steps = 1320 distance evaluations per fragment. At 300×300 = ~118M calls/frame. Still runs at acceptable FPS because segDist is cheap (dot products only).

### Vein Network
Use gradient magnitude of FBM noise to find "edges" — regions where noise transitions sharply. These appear as thin veins. Only show near surface (length(p) > 0.78). Cost: 5 extra FBM samples per step.

## Performance Notes

At 300×300 with pixelRatio=1:
- Supernova (3 cores + veins + god rays): 44 steps, ~35-45fps on mid-tier GPU
- Heartbeat (single ember + shockwave + sigil): 40 steps, ~50fps
- Nebula (3-channel per-step): 42 steps, heavy. ~25-35fps
- Lightning (6 bolts × 5 segs): 44 steps, ~35-40fps

For better perf: reduce steps to 32, reduce ray origin offset.

## Reference Files

- Built artifact: `exports/avatar-prototypes-v3/page-8-glass-ember.html`
- Parent implementation: `exports/avatar-prototypes-v3/page-7-liquid-metal.html` (Glass Ember original)

## GLSL ES 1.0 Quick Reference

| Feature | ES 1.0 | ES 3.0 |
|---------|--------|--------|
| Dynamic array index | NO | YES |
| Struct return from fn | Partial | YES |
| Constant loop bounds | Required | Flexible |
| int/float implicit cast | NO | NO (neither) |
| texture2D vs texture | texture2D | texture |

Three.js r128 defaults to WebGL 1.0 (GLSL ES 1.0). To force WebGL 2.0:
```js
const renderer = new THREE.WebGLRenderer({ canvas, context: canvas.getContext('webgl2') });
```
