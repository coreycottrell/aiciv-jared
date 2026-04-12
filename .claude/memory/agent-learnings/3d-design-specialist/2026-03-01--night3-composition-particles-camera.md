# Memory: Night 3 — Composition Scene, Two-Layer Particles, Camera Shot System

**Date**: 2026-03-01
**Agent**: 3d-design-specialist
**Type**: teaching + technique
**Topic**: Multi-object glass composition, dual particle layers, cinematic camera shots, radial DoF, SMAA
**Confidence**: high
**Tags**: gleb-kuznetsov, composition, particles, camera-animation, depth-of-field, SMAA, three-js, glass, torus, sphere, hex, purebrain, study, night3

---

## Context

Night 3 of the Gleb Kuznetsov mastery sprint. Signature technique: **composition** — three glass
objects (sphere, hex prism, torus) in dialogue, unified by two-layer particle atmosphere and
cinematic automated camera system.

File: `exports/3d-design-study/night3-composition-scene.html` (1,072 lines)

---

## Core Architecture: Multi-Object Glass Composition

Three distinct glass objects, each with unique material identity:

| Object | Glass Color | Attenuation | Core | Position |
|--------|-------------|-------------|------|---------|
| Sphere | Blue-white `#e8f4ff` | PureBrain blue `#6bbfe8` | Blue emissive + orbiting orange micro | (-1.2, 0.4, 0) |
| Hex    | Warm white `#fff5ee` | Amber `#f0b888` | Orange + secondary blue | (1.35, -0.35, -0.5) |
| Torus  | Iridescent metallic | n/a | `#6688ff` emissive | (0.8, 1.2, -1.8) |

The torus being metallic (not transmission) creates material contrast — two transparent + one reflective.

---

## Technique: Two-Layer Particle System

### Layer 1: Ambient Dust (2,800 particles)

```javascript
// Wide ellipsoid distribution
const theta = Math.random() * Math.PI * 2;
const phi   = Math.acos(Math.random() * 2 - 1);
const r     = Math.cbrt(Math.random()) * 5.5;  // cubic root = uniform sphere volume
partPositions[idx    ] = r * Math.sin(phi) * Math.cos(theta) * 1.5;
partPositions[idx + 1] = r * Math.sin(phi) * Math.sin(theta) * 0.9 + 0.2;
partPositions[idx + 2] = r * Math.cos(phi) * 1.2 - 1.0;

// Very slow drift: ±0.0004/frame, slight upward bias
partVelocities[idx + 1] = (Math.random()-0.5)*0.0003 + 0.00015;

// Boundary wrap
if (pos[idx + 1] >  3.5) pos[idx + 1] = -2.0;  // Y wrap (teleport)
if (Math.abs(pos[idx]) > 7.0) pos[idx] *= -0.95; // XZ bounce (reverse)
```

Color in fragment shader: cool blue-white `(0.65, 0.78, 0.95)` — suggests cold atmospheric light.

### Layer 2: Energy Particles (600 particles, near objects)

The key insight: **orbital velocity without explicit angle tracking**

```javascript
const dx = partPositions[globalIdx]     - obj.x;
const dz = partPositions[globalIdx + 2] - obj.z;
const distXZ = Math.sqrt(dx*dx + dz*dz) + 0.01;
// Tangential velocity = perpendicular to radial direction
partVelocities[globalIdx    ] = -dz / distXZ * 0.0018 + (Math.random()-0.5)*0.0008;
partVelocities[globalIdx + 2] =  dx / distXZ * 0.0018 + (Math.random()-0.5)*0.0008;
```

(-dz, dx) is the 2D perpendicular to (dx, dz) — gives CCW orbital motion.
Small random additions break perfect orbit into organic drift.

Color: PureBrain blue-white `(0.42, 0.78, 1.00)` — active, luminous.

### Particle Size Attenuation

```glsl
// Critical: clamp prevents close particles from filling screen
vec4 mvPos = modelViewMatrix * vec4(position, 1.0);
float dist = -mvPos.z;
float sz = aSize * uPixelRatio * (1.8 + aType * 1.2);
sz *= (18.0 / dist);
gl_PointSize = clamp(sz, 0.5, 6.0);  // min 0.5, max 6.0 — keeps as dots
```

### Dual Twinkle System

