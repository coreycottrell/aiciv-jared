# Night 10: Advanced Materials + Post-Processing (Multi-Shell Dispersion + 5-Effect Pipeline)

**Date**: 2026-03-30
**Type**: technique + teaching
**Agent**: 3d-design-specialist
**Score**: 91% (up from 89% Night 9)
**Tags**: chromatic-dispersion, multi-shell-ior, postprocessing, depth-of-field, bloom, vignette, film-grain, ssr, volumetric, beer-lambert, three-js, react-three-fiber, gleb-kuznetsov

## Core Techniques Added

### 1. Multi-Shell IOR Chromatic Dispersion
- Three nested MeshTransmissionMaterial shells with IOR 1.45, 1.50, 1.55
- Each shell rotates at different speed for temporal parallax
- Different attenuationColor per shell (blue gradient: deep -> mid -> light)
- chromaticAberration property per-material (1.2, 0.8, 0.5) + postprocessing CA (0.0015)
- Dual-layer dispersion: material-level + screen-level
- Anisotropy 0.6 on outer shell for directional specular on glass

### 2. 5-Effect PostProcessing Pipeline (Correct Order)
- **Order**: DepthOfField -> Bloom -> ChromaticAberration -> Vignette -> Noise
- **WHY this order**: DoF reads depth buffer (must be first). Bloom adds to DoF result. CA adds fringing. Vignette frames. Grain is final texture.
- DoF before Bloom = physically correct (in-focus bloom is crisp, out-of-focus bloom is soft)
- Bloom AFTER DoF = bloom halos appear on the already-blurred image, which looks natural

### 3. MeshReflectorMaterial Planar SSR
- drei's MeshReflectorMaterial on floor plane
- blur: [400, 100] (anisotropic -- horizontal more than vertical)
- mixStrength: 0.6, roughness: 0.15, mirror: 0.5
- resolution: 1024 (balance quality/performance)
- NOT true screen-space raytracing -- renders reflected camera view from below plane
- Indistinguishable from SSR for horizontal surfaces, much cheaper

### 4. Volumetric Light Beams (Billboard + Beer-Lambert)
- Custom ShaderMaterial on PlaneGeometry billboards
- Beer-Lambert absorption: exp(-depth * 0.3)
- Noise function for visible scattering particles
- Cone falloff (center bright, edges fade) + length falloff (source bright, end fades)
- Limitation: does not interact with geometry (passes through prism)

### 5. Cinematic Polish (Grain + Vignette)
- Film grain: Noise pass, ADD blend, opacity 0.015 (subliminal)
- ADD blend brightens slightly without muddying colors (vs MULTIPLY which darkens)
- Vignette: offset 0.3, darkness 0.7 (sweet spot: frames without claustrophobia)
- Range: <0.5 invisible, >0.9 tunnel vision, 0.6-0.8 is cinematic

## Parameter Reference (Three Laws Compliant)

| Parameter | Value | Law |
|-----------|-------|-----|
| Bloom threshold | 0.85 | Law 2 (restraint) |
| Bloom intensity | 0.6 | Law 2 |
| Film grain opacity | 0.015 | Law 2 |
| Chromatic aberration | 0.0015 | Law 2 |
| Vignette darkness | 0.7 | Law 2 |
| DoF bokehScale | 4 | Law 2 |
| Shell rotation speeds | 0.05, -0.03, 0.07 | Law 3 (nothing static) |
| Group rotation | 0.15 | Law 3 |
| Dust motes | 250 instanced | Law 3 |
| Animation groups | 12+ independent | Law 3 |

## Remaining Gaps (Priority Order)

1. Raymarched volumetric light cones (-3 pts) -- replace billboards with true 3D volumes
2. Hexagonal bokeh aperture shape (-1.5 pts) -- custom DoF kernel
3. Full screen-space reflections (-1.5 pts) -- all surfaces, not just floor
4. Caustic floor patterns (-1 pt) -- rainbow light spillover under glass
5. Micro-detail surface imperfections (-1 pt) -- scratch normal maps

## Files

- Component: `/home/jared/exports/portal-files/3d-training-night10-advanced-materials.jsx`
- Assessment: `/home/jared/exports/portal-files/3d-training-night10-assessment.md`
