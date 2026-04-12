# Avatar Prototypes — 4 WebGL/Canvas Concepts

**Date**: 2026-03-17
**Type**: technique
**Topic**: Self-contained HTML page with 4 interactive avatar options for Aether AI persona

## What Was Built

`/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/avatar-prototypes/index.html`

1,822 lines / ~67KB, zero external JS dependencies. Four 300x300 card avatars + modal at 500x500 with fluid background.

## Option 1 — Neural Orb (WebGL fragment shader)

- GLSL raymarcher with 28 projected 3D nodes + edge glow between close node pairs
- All node positions computed in shader via `nodePos(int i, float t)` — hash-based spherical coords
- Edge glow: inner loop over all node pairs, smoothstep line glow weighted by node distance and pulse
- Mouse brightening: `exp(-md*md * 8.0)` falloff applied to both edges and nodes
- Breathing: `scale pulse = 0.5+0.5*sin(t*0.9)` on node radii
- Orb clipping: `smoothstep(orbR+0.02, orbR-0.02, orbDist)` alpha mask

## Option 2 — Fluid Consciousness (Navier-Stokes WebGL)

- Miniature version of investor page fluid sim (SIM=128, DYE=256, ITER=20)
- Key pattern: `createDoubleFBO` with swap(), full curl+vorticity+divergence+pressure+gradient subtract pipeline
- Display shader: circle mask via `smoothstep(0.92, 0.88, dist)` in fragment shader
- Orange/blue `generateFluidColor()` using HSV: orange hue 12-34°, blue hue 195-225°, both at reduced multiplier for dark bg
- Auto-splat: `setInterval(1400ms)` + breathing ring splat `setInterval(2200ms)`
- Mouse tracking: delta between frames drives splat force

## Option 3 — Particle Entity (Canvas 2D)

- 2,200 particles placed in sphere volume via `Math.cbrt(Math.random())` for uniform density
- Sorted by projected Z each frame for depth-correct rendering
- Color gradient: `lerp(30,241,layer)` R, `lerp(100,66,layer)` G, `lerp(220,11,layer)` B — core blue, shell orange
- Escape animation: particles escape at random, travel 1.8x radius out over 2.2s then reset
- Mouse attraction: `(1-dist/80)*12*dt` force pushes particles toward cursor within 80px
- Clip circle: uses `globalCompositeOperation='destination-in'` with radial gradient at end of frame

## Option 4 — Crystalline Intelligence (WebGL raymarcher)

- Hybrid icosahedron + octahedron SDF with `smin()` smooth union
- Icosahedral folding via PHI (golden ratio) dot products with 3 normalized face vectors
- Two-pass rendering: refraction ray traces through interior with `marchInside()`, exit point refracted again
- Schlick fresnel: `F0=0.045` (glass-like)
- Color absorption: `exp(-vec3(0.35,0.18,0.06)*thickness)` tints interior blue/orange
- Energy pulses: `sin(dot(p, vec3(8,12,6)) + t*3.5)` running along edges
- stateT: `sin(t*0.35)` drives blue↔orange transition continuously

## Modal Pattern

- Background: fresh Navier-Stokes WebGL instance on `modal-fluid` canvas (560x560, orange-dominant)
- Avatar: large WebGL re-instantiation (500x500) overlaid with `position:absolute`
- Particle modal: Canvas 2D at larger scale (NUM=5000, RADIUS=210)
- Both loops gated on `modalFluidRunning` / `modalAvatarRunning` boolean flags
- Modal closed: flags set to false, both loops exit on next RAF

## Performance Notes

- Neural Orb: O(n²) edge loop in GLSL, n=28 → 378 pairs, fine for GPU
- Fluid: two WebGL contexts running simultaneously (mini + modal) — acceptable at 128 SIM
- Crystal: 90 march steps + 35 inside steps — heaviest, but contained to 300x300 canvas

## Gotchas

- Two WebGL contexts on same page: each canvas needs its own `gl` — do NOT share contexts
- Modal fluid needs fresh `gl.createBuffer()` / program setup — cannot reuse card-level programs
- `facetShift` used as GLSL global-like: declared in frag before scene() — works as implicit uniform via closure since it's a uniform
- Actually `facetShift` is a GLSL `float` set in `main()` before calling `scene()` — GLSL functions share file-scope vars, this is valid
- Canvas 2D clip trick: draw all particles, THEN apply `destination-in` circle mask as final step

## File

`exports/cf-pages-deploy/avatar-prototypes/index.html`
