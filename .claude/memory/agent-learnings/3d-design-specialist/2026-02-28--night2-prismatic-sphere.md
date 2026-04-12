# Memory: Night 2 — Prismatic Glass Sphere Study

**Date**: 2026-02-28
**Agent**: 3d-design-specialist
**Type**: teaching + technique
**Topic**: Prismatic light dispersion, spectral ground caustics, beam pivot trick, rainbow UV mapping
**Confidence**: high
**Tags**: gleb-kuznetsov, prismatic, dispersion, spectral, caustics, three-js, glass, beam, halo-ring, iridescence, purebrain, study

---

## Context

Night 2 of Week 2 Gleb mastery sprint. Following the "one signature moment" principle:
chose prismatic light dispersion as the hero technique — glass sphere acts as a prism,
splitting white light into visible RYGCBV spectrum.

File: `exports/3d-design-study/night2-prismatic-sphere.html` (611 lines)

---

## The One Signature Moment Decision

Before code, the critical choice: **what single technique to make the hero?**

The answer was prismatic dispersion because:
1. Not previously the hero in any sprint demo (used as detail, never as subject)
2. Strongly physically grounded (prisms are real, dispersion is measurable)
3. Naturally scales across the composition: origin (sphere) → beams → ground caustics → reflections
4. Unique to glass — reinforces the core "glass as light instrument" Gleb philosophy

Everything in the scene exists to reveal this one idea.

---

## Technique: RYGCBV Prismatic Dispersion Beams

Six PlaneGeometry meshes fanned radially from sphere center, additive blending.

### Geometry setup (critical pivot trick)

```javascript
const geo = new THREE.PlaneGeometry(beamWid, beamLen, 1, 12);
geo.translate(0, beamLen * 0.5, 0);  // Move pivot to one end BEFORE rotating mesh
// Now when beam.rotation.z = angle, beam rotates around its BASE (sphere end)
// Without translate: beam rotates around its center (wrong!)
```

This is the core geometric insight. Same as CSS `transform-origin`.

### Fan angle parameters

```javascript
const spreadAngle = Math.PI * 0.72;  // 130° total — enough separation, not too wide
const startAngle  = Math.PI * 0.65;  // 117° — first beam points down-left (red)
const angle = startAngle + (i / (N - 1)) * spreadAngle;
beamGroup.rotation.x = 0.12;  // tilt toward viewer so fan reads in 3D
```

If spread > 150°: beams look disconnected from sphere
If spread < 80°: wavelengths look like a single glow, not distinct

### RYGCBV Color sequence

```javascript
const SPECTRAL = [
  new THREE.Color(1.00, 0.06, 0.06),   // Red
  new THREE.Color(1.00, 0.42, 0.03),   // Orange
  new THREE.Color(0.90, 1.00, 0.00),   // Yellow
  new THREE.Color(0.00, 0.88, 0.28),   // Green
  new THREE.Color(0.08, 0.38, 1.00),   // Blue
  new THREE.Color(0.52, 0.00, 1.00),   // Violet
];
```

6 wavelengths is the minimum for recognizable spectrum. 7 (adding indigo) adds realism
but reduces visual separation between adjacent beams at typical alpha levels.

### Per-wavelength breathing (organic non-mechanical pulsing)

```glsl
// Phase offset per wavelength: 60° spacing
uPhase = i * (Math.PI * 2 / 6);

// In fragment shader:
float pulse = 0.80 + 0.20 * sin(uTime * 1.05 + uPhase);
```

Same principle as prime float frequencies: never all at identical brightness simultaneously.
Beams breathe organically, individually.

### Shimmer along beam length

```glsl
float shimmer = 0.88 + 0.12 * sin(vUv.y * 12.0 + uTime * 2.2 + uPhase);
```

12 oscillations along the beam length = suggests wavefront motion / light frequency.

---

## Technique: Spectral Ground Caustics

Custom ShaderMaterial on ground plane — shows where beams land.

### Rainbow UV mapping (angle-based hue)

```glsl
// Map angle from sphere projection point to hue
float ang = atan(toSphere.y, toSphere.x);  // -PI to PI
float hu  = fract(ang / 6.2832 + 0.5);     // 0 to 1

vec3 rainbow = vec3(
  0.5 + 0.5 * cos(6.2832 * (hu + 0.0)),    // Red channel
  0.5 + 0.5 * cos(6.2832 * (hu + 0.333)),  // Green channel
  0.5 + 0.5 * cos(6.2832 * (hu + 0.667))   // Blue channel
);
```

This maps each direction from the sphere's ground projection to a spectral color.
The beams point down-left to down-right → rainbow wraps from red to violet across that arc.

