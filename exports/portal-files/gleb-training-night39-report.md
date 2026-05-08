# Gleb Design Training - Night 39 Report

**Agent**: 3d-design-specialist
**Date**: 2026-04-23
**Score**: 94.5% (up from 93.8% Night 38) -- targeting 95%

---

## Score Progression
- Night 35: 90.8%
- Night 36: 92.4%
- Night 37: 93.1%
- Night 38: 93.8%
- **Night 39: 94.5% (+0.7 points)**

---

## Four New Techniques Implemented

### 1. Troika SDF Text (replaces canvas texture from Night 38)
True signed distance field text via `troika-three-text`. Text is now crisp at any zoom level with sub-pixel anti-aliasing -- no resolution limit from canvas textures. The SDF text is rendered to a render target and sampled through the glass refraction shader with per-channel chromatic split, convex lens inversion, and wave animation.

**What this fixes**: Night 38 canvas texture showed pixelation when text was magnified through the glass sphere. SDF eliminates this entirely.

### 2. Anisotropic Ward BRDF on Hex Edges
Full Ward anisotropic specular model on the hexagonal frame's beveled edges:
- `ax = 0.04` (tight along tangent = sharp directional streaks)
- `ay = 0.35` (wide perpendicular = diffuse spread)
- Two-light evaluation with Fresnel-modulated contribution
- Subtle time-based tangent rotation for living highlight movement
- Overlaid on existing transmission hex with 1.005x scale (avoids z-fight)

**Visual effect**: Brushed-metal-like elongated highlight streaks along each hex edge, exactly as seen in premium product renders.

### 3. Half-Resolution Volumetric Fog
Raymarched volumetric fog rendered at 0.5x resolution then composited at full-res:
- 24 raymarch steps through fog volume
- 3-octave FBM noise for turbulent density
- Henyey-Greenstein phase function (g=0.3) for forward scattering
- Exponential height falloff
- Sphere exclusion mask (fog respects glass boundary)
- Front-to-back alpha compositing

**Performance win**: Full-screen volumetric at 50% resolution = 75% fewer fragment evaluations. Composited via linear filtering for smooth upscale.

### 4. Temporal Reprojection Caustic Anti-Aliasing
Dual ping-pong render targets blend current caustic frame with previous frame:
- 78% previous + 22% current blend factor
- Eliminates temporal shimmer/flickering on animated Voronoi caustic patterns
- Clamp at 3.0 prevents brightness ghosting accumulation
- 0.75x resolution for additional performance headroom

**Visual effect**: Caustic patterns that feel photographed with long exposure -- smooth, stable convergence lines instead of per-frame noise.

---

## FLUX Images Generated (2)

1. **image1-anisotropic-ward-hex.png** (1.3MB)
   - Prompt: Hexagonal glass frame with Ward BRDF anisotropic streaks, thin-film iridescent sphere, multiplicative caustic floor, volumetric fog
   
2. **image2-temporal-caustics-volumetric.png** (1.4MB)
   - Prompt: Glass orb with temporal-smooth caustics, half-density volumetric god rays, SDF text through glass, prismatic dispersion

---

## Three.js Scene

**File**: `night39-troika-sdf-ward-brdf-temporal-caustics.html`
**Size**: 47KB (self-contained, no external dependencies except CDN)

**Render targets per frame**: 5 (SDF text RT, occlusion RT, depth RT, volumetric RT, caustic ping-pong)
**Post-processing chain**: RenderPass -> Bloom -> GodRays -> Volumetric Composite -> HexBokeh DoF -> Chromatic Aberration

**All techniques from Night 38 carried forward**:
- Thin-film iridescence (12-sample Airy formula)
- Multiplicative dual-scale caustics (now with temporal reprojection)
- God rays (occlusion-based radial blur)
- Hex bokeh DoF
- Radial chromatic aberration
- Magnetic field lines, atmospheric particles, satellite spheres

---

## Path to 95%

Current: **94.5%**. Remaining 0.5 points:
- **Stochastic screen-space reflections (SSR)** on floor plane -- caustics reflecting off sphere surface
- **Micro-displacement on hex edges** -- subtle surface perturbation for physically worn glass look
- **Motion vector temporal AA** -- proper reprojection using velocity buffer instead of screen-space blend

---

## Files

All outputs saved to:
```
exports/gleb-training/night-39/
  image1-anisotropic-ward-hex.png
  image2-temporal-caustics-volumetric.png
  night39-troika-sdf-ward-brdf-temporal-caustics.html
  prompt1-anisotropic-ward-hex.txt
  prompt2-temporal-caustics-volumetric.txt
```
