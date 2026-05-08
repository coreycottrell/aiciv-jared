# Gleb Training Session 6 — Per-Channel IOR Dispersion (Heckel Multi-Pass)

**Date**: 2026-05-08
**Type**: teaching
**Agent**: 3d-design-specialist
**Confidence**: high
**Tags**: gleb-kuznetsov, dispersion, chromatic-refraction, per-channel-ior, heckel-multipass, prismatic-glass, training

## Context

Sixth session in the Gleb training series. Closed the explicit gap from Session 5 ("Per-channel IOR dispersion (Heckel multi-pass)"). Single-technique deep drill, not a kitchen-sink scene. Score: 9.8/10.

## The Drill: Per-Channel IOR Dispersion

### Why dispersion ≠ chromatic aberration

CA shifts a single sampled color by a vec2 offset per channel — it tints edges. **Dispersion** evaluates the GLSL `refract()` function THREE times with three different IOR values, producing physically distinct refraction vectors per channel. The result is rainbow-spread inside the glass volume, not just edge-tint.

### Locked parameters (Gleb sweet spot)

```glsl
float etaR = 1.0 / 1.15;  // 0.870 - red bends LEAST
float etaG = 1.0 / 1.18;  // 0.847 - reference
float etaB = 1.0 / 1.22;  // 0.820 - blue bends MOST
```

**IOR spread = 0.07** between R and B. Tighter (0.02-0.04) = production-subtle. Wider (0.10+) = artistic prism. 0.07 is the calibrated sweet spot.

### The 16-sample loop is non-negotiable

```glsl
vec3 color = vec3(0.0);
const int LOOP = 16;
for (int i = 0; i < LOOP; i++) {
  float slide = float(i) / float(LOOP) * 0.1;
  vec2 oR = refractR.xy * (uRefractPow + slide) * uChromaAb;
  // ... oG, oB
  color.r += texture2D(uSceneTex, screenUV + oR).r;
  color.g += texture2D(uSceneTex, screenUV + oG).g;
  color.b += texture2D(uSceneTex, screenUV + oB).b;
}
color /= float(LOOP);
```

- 1 sample = looks like CA (banding, no spread)
- 8 samples = grainy on faceted geometry
- **16 samples = the floor for production quality**
- 32 samples = no visible improvement, ~30% perf hit
- Mobile fallback: drop to 8 with `#define`

### Backside FBO is mandatory

Glass refracts what's BEHIND it. You need a pre-rendered scene texture WITHOUT the glass mesh:

```js
// Pass 1
glassMesh.visible = false;
renderer.setRenderTarget(sceneRT);
renderer.render(scene, camera);
renderer.setRenderTarget(null);

// Pass 2
glassMesh.visible = true;
composer.render();  // glass shader samples sceneRT
```

`HalfFloatType` RGBA target preserves HDR for downstream bloom.

### Edge prismatic boost (my addition beyond Heckel)

```glsl
float edge = pow(1.0 - abs(dot(V, N)), 6.0);
vec3 prismatic = vec3(
  sin(uTime * 0.3 + edge * 8.0),
  sin(uTime * 0.3 + edge * 8.0 + 2.094),
  sin(uTime * 0.3 + edge * 8.0 + 4.188)
) * 0.5 + 0.5;
color += prismatic * edge * 0.35;
```

Power-6 falloff isolates near-grazing pixels. Real prisms cast strongest rainbows at glancing incidence. This is Gleb's signature edge-glow tell.

### Fresnel mix at 0.55

Schlick fresnel with envmap reflection blended at 0.55 ratio. Higher = mirror, lower = no shine. 0.55 = correct.

### Saturation post-boost = 1.35x

16-sample averaging desaturates output. Boost back: `mix(vec3(luminance), color, 1.35)`.

## Cauchy physics anchor

Real dispersion: `n(λ) = A + B/λ²`. Crown glass A=1.5046, B=4.2e-14. R=650nm, G=510nm, B=475nm. True IOR spread is 0.01. We exaggerate to 0.07 for visible artistic effect. Knowing the physics anchors parameter choices.

## Background design rule

Dispersion is INVISIBLE on uniform backgrounds. Practice scene uses:
- Radial blue gradient (PureBrain blue)
- Animated orange ribbons (sin-driven)
- 8 floating brand-color accent spheres
- Vertical R/G/B test stripes (subtle)

This gives the dispersion something to *split*. Production scenes need this principle baked into composition.

## Geometry behavior matrix

| Geometry | Dispersion character |
|---|---|
| Faceted icosahedron (subdiv 1) | Visible prismatic spikes at facet edges — strongest "Gleb crystal" look |
| Smooth sphere (96x96) | Soft gradient dispersion — production-hero subtle |
| Triangular prism (CylinderGeometry, 3 sides) | Canonical "Pink Floyd" rainbow split — most explicit |

Use faceted for hero/identity, smooth for atmospheric, prism only when explicit prismatic is the message.

## Production application matrix

| PureBrain asset | IOR spread | Notes |
|---|---|---|
| Blog banner 1200x630 | 0.04 | Subtle production-grade |
| LinkedIn 1080x1350 | 0.08 | Thumb-stop edge boost 0.5 |
| Homepage hero 3D | 0.05 | Live Three.js, mobile fallback |
| Aether avatar orb | 0.06 | Refract brand-token backdrop |

## Files

- Practice scene: `/home/jared/exports/portal-files/3D-TRAINING-SESSION-6-DISPERSION-2026-05-08.html` (393 lines, 15.2KB)
- Training notes: `/home/jared/projects/AI-CIV/aether/exports/portal-files/overnight-design-training-2026-05-08.md`

## Score progression

- S1: 7.0 | S2: 8.5 | S3: 9.0 | S4: 9.5 | S5: 9.7 | **S6: 9.8**

## Remaining for 10/10

- Anisotropic specular (next night drill — Session 7)
- Motion-vector TAA reprojection
- Microphone audio reactivity
- True SSR (depth+normal MRT)

## Gotchas

- `texture2D(uSceneTex, uv + offset)` MUST clamp UV to `0.001 - 0.999` or you get edge wrap artifacts at extreme refraction.
- The `refract()` function returns `vec3(0)` for total internal reflection. Test with `length(refractVec) < 0.01` if you need to handle that case (we don't here — backside Fresnel covers it).
- Don't add the dispersion samples in linear space then tonemap — that double-tonemaps. Composer's OutputPass handles final tonemap; shader output is HDR.
- PMREM env map fromScene needs `roughness 0.04` not 0 — exact 0 produces banded reflections.

## Next-night plan (Session 7, May 9)

Anisotropic specular drill. Tangent-space anisotropy + GGX anisotropic distribution. Combine with dispersion glass from tonight on a hex mark — half prismatic glass, half brushed brand-orange metal. The glass+metal hybrid is what Gleb does on hardware mockups.
