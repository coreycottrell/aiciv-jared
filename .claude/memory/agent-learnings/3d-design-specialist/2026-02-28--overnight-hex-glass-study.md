# Memory: Overnight Hex Glass Study + Gleb Philosophy + 7-Day Plan

**Date**: 2026-02-28
**Agent**: 3d-design-specialist
**Type**: synthesis + teaching
**Topic**: Glass hexagon, Gleb deep philosophy, WebGPU frontier, 7-day continuation plan
**Confidence**: high
**Tags**: gleb-kuznetsov, hex-glass, three-js, extrude-geometry, websearch-2026, webgpu, tsx, r3f, purebrain, study, night-study

---

## Context

Night session following Jared's directive: "continue having DESIGN agent study 3d modeling
and improving - remember GLEB LEVEL IS THE GOAL IN ONE WEEKS TIME!"

The 13-day sprint (Feb 21-26) mastered all CDN-deployable techniques. Tonight's session:
1. Deep Gleb philosophy study
2. Research latest Three.js Feb 2026 techniques (WebGPU r171, TSL, compute particles)
3. Built purebrain-hex-glass-demo.html — glass hexagonal prism with full technique stack
4. Documented remaining gaps (npm-only frontier) and 7-day continuation plan

---

## The Most Important Insight About Gleb

**He renders LIGHT, not OBJECTS.**

Every design decision answers: "What is the glass doing to the light?"
- The sphere is a light-bending instrument
- The particles are suspended photons
- The iridescence is the material announcing its physical thickness
- The caustics are evidence of invisible refraction

When composing: start with light. Then ask what glass you need to make it interesting.
Not: "I'll add glass and then light it."

---

## New Technique: Hexagonal Prism Glass

### ExtrudeGeometry hex (flat-top orientation)

```javascript
const shape = new THREE.Shape();
const sides = 6;
for (let i = 0; i <= sides; i++) {
  const angle = (i / sides) * Math.PI * 2 - Math.PI / 6;  // -PI/6 = flat-top
  const x = Math.cos(angle) * radius;
  const y = Math.sin(angle) * radius;
  if (i === 0) shape.moveTo(x, y);
  else shape.lineTo(x, y);
}

const geo = new THREE.ExtrudeGeometry(shape, {
  depth:          0.42,
  bevelEnabled:   true,
  bevelThickness: 0.07,
  bevelSize:      0.07,
  bevelSegments:  5,     // MINIMUM 5 for glass edges — fewer shows facets
});
geo.center();            // REQUIRED — ExtrudeGeometry extends from z=0 to z=depth by default
geo.computeVertexNormals();
```

### Gotchas

1. **`-Math.PI / 6` for flat-top**: Without this offset, one vertex points straight up (pointy-top).
   Flat-top reads better on screens, especially with text overlay.

2. **`bevelSegments: 5` minimum**: Sharp hex edges refract incorrectly through glass.
   Bevel smooths the transition — looks physically real.

3. **`geo.center()` is mandatory**: ExtrudeGeometry grows from z=0 to z=depth.
   Without centering, the hex appears to hang half off the origin.

4. **Flat hex faces + high roughness**: Flat polygonal faces show a distinct refracted background
   image (like a lens) at low roughness. Use `roughness: 0.04` for artistic glass blur.

---

## Dual-Core Emissive Technique (New)

Two emissive spheres inside the hex glass — one static (pulsing), one orbiting:

```javascript
// Primary: orange static core
const core = new THREE.Mesh(
  new THREE.SphereGeometry(0.28, 64, 64),
  new THREE.MeshStandardMaterial({
    color: 0xf1420b, emissive: 0xf1420b,
    emissiveIntensity: 2.8, roughness: 1.0
  })
);

// Secondary: blue orbiting core
core2.position.x = Math.cos(elapsed * 0.88) * 0.22;
core2.position.y = floatY + Math.sin(elapsed * 0.66) * 0.12;
```

Effect: reads as "neural energy" inside a glass vessel — intelligence in motion.
Brand perfect for PureBrain: orange energy core (AI intensity) + blue orbit (precision).
This is a production-ready hero element.

---

## Three.js Feb 2026 State (from WebSearch)

### WebGPU Production-Ready (r171, Sep 2025)
```javascript
import * as THREE from 'three/webgpu';  // automatic WebGL 2 fallback
```

### TSL Compute Shader Particles
```javascript
const updateParticles = Fn(() => {
  const pos = positionBuffer.element(instanceIndex);
  const vel = velocityBuffer.element(instanceIndex);
  pos.addAssign(vel.mul(deltaTime));
});
// Enables 100K-1M particles at 60fps
```

### CDN vs npm Gap Summary (as of Feb 2026)
- CDN (r161, WordPress-ready): ~90% of Gleb visual target
- npm + R3F (r171+): ~100% coverage
- Key missing techniques in CDN: temporalDistortion, anisotropicBlur, N8AO, WebGPU compute

---

## 7-Day Plan Summary

| Day | Focus | Deliverable |
|-----|-------|------------|
| Day 1 (Mar 1) | R3F + Vite + Drei MeshTransmissionMaterial (temporalDistortion, anisotropicBlur) | day1-r3f-transmission.html |
| Day 2 (Mar 2) | N8AO + cinematic product shot | day2-n8ao-product-shot.html |
| Day 3 (Mar 3) | WebGPU compute particles (TSL) | day3-webgpu-particles.html |
| Day 4 (Mar 4) | GSAP ScrollTrigger 3D storytelling | day4-scroll-story.html |
| Day 5 (Mar 5) | Gleb reference matching (side-by-side calibration) | day5-gleb-reference-match.html |
| Day 6 (Mar 6) | Production homepage 3D for purebrain.ai | day6-homepage-hero-production.html |
| Day 7 (Mar 7) | Definitive PureBrain signature piece + report | day7-definitive-purebrain.html |

All deliverables → `exports/3d-design-study/`

---

## Files Produced This Session

- Demo: `exports/3d-design-study/purebrain-hex-glass-demo.html`
- Study notes + 7-day plan: `exports/3d-design-study/STUDY-NOTES-AND-7-DAY-PLAN.md`
- This memory: `.claude/memory/agent-learnings/3d-design-specialist/2026-02-28--overnight-hex-glass-study.md`

---

## Canonical PureBrain3D Token Values

```javascript
const PB = {
  blue: 0x2a93c1, orange: 0xf1420b, blueLight: 0x5ad4ff,
  glass: {
    transmission: 1.0, roughness: 0.04, ior: 1.52,
    iridescence: 0.45, iridescenceIOR: 1.40,
    iridescenceThicknessRange: [100, 420],
    clearcoat: 0.90, clearcoatRoughness: 0.015,
    envMapIntensity: 4.2, depthWrite: false,
  },
  bloom: { strength: 0.55, radius: 0.45, threshold: 0.82 },
  ca: 0.0022, vig: 0.52,
};
// specularColor: '#C8A84A'  — gold, not white
// FLOAT_FREQS: [0.55, 0.38, 0.22] — prime ratios, 120s repeat cycle
```
