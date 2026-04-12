# Night 9: Depth of Field + Anisotropic Specular

**Date**: 2026-03-30
**Type**: technique + teaching
**Agent**: 3d-design-specialist
**Score**: 89% (up from 87% Night 8)

## Core Techniques Added

### Anisotropic GGX BRDF
- Split roughness into alphaT (along tangent) and alphaB (along bitangent)
- Formula: `alphaT = roughness * (1 + anisotropy)`, `alphaB = roughness * (1 - anisotropy * 0.7)`
- Need TdotH, BdotH, TdotV, BdotV for the NDF and geometry terms
- Tangent direction from FBM displacement gradient (same finite-difference as normal computation)
- Anisotropy value 0.78 is aggressive but reads clearly as "flowing metal"
- Below 0.3 the stretch is too subtle to notice
- The 0.7 factor on alphaN prevents cross-flow roughness hitting zero (avoids NaN/singularities)

### BokehPass Depth of Field
- Three.js BokehPass: `focus`, `aperture`, `maxblur` uniforms
- For web 3D at camera z=5-6: aperture 0.01-0.02, maxblur 0.01-0.015
- Measure actual distance from camera to hero object for focus value
- Breathing animation on focus (+/- 0.15 units at 0.25 Hz) adds life without visible jitter
- BokehPass BEFORE BloomPass in chain (bloom on blurred areas = pleasant glow-in-bokeh)

### Depth Staging for DoF
- Added 6 glass spheres at deliberate depths (3 near z=3.8-4.5, 3 far z=-3 to -5)
- Makes DoF effect unmistakable -- objects outside focal plane visibly blur
- DoF creates visual hierarchy without changing object size/position

## Gotchas
- BokehPass reads depth buffer automatically -- no manual depth texture setup needed
- Must pass tangent AND bitangent as varyings from vertex shader (not just normal)
- Anisotropic Smith geometry term must also use tangent-space dot products (not just NDF)
- maxblur caps prevent smearing artifacts at extreme depth differences

## Files
- Demo: `/home/jared/exports/portal-files/gleb-training-march30.html`
- Notes: `/home/jared/exports/portal-files/3d-training-notes-march30.md`

## What Still Needs Work
- Hexagonal bokeh aperture shape (current is gaussian, not cinematic)
- Spatially varying anisotropy (flow velocity per vertex)
- Screen-space reflections (SSR)
- Split-sum approximation for anisotropic env map filtering
