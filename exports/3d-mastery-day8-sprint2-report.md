# 3D Mastery Sprint 2 — Day 1 Report: Hex-Cube Geometry Implementation

**Date**: 2026-02-23
**Sprint**: Sprint 2 (Closing the Remaining 15% Technical Gap)
**Day**: 1 of 7
**Agent**: 3d-design-specialist

---

## Summary

Day 1 of Sprint 2 implements the most critical missing capability identified in the gap analysis: **hex-cube geometry with glass transmission material at the isometric viewing angle**.

The output is a complete, production-quality avatar scene built on vanilla Three.js r0.161.0 ESM with all battle-tested patterns from the 7-day sprint carried forward — plus the new hex-cube geometry and two new capabilities:

1. **RoundedBoxGeometry at isometric rotation** — the Samsung R3 insight
2. **Multi-frequency float animation** — three sine waves for organic non-repeating motion
3. **PureBrain design tokens** — first pass at formalizing brand values as code constants

---

## The Core Technical Achievement: Hex-Cube at Isometric Angle

### The Samsung R3 Insight

The gap analysis revealed that Gleb uses **cube geometry rotated to the isometric diagonal** rather than hexagonal prism geometry. This produces a more premium result because:

- A cube viewed from its vertex diagonal reads as a **perfect regular hexagon**
- The rotation also positions one face away from the viewer, allowing the transmission material to show **refracted internal depth**
- `RoundedBoxGeometry` with chamfered edges gives the glass soft refractive edges rather than the hard-edge artifacts that appear on sharp cube corners

### The Magic Numbers

```
rotX = -arctan(1/sqrt(2)) = -35.264 degrees
rotY = 45 degrees
```

At exactly this rotation, each vertex of the cube projects to the center of the hexagonal face in the viewer's plane. The hexagonal silhouette is **geometrically exact**, not approximated.

### Implementation

```javascript
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const hexCubeGeo = new RoundedBoxGeometry(
  1.3,    // width (side length)
  1.3,    // height
  1.3,    // depth
  8,      // smoothness (segments per side — controls chamfer quality)
  0.08    // chamfer radius (subtle edge softening)
);

const hexCubeMesh = new THREE.Mesh(hexCubeGeo, glassMat);
hexCubeMesh.rotation.order = 'YXZ';
hexCubeMesh.rotation.x = -35.264 * Math.PI / 180;  // isometric X
hexCubeMesh.rotation.y =  45.0   * Math.PI / 180;  // isometric Y
```

**Why `rotation.order = 'YXZ'`**: Default Euler order is XYZ. For the isometric rotation, YXZ gives more stable interpolation when the animation adds continuous Y rotation on top of the base pose.

### Glass Material on the Hex-Cube

The MeshPhysicalMaterial parameters are tuned for the chamfered cube geometry:

- `transmission: 1.0` — fully transparent glass
- `thickness: 0.80` — drives light attenuation through the glass volume
- `ior: 1.50` — standard glass refractive index
- `roughness: 0.04` — nearly mirror smooth (shows sharp refraction of internal core)
- `iridescence: 0.60` — thin-film shimmer approximation (from hex avatar memory)
- `side: THREE.DoubleSide` — **critical**: renders back faces, shows internal structure through glass
- `attenuationColor: PB_BLUE` — state-driven, lerps toward current mode color
- `specularColor: GOLD (#C8A84A)` — Gleb's gold specular signature

---

## New Capabilities Added

### 1. Multi-Frequency Float Animation

**Previous implementation**: Single sine wave float — creates a regular, machine-like bob.

**New implementation**: Three sine waves at prime-ish frequency ratios, with offset phases:

```javascript
const f = cfg.float;  // { freq1, amp1, freq2, amp2, freq3, amp3 }
const floatY = Math.sin(floatPhase1) * f.amp1 * cfg.floatAmp
             + Math.sin(floatPhase2) * f.amp2 * cfg.floatAmp;
const floatX = Math.sin(floatPhase3) * f.amp3 * cfg.floatAmp;
```

Each mode has different frequencies and amplitudes, so the float character changes with mode:
- **Idle**: slow, meditative (0.55 Hz primary)
- **Speaking**: faster, more energetic (0.70 Hz primary)
- **Thinking**: very slow, ponderous (0.35 Hz primary)
- **Listening**: moderate, attentive (0.50 Hz primary)

### 2. PureBrain Design Tokens (First Pass)

All design values are now centralized in a `TOKEN` object rather than scattered as magic numbers:

```javascript
const TOKEN = {
  color: { blue, orange, dark, gold, purple, cyan, white },
  glass: { rotX, rotY, sideLength, chamfer, smoothness, transmission, thickness, ... },
  postprocessing: { bloomStrength, bloomRadius, bloomThreshold },
};
```

This is the foundation for Day 6 (Design Token System formalization). When Day 6 arrives, these values move to a separate `tokens.js` file and all components consume them. The architecture is already correct — just needs extraction.

### 3. State-Dependent Hex Emissive

The glass cube itself has a very faint state-dependent emissive color. This is subtle (emissiveIntensity 0.25-0.50) but adds the impression that the cube is internally lit from within — the glass reads as a living container rather than an empty shell.

---

## Carried Forward from Avatar v2

All proven patterns from the 7-day sprint are preserved:

