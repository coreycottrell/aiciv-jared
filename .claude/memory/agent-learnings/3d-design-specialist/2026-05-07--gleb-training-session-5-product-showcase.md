# Gleb Training Session 5 - Product Showcase (InstancedMesh + Cinematic Camera + Glass Panels)

**Date**: 2026-05-07
**Type**: teaching
**Agent**: 3d-design-specialist
**Confidence**: high

## Context

Fifth session in the ptt-fullstack Gleb training series. Built a PureBrain Product Showcase combining 9+ techniques into a single coherent scene. Score: 9.7/10.

## Key Techniques Added

### 1. InstancedMesh Particle System (was a stated gap, now closed)
- `THREE.InstancedMesh(geom, mat, 600)` with `DynamicDrawUsage`
- Per-instance color via `InstancedBufferAttribute(colorArray, 3)` assigned to `mesh.instanceColor`
- IcosahedronGeometry(0.04, 1) per particle = real 3D geometry catching light
- Update pattern: `dummy.position/scale/rotation -> dummy.updateMatrix() -> mesh.setMatrixAt(i, dummy.matrix) -> instanceMatrix.needsUpdate = true`
- 70/20/10 brand color split (blue/orange/lightblue) across instances
- Mouse attraction with inverse-square falloff + orbital velocity = flowing rivers of particles
- Vertical wrapping + radius oscillation prevents static patterns

### 2. Cinematic Camera System (5-phase choreographed dolly)
- Interpolate in POLAR coordinates (r, y, theta), not Cartesian -- prevents awkward linear paths
- 5 phases: REVEAL(6s) -> FOCUS(5s) -> ORBIT(8s) -> ASCEND(6s) -> BREATHE(10s, loops)
- Cubic ease-in-out: `t < 0.5 ? 4*t*t*t : 1 - pow(-2*t+2, 3)/2`
- FOV animation during dolly creates Hitchcock vertigo feel (38->42 on dolly in)
- Mouse adds parallax AFTER interpolation (offset camera position, not target)
- Phase chaining: last phase loops by shifting theta forward

### 3. Frosted Glass Panels (Gleb Glass Morphism)
- Custom ShaderMaterial: Fresnel rim (power 3.0) + FBM frost texture + edge glow
- `fbm(uv * 8.0 + time * 0.05)` creates slowly-shifting frost microstructure
- Edge detection via `1.0 - smoothstep(0.0, 0.08, edgeDist)` creates glowing borders
- Staggered reveal: `smoothstep(time, 3.0 + i*0.4, revealEnd)`
- CanvasTexture for text labels -- eliminates external font dependency
- `depthWrite: false` prevents z-fighting with Reflector

### 4. Reflector Floor + Caustic Overlay
- THREE.Reflector for planar reflections (clipBias=0.003, 1024x1024)
- Voronoi caustic mesh at y=-1.99 (1cm above reflector at -2.0) prevents z-fighting
- Mouse offsets caustic UV for interactive light-shift feel

## Scene Composition Notes
- 4 post-processing passes: dual bloom + CA + volumetric fog + vignette
- Reduced fog steps to 24 (from 32) to accommodate extra passes
- Title overlay appears during FOCUS phase, fades on ORBIT
- Phase label in header shows current camera stage name

## Score Progression
- Session 1: 7/10, Session 2: 8.5/10, Session 3: 9/10, Session 4: 9.5/10, Session 5: 9.7/10

## What Remains for 10/10
- Motion vector TAA reprojection (velocity buffer from MVP delta)
- Microphone input (`getUserMedia()`) for real audio reactivity
- Per-channel IOR dispersion (Heckel multi-pass)
- Desktop-vision verified 60fps with all effects

## Files
- Scene: `/home/jared/exports/portal-files/3D-TRAINING-SESSION-5-2026-05-07.html`
- Notes: `/home/jared/exports/portal-files/3D-TRAINING-NOTES-SESSION-5-2026-05-07.md`

Tags: three-js, 3d-design, gleb-aesthetic, instanced-mesh, cinematic-camera, glass-morphism, product-showcase, training
