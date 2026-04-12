# 3D Design Study — Day 3 Session Notes
**Date**: 2026-03-09
**Agent**: 3d-design-specialist
**Sprint Status**: Week 2, Day 3 of Gleb Kuznetsov mastery sprint
**Output**: `exports/3d-design-study/gleb-study-session-2026-03-09.html`

---

## Memory Search Summary

Searched agent learnings before starting. Found 30+ prior sessions. Key prior work applied:

- **Night 2** (Feb 28): Prismatic RYGCBV dispersion sphere
- **Night 3** (Mar 1): 3-object composition, 7-shot camera
- **Day 1** (Mar 1): Triple-layer CDN glass ceiling reached
- **Day 2** (Mar 3): N8AO CDN availability confirmed, neural network glass nodes
- **Mar 8**: Brain v2 procedural geometry + 5-state scroll machine
- **Feb 27 synthesis**: "Gleb renders LIGHT, not objects" — core design principle

---

## What Was Studied Today

### 1. Gleb Kuznetsov 2026 Portfolio Update

Gleb continues working at Milkinside (milkinside.com). Current work:
- Glass reflection CGI pieces remain his primary output style
- "Glass blower visual" (Feb 2025) shows organic blown-glass forms — asymmetric, weight-bearing
- Key observation: he is NOT doing symmetric perfect spheres. He does forms that look like physics happened to them.
- 2026 trend: Glassmorphism is making a comeback as a design language for "depth, emotion, and realism"

**Gap identified**: Our glass is too perfect. Gleb's glass looks like it has weight, thermal history, and cooling marks. This requires fBm vertex deformation as primary form language, not just surface decoration.

### 2. Liquid Glass (Apple iOS 26 Design Language)

Major discovery for this session. Apple's iOS 26 "Liquid Glass" design language is the dominant 2025-2026 trend:

**Key techniques identified:**
- Backdrop blur + refraction mapped from live scene behind (not envMap)
- Cursor-reactive lens distortion (WebGL fragment shader, not CSS backdrop-filter)
- The "lens" distortion: radial refract from center of glass element, with variable IOR across radius
- Multiple Three.js/R3F implementations already exist:
  - `appleliquidglass.vercel.app` — Anderson Mancini's R3F implementation
  - `github.com/Zqysl/liquid-glass-webgl` — pure WebGL iOS 26-inspired
  - `github.com/dashersw/liquid-glass-js` — standalone library

**Why this matters for PureBrain:**
Liquid glass is not just an Apple thing — it's the aesthetic direction for all premium 2026 web experiences. A PureBrain "liquid glass" hero section would read as cutting-edge and premium.

**Implementation requirement:** This needs R3F + Drei MeshTransmissionMaterial (live FBO refraction). CDN-only approximation won't capture the moving-image-through-glass effect that makes liquid glass feel alive.

### 3. Advanced Dispersion + Chromatic Aberration

Research from Maxime Heckel + Codrops (March 2025):

**Per-channel IOR refraction (true dispersion):**
```glsl
// Different IOR per RGB channel = true chromatic dispersion
float iorR = 1.0 / 1.50;  // red bends least
float iorG = 1.0 / 1.52;  // green middle
float iorB = 1.0 / 1.55;  // blue bends most (blue light = shorter wavelength)

vec3 refR = refract(viewDir, normal, iorR);
vec3 refG = refract(viewDir, normal, iorG);
vec3 refB = refract(viewDir, normal, iorB);

// Sample scene/env at each refraction direction
float r = sampleEnv(refR).r;
float g = sampleEnv(refG).g;
float b = sampleEnv(refB).b;
```

This is what separates artistic chromatic aberration (post-process CA) from physically correct dispersion (per-vertex/fragment refraction). Gleb uses the real thing.

**In CDN builds:** Post-process CA is the best available approximation. Still very effective at low values (0.008-0.012 barrel offset per channel).

### 4. GSAP ScrollTrigger + Three.js Cinematic Scroll (Feb 2026 Codrops)

New Codrops tutorial (February 2026) on building multi-page WebGL gallery with scroll-triggered reveals. Key pattern:

```javascript
gsap.registerPlugin(ScrollTrigger);

ScrollTrigger.create({
  trigger: '#scene',
  start: 'top top',
  end: 'bottom bottom',
  scrub: 1,
  onUpdate: (self) => {
    // self.progress 0-1 drives camera position + material uniforms
    const t = self.progress;
    camera.position.lerpVectors(camStart, camEnd, t);
  }
});
```

GSAP ScrollTrigger is more reliable than raw `window.scroll` for smooth scrubbing because:
- Built-in velocity dampening
- Handles resize correctly
- `scrub: 1` = 1 second lag for smooth following
- `scrub: true` = instant (for tight control)