```glsl
// Dust: slow twinkle
float twinkle = 0.55 + 0.45 * sin(uTime * 1.2 + aPhase);

// Energy: fast twinkle overlaid
float energyBoost = aType * (0.5 + 0.5 * sin(uTime * 3.8 + aPhase * 2.2));

vAlpha = twinkle * (0.28 + aType * 0.45) + energyBoost * 0.3;
```

`aType` (0 or 1) gates the energy boost to energy particles only.

---

## Technique: Cinematic Camera Shot System

7 named shots that cycle automatically. Shot definition:

```javascript
const shot = {
  pos:      new THREE.Vector3(x, y, z),  // camera world position
  target:   new THREE.Vector3(x, y, z),  // look-at point
  fov:      38,           // FOV in degrees
  dof:      0.85,         // depth-of-field blur strength (0-1)
  duration: 7.0,          // seconds before next shot
  name:     'close-sphere'
};
```

Shot transition: just update `shotTimer`, the camera lerps itself.

### Frame-Rate Independent Camera Lerp

```javascript
// CORRECT: Math.pow gives same result at any frame rate
const camLerp = 1 - Math.pow(0.012, dt);
camState.pos.lerp(camTarget.pos, camLerp);

// At 60fps (dt≈0.0167): camLerp ≈ 0.075
// At 30fps (dt≈0.033):  camLerp ≈ 0.145
// Both reach target in same wall-clock time
```

### Keyboard Shot Navigation

```javascript
window.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight' || e.key === ' ') {
    shotTimer = 9999;  // force next shot
  }
  if (e.key === 'ArrowLeft') {
    currentShot = (currentShot - 2 + shots.length) % shots.length;
    shotTimer = 9999;
  }
});
```

ArrowLeft goes back 2 (because next frame will immediately increment to -1 mod N = N-1).

---

## Technique: Radial Depth-of-Field (CDN-compatible)

True DoF requires depth buffer. CDN approximation: radial blur that grows at frame edges.

```glsl
float d = length(uv - center);  // distance from image center
float edgeFactor = smoothstep(0.25, 0.7, d);  // 0 at center, 1 at outer edge

// Gaussian radial blur
vec2 dir = (uv - center) * uDof * edgeFactor * 0.012;
vec4 col = vec4(0.0); float w = 0.0;
for (int i = -3; i <= 3; i++) {
  float s  = float(i) / 3.0;
  float wt = exp(-s*s*2.0);  // Gaussian weights
  col += texture2D(tex, uv - dir * float(i)) * wt;
  w   += wt;
}
col /= w;
```

Works well for establishing/landscape shots. Less convincing for single-object macro shots
where you want sharp subject + blurred BG (that needs real depth buffer).
Each shot's `dof` value (0-1) drives `uDof` uniform — close shots get higher dof.

---

## Technique: SMAA vs FXAA for Glass Materials

SMAA handles glass better than FXAA:
- FXAA = edge detection based on brightness differences → misses thin glass edges
- SMAA = contrast-adaptive, geometrically aware → correctly handles glass specularity

```javascript
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
const smaaPass = new SMAAPass(
  innerWidth * renderer.getPixelRatio(),
  innerHeight * renderer.getPixelRatio()
);
composer.addPass(smaaPass); // Add BEFORE bloom — SMAA on raw render, not bloomed
```

Note: SMAA resolution must match device pixel ratio, not just canvas CSS size.

---

## Critical Gotcha: Background Scene + EffectComposer

When rendering separate ortho background + main scene through composer:

```javascript
// REQUIRED order:
renderer.autoClear = false;  // prevent Three.js auto-clearing between renders
renderer.clear();              // manually clear color + depth
renderer.render(bgScene, bgCamera);  // background (ortho, no depth test)
renderer.clearDepth();         // CLEAR DEPTH before main scene — critical!
composer.render();             // main scene (uses depth correctly)
```

Without `renderer.clearDepth()`:
- Background quad at z=1.0 writes to depth buffer
- All main scene fragments fail depth test
- Scene appears empty (everything occluded by invisible background)

---

## Satellite Sphere Elliptical Orbits

```javascript
const angle  = t * sat.speed + sat.phase;
const radius = 2.6 + Math.sin(t * 0.22 + i * 1.2) * 0.3;  // breathing radius
const height = Math.sin(angle * 0.55 + i * 2.0) * 0.8 + 0.3;  // wavy altitude

sat.group.position.set(
  Math.cos(angle) * radius,
  height,
  Math.sin(angle * 0.88) * radius * 0.6 - 0.5  // elliptical: Z compressed 0.6×
);
```

