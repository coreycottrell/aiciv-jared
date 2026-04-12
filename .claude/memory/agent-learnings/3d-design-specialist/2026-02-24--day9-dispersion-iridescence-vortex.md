# Day 9: Iridescence, Clearcoat, RYGCBV Dispersion, Vortex Interior

**Date**: 2026-02-24
**Agent**: 3d-design-specialist
**Type**: teaching
**Confidence**: high
**Tags**: three-js, glass, iridescence, clearcoat, dispersion, vortex, particles, MeshPhysicalMaterial, rygcbv

---

## Context

Overnight study session. Sprint Day 9. Gap analysis from Day 8b (Dribbble study) identified iridescence, clearcoat, dispersion, and vortex interior as the remaining real-time technical gaps. Tonight filled 4 of the 5 remaining gaps.

---

## 1. Native Iridescence in MeshPhysicalMaterial

Three.js `MeshPhysicalMaterial` has had native iridescence since r145 — thin-film optical interference effect. This was NOT in the sprint documentation until tonight.

```javascript
new THREE.MeshPhysicalMaterial({
  iridescence: 0.55,                      // 0=none, 1=full rainbow
  iridescenceIOR: 1.38,                   // MgF2 anti-reflective coating standard
  iridescenceThicknessRange: [100, 400],  // nm range affects which colors appear
});
```

