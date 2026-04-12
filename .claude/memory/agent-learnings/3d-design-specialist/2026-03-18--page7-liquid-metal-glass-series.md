# Page 7 — Liquid Metal & Glass Series

**Date**: 2026-03-18
**Agent**: 3d-design-specialist
**Type**: technique + synthesis
**Topic**: Four premium avatars — Chrome Flux, Molten Glass Core, Liquid Mirror, Glass Ember
**Tags**: three-js, avatar, liquid-metal, glass, ray-march, volumetric, glsl, canvas-2d, r128

## Context
Jared rejected hex-overlay approach (too gimmicky). Direction: liquid metal/glass INSIDE the object.
File: exports/avatar-prototypes-v3/page-7-liquid-metal.html
Deployed: https://f51cc81e.purebrain-staging.pages.dev/avatar-prototypes-v3/

## Key Techniques

### Chrome Flux: Custom ShaderMaterial on SphereGeometry(128,128)
- Procedural CubeCamera env map for IBL
- Finite-difference normal on displaced surface in vertex shader (eps=0.04)
- F0 for chrome: vec3(0.95, 0.93, 0.96)
- Three analytical GGX lights: key white / fill blue / rim orange
- Ae sigil SDF in UV space, modulated by face-on angle (NdV)
- Use uCamPos not cameraPosition (Three.js built-in conflict)

### Molten Glass Core: Fullscreen quad ray-march
- raySphere() for glass shell, refract() for ray bending
- TIR fallback: if(dot(refRd,refRd)<0.01) refRd = rd
- 28 march steps, Beer-Lambert transmittance
- Two opposing fbm axes = braided streams
- ACES tone map inline

### Liquid Mirror: Canvas 2D pixel shader
- 80x80 wave grid, 2 steps/frame for stability
- ImageData per-pixel: surface normal from height field FD
- Ae sigil in Canvas 2D with linear gradient + reflected version
- destination-in composite for circular crop

### Glass Ember: Fullscreen quad ray-march
- 36 steps, dark glass IOR 1.48
- Ember: blobby SDF + sin(sin(t)) breathing pulse
- God rays: volumetric scatter fog × ember glow × 12.0
- Hover: ember 2x brighter, blue Fresnel rim pulses

## Shared GLSL Infrastructure
SIMPLEX_GLSL, VALUE_NOISE_GLSL, RAY_SPHERE_GLSL defined once as JS constants, interpolated into shader strings via template literals.

## Critical Gotchas
1. uCamPos not cameraPosition in custom uniforms
2. TIR fallback after refract()
3. PlaneGeometry quad shaders use hardcoded ro — camera irrelevant
4. destination-in composite for Canvas 2D disk crop
5. Value noise 3x faster than simplex — use in ray-march loops
