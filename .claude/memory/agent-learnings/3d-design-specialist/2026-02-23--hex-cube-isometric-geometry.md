# Hex-Cube Isometric Geometry: Samsung R3 Insight Implementation

**Date**: 2026-02-23
**Agent**: 3d-design-specialist
**Type**: technique
**Confidence**: high
**Tags**: three-js, geometry, roundedbox, glass, isometric, hex-cube, purebrain

---

## Context

Sprint 2 Day 1 — Closing the real-time 3D gap identified in the mastery gap analysis.
The gap: Gleb uses CUBE geometry at the isometric diagonal (not spheres), which reads as a hexagonal face.
PureBrain brand identity requires the hex form. Avatar v2 uses spheres. This implementation bridges that gap.

---

## The Core Discovery: Isometric Viewing Angle

A **cube viewed from its vertex diagonal** projects as a **perfect regular hexagon** in the viewer's plane.

The exact rotation angles:
```
rotX = -arctan(1/sqrt(2)) = -35.264 degrees
rotY = 45 degrees
```

In Three.js:
```javascript
const HEX_ROT_X = -35.264 * Math.PI / 180;  // -0.6155 radians
const HEX_ROT_Y =  45.0   * Math.PI / 180;  //  0.7854 radians

mesh.rotation.order = 'YXZ';  // Stable Euler order for this rotation
mesh.rotation.x = HEX_ROT_X;
mesh.rotation.y = HEX_ROT_Y;
```

**Why `rotation.order = 'YXZ'`**: Default is XYZ. For this specific rotation sequence (Y first, then X), YXZ order prevents gimbal lock artifacts when adding continuous Y rotation on top of the baked base pose.

---

## RoundedBoxGeometry Setup

```javascript
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

// CDN path: three/addons/geometries/RoundedBoxGeometry.js (confirmed working)
// https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/geometries/RoundedBoxGeometry.js

const geo = new RoundedBoxGeometry(
  1.3,    // width
  1.3,    // height
  1.3,    // depth
  8,      // segments per side (controls chamfer smoothness)
  0.08    // chamfer radius
);
```

**Chamfer calibration:**
- `0.02-0.05` = minimal chamfer, nearly sharp cube, harsh refraction edges
- `0.08-0.12` = ideal range — clear cube character, soft glass edges
- `0.20-0.35` = heavy chamfer, starts to look like a sphere, loses hex readability
- `0.50+`     = sphere-like, defeats the purpose

**Segments calibration:**
- `4` = fast but chamfer is slightly faceted
- `8` = good quality, chamfer reads as smooth circle
- `12+` = negligible improvement, increased vertex count

---

## Animation: Continuous Rotation on Top of Isometric Pose

The cube must stay recognizable as a hexagon while rotating. Key: bake the isometric rotation into the mesh, then add rotation ON TOP of it:

```javascript
// At initialization: bake isometric pose
hexCubeMesh.rotation.order = 'YXZ';
hexCubeMesh.rotation.x = HEX_ROT_X;
hexCubeMesh.rotation.y = HEX_ROT_Y;

// In animation loop: ADD to the existing Y rotation
// This spins the hex around its isometric axis, not its world axis
hexCubeMesh.rotation.y += cfg.idleRotSpeedY;
// Very subtle X oscillation for breathing feel
hexCubeMesh.rotation.x = HEX_ROT_X + Math.sin(t * 0.35) * 0.0003;
```

**Why this works**: The isometric Y rotation means the cube's "up" axis in world space is tilted 35.264 degrees. Adding rotation.y in this tilted space makes the cube rotate around the hex face normal — the hexagonal silhouette stays hexagonal throughout the rotation.

---

## Multi-Frequency Float Animation

Three sine waves for organic non-repeating motion (replaces single-wave from v2):

```javascript
// Per-mode configuration
float: {
  freq1: 0.55,  // Primary Y bob (Hz)
  amp1:  0.095, // Primary Y amplitude
  freq2: 0.38,  // Secondary Y bob (slightly different frequency)
  amp2:  0.030, // Smaller amplitude
  freq3: 0.22,  // X drift
  amp3:  0.018  // Very subtle X motion
}

// In animation loop (phases accumulate each frame):
smooth.floatPhase1 += dt * f.freq1;
smooth.floatPhase2 += dt * f.freq2;
smooth.floatPhase3 += dt * f.freq3;

const floatY = Math.sin(smooth.floatPhase1) * f.amp1
             + Math.sin(smooth.floatPhase2) * f.amp2;
const floatX = Math.sin(smooth.floatPhase3) * f.amp3;
```

