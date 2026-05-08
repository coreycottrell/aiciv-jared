# Gleb Training Session 4 - Advanced Techniques

**Date**: 2026-05-06
**Type**: teaching
**Agent**: 3d-design-specialist
**Confidence**: high

## Context

Fourth session in the ptt-fullstack Gleb training series. Closed 5 of 5 gap areas from session 3. Score: 9.5/10.

## Key Techniques Added

### 1. Volumetric Fog via Raymarching ShaderPass
- Fullscreen post-process, NOT scene geometry
- 32 steps, stepSize=0.3, Beer's Law transmittance: `exp(-totalDensity * 4.0)`
- Henyey-Greenstein phase function with g=0.7 (forward scatter)
- FBM noise (3 octaves) for density variation
- Height falloff + radial falloff keeps fog grounded near scene center
- Requires: camera position, inverse projection+view matrices as uniforms

### 2. Reflective Floor (Fresnel Pseudo-Reflection + Voronoi Caustics)
- Schlick Fresnel: `pow(1.0 - NdotV, 5.0)` for reflection intensity
- Dual-layer Voronoi caustics at 3.0x and 5.1x scale
- `pow(1.0 - m_dist, 8.0)` transforms Voronoi cells to sharp caustic lines
- Not true SSR but reads convincingly on dark floors

### 3. Temporal Anti-Aliasing
- Halton sequence (base 2,3) for 8 sub-pixel jitter offsets
- `camera.setViewOffset()` applies jitter, `camera.clearViewOffset()` after render
- 3x3 neighbor clamping prevents ghosting: `clamp(prev, neighborMin, neighborMax)`
- Blend weight 0.9 (90% previous frame)
- IMPORTANT: use uniform uResolution instead of `textureSize()` for WebGL1 compat

### 4. Audio Reactivity
- `AnalyserNode` with fftSize=512, `getByteFrequencyData()`
- Band split: bass(0-15), mid(16-80), treble(80+)
- Map: bass->IOR shift+CA, mid->caustic scale, treble->fog density
- Demo: dual oscillators (80Hz+LFO + 220Hz triangle) for built-in source
- Smooth decay when audio disabled: `level *= 0.95`

### 5. Choreographed 4-Phase Timeline
- 8s per phase, cubic ease-in-out transitions
- Phases: AWAKENING (scale in) -> EXPANSION (grow+intensify) -> PULSE (rhythmic) -> TRANSCENDENCE (calm)
- Each phase modulates: scale, bloom strength, fog density, rotation speed, light color, particle size
- Stage name displayed as UI overlay

## Gotchas

- `textureSize(tDiffuse, 0)` fails on WebGL1 -- use uniform resolution
- TAA jitter must be cleared (`camera.clearViewOffset()`) after render or UI gets jittery
- Fog raymarching is expensive -- 32 steps is the sweet spot (16 too grainy, 64 kills fps)
- Audio reactivity needs gradual decay, not instant zero, or visuals "pop" when audio stops
- Choreography easing: cubic is better than linear but quadratic is too sharp for long phases

## Score Progression
- Session 1: 7/10, Session 2: 8.5/10, Session 3: 9/10, Session 4: 9.5/10

## What Remains for 10/10
- True SSR (depth+normal MRT, screen-space ray march)
- Motion vector TAA reprojection
- Microphone input for real audio
- Instanced mesh particles instead of Points
- Combine with nightly series: thin-film iridescence, SDF morphing, anisotropic specular

## Files
- Scene: `/home/jared/exports/portal-files/gleb-training-scene-4-2026-05-06.html`
- Report: `/home/jared/exports/portal-files/3D-DESIGN-TRAINING-SESSION-4-2026-05-06.md`

Tags: three-js, 3d-design, gleb-aesthetic, volumetric-fog, raymarching, taa, audio-reactive, choreography, training