**Quality levels**:
- `iridescence: 0.0` = generic glass (what we had before)
- `iridescence: 0.35` = subtle premium optical glass (Gleb's actual level)
- `iridescence: 0.65` = visible rainbow shift (artistic)
- `iridescence: 1.0` = soap bubble / full iridescent effect

**Rule**: EVERY future glass object should have at minimum `iridescence: 0.35`. It is the single biggest visual differentiator between generic and premium glass. Zero performance cost vs existing transmission material.

---

## 2. Clearcoat for Optical Depth

`clearcoat` adds a second glassy layer over the base material:

```javascript
clearcoat: 0.85,
clearcoatRoughness: 0.02,
```

**Why it matters**: At `clearcoat: 0.8`, glass looks like it has two separate glass layers — the "lens within a lens" quality. This is what distinguishes cheap glass from optical glass.

**Performance**: Adds ~1 extra rendering pass per pixel. Worth it.

---

## 3. RYGCBV 6-Channel Chromatic Dispersion

True dispersion requires per-wavelength IOR, not just RGB. 6-channel approach:

```
Red    645nm  IOR 1.500
Yellow 580nm  IOR 1.505
Green  520nm  IOR 1.510
Cyan   490nm  IOR 1.515
Blue   450nm  IOR 1.520
Violet 400nm  IOR 1.525
```

IOR increments match Cauchy dispersion equation for crown glass.

**Key insight**: Dispersion is ONLY visible at the Fresnel rim (grazing angles). Always multiply dispersion color by edge mask:
```glsl
float edgeMask = pow(1.0 - max(dot(V, N), 0.0), 2.5);
dispColor *= edgeMask;
```

Without this mask, dispersion looks garish. With it, it reads as premium optical quality.

---

## 4. Vortex Interior Particle Architecture

5,000 orbital particles inside glass sphere, AdditiveBlending, GPU-computed orbit:

```javascript
// Per-particle: orbit angle in vertex shader
float angle = aPhase + uTime * aSpeed;
vec3 pos = vec3(cos(angle) * aRadius, position.y + wave, sin(angle) * aRadius);
```

Color gradient: PureBrain blue (inner) → gold (mid) → orange (outer) matches logo vortex.

Key: `depthWrite: false` + `AdditiveBlending` so particles accumulate light rather than occlude each other.

Fade at sphere boundary using `smoothstep(0.92, 0.72, dist)` to prevent particles showing outside glass.

---

## 5. MeshTransmissionMaterial New Parameters (Drei, R3F only)

Cannot use in vanilla Three.js — requires React Three Fiber:

```jsx
<MeshTransmissionMaterial
  distortion={0.15}         // surface distortion amount
  distortionScale={0.4}     // wave frequency
  temporalDistortion={0.05} // ANIMATES the distortion — "breathing glass"
  anisotropicBlur={0.08}    // directional blur
/>
```

`temporalDistortion: 0.04-0.06` is the "living glass" technique in Milkinside's latest work.

**Note**: These properties are documented at drei.docs.pmnd.rs/shaders/mesh-transmission-material. They are NOT in Three.js core documentation. This is why they were missed in earlier sprint research.

---

## 6. Three.js TSL + WebGPU (r171+) — Production Ready

Since September 2025, Three.js r171+ has production-ready WebGPU:
- `THREE.WebGPURenderer` with zero configuration
- TSL (Three Shader Language): JavaScript → compiles to GLSL or WGSL
- Safari 26 supports WebGPU = full cross-browser coverage
- `MeshPhysicalNodeMaterial` has native `dispersion` property

**What this enables**: Compute shaders for 100K+ particles (impossible in WebGL). The next frontier for particle vortex systems.

---

## 7. Float Animation: Prime Frequency Ratios

The "breathing" quality in Gleb's work comes from irrational frequency ratios:
```javascript
Y primary:   0.55 Hz  (period ~1.8s)
Y secondary: 0.38 Hz  (ratio to primary ≈ 1.447, irrational)
X drift:     0.22 Hz  (irrational to both)
```

Pattern doesn't repeat for ~120 seconds = feels alive, not mechanical.

Compare to single-frequency: `Math.sin(t * 0.5)` — loops every 12.5 seconds, immediately reads as fake.

---

## 8. Cinematic GSAP Scroll Architecture (2025 Pattern)

Pattern from Codrops November 2025 — authoritative approach for scroll-driven 3D:

```javascript
// GSAP animates refs. Three.js reads refs. Never animate Three.js objects directly from scroll.
const cameraRef = useRef({ x: 0, y: 2, z: 5 })

gsap.timeline({ scrollTrigger: { scrub: true } })
  .to(cameraRef.current, { x: 3, z: 3 })

// In render loop:
camera.position.lerp(new THREE.Vector3(
  cameraRef.current.x, cameraRef.current.y, cameraRef.current.z
), 0.05)
```

Custom cinematic eases:
```javascript
CustomEase.create("cinematicSilk", "0.45,0.05,0.55,0.95")  // smooth reveals
CustomEase.create("cinematicFlow", "0.33,0,0.2,1")          // model rotation
```

---

## 9. N8AO Ambient Occlusion

Better than built-in SSAO. Makes glass spheres appear grounded (not floating):

```javascript
import { N8AOPass } from 'n8ao'
const n8ao = new N8AOPass(scene, camera, W, H)
n8ao.configuration.aoRadius = 1.5
n8ao.configuration.intensity = 3.0
n8ao.configuration.aoSamples = 16
n8ao.configuration.halfRes = true  // 2-4x faster, minimal quality loss
composer.addPass(n8ao)
// OutputPass MUST come after N8AO
```

---

## Reference Files

- Demo: `/home/jared/projects/AI-CIV/aether/exports/3d-experiments/gleb-day9-dispersion-vortex.html`
- Study notes: `/home/jared/projects/AI-CIV/aether/to-jared/overnight/3d-gleb-study-2026-02-24.md`
- Full report: `/home/jared/projects/AI-CIV/aether/to-jared/overnight/3d-gleb-mastery-progress-2026-02-24.md`

---

## Remaining Gaps

1. `temporalDistortion` + `anisotropicBlur` (needs R3F build)
2. TSL/WebGPU compute particles (100K+)
3. N8AO ambient occlusion (integration pattern documented — needs implementation)
4. Screen Space Reflections (SSR)
5. Design system depth (18% → dedicated sprint needed)
