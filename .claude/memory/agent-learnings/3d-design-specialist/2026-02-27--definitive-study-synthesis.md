# Memory: Definitive Gleb Kuznetsov Study Piece — Feb 27 Synthesis

**Date**: 2026-02-27
**Agent**: 3d-design-specialist
**Type**: synthesis
**Topic**: All 13-day sprint techniques crystallized into single showcase piece
**Confidence**: high
**Tags**: gleb-kuznetsov, three-js, glass, iridescence, pmrem, particles, caustics, synthesis, definitive, purebrain

---

## Context

The 13-day Gleb Kuznetsov mastery sprint concluded on Feb 26. Tonight (Feb 27) the directive was:
study Gleb's work deeply and produce a showcase piece at `exports/3d-study/gleb-study-2026-02-27.html`.

Since the sprint is already complete, this session was a **synthesis** — all techniques combined
into a single definitive composition rather than new technique discovery.

---

## Key Architectural Decisions

### 1. Custom GLSL > MeshPhysicalMaterial for Study Pieces

For maximum artistic control, the primary glass sphere uses custom ShaderMaterial:
- Vertex: 5-octave fBm deformation with finite-difference normals
- Fragment: Schlick Fresnel + GGX specular + spectral iridescence + dispersion + brand tint

Trade-off: No GLTF serialization. Correct for hero/showcase, not for model-loaded assets.

### 2. Background in Separate Ortho Scene

```javascript
renderer.autoClear = false;
renderer.clear();
renderer.render(bgScene, bgCamera);  // ortho, background first
composer.render(delta);               // main scene second
```

Cleaner than `renderOrder = -1` in main scene — no z-fighting with ground plane.

### 3. Prime Float Frequencies (120s Repeat Cycle)

```javascript
const FLOAT_FREQS = [0.55, 0.38, 0.22];
const FLOAT_AMPS  = [0.12, 0.08, 0.05];
```
Golden-ratio-approximate frequencies = 120+ seconds before pattern repeats = biological feel.
Single frequency = 12.5s repeat = obviously mechanical. Always use prime/irrational ratios.

### 4. PMREM Probe Color Choices

```javascript
kLight = 0xfff4e8  // warm white key
fLight = 0x2a93c1  // PureBrain blue fill
rLight = 0xf1420b  // orange rim (warm edge on glass)
gLight = 0x4ab8ff  // cool blue ground bounce
```

The rim light being orange is what puts brand color INSIDE the glass without tinting the glass.
When orange rim reflects off the inner glass surface, it reads as "warm light from within" — exactly
the Gleb aesthetic.

### 5. Spectral Iridescence Formula

```glsl
float phi = 6.2832 * thickness * cosTheta;
return vec3(
  0.5 + 0.5 * cos(phi + 0.0),
  0.5 + 0.5 * cos(phi + 2.094),  // 2pi/3 offset
  0.5 + 0.5 * cos(phi + 4.189)   // 4pi/3 offset
);
```

Thin-film interference physics in one function. Animate `thickness` with `sin(uTime)` = living
iridescence that shifts through spectral colors over ~8 second cycles.

---

## Techniques in the Piece

| Technique | Implementation |
|-----------|---------------|
| fBm vertex deformation | 5-octave hash noise in vertex shader |
| Finite-difference normals | Required with vertex displacement |
| Spectral iridescence | Thin-film formula in fragment shader |
| Chromatic dispersion | Per-wavelength IOR in refract() calls |
| Dual-IOR nested glass | Outer FrontSide IOR 1.52, inner BackSide IOR 1.68 |
| PMREM studio probe | 4-light setup, compiled once, disposed |
| GPU particles (30K) | All position math in vertex shader |
| Chromatic caustics | Voronoi noise with per-channel UV offset |
| Spring camera | delta-time spring, constant 4.0 |
| Prime float | 3 overlapping frequencies at irrational ratios |
| rotateOnWorldAxis rings | Tumbling orbital system, not flat spin |
| UnrealBloomPass | strength 0.52, threshold 0.82 (conservative) |
| CA + Vignette + grain | Custom ShaderPass, always before OutputPass |

---

## What This Revealed About Gleb's Work

**The core insight**: Gleb renders LIGHT, not OBJECTS.

Every composition decision in his work answers: "How is light moving through this scene,
and what is the glass doing to it?"

- The sphere is not a sphere. It is a light-bending instrument.
- The particles are not decoration. They are suspended photons.
- The caustics are not effects. They are evidence of invisible refraction happening.
- The iridescence is not color. It is the material reminding you it has thickness.

When designing future 3D for PureBrain, start with: "Where does the light come from,
what is the glass doing to it, and how does the viewer experience that?"

---

## Capability Gap (CDN vs npm)

The CDN single-file approach (used here) hits a ceiling:

| Technique | CDN Available | npm Only |
|-----------|--------------|----------|
| `temporalDistortion` | No | `@react-three/drei` |
| `anisotropicBlur` | No | `@react-three/drei` |
| N8AO ambient occlusion | No | `n8ao` package |
| MeshTransmissionMaterial | No | `@react-three/drei` |
| WebGPU compute particles | No | Three.js r171+ |
| TSL material system | No | Three.js r171+ |

For production purebrain.ai deployment: the R3F npm build unlocks 4-5 more quality tiers.
Single-file CDN is for rapid prototyping and WordPress HTML block embedding.

---

## File References

- Study piece: `exports/3d-study/gleb-study-2026-02-27.html` (1,181 lines, 35KB)
- Overnight report: `to-jared/overnight-reports/3d-design-study-2026-02-27.md`
- Sprint synthesis (definitive reference): `to-jared/3d-gleb-mastery-study-2026-02-26.md`
- All prior technique memories: `.claude/memory/agent-learnings/3d-design-specialist/2026-02-21--` through `2026-02-26--`