| Feature | Source | Status |
|---------|--------|--------|
| 4 behavioral states (idle/speaking/thinking/listening) | Avatar v2 | Carried forward |
| Synthetic audio engine (5-band) | Avatar v2 | Carried forward |
| 6-light studio rig | Avatar v2 | Carried forward |
| Procedural environment map (PMREMGenerator) | Avatar v2 | Carried forward |
| Bloom + ChromaticAberration + Vignette | Avatar v2 | Carried forward |
| Cursor gaze tracking (gazeGroup separation) | Avatar v2 | Carried forward |
| Orange spark particles (speaking) | Avatar v2 | Carried forward |
| Ambient blue + gold particles | Avatar v2 | Carried forward |
| PostMessage API (WordPress iframe) | Avatar v2 | Carried forward |
| Auto demo cycle | Avatar v2 | Carried forward |
| Loading screen with PureBrain logo | Avatar v2 | Carried forward |
| OutputPass (last in chain, r0.161.0) | Day 8 memory | Added |

---

## Performance Notes

- File size: 56KB (single self-contained HTML)
- Geometry: RoundedBoxGeometry with 8 segments per side = manageable vertex count for glass rendering
- The FBO (Frame Buffer Object) for transmission rendering is the main GPU cost — unchanged from v2
- Multi-frequency float: 3 Math.sin() calls per frame — negligible CPU cost
- Design tokens: zero runtime overhead (constants, not computed)
- OutputPass added: required in r0.161.0 for correct SRGB output, negligible cost

Expected 60fps on any dedicated GPU. Same performance envelope as Avatar v2.

---

## Visual Comparison: Sphere vs Hex-Cube

| Dimension | Sphere (v2) | Hex-Cube (Day 1) |
|-----------|-------------|------------------|
| Brand connection | Generic premium | Direct PureBrain logo geometry |
| Glass refraction | Smooth radial | Faceted planes creating angular refractive patterns |
| Edge character | Soft, continuous | Soft but geometric — the chamfer reads as precision |
| Floating feel | Natural, organic | Architectural yet alive |
| State visibility | Subtle color shifts | Color shifts + subtle emissive tint on glass faces |

The hex-cube is not better than the sphere — it is **different and more brand-connected**. The sphere says "premium AI." The hex-cube says "premium AI built by PureBrain specifically."

Both should exist in the design system as alternating forms.

---

## What Day 2 Builds: Orbital Ring System

Day 2 adds the 3-ring orbital system that Gleb uses in the Cirus sphere and 2024 voice reaction sphere:

```javascript
// Three rings at different inclinations, speeds, and state responses
const RING_CONFIGS = [
  { radius: 1.8, speed: 0.003,  inclination: 'equatorial',  color: PB_BLUE   },
  { radius: 2.1, speed: -0.001, inclination: 'tilted_30deg', color: WHITE     },
  { radius: 1.5, speed: 0.0005, inclination: 'nearly_polar', color: PB_ORANGE },
];
```

State behavior:
- **Idle**: slow, barely moving, low opacity — the rings are present but background
- **Listening**: rings speed up and brighten — the avatar is actively receiving
- **Thinking**: rings slow dramatically, opacity drops — turning inward
- **Speaking**: full speed, pulsing opacity — radiating outward

**Note**: The hex-cube already has 3 rings from the Avatar v2 ring system. Day 2 will specifically implement the Gleb-style flat torus rings with distinct PureBrain color coding (blue/white/orange) at calibrated distances for the full orbital-system aesthetic.

---

## What Day 3 Builds: Vertex Displacement Noise

Day 3 implements the surface deformation that Gleb's work has — where the sphere/cube surface displaces organically with simplex noise:

```glsl
// In vertex shader:
vec3 noiseCoord = pos * 1.2 + vec3(uTime * 0.3);
float noiseVal = fbm5(noiseCoord);
vec3 displaced = pos + normal * noiseVal * uAmplitude;

// Finite-difference normal recomputation (from Day 8 memory):
float nx = fbm5((pos + vec3(eps,0,0)) * 1.2 + timeOffset);
float ny = fbm5((pos + vec3(0,eps,0)) * 1.2 + timeOffset);
float nz = fbm5((pos + vec3(0,0,eps)) * 1.2 + timeOffset);
vec3 displacedNormal = normalize(normal - vec3(nx,ny,nz) * uAmplitude);
```

The MeshPhysicalMaterial FBO render will still run on the displaced geometry — the challenge is ensuring the transmission render picks up the displaced normals correctly.

---

## Memory Written

**Path**: `.claude/memory/agent-learnings/3d-design-specialist/2026-02-23--hex-cube-isometric-geometry.md`
**Type**: technique
**Topic**: RoundedBox at isometric angle — Samsung R3 hex-face insight + glass material tuning

---

## File

**Primary deliverable**: `/home/jared/projects/AI-CIV/aether/exports/hex-cube-day1.html`

- 1548 lines, 56KB
- Self-contained, loads from CDN (Three.js r0.161.0)
- Works in any modern browser via file:// or HTTP
- All 4 behavioral states with buttons and keyboard shortcuts [1]-[4]
- Auto demo cycles through all modes every 5 seconds until manual interaction
- Cursor gaze tracking (hover to activate)
- PostMessage API ready for WordPress iframe embed
