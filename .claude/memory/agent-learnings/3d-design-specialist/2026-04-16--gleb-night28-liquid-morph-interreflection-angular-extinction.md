# Night 28: Liquid Morphing + Multi-Object Interreflection + Angular Extinction

**Date**: 2026-04-16
**Type**: technique + teaching
**Agent**: 3d-design-specialist
**Score**: 78.6/100 overall (up from ~76 est. prior)
**Tags**: gleb-kuznetsov, anisotropic-specular, liquid-morphing, interreflection, angular-extinction, atmospheric-scattering, chromatic-fresnel

## Key Discoveries

### 1. Ward Anisotropic Specular Creates Liquid Surface Tension Feel
- Ward model with flow-field-driven tangent rotation produces directional highlight streaks
- alphaX=0.05 (along flow), alphaY=0.15 (across flow) gives convincing liquid surface
- Varying anisotropy with morph phase makes transitions feel physically motivated
- This is more convincing than isotropic Blinn-Phong for liquid surfaces

### 2. Inter-Object Glass Refraction is THE Multi-Object Technique
- Light refracted through blue glass hitting orange glass creates convincing colored illumination
- Secondary bounce approximation (one extra refraction trace after exit ray) is enough
- Per-object IOR + absorption coefficients make each object visually distinct
- Shared ground plane collecting caustics from all objects unifies the scene

### 3. Angular Extinction Creates "Living Material" Effect
- Rayleigh wavelength^-4 absorption dependence: blue at head-on, amber at grazing
- This makes glass look alive - the color shifts as you orbit the camera
- Combined with chromatic Fresnel (per-channel IOR variation), edges get color fringing
- The "atmospheric shell" technique (thin scattering layer around object) adds depth

### 4. Composition is Now the Primary Growth Area
- Shader technique capability is at 90%+
- Art direction / composition skill is at ~72%
- Diminishing returns on new shader effects
- Next training sessions should focus on WHERE to place objects, not WHAT effects to apply
- Study Gleb's framing: rule of thirds, negative space, visual hierarchy

### 5. Smooth-Min SDF Blending Parameters
- k=0.4 for viscous liquid transitions (honey-like)
- k=0.2 for quick water-like blending
- Animated k (0.2-0.6 via sine) creates breathing/pulsing morph quality
- Noise displacement on top of smooth-min adds organic surface detail

## Gotchas
- Ward anisotropic model can produce NaN if NdH approaches zero - use max(NdH, 0.001)
- Atmospheric shell requires careful sphere intersection math (two nested spheres)
- Multi-object scenes with inter-object rays need careful self-intersection avoidance (offset by N * 0.01)
- 5-wavelength loop is sufficient for visual quality; 7-wavelength adds cost without visible improvement

## Files Generated
- `exports/3d-experiments/gleb-night28-liquid-morphing-anisotropic.html` (14.8KB)
- `exports/3d-experiments/gleb-night28-multi-object-interreflection.html` (16.0KB)
- `exports/3d-experiments/gleb-night28-angular-extinction-atmosphere.html` (16.4KB)

## Training Log Entry
- Training report: `/home/jared/exports/portal-files/overnight-gleb-training-session-2026-04-16.md`
- Prior nights studied: 24, 25, 26, 27
- New techniques: 3 (anisotropic specular, inter-object refraction, angular extinction)
- Cumulative technique count: 25+ distinct shader techniques mastered

## Next Session Goals
1. Composition exercises: asymmetric placement, negative space, visual hierarchy
2. Study Gleb's Ava RC series for composition principles
3. Color palette restraint: 2-3 colors max per scene
4. Scale contrast: large hero + small detail elements
5. Background gradient as design element (not just "dark")
