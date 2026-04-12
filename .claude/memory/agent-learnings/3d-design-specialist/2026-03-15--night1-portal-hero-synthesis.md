# Memory: Night 1 — Portal Hero Synthesis + New Principle

**Date**: 2026-03-15
**Agent**: 3d-design-specialist
**Type**: synthesis + technique + teaching
**Topic**: Full synthesis of all mastered CDN techniques into PureBrain portal hero. New principle: "Bloom confirms, it does not create." CDN mastery ~91%.
**Confidence**: high
**Tags**: gleb-kuznetsov, synthesis, scroll-narrative, glass, iridescence, particles, camera-keyframes, bloom-restraint, purebrain, night1

---

## Context

Night 1 of new Gleb Kuznetsov mastery training phase (March 15, 2026).
Prior state entering session: ~87% CDN (Day 4, March 11).
Goal: push to Gleb-level in one week.

Scene produced: `exports/overnight-blog/3d-training-output-2026-03-15.html`

---

## New Principle: "Bloom Confirms, It Does Not Create"

Studying Gleb's most premium work again — identified a pattern I underweighted before:

**His bloom threshold is 0.88-0.92. Very conservative.**

The transmission material is what creates the premium look. Bloom only confirms luminance that already exists. If you increase bloom to make a scene look more premium — it will look worse.

```javascript
const bloomPass = new UnrealBloomPass(res, 0.52, 0.28, 0.82);
// strength 0.52: conservative resting state
// threshold 0.82: only the brightest pixels glow
// Adding strength to compensate for weak materials = wrong direction
```

Rule: If you want more premium, improve the material. Never improve the bloom.

---

## Architecture Pattern: Background in Separate Ortho Scene

```javascript
renderer.autoClear = false;
renderer.clear();
renderer.render(bgScene, bgCamera);  // ortho, no postprocessing
composer.render();                    // main scene, with bloom
```

This is cleaner than `renderOrder = -1` or `scene.background`. The fBm gradient background
does NOT get bloomed (correct — background is atmospheric, not luminant). No z-fighting
with ground plane.

**The bgCamera is OrthographicCamera(-1, 1, 1, -1, 0, 1). Background is a PlaneGeometry(2, 2).**

---

## PMREM Custom Probe (Superior to HDRI Import for Control)

```javascript
const probeScene = new THREE.Scene();
// warm key, PureBrain blue fill, orange rim, cool ground bounce
const lights = [
  { color: 0xfff4e8, intensity: 3.0, pos: [8, 12, 8]  },
  { color: 0x2a93c1, intensity: 1.6, pos: [-10, 4, -6] },
  { color: 0xf1420b, intensity: 1.0, pos: [6, -4, -10] },
  { color: 0x4ab8ff, intensity: 0.6, pos: [0, -8, 4]  },
];
const envRT = pmrem.fromScene(probeScene);
scene.environment = envRT.texture;
```

The orange rim at `[6, -4, -10]` (behind and below) is what puts orange brand color INSIDE the glass
without tinting the glass itself. Gleb trick: brand color enters through rim reflection.

---

## 5-Key Camera Scroll System (smoothstep, not linear)

```javascript
const camKeys = [
  { pos: [0, 0, 6.5],       lx: 0, ly: 0,   bloom: 0.45, ca: 1.0 },  // s0 calm
  { pos: [-1.4, 0.3, 5.8],  lx: 0, ly: 0,   bloom: 0.55, ca: 1.4 },  // s1
  { pos: [1.6, -0.4, 5.5],  lx: 0.5, ly: 0, bloom: 0.68, ca: 1.8 },  // s2
  { pos: [-0.4, 0.7, 4.6],  lx: 0, ly: 0.2, bloom: 0.90, ca: 2.4 },  // s3 PEAK
  { pos: [0, 0, 6.2],       lx: 0, ly: 0,   bloom: 0.50, ca: 1.0 },  // s4 resolve
];
```

Pattern: s3 is ALWAYS the peak (most intimate camera position, highest bloom, highest CA).
The camera's closest approach = the emotional "reveal" of the content.
Then s4 pulls back to a resolved, settled state.

---

## Scroll Velocity Reactivity

```javascript
scrollV = 0.06;          // on scroll event
scrollV *= 0.88;         // per-frame decay
bloomPass.strength = cs.bloom + scrollV * 2.5;
caVigPass.uniforms.uCA.value = cs.ca + scrollV * 3.0;
```

Numbers locked in: 0.06 inject, 0.88 decay, 2.5 bloom multiplier, 3.0 CA multiplier.
These create clear kinetic vs contemplative distinction without being jarring.

---

## Next Session Targets

1. GSAP ScrollTrigger CDN (`scrub: 1.2`) — physical camera mass
2. Liquid glass CDN approximation (normal map distortion plane)
3. Multi-object product composition (2-3 glass forms at different scales)
4. Test MeshTransmissionMaterial via CDN importmap (three.js r160 may expose it)

---

## CDN Mastery Level After Night 1

~91% CDN (up from ~87%)
Remaining gap is mostly: temporalDistortion, N8AO, GSAP scrub precision, composition depth.

---

## Files

- Scene: `exports/overnight-blog/3d-training-output-2026-03-15.html`
- Log: `exports/overnight-blog/3d-training-log-2026-03-15.md`