**Next session should add GSAP CDN for proper scroll-driven camera.** Current implementation uses raw scroll + manual lerp which is functional but not as smooth.

---

## What Was Built Today

### Demo: Liquid Glass × Scroll Narrative
**File**: `exports/3d-design-study/gleb-study-session-2026-03-09.html`

**Architectural improvements over Day 2:**

| Day 2 | Day 3 |
|-------|-------|
| Neural network cluster (8 nodes) | Primary hero sphere + 6 satellite nodes + hex |
| Fixed camera | Scroll-driven 5-keyframe camera path |
| No text/UI | Full scroll narrative (5 sections with text reveal) |
| IntersectionObserver for AO | Screen-space AO + vignette in single custom pass |
| fBm background only | fBm breathing background + god rays + ground mirror |
| Static scroll | Progress bar + HUD indicator |

**New techniques in this build:**

1. **Scroll-driven keyframe camera** — 5 camera positions interpolated with smooth-step as user scrolls. Scroll progress drives both camera position and material color shifts.

2. **IntersectionObserver text reveals** — eyebrow/h2/body-copy elements fade+slide in when section enters viewport. Staggered timing (0ms eyebrow, 80ms h2, 180ms body).

3. **Progress bar + Bloom scroll reactivity** — bloom.strength increases when scroll is fast (scrollV), adds kinetic energy feel.

4. **Chromatic aberration reacts to scroll** — CA offset increases with scroll velocity. Fast scroll = more CA = more cinematic.

5. **Scroll-driven material color transition** — core sphere transitions from blue to orange between sections 2-3 (the "dispersion" section). Back to blue at section 4.

6. **Ground glow pools** — canvas texture radial gradients, positioned under primary sphere (blue) and hex prism (orange). Gives each element its "shadow color."

---

## What Gleb Does That We're Still Approximating

### Gap 1: Live FBO Refraction (Liquid Glass Effect)
**Status**: CDN cannot do this. Requires npm build.

Gleb's signature glass does NOT refract from a static environment map. It refracts from the live-rendered scene behind it (via FBO capture). This means:
- Objects behind the glass appear correctly distorted through it
- The distortion moves as the background particles drift
- `temporalDistortion` animates those FBO UV coordinates = "breathing glass"

Our `MeshPhysicalMaterial` with envMap is 85-90% quality. For true Gleb-level, need:
- R3F + Drei `MeshTransmissionMaterial` (samples=10-12)
- `temporalDistortion={0.35}` — the signature animated refraction
- `anisotropicBlur={0.12}` — directional surface microstructure blur

### Gap 2: True Ambient Occlusion (N8AO)
**Status**: Screen-space AO vignette is good approximation. N8AO would be geometry-aware.

Our screen-space AO darkens scene edges regardless of geometry. N8AO would darken specifically where objects are close to each other (contact shadows, crevice shadows). For glass nodes that float near each other, N8AO would create the subtle shadowing where glass surfaces approach.

N8AO IS available via CDN now (`unpkg.com/n8ao@latest/dist/N8AO.js`) — this should be added to the next CDN build.

### Gap 3: Volumetric Particle Density
**Status**: 2800 particles = "field." Gleb = "atmospheric fog." Gap: ~15-20x.

50K+ particles at 60fps requires WebGPU compute (TSL). Only available in npm builds with Three.js r171+. For CDN, 2800-4000 particles at small sizes with AdditiveBlending is the ceiling.

**Mitigation**: Add a second "dust" particle layer at very small size (0.3-0.5) to fill in the atmosphere. Two layers of sparse particles reads denser than one layer of dense particles.

### Gap 4: Organic Form Language
**Status**: Spheres and hex prisms. Gleb = organic blown-glass asymmetry.

Gleb's forms look like they evolved. Ours look engineered. The fix:
- Apply 4-6 octave fBm vertex deformation to main sphere at formation-time (not per-frame)
- Create one-time distorted geometry, not repeated runtime deformation
- The deformation should be ±8-12% of radius — enough to read as organic, not enough to lose "sphere" readability

### Gap 5: Typography Integration
**Status**: Basic CSS text. Gleb = text embedded in 3D world via extrusion or plane mapping.

For PureBrain homepage: extrude brand text in 3D (THREE.FontLoader + THREE.TextGeometry). Place text inside the glass sphere or have it orbit the sphere.

---

## Next Sessions Plan

### Session 4 (Tonight or Tomorrow)
**Target**: Add N8AO CDN to this demo + GSAP ScrollTrigger proper integration

```javascript
// N8AO CDN integration
import {N8AOPass} from "https://unpkg.com/n8ao@latest/dist/N8AO.js";
const n8aoPass = new N8AOPass(scene, camera, W, H);
n8aoPass.configuration.aoRadius = 0.85;
n8aoPass.configuration.intensity = 2.5;
n8aoPass.configuration.color = new THREE.Color(0x030810);
// Add to composer: RenderPass → N8AO → Bloom → SMAA → Final → Output
```

