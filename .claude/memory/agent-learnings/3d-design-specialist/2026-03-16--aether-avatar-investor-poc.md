# Aether Avatar — Investor POC (Neural Network Presence)

**Date**: 2026-03-16
**Type**: technique + synthesis
**Agent**: 3d-design-specialist
**Topic**: Full investor-grade Aether avatar POC with 4 states, glass shell, neural network, postprocessing
**Confidence**: high
**Tags**: three-js, neural-network, glass, investor-poc, avatar, postprocessing, purebrain, r0.161.0

---

## Context

Built investor-grade standalone HTML Aether avatar POC for purebrain.ai/investors/.
File: `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-poc.html`
Size: ~48KB, 1350 lines

---

## Architecture: Three Concentric Layers

1. **fBm gradient background** — rendered to ortho scene (not bloomed). Deep atmospheric dark blue.
2. **Neural network sphere** (networkGroup) — 96 Fibonacci-lattice nodes, ~300+ edges, pulse particles, glass inner shell. Rotates as a group.
3. **Glowing core** — free-floating in main scene (not in networkGroup), breathes with multi-frequency float.

Key: Background → main scene render via `renderer.autoClear = false` pattern. Separates atmospheric bg from bloomable 3D content.

---

## Key Technical Decisions

### Fibonacci Lattice Node Distribution

```javascript
function fibonacciSphere(count, radius) {
  const phi = Math.PI * (3 - Math.sqrt(5));
  // ... standard Fibonacci lattice
}
```

Superior to random sphere distribution: no clustering, perfectly even spacing. Critical for neural network look — random distribution creates ugly sparse/dense regions.

### PMREM Probe with Brand Colors

```javascript
const probePoints = [
  { color: 0xfff4e8, i: 3.0, p: [ 8,  12,  8] },  // warm white key
  { color: 0x2a93c1, i: 2.2, p: [-10,  4, -6] },   // PureBrain blue fill
  { color: 0xf1420b, i: 1.4, p: [  6, -4,-10] },   // orange rim (enters glass)
  { color: 0x4ab8ff, i: 0.7, p: [  0, -8,  4] },   // cool bounce
  { color: 0xffffff, i: 0.5, p: [  2,  6, -2] },   // neutral specular
];
```

The orange rim at [6, -4, -10] is behind/below — makes brand orange appear INSIDE the glass refraction without tinting the glass itself. Gleb Kuznetsov trick.

### Glass Inner Shell (MeshPhysicalMaterial)

```javascript
{
  transmission: 1.0,
  thickness: 0.35,
  roughness: 0.02,
  ior: 1.48,
  side: THREE.DoubleSide,
  depthWrite: false,
  iridescence: 0.3,
  iridescenceIOR: 1.6,
  sheen: 0.15,
  sheenColor: PureBrain blue,
}
```

128-segment sphere. Iridescence 0.3 is the key quality upgrade — zero performance cost, huge visual improvement.

### Mode Color System

| Mode     | Core Color | Ring Color | Bloom  | CA    |
|----------|-----------|-----------|--------|-------|
| idle     | Blue       | Blue       | 0.45   | 0.8   |
| listening| Cyan       | Cyan       | 0.62   | 0.8   |
| thinking | Violet     | Violet     | 0.55   | 1.6   |
| speaking | White      | Orange     | 0.80   | 2.2   |

Speaking mode uses white core + orange ring = premium contrast. Chromatic aberration increases during speaking to suggest energy/output.

### State Transition System

All modes lerp with `modeT` (0→1, rate 1.8/s). Bloom, orbitSpeed, nodeSpeed, fireRate, emitR all cross-fade. Feels alive, not instant snap.

### Conservative Bloom ("confirms, does not create")

```javascript
// strength 0.45-0.80 range
// threshold 0.82 — only brightest pixels
const bloomPass = new UnrealBloomPass(res, 0.45, 0.30, 0.82);
```

Following the principle: transmission material IS the premium. Bloom only confirms. Never increase bloom to compensate for weak materials.

### Ripple Rings (Listening Mode)

4 torus rings expand outward from inner shell to emitR, fade in/out as they travel. Speed: 0.65/s. Opacity cap: 0.22 * modeT (fades in with mode transition).

### Speaking Wave Rings

5 torus rings at different starting radii, pulsing with audio-like rhythm via `Math.sin(t * 4.2)`. Chromatic aberration jumps to 2.2 in speaking mode.

### Chat Integration (Demo)

Full chat UI with glassmorphic cards, thinking dots, demo responses. Chat input triggers: listening → thinking (1.6s) → speaking (3s) → idle. Fully interactive proof of concept.

---

## PostMessage API (iframe-embeddable)

```javascript
// From parent page:
iframe.contentWindow.postMessage({ type: 'SET_MODE', mode: 'thinking' }, '*');

// Avatar emits on load:
{ type: 'READY', version: 'poc-v1' }
```

---

## Performance Profile

- 96 individual node meshes (need per-node emissiveIntensity)
- 1 LineSegments for ~300+ edges (single draw call)
- 280 orbit particles (ShaderMaterial, AdditiveBlending)
- 140-slot pulse particle pool (object pool, ShaderMaterial)
- 9 ring/wave meshes (TorusGeometry, BasicMaterial)
- 1 EffectComposer with 4 passes (RenderPass + Bloom + CA/Vignette + OutputPass)
- fBm background (separate ortho render)

Estimated: well under 60fps budget on modern desktop.

---

## Gotchas

1. **coreMesh/haloMesh are NOT in networkGroup** — they float independently via multi-frequency sine. If you add them to the group, they rotate with the network and the "floating core" effect is lost.

2. **PMREM must use compileEquirectangularShader() not compileCubemapShader()** when using a fromScene probe (not a cubemap texture). This is counter-intuitive.

3. **Fibonacci sphere produces non-random but uniformly distributed nodes** — this is intentional. Random distribution (random angles) has clustering artifacts that break the clean neural network aesthetic.

4. **lineColors array is pre-allocated** — must set `needsUpdate = true` after per-frame modification. The "dim normally, bright when active node fires" effect is purely in the color channel, not opacity.

5. **The `depthWrite: false` on transmission AND on glow materials** is non-negotiable for multi-transparent-object scenes.

---

## What's Next / Improvements

1. Add GSAP ScrollTrigger for scroll-driven appearance when page scrolls to it
2. Web Audio API mic input (pattern already documented in 2026-03-09 memory)
3. RoomEnvironment from three/addons for better reflections (no external file needed)
4. SMAAPass for better glass edge anti-aliasing
5. Thinking mode: add a rotating ring of data glyphs (Unicode numbers) around inner shell
6. Consider depth-of-field pass (focal plane at core = background nodes softer)

---

## File

`/home/jared/projects/AI-CIV/aether/exports/aether-avatar-poc.html`
Single self-contained HTML. No external assets. ESM importmap for Three.js r0.161.0.