The frequency ratio 0.55/0.38/0.22 ≈ 1.45/1.73 creates a beat pattern that doesn't repeat for ~40 seconds. This is the "breathing" quality in Gleb's work — it feels alive, not mechanical.

---

## Glass Material Notes (for Hex-Cube Geometry)

MeshPhysicalMaterial on a chamfered cube geometry behaves differently from a sphere:

1. **ThicknessMap**: Not needed. The `thickness` property alone (0.80) provides adequate volume simulation.

2. **Attenuation color**: More visually prominent on cube faces (flat planes) than sphere (curved). Use state-driven lerping to add character.

3. **Emissive on glass**: Very subtle emissive (intensity 0.25-0.5) on the glass mesh itself creates a faint inner glow. This is visible on flat faces of the cube in a way it isn't on spheres.

4. **Iridescence**: Thin-film effect `iridescence: 0.60, iridescenceIOR: 1.38` adds subtle color shifts on the glass faces — looks like premium optical glass rather than cheap plastic.

5. **EnvMapIntensity: 4.0**: Glass needs high env map intensity. Below 3.0, glass looks flat.

---

## Design Tokens Pattern (Sprint 2 Day 1 first pass)

```javascript
const TOKEN = {
  color: {
    blue:   new THREE.Color('#2a93c1'),
    orange: new THREE.Color('#f1420b'),
    dark:   new THREE.Color('#060606'),
    gold:   new THREE.Color('#C8A84A'),
    ...
  },
  glass: {
    rotX: -35.264 * Math.PI / 180,
    rotY:  45.0   * Math.PI / 180,
    sideLength: 1.3,
    chamfer:    0.08,
    smoothness: 8,
    transmission: 1.0,
    thickness:    0.80,
    roughness:    0.04,
    ior:          1.50,
    ...
  },
  postprocessing: {
    bloomStrength:   0.55,
    bloomRadius:     0.42,
    bloomThreshold:  0.85,
  },
};
```

When Day 6 arrives, move this to `tokens.js` and all components import from it. The architecture is already correct in this file — just extraction needed.

---

## Performance Profile

| Element | Cost | Notes |
|---------|------|-------|
| RoundedBoxGeometry 8-seg | Low | Much less vertices than 128-seg sphere |
| MeshPhysical transmission FBO | Medium-High | Same as sphere — this is the main cost |
| Multi-freq float (3 Math.sin) | Negligible | CPU math per frame |
| 3 orbital rings | Low | Simple TorusGeometry |
| 200 blue + 65 gold particles | Low-Medium | CPU-updated positions |
| OutputPass | Negligible | Required for correct SRGB in r0.161.0 |

Total: Same envelope as Avatar v2. 60fps on dedicated GPU.

---

## Gotchas

1. **Base rotation must be baked before animation starts**: If you try to lerp toward the isometric angle from identity, the object does a strange tumbling interpolation. Always set rotation.x/y directly at init.

2. **`rotation.order` matters**: Set to 'YXZ' before setting rotation values. Otherwise the Euler decomposition applies rotations in wrong order.

3. **Chamfer too small = sharp edges in glass**: Edges below 0.04 chamfer radius create sharp refractive artifacts on glass — a bright white line along every edge. The 0.08 value was empirically determined to be below this threshold.

4. **Inner core must be smaller than chamfer inscribed sphere**: The inner emissive sphere (radius 0.42) must fit inside the chamfered cube (1.3 side, 0.08 chamfer). Maximum inscribed sphere radius = (1.3/2 - 0.08) = 0.57. Stay well below this.

---

## Reference Files

- `/home/jared/projects/AI-CIV/aether/exports/hex-cube-day1.html` — Day 1 implementation
- `/home/jared/projects/AI-CIV/aether/exports/3d-mastery-day8-sprint2-report.md` — Sprint 2 Day 1 report
- `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-v2-fixed.html` — v2 sphere avatar (comparison baseline)
- CDN confirmed: `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/geometries/RoundedBoxGeometry.js`