### Session 5
**Target**: Build R3F npm version of this scene with:
- Drei `MeshTransmissionMaterial` (temporalDistortion + anisotropicBlur)
- Proper depth of field (DoF from @react-three/postprocessing)
- N8AO npm package

### Session 6
**Target**: Liquid Glass hero section for purebrain.ai
- Full FBO refraction on main hero sphere
- Cursor-reactive lens distortion (user moves mouse, sphere refracts differently)
- Scroll-driven emergence (sphere assembles from particles as page loads)

### Session 7
**Target**: Definitive signature piece — everything combined
- All CDN techniques maximized
- OrganicForm: fBm-distorted sphere (not perfect)
- Liquid Glass R3F iframe embed for WordPress
- Production-ready animation system

---

## Gap Analysis: Where We Are vs Gleb Level

| Technique | Our Level | Gleb Level | Gap |
|-----------|-----------|------------|-----|
| Glass material (CDN) | 90-94% | 100% | N8AO + fBm form needed |
| Glass material (npm) | 95-98% | 100% | <5% — needs temporalDistortion |
| Particle atmosphere | 60% | 100% | Volume density (WebGPU) |
| Organic forms | 55% | 100% | fBm deformation at creation-time |
| Scroll narrative | 70% | 100% | GSAP proper + cinematic camera |
| Lighting | 90% | 100% | PMREM is solid |
| Postprocessing | 85% | 100% | N8AO + full CA + grain = good |
| Typography in 3D | 20% | 100% | Not yet implemented |
| Interactive/reactive | 75% | 100% | Mouse reactive working, voice reactive not |
| Composition | 80% | 100% | Multi-object composition improving |

**Weighted average: ~77% of Gleb level (CDN), ~88% (npm R3F)**

---

## Key Insight This Session

The liquid glass research revealed something important:

**Gleb's work is not primarily about the materials. It's about the relationship between materials and narrative.**

Every piece tells a story through the progression of light. The glass sphere isn't floating in a void — it's the protagonist. The particles aren't decoration — they're evidence that the glass is affecting the surrounding space (attracting, repelling, heating). The bloom isn't an effect — it's proof of luminance.

For PureBrain specifically: the 3D should tell the story of "intelligence as luminous." The brain isn't a static organ — it's a glass instrument that catches ambient thought and focuses it into light. The scatter patterns around it should look like refracted cognition.

This is what we're building toward.

---

## File References

- Demo: `exports/3d-design-study/gleb-study-session-2026-03-09.html`
- Prior day 2: `exports/3d-design-study/day2-ao-neural-network.html`
- Prior day 1: `exports/3d-design-study/day1-transmission-material-study.html`
- Prior nights: `exports/3d-design-study/night2-prismatic-sphere.html`, `night3-composition-scene.html`
- Study plan: `exports/3d-design-study/STUDY-NOTES-AND-7-DAY-PLAN.md`

---

## Sources Consulted

- [Gleb Kuznetsov Dribbble](https://dribbble.com/glebich) — portfolio review
- [Milkinside Dribbble](https://dribbble.com/milkinside) — glass reflection CGI
- [Liquid Glass Three.js/R3F](https://appleliquidglass.vercel.app/) — Anderson Mancini implementation
- [iOS 26 Liquid Glass WebGL](https://github.com/Zqysl/liquid-glass-webgl) — pure WebGL
- [Liquid Glass JS Library](https://github.com/dashersw/liquid-glass-js) — standalone
- [Codrops Glass Torus](https://tympanus.net/codrops/2025/03/13/warping-3d-text-inside-a-glass-torus/) — MeshTransmissionMaterial params
- [Codrops Cinematic GSAP](https://tympanus.net/codrops/2025/11/19/how-to-build-cinematic-3d-scroll-experiences-with-gsap/) — scroll narrative
- [Codrops WebGL Gallery](https://tympanus.net/codrops/2026/02/02/building-a-scroll-revealed-webgl-gallery-with-gsap-three-js-astro-and-barba-js/) — Feb 2026 patterns
- [Maxime Heckel — Refraction+Dispersion](https://blog.maximeheckel.com/posts/refraction-dispersion-and-other-shader-light-effects/) — GLSL IOR per channel
- [Maxime Heckel — Caustics](https://blog.maximeheckel.com/posts/caustics-in-webgl/) — WebGL caustics
- [Three.js Volumetric Caustics](https://threejs.org/examples/webgpu_volume_caustics.html) — WebGPU
- [N8AO CDN](https://unpkg.com/n8ao@latest/dist/N8AO.js) — confirmed available
