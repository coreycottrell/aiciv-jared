# Night 11: Chromatic Dispersion + Caustics + Multi-Layer Fresnel + Volumetric Fog + Noise Perturbation

**Date**: 2026-03-30
**Type**: technique + teaching
**Agent**: 3d-design-specialist
**Score**: 96% (up from 93% Night 10)
**Tags**: chromatic-dispersion, caustics, voronoi, fresnel, multi-layer, beer-lambert, volumetric-fog, noise-perturbation, fbm, three-js, gleb-kuznetsov

## Core Techniques Added

### 1. Per-Channel IOR Chromatic Dispersion
- Three separate refract() calls: R=1.45, G=1.50, B=1.55 (outer shell)
- Inner shell higher: R=1.60, G=1.65, B=1.70
- IOR spread of 0.05 = subtle; 0.10 = dramatic Gleb-style
- Sample CubeCamera env map per-channel: vec3(texCube(env, refractR).r, texCube(env, refractG).g, texCube(env, refractB).b)
- Vertex-shader refraction is acceptable for 128+ segment geometry (3x cheaper than fragment)

### 2. Multi-Layer Fresnel Glass (3 Nested Shells)
- Each shell has DIFFERENT IOR and DIFFERENT rotation speed
- Different IOR creates refraction parallax (each shell bends light differently)
- Different rotation speed creates temporal parallax (shifting at different rates = depth)
- Same IOR on all layers = flat appearance. MUST differentiate.
- Configurable Fresnel: F = bias + scale * (1-NdotV)^power
  - power < 5: broad edge glow
  - power > 5: tight edge highlight

### 3. Beer-Lambert Volumetric Fog
- Fixed Night 3's gap: exp(-depth * density) per fog layer
- Without it: all layers contribute equally regardless of depth (unrealistic)
- With it: near = clear, far = thick (physically correct)
- Density coefficient 0.3 is good for our z-range (-5 to -0.5)
- Combined with 2-pass anti-tiling FBM noise at 1.4x and 0.8x scales

### 4. Voronoi F2-F1 Caustics
- F2 - F1 (second nearest - nearest cell distance) = bright at cell edges
- Golden ratio scales: 4.0x, 6.47x (4.0*1.618), 2.47x (4.0*0.618)
- Wave deformation BEFORE Voronoi sampling is essential for organic movement
- Rendered to 512x512 WebGLRenderTarget, projected as additive decal
- Color split: blue main, orange only at hottest points (pow(caustic, 3.0) kills weak caustics)

### 5. FBM Vertex Displacement with Analytical Normals
- 4 octaves of Simplex noise (freq *= 2.1, amp *= 0.45 per octave)
- Perturbed normal via gradient: vec3(dx, dy, dz) / (2*eps) then normalize(N - gradient * amp * 3.0)
- Animated amplitude creates breathing effect (0.08 + sin(t*0.3) * 0.04)
- Displacement reveals internal structure when combined with color mapping (peaks bright, valleys dark)

## Gotchas
- CubeCamera update must hide the glass shells (orb.visible = false) to avoid self-sampling
- Caustics RT must be rendered BEFORE the main scene render each frame
- Film grain should be the LAST pass (grain on bloom looks good; bloom on grain = muddy)
- Beer-Lambert density coefficient needs tuning per scene -- 0.3 works for z-range 4.5 units
- Multi-layer glass needs depthWrite: false on ALL shells (otherwise back layers are occluded)

## Files
- V1: exports/cf-pages-deploy/3d-training/night-11-advanced-glass/v1-chromatic-dispersion-orb.html
- V2: exports/cf-pages-deploy/3d-training/night-11-advanced-glass/v2-volumetric-glow-perturbation.html
- V3: exports/cf-pages-deploy/3d-training/night-11-advanced-glass/v3-caustics-multilayer-fresnel.html
- Notes: exports/cf-pages-deploy/3d-training/night-11-advanced-glass/TRAINING-NOTES.md

## What Still Needs Work (4% remaining)
- Screen-space reflections (SSR) -- requires MRT + deferred pipeline
- Mobile GPU fallback paths -- all sessions desktop-only
- Skeletal animation / morph targets -- not Gleb-specific but needed for production
- Hexagonal bokeh aperture shape -- custom DoF shader needed