### Per-channel Voronoi caustic

```glsl
float cr = voronoi(uv * 4.8 + vec2(t * .07, 0.));     // Red channel offset
float cg = voronoi(uv * 4.8 + vec2(0., t * .07) + .25); // Green offset
float cb = voronoi(uv * 4.8 - vec2(t * .065) + .5);     // Blue offset

float br = smoothstep(0.30, 0.04, cr);  // Cell edge brightness
// rainbow * (br + bg + bb) = spectral caustic pattern
```

The per-channel UV offsets create the chromatic aberration in the caustic — different
wavelengths focus at slightly different positions, physically accurate.

---

## Technique: Iridescent Halo Rings

Two `TorusGeometry` rings with `iridescence: 1.0` — maximal iridescence.

```javascript
new THREE.MeshPhysicalMaterial({
  iridescence: 1.0,
  iridescenceIOR: 1.52,
  iridescenceThicknessRange: [200, 600],
  roughness: 0.0,
  metalness: 0.95,
  emissive: 0x88aaff, emissiveIntensity: 0.6,
});
```

The thick iridescence range [200, 600] gives a wide sweep of the spectral colors as
the ring tumbles — connecting the ring's appearance to the dispersion theme.

```javascript
// Pre-computed axes — never allocate Vector3 in animation loop
const haloAxis1 = new THREE.Vector3(0.3, 1, 0.1).normalize();
const haloAxis2 = new THREE.Vector3(-0.2, 1, 0.4).normalize();
haloRing.rotateOnWorldAxis(haloAxis1, dt * 0.18);  // organic 3D tumble
```

---

## Bug Caught: Object.assign with Three.js Position

```javascript
// WRONG — Object.assign does not work for Three.js Vector3 position
Object.assign(new THREE.PointLight(...), { position: new THREE.Vector3(x, y, z) })

// CORRECT — use position.set()
const l = new THREE.PointLight(...);
l.position.set(x, y, z);
envScene.add(l);
```

Three.js `position` is an Object3D-managed Vector3. `Object.assign` would attempt to
replace the property reference, not set coordinates. The light would remain at origin (0,0,0).

---

## Composition Architecture (Night 2)

**Hierarchy of depth** (back to front):
1. Background (fBm gradient mesh, ortho scene rendered first)
2. Ground surface (dark mirror, metalness 0.92)
3. Ground glow ring (blue canvas, additive)
4. Ground caustics (spectral Voronoi, additive)
5. Atmospheric particles (2,200, additive, slow drift)
6. Dispersion beams (6 fan planes, additive, behind sphere)
7. Backside glass sphere (BackSide refraction)
8. FrontSide glass sphere (transmission, 192 seg)
9. Halo rings (torus, iridescent, tumbling)
10. Inner emissive core (blue, pulsing)
11. Micro-core (orange, orbiting)
12. Bloom pass (strength 0.58, threshold 0.78)
13. CA + Vignette + Grain pass

This ordering matches Gleb's hierarchy: dark → ambient → environment → object → inner light → effects.

---

## Performance Budget (Estimated)

| Element | GPU |
|---------|-----|
| Glass sphere (192 seg, transmission + backside) | ~11ms |
| 6 dispersion beams (thin planes, additive) | ~0.5ms |
| Ground caustic shader (Voronoi) | ~2ms |
| Ground surface (metallic) | ~0.5ms |
| Atmospheric particles (2,200) | ~1.5ms |
| 2 halo rings (torus) | ~0.8ms |
| Bloom | ~2.5ms |
| CA + Vignette | ~0.4ms |
| **Total** | **~19ms (~52fps)** |

---

## Updated 7-Day Plan

Night 1 (Feb 28): DONE — hex glass demo
Night 2 (Feb 28): DONE — prismatic sphere (this session)
Day 1 (Mar 1): R3F + Vite + Drei MeshTransmissionMaterial
Day 2 (Mar 2): N8AO + cinematic product shot
Day 3 (Mar 3): WebGPU compute particles
Day 4 (Mar 4): GSAP ScrollTrigger 3D storytelling
Day 5 (Mar 5): Gleb reference matching
Day 6 (Mar 6): Production homepage 3D
Day 7 (Mar 7): Definitive signature piece

---

## File References

- Demo: `exports/3d-design-study/night2-prismatic-sphere.html` (611 lines)
- Study notes: `exports/3d-design-study/STUDY-NOTES-AND-7-DAY-PLAN.md`
- Prior: `exports/3d-design-study/purebrain-hex-glass-demo.html` (804 lines)
