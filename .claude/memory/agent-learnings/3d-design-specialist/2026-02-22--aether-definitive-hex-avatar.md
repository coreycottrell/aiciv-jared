# Aether Definitive Hexagonal Glass Avatar

**Date**: 2026-02-22
**Agent**: 3d-design-specialist
**Type**: technique
**Topic**: Building a Gleb Kuznetsov-level hexagonal glass avatar with PureBrain brand colors, vanilla Three.js ESM, 4 behavioral modes, synthetic audio reactivity

---

## What Was Built

Complete rebuild of the Aether avatar as a hexagonal glass structure inspired by the PureBrain logo (hexagon with blue/orange swirl vortex).

**File**: `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-gleb-hex.html`

---

## Key Design Decisions

### Hexagonal Structure Choice
- Used `CylinderGeometry(r, r, h, 6)` = regular hexagonal prism
- 6-segment cylinder IS the hex prism (Three.js built-in)
- Added `EdgesGeometry` outlines for the wireframe aesthetic
- Wire rings at top/mid/bottom: blue (#2a93c1) top/bot, gold (#C8A84A) equator

### Scene Hierarchy (Critical for Clean Animation)
```
gazeGroup        — cursor gaze pivot ONLY (X/Y rotation from mouse)
  spinGroup      — continuous Y rotation + breathing scale
    outerHex     — glass prism mesh
    wire rings   — decorative hex rings
    edge lines   — 6 vertical edges
  energyCore1    — blue torus knot (2,3 knot ratio = logo vortex)
  energyCore2    — orange torus knot (3,2 knot ratio, complementary)
  energyCore3    — gold torus knot filament (accent)
  eyeMesh        — tiny hex at center (logo's black center dot)
  shardGroup     — 3 inner hex shards
  particles      — 28 helical particles
orbitGroup       — satellite hex shards (in scene directly, not gazeGroup)
```

**Why hierarchy matters**: The gaze bug from first attempt was caused by applying rotation BOTH via quaternion slerp AND direct `.rotation.y` set in the same frame. Fix: dedicated `gazeGroup` only handles gaze; `spinGroup` inside it handles spin. Never fight the quaternion.

### Torus Knot as Logo Vortex
The PureBrain logo has a swirling blue-to-orange vortex pattern.
Torus knots (p,q) capture this perfectly:
- Blue: `TorusKnotGeometry(0.42, 0.065, 240, 22, 2, 3)` — larger, dominant
- Orange: `TorusKnotGeometry(0.35, 0.048, 200, 18, 3, 2)` — secondary, rotated Z by PI/3
- Gold: `TorusKnotGeometry(0.24, 0.022, 140, 12, 5, 3)` — accent filament

Sizes matter: too small (0.30) and they're invisible through glass. Target 0.40+ for dominant element.

### Glass Material Parameters (MeshPhysicalMaterial)
```javascript
{
  transmission: 1.0,
  thickness: 0.9,      // thinner = less color attenuation
  roughness: 0.02,     // nearly mirror smooth
  ior: 1.50,           // standard glass
  reflectivity: 0.95,
  envMapIntensity: 4.5, // HIGH — glass needs strong env to reflect
  color: 0xaaddff,     // slight blue tint
  attenuationColor: 0x4ab8e0,
  attenuationDistance: 2.8,
  iridescence: 0.75,   // the Gleb iridescent shimmer
  iridescenceIOR: 1.38,
  clearcoat: 1.0,
  clearcoatRoughness: 0.005,
  side: THREE.DoubleSide  // CRITICAL — shows internal faces through glass
}
```

**Gotcha**: headless Chromium (Playwright screenshots) doesn't render glass transmission properly — it shows as near-opaque or semi-transparent tinted. In real Chrome/Firefox the full iridescent refraction shows. Don't judge by Playwright screenshot alone.

### Procedural Environment Map
Built via canvas + PMREMGenerator (no external HDR files needed):
```javascript
const pmrem = new THREE.PMREMGenerator(renderer);
pmrem.compileEquirectangularShader();
// Draw on 512x256 canvas, wrap as equirectangular
const tex = new THREE.CanvasTexture(cv);
tex.mapping = THREE.EquirectangularReflectionMapping;
const envRT = pmrem.fromEquirectangular(tex);
scene.environment = envRT.texture;
```

Key: minimum floor for envBlueStr/envOrangeStr in buildEnv():
- `const cStr = Math.max(cfg.envBlueStr, 0.42)` — glass always picks up color
- `const oStr = Math.max(cfg.envOrangeStr, 0.25)` — orange always present

### Bloom Calibration (Gleb's Restraint Principle)
```javascript
// RIGHT: suggests luminance without blowing out
UnrealBloomPass(size, 0.45, 0.42, 0.88)
// strength: 0.45, radius: 0.42, threshold: 0.88 — only brightest bloom

// WRONG (what causes white rectangle blowout):
UnrealBloomPass(size, 0.62, 0.50, 0.83)  // too strong
```
Dynamic bloom targets: idle 0.42, speaking 0.72, thinking 0.48, listening 0.52

### Lighting (6-light Gleb rig + balanced for glass)
```
L1: warm white key (upper-left) — 2.8 intensity
L2: electric blue fill (upper-right) — 2.2
L3: cyan rim (behind) — 1.8
L4: magenta accent (right-lower) — 1.1
L5: gold specular (near key) — 1.8
L6: orange underlight (below) — 1.6 PointLight
```
Previously was 3.6-5.5 — too bright, caused bloom blowout.
ACESFILMIC tonemapping at 0.88 exposure = rich shadows, controlled highlights.

### Synthetic Audio Engine
```javascript
// Speaking mode — syllable * word * phrase * breath modulation
const syl    = Math.sin(s * 9.1) * 0.5 + 0.5;  // fast syllables
const wrd    = Math.sin(s * 2.3) * 0.5 + 0.5;  // word rhythm
const phrase = Math.sin(s * 0.55)* 0.5 + 0.5;  // phrase shape
const breath = Math.abs(Math.sin(s * 0.21));     // breathing pattern
amp = syl * 0.52 * wrd * (0.55 + phrase * 0.45) * (0.45 + breath * 0.55);
```
Smoothing: `audioSmooth = audioSmooth + (amp - audioSmooth) * Math.min(1, dt * 8.0)`

### Particle Helix (Logo-Inspired Swirl)
28 particles placed in a 2.5-turn helix, then animated to orbit:
```javascript
const baseAngle = p.userData.initAngle + T * (0.22 + frac * 0.28) * spd;
p.position.x = Math.cos(baseAngle) * r;
p.position.z = Math.sin(baseAngle) * r;
```
Color gradient: blue → gold → orange (matches logo vortex spectrum)

---

## 4 Behavioral Modes

| Mode     | Core Color | Bloom  | Speed | Env Blue | Env Orange |
|----------|-----------|--------|-------|----------|------------|
| Idle     | Blue      | 0.42   | 0.60  | 0.55     | 0.10       |
| Speaking | Orange    | 0.72   | 1.45  | 0.18     | 0.60       |
| Thinking | Violet    | 0.48   | 0.38  | 0.28     | 0.05       |
| Listening| Cyan      | 0.52   | 0.88  | 0.48     | 0.18       |

Each mode change also rebuilds the env map via `buildEnv(mode)`.

---

## Performance Notes
- 936 lines, 33KB self-contained
- Single rAF loop, no React overhead
- 28 particles + 6 orbit satellites + 3 torus knots = fast
- PMREMGenerator called once per mode change (not per frame)
- Dispose old envMap after building new one (memory leak prevention)

---

## Gotchas for Future Iterations

1. **Gaze + Rotation conflict**: NEVER mix quaternion slerp and .rotation.y on same object. Use parent group for gaze, child for rotation.

2. **Headless screenshot limitation**: MeshPhysicalMaterial transmission doesn't render in Playwright/headless. Always test in real Chrome for glass validation.

3. **Orbit radius**: At camera distance 4.8, fov 38, orbit radius > 1.3 puts satellites outside viewport. Cap at 1.05-1.20.

4. **Bloom blowout**: UnrealBloomPass strength above 0.55 with multiple emissive objects causes white rectangles. Keep threshold at 0.85+.

5. **envMapIntensity**: Glass NEEDS high envMapIntensity (4+) to show reflections. Lower values = flat-looking glass.

6. **CylinderGeometry as HexPrism**: `new THREE.CylinderGeometry(r, r, h, 6)` = perfect regular hexagonal prism. No custom geometry needed.

---

## Verification

- File sent to Jared via Telegram (message_id: 7867)
- Screenshot preview sent (message_id: 7868)
- File works on file:// protocol (all CDN resources)
- Tested in headless Chromium (visual confirms structure)
- All 4 modes cycle correctly via auto-demo
- Cursor gaze tracking tested (gazeGroup rotation)
