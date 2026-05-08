# Session 41: SDF Morphing Geometry + Generative Color Fields

**Date**: 2026-04-29
**Type**: teaching
**Agent**: 3d-design-specialist
**Score**: 95.5/100 overall (up from 95.0 Session 40)
**Tags**: gleb-kuznetsov, sdf-morphing, raymarching, smoothMin, generative-color, cosine-palette, noise-driven-color, FBM

## Key Discoveries

### 1. SDF Morphing Between Arbitrary Primitives

The key insight for runtime shape morphing: linear interpolation in SDF space (`mix(sdf1, sdf2, t)`) produces physically plausible intermediate shapes because SDFs encode continuous distance information. No mesh topology changes needed.

**Morph cycle implementation**:
- Divide cycle into N segments (one per shape pair)
- Use `fract(phase)` for segment-local progress
- Apply smoothstep to progress for ease-in-out
- Result: hex -> sphere -> torus -> octahedron flows naturally

**SmoothMin for organic appendages**:
```glsl
float smin(float a, float b, float k) {
  float h = clamp(0.5 + 0.5*(b-a)/k, 0.0, 1.0);
  return mix(b, a, h) - k*h*(1.0-h);
}
```
k=0.35-0.5 for liquid organic merging of small blobs into main body. Lower k (0.1-0.2) for subtle fillets. Higher k (0.8+) for fully liquid blending.

**Performance budget**: 96 marching steps at 0.75x resolution. Sufficient for smooth shapes without artifacts. Soft shadow adds 24 steps, AO adds 5 evaluations. Total ~125 SDF evaluations per pixel. Acceptable at 0.75x res on modern GPU.

**Gotcha**: Must apply rotation to point `p` before evaluating SDFs, not after. Otherwise rotation breaks distance field properties.

**Gotcha**: Micro-displacement via noise MUST be added AFTER the mix/smin operations, not inside individual SDFs. Otherwise the morph interpolates displaced surfaces incorrectly.

### 2. Generative Color Fields via Cosine Palette + FBM

**The technique**: Use a noise field (4-octave FBM) to generate a continuously varying coordinate that samples from a parametric cosine color palette.

**Cosine palette (IQ)**:
```glsl
vec3 pal(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
  return a + b * cos(6.28318 * (c*t + d));
}
```

**PureBrain-tuned palette parameters** (bias toward brand blue, orange as accent):
- a = vec3(0.15, 0.45, 0.55) -- baseline bias toward teal/blue
- b = vec3(0.45, 0.35, 0.40) -- amplitude of variation
- c = vec3(1.0, 0.8, 0.7) -- frequency per channel
- d = vec3(0.0, 0.15, 0.55) -- phase offset (introduces orange at specific t values)

**Noise field driving the palette**:
- 4 octaves of FBM (value noise or simplex)
- Time-advected: add `vec3(t*0.15, t*0.1, t*0.12)` to sample position
- Result: flowing rivers of color that shift continuously but slowly
- Additional view-dependent term: `dot(normal, viewDir) * 0.3` adds iridescent angle-dependence

**Integration with glass materials**:
- Tint refracted color: `refracted * mix(vec3(1.0), generativeColor * 1.5, 0.35)`
- Beer's law absorption uses flowing color: `exp(-absorbColor * thickness * 0.4)`
- Rim glow uses palette-shifted color for variety

**Critical insight**: Keep 60-70% of palette output in brand-blue territory. Use `smoothstep` boost after palette evaluation: `mix(baseColor, brandBlue, blueStrength * 0.4)`. This ensures brand recognition while allowing generative variation.

### 3. Combining SDF + Color Field on Same Surface

The SDF morph surface uses the generative color field as its primary material color. The technique:
1. Evaluate FBM at hit position (world space) with time advection
2. Remap to 0-1 for palette sampling
3. Add view-angle iridescence shift
4. Apply standard lighting (diffuse + specular + fresnel rim)
5. Tint specular and rim with palette-shifted variants

Result: the morphing shape looks like it's made of living, flowing branded glass rather than a solid color.

### 4. Architecture: SDF as Render Target Composited into 3D Scene

Rather than raymarching the entire scene, render SDF morph to a separate render target, then display it on a positioned plane in the main Three.js scene. This allows:
- Traditional mesh objects (glass hexes, particles) to coexist with raymarched SDF
- Independent resolution control for SDF (0.75x for performance)
- Depth compositing via plane position

**Gotcha**: Must use HalfFloatType for the SDF render target to preserve HDR values for bloom to work on.

## Performance Notes

- SDF at 0.75x resolution: negligible impact vs S40 baseline
- 6 glass hexes with generative color field: ~0.5ms additional fragment computation
- Total estimated 45-55fps on mid-range GPU (similar to S40 despite new techniques)
- FBM (4 octaves) in fragment shader: the most expensive color operation, but 4 octaves is well within budget

## Score Progression
- Night 35: 90.8% | Night 36: 92.4% | Night 37: 93.1%
- Night 38: 93.8% | Night 39: 94.5% | Session 40: 95.0%
- **Session 41: 95.5% (+0.5 points)**

## Remaining Path to 96%+
- Stochastic SSR (floor reflections of morphing shape)
- Spatial UI (3D HTML compositing with parallax depth)
- Micro-displacement (worn glass edges via heightmap perturbation)

## Files
- Scene: `exports/gleb-training/session-apr29/purebrain-hero-gleb41.html`
- Notes: `exports/portal-files/overnight-gleb-training-notes-apr29.md`
