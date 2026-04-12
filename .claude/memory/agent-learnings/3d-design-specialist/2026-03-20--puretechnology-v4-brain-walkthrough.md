# Pure Technology V4 — "Step Inside the Brain"

**Date**: 2026-03-20
**Type**: technique + synthesis
**Agent**: 3d-design-specialist
**Tags**: three.js, brain, neural-network, scroll-camera, inside-brain, fibonacci-lattice, pure-technology, gsap, postprocessing
**Confidence**: high

---

## Context

Jared requested V4 of the Pure Technology 3D page: "Step Inside the Brain" — a scroll-driven camera journey that starts outside a 3D neural brain and ENTERS it at 45-70% scroll.

Previous versions:
- V1/V2: particle lines (underwhelming per Jared)
- V3: full Navier-Stokes fluid simulation (dynamic but not brain-specific)
- V4: actual brain neural network you walk inside (this build)

---

## What Was Built

Single-file Three.js page (no R3F, no external build required). CDN imports via importmap (`three@0.161.0`).

### Brain Architecture

**Brain geometry**: Fibonacci lattice of 200 nodes (80 mobile) distorted into brain-lobe shape:
- Frontal lobe: `z * (1.0 + 0.35 * z)` — protrudes forward
- Vertical flatten: `y * 0.82` — brain is not perfectly spherical
- Left/right asymmetry: `x * (1.0 + 0.05 * Math.sin(theta * 3))`

**Node material**: `MeshPhysicalMaterial` with `transmission: 0.7` — glass nodes that refract light

**Neural pathways**: Line segments connecting all node pairs within `CONNECTION_DIST = 2.8` units (caps at 320 lines). Opacity based on inverse distance.

**Signal particles**: 100 mesh spheres that travel along node-to-node paths. Orange (30%) and blue (70%). Fade in/out using `Math.sin(t * Math.PI)`.

### 5-Section Scroll Journey

Camera keyframes for 7-point spline through brain:
```
0.00 → z=14 (outside, full brain view)
0.18 → z=11, x=5 (orbits right, temporal lobe)
0.38 → z=7 (moving forward, brain separates visually)
0.58 → z=1.2 (entering brain)
0.75 → z=-0.5 (fully inside, looking around)
0.88 → z=0.2 (deepest inside)
1.00 → z=13, y=2 (pulls back — CTA, full orange state)
```

`currentScrollProgress += (rawProgress - currentScrollProgress) * 0.05` — 5% lerp gives smooth camera inertia.

### Panel System

5 `position: fixed` panels, toggled by `.visible` class on scroll section detection. Panels:
0. Hero (scroll 0-18%)
1. Services / What PT Does (18-40%)
2. Process / How It Works (40-60%) — lobes light up sequentially
3. Inside the Brain / Features grid (60-82%)
4. CTA (82-100%) — brain explodes + reassembles

### Brain Explosion (CTA Section)

Pre-computed random "explode targets" per node, linear interpolation out and back:
```js
if (explosionProgress < 0.5) lerp(originalPos, explodeTarget, t*2)
else lerp(explodeTarget, originalPos, (1-t)*2)
```
`explosionProgress` advances at `delta * 0.35` when section === 4.

### Postprocessing

`UnrealBloomPass` intensity dynamically scales:
- Base: 0.8
- Inside factor adds +0.8 (bloom intensifies as you enter)
- CTA explosion adds +1.5

---

## Performance Notes

- `Math.min(window.devicePixelRatio, 2)` to prevent 4k rendering on retina
- Signal particles: 100 desktop / 40 mobile
- Node count: 200 desktop / 80 mobile
- Connection lines: 320 desktop / 120 mobile
- Single WebGL context throughout

---

## Files

- Source: `exports/puretechnology-3d-redesign/v4-brain-walkthrough.html`
- CF Deploy: `exports/cf-pages-deploy/puretechnology-3d-redesign/v4-brain-walkthrough.html`
- Live URL: `https://a7a74329.purebrain-staging.pages.dev/puretechnology-3d-redesign/v4-brain-walkthrough.html`

---

## Gotchas

- `scene.fog = new THREE.FogExp2(#080a12, 0.018)` — essential for the "entering darkness" effect as camera goes inside. Without fog, the experience feels flat.
- Connection lines need `.rotation.copy(nodeGroup.rotation)` to stay aligned as brain rotates. Easy to miss, causes visual disconnect.
- `OutsideFactor = Math.max(0, 1 - progress * 3)` controls how much mouse tilt applies. Must fade to 0 before entering brain or camera jerks wildly inside.
- Signal particles: apply `nodeGroup.rotation` as euler to get world-space positions: `from.clone().applyEuler(nodeGroup.rotation)`.
- Brain rotation stops as you go inside (`rotSpeed = Math.max(0, 1 - progress * 4)`). If it keeps rotating inside the brain, orientation becomes disorienting.

## Lobe Sequence Animation

`activeLobeTimer` accumulates delta time at `* 0.4` rate, triggers lobe switch at `> 1`. Orange lobe illumination uses `material.color.lerpColors(current, ORANGE, 0.06)` per frame — smooth color transition.