The `0.88` on the Z sin and `0.6` depth scale creates an elliptical orbit — reads as more
cinematically interesting than perfect circle. The 0.3 radius breathing prevents mechanical feel.

---

## Three Object Float Frequencies (Non-Periodic System)

Each object floats at different prime-ratio frequencies so the pattern never repeats:

```javascript
const FF = [0.55, 0.38, 0.22];  // Hz — prime ratios, 120s+ before pattern repeats

// Sphere: FF[0] + FF[1]
sphereGroup.position.y = 0.4 + sin(t * FF[0]) * 0.11 + sin(t * FF[1]) * 0.075;

// Hex: FF[1] + FF[2] with phase offsets
hexGroup.position.y = -0.35 + sin(t * FF[1] + 1.2) * 0.11 + sin(t * FF[2] + 0.8) * 0.075;

// Torus: FF[2] only
torusGroup.position.y = 1.2 + sin(t * FF[2] + 2.1) * 0.11;
```

Satellite speeds are scaled from FF: `sat.speed = FF[i] * 0.38`

---

## Ground Glow System (Two-Color)

Blue glow pool under sphere, orange under hex — objects affect their environment:

```javascript
function makeCanvasGlow(innerColor, outerColor, res = 256) {
  const cv = document.createElement('canvas');
  cv.width = cv.height = res;
  const gc = cv.getContext('2d');
  const grd = gc.createRadialGradient(res/2,res/2,0, res/2,res/2,res*0.48);
  grd.addColorStop(0, innerColor);  // 'rgba(42,147,193,0.18)'
  grd.addColorStop(1, outerColor);  // 'rgba(42,147,193,0.0)'
  gc.fillStyle = grd;
  gc.fillRect(0, 0, res, res);
  return new THREE.CanvasTexture(cv);
}

// Position under each object, slightly above ground
hexGlow.position.set(1.35, -1.83, -0.5);  // matches hex object position
hexGlow.rotation.x = -Math.PI * 0.5;      // flat on ground
```

AdditiveBlending means glow adds to dark ground without covering it.
The canvas gradient texture approach creates a smooth radial falloff without any GLSL.

---

## Composition Design Principles Tested in Night 3

1. **Material contrast**: 2 transmission + 1 iridescent metallic creates visual hierarchy without uniformity

2. **Position asymmetry**: Objects at (-1.2, 0.4, 0), (1.35, -0.35, -0.5), (0.8, 1.2, -1.8) —
   staggered in all 3 axes. Never aligned. Gleb's compositions breathe in 3D.

3. **Ground color as narrative**: Blue glow = sphere territory. Orange glow = hex territory.
   The viewer's eye reads the ground before looking up — it sets expectations.

4. **DoF shot variance**: Each camera shot has different dof. Close shots = more blur = more intimate.
   Wide establishing = 0 dof. This teaches the viewer to read depth-of-field as camera language.

5. **Satellite hierarchy**: Small spheres orbit the composition center, not individual objects.
   They unify the composition without competing with the primary objects.

---

## Performance Budget

| Element | GPU (estimated) |
|---------|----------------|
| Primary sphere (128seg, transmission×2) | ~11ms |
| Hex prism (ExtrudeGeo bevel6, transmission×2) | ~6ms |
| Torus rings (iridescent×2) | ~2ms |
| 3 satellite spheres (64seg, transmission×2 each) | ~4ms |
| 3,400 particles total (ShaderMaterial) | ~2ms |
| 4 god rays (additive cones) | ~0.3ms |
| Ground + glow planes | ~0.5ms |
| SMAA | ~1ms |
| Bloom (strength 0.52, threshold 0.82) | ~2.5ms |
| CA + radial DoF + grain | ~0.8ms |
| **Total** | **~30ms (~33fps integrated, ~50fps dedicated GPU)** |

Night 3 is most expensive so far. Multiple transmission objects are the cost.
Optimization path: reduce satellite segments to 48, add LOD on background objects.

---

## File References

- Demo: `exports/3d-design-study/night3-composition-scene.html` (1,072 lines)
- Study notes: `exports/3d-design-study/STUDY-NOTES-AND-7-DAY-PLAN.md`
- Night 2: `exports/3d-design-study/night2-prismatic-sphere.html`
- Night 1: `exports/3d-design-study/purebrain-hex-glass-demo.html`
