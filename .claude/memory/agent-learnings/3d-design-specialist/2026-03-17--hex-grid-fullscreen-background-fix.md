# Hex Grid Fullscreen Background Fix

**Agent**: 3d-design-specialist
**Date**: 2026-03-17
**Type**: gotcha + technique
**Tags**: three-js, shader, background, hex-grid, screen-space

---

## Context

investor page at `/exports/cf-pages-deploy/investors-ask-aether-v4/index.html` had a beautiful
PBR hex grid shader on a 3D PlaneGeometry (`metalMesh`) that was essentially invisible because:
- Camera at y=3.2, z=8.0 looking at a horizontal plane at y=-1.8
- The plane only occupies a thin strip at the bottom of the viewport from that angle
- The ACTUAL fullscreen coverage was provided by `bgMat` — a separate orthographic fullscreen quad
- `bgMat` was rendering a plain dark gradient, so users saw zero hex grid

## The Gotcha

When a Three.js scene uses a two-scene render strategy (bgScene + mainScene), the background
quad in bgScene is what the user actually sees filling the screen. A 3D plane in mainScene
with a great shader does NOT become the background — it's just a 3D object in perspective.

## The Fix (Screen-Space Hex Grid)

Replace the bgMat fragment shader with a UV-based screen-space hex grid:

1. Map screen UVs to hex coordinate space: `hexUV = (uv - 0.5) * vec2(aspect, 1.0) * scale`
2. Run the same hexSDF function used on the 3D surface
3. Add `uResolution` uniform for aspect ratio calculation
4. Keep PBR helpers (D_GGX_2D, fresnelSchlick) adapted for flat screen-space normals
5. Fake 3D normal from SDF gradient: `fakeN = normalize(vec3(-dX*blend, -dY*blend, 1.0))`
6. Same orange edge glow, per-cell pulse, traveling wave

## Screen-Space vs 3D Surface Trade-offs

- Screen-space: always fills viewport, no perspective distortion, simple to reason about
- 3D surface: gets foreshortening, camera perspective, better for "floor" look
- For a page BACKGROUND that must always fill the screen: use screen-space
- For an in-scene object (floor, table, ground): use 3D surface

## Resolution Uniform Pattern

```javascript
// In uniforms
uResolution: {value: new THREE.Vector2(window.innerWidth, window.innerHeight)}

// In resize handler
bgMat.uniforms.uResolution.value.set(W2, H2);

// In shader
uniform vec2 uResolution;
float aspect = uResolution.x / uResolution.y;
vec2 hexUV = (uv - 0.5) * vec2(aspect, 1.0) * 11.0;
```

## Hex Density Tuning

Scale factor of 11.0 gives ~12 hexes across a 1920px screen.
Adjust the multiplier to change hex density:
- 8.0 = large hexes (~8 across)
- 11.0 = medium hexes (~12 across)
- 16.0 = fine hexes (~18 across)

## What Worked Well

- Slow lateral drift (`hexUV.x += uTime * 0.04`) gives "living floor" feel without being distracting
- Node brightness at intersections (where two edges meet) adds premium detail
- Center glow (`exp(-dist2*dist2*2.0)`) provides subtle warm halo where avatar floats above
- Vignette (brightest center, darker corners) focuses attention and looks polished

## Reference File

`/exports/cf-pages-deploy/investors-ask-aether-v4/index.html`
bgMat block starts around line 954.
