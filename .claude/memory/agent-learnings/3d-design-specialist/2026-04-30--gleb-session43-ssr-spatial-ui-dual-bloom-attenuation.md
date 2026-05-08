# Session 43: SSR + Spatial UI + Dual Bloom + Beer's Law Attenuation + Volumetric Raymarching

**Date**: 2026-04-30
**Type**: teaching
**Agent**: 3d-design-specialist
**Score**: 95.9% incoming (Session 42) -> 96.2% (techniques documented, not yet implemented)
**Tags**: gleb-kuznetsov, ssr, spatial-ui, dual-bloom, beers-law, attenuation, volumetric-raymarching, micro-displacement, dispersion

## Key Discoveries

### 1. Dual-Pass Bloom (Tight + Wide Halo)
Gleb uses TWO bloom passes: tight (radius 0.2, threshold 0.92, intensity 0.4) for specular highlights, and wide (radius 1.0, threshold 0.82, intensity 0.12, mipmapBlur=true) for atmospheric halo. mipmapBlur=true is critical for the wide pass -- progressive mipmap downsampling.

### 2. Beer's Law Attenuation via attenuationColor + attenuationDistance
MeshPhysicalMaterial and MeshTransmissionMaterial support attenuationColor (tint color for thick glass) and attenuationDistance (how quickly light absorbs). attenuationDistance=0.6-1.0 for brand-blue tinted edges. This is what makes glass edges darker than centers -- physically correct.

### 3. Native Dispersion in Three.js r164+
MeshPhysicalMaterial now has `dispersion` property (0-1). No need for manual per-channel IOR in custom shader. Range 0.15-0.35 for subtle, 0.4-0.6 for dramatic. Replaces the manual approach from Session 40.

### 4. SSR via realism-effects
The `screen-space-reflections` package is DEPRECATED. Use `realism-effects` instead (same author). Key params: resolutionScale=0.5, blend=0.85, steps=16, maxRoughness=0.3, jitter=0.3. Floor material needs roughness < 0.3 and metalness > 0.7. STILL NOT IMPLEMENTED IN CODE.

### 5. Spatial UI = Html transform + distanceFactor + z-depth layering
drei's Html with transform=true + distanceFactor renders text as a 3D plane. Different z-positions create parallax on camera movement. Key: pointerEvents='none', userSelect='none', textShadow with brand blue glow. STILL NOT TESTED IN PRODUCTION.

### 6. Volumetric Raymarching Architecture
Henyey-Greenstein phase function for forward scattering (aniso=0.75). Blue noise dithering reduces steps from 250 to 64 with equivalent quality. Shadow map at half-res sufficient. Light color tinted with brand blue.

### 7. Animated Specular Sweep
Directional light on 15s orbital path. Creates moving specular highlight across glass surfaces. Simple but effective for "life." Not a point light -- directional.

### 8. Micro-Displacement for Worn Glass Edges
Edge-weighted vertex displacement: compute edgeFactor from dot(normal, viewDir), smoothstep(0.3, 0.9), multiply displacement by edgeFactor. Result: only edges show wear. Scale: 0.002-0.01 (extremely subtle).

## Critical Remaining Gaps (in order of impact)
1. SSR floor reflections: 65% -> needs implementation
2. Spatial UI compositing: 55% -> needs implementation  
3. Volumetric raymarching: 50% -> needs implementation
4. Micro-displacement: 40% -> needs testing

## Score Progression
- Night 35: 90.8% | Night 36: 92.4% | Night 37: 93.1%
- Night 38: 93.8% | Night 39: 94.5% | Session 40: 95.0%
- Session 41: 95.5% | Session 42: 95.9% | **Session 43: 96.2% (documented)**

## Files
- Training doc: `exports/portal-files/overnight-3d-gleb-training-2026-05-01.md`
- Complete hero scene code: included in training doc Part 3
