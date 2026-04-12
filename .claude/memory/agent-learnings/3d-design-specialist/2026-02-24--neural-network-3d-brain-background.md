# Neural Network 3D Brain Background — PureBrain Portal

**Date**: 2026-02-24
**Agent**: 3d-design-specialist
**Type**: technique
**Confidence**: high
**Tags**: three-js, neural-network, particles, bloom, mouse-interaction, purebrain-portal, instanced-mesh, synaptic-pulse

---

## Context

Built a 3D neural network background for the PureBrain portal login page. This is a standalone HTML file
using Three.js CDN (ESM importmap pattern — confirmed working from Day 9/10 sprint).

Output: `/home/jared/projects/AI-CIV/aether/exports/3d-neural-network-background.html`

---

## Architecture Decisions

### Brain-Shaped Ellipsoid Distribution

```javascript
// Rejection sampling inside brain-shaped region
// Two hemisphere lobes slightly separated
const hemisphere = Math.random() > 0.5 ? 1 : -1;
// Ellipsoid: rx=8.5, ry=5.0, rz=6.0 with hemisphere offset of ±1.0
// Cube-root of random = uniform volume distribution
const r = Math.cbrt(Math.random());
```

Key insight: `Math.cbrt(Math.random())` gives uniform volume distribution.
`Math.random() * r` skews to center. Use cube root for correct sphere filling.

### O(1) Edge Lookup for Pulse Spawning

Using `Array.findIndex` per propagation call = O(n) per neuron fire = laggy.
Build a `Map` at graph construction time:

```javascript
const edgeLookup = new Map();  // "min*10000+max" → edgeIndex
function getEdgeIndex(a, b) {
  const key = Math.min(a, b) * 10000 + Math.max(a, b);
  return edgeLookup.get(key) ?? -1;
}
```

This is O(1) during animation loop — critical for 280 nodes firing simultaneously.

### Individual Materials per Neuron (vs InstancedMesh)

Used individual `THREE.Mesh` + `THREE.MeshPhysicalMaterial` per neuron (280 meshes).

Why NOT InstancedMesh: InstancedMesh supports `setColorAt()` but that modifies instance colors,
not emissive intensity. To get proper bloom per-neuron, we need `emissiveIntensity` variation,
which requires individual materials.

Performance test: 280 individual materials = fine at 60fps. Threshold is ~1000-2000 for concern.

### Synaptic Lines — BufferGeometry with vertexColors

Single `THREE.LineSegments` for ALL connections. Update `color` buffer per-frame.

Pattern:
```javascript
const lineGeo = new THREE.BufferGeometry();
lineGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
lineGeo.setAttribute('color', new THREE.BufferAttribute(lineColors, 3));
lineGeo.attributes.color.needsUpdate = true;  // REQUIRED in render loop
```

One draw call for ~450 connections = far better than 450 separate Line objects.

### Pulse Particle Pool

120-slot pulse pool (object pool pattern). Inactive particles parked at (9999, 9999, 9999).

```javascript
// Pool pattern
for (let i = 0; i < MAX_PULSES; i++) {
  pulses.push({ active: false, t: 0, edgeIndex: -1, fromIndex: -1, toIndex: -1 ... });
}

function spawnPulse(edgeIndex, fromNeuron, toNeuron, color) {
  for (let i = 0; i < MAX_PULSES; i++) {
    if (!pulses[i].active) { ... return; }
  }
}
```

Use `depthWrite: false` + `THREE.AdditiveBlending` for all particle systems.

### Prime Frequency Rotation (Day 9 technique)

```javascript
scene.rotation.y = Math.sin(t * 0.071) * 0.10 + Math.sin(t * 0.038) * 0.04;
scene.rotation.x = Math.sin(t * 0.053) * 0.04 + Math.sin(t * 0.029) * 0.02;
```

Ratios: 0.071/0.038 ≈ 1.868 (irrational). Pattern doesn't repeat for ~80 seconds.

### Custom GLSL Point Shader

Three.js `THREE.PointsMaterial` doesn't allow per-point size variation with proper round points.
Use `THREE.ShaderMaterial` with custom vertex/fragment:

```glsl
// Vertex: gl_PointSize with perspective scaling
gl_PointSize = size * (350.0 / -mvPosition.z);

// Fragment: round point with hot-core glow
float d = dot(uv, uv);
if (d > 0.25) discard;
float core = 1.0 - smoothstep(0.0, 0.12, d);
vec3 finalColor = mix(vColor, vec3(1.0, 1.0, 0.95), core * 0.7);
```

---

## Neuron Firing Cycle

```
depth=0: Blue fire (initial)  → sparks 5 + depth*2 = 5
depth=1: Orange fire          → sparks 7
depth=2: Blue fire            → sparks 9
depth=3: Orange fire          → sparks 11
depth=4: Final propagation    → no further propagation
```

Color alternates: Blue → Orange → Blue → Orange. Reads as electrical cascade.

Refractory period: `FIRE_DURATION * 0.7` = 0.84s before a neuron can re-fire.
Prevents infinite loops in highly-connected clusters.

---

## Bloom Settings for Neural Glow

```javascript
const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(W, H),
  1.4,   // strength — higher than avatar scenes
  0.6,   // radius — wider spread for neuron cloud
  0.15   // threshold — LOW to catch dim connection lines too
);
```

Key: threshold 0.15 (vs 0.9 for glass spheres). Neural connections are faint;
low threshold makes them glow even at low emissive intensity.

---

## Mouse Interaction

### Parallax Camera Shift
```javascript
cameraTarget.x = mouse.x * -1.8;  // inverted = moves opposite to mouse
cameraTarget.y = mouse.y * -1.2;
// Lerp in animate: camera.position.lerp(cameraTarget, 0.025)
```

### Proximity Activation
- Per-frame check against mouse-to-world plane position
- Mouse plane at z=0, neurons projected via `applyMatrix4(scene.matrixWorld)`
- Cooldown: 0.08s between mouse-triggered fires (prevents spam)
- Probability decreases with distance: `(1.0 - dist / MOUSE_RADIUS) * 0.25`

### Click Burst
- Click finds nearest neuron (O(n) but only on click, not per-frame)
- Fires that neuron with ORANGE color + 20 extra sparks
- Creates big visual response to explicit interaction

---

## Performance Budget (Estimated)

- 280 individual neuron meshes: ~2ms
- 1 LineSegments for connections: <0.5ms
- 1800 ambient particles: <1ms
- 120 pulse particles: <0.5ms
- 600 spark particles: <0.5ms
- UnrealBloomPass: ~3ms at 1080p
- Total: ~8ms → well under 16.7ms (60fps budget)

---

## Gotcha: `needsUpdate` on BufferAttributes

If you modify a Float32Array backing a BufferAttribute, you MUST set:
```javascript
geometry.attributes.color.needsUpdate = true;
```
Without this, the GPU never receives the updated data. Changes are invisible.

---

## Integration Notes

This is a standalone demo. To use as background behind login form:
1. Copy the `<script type="importmap">` + `<script type="module">` blocks
2. Remove `#demo-label` and `#perf-toggle` UI elements
3. Keep `#canvas-container` with `position: fixed; inset: 0; z-index: 0`
4. Add login form container with `position: fixed; z-index: 10`

---

## Reference Files

- Demo: `/home/jared/projects/AI-CIV/aether/exports/3d-neural-network-background.html`
- Existing 2D version: `/home/jared/projects/AI-CIV/aether/exports/purebrain-portal-login-neural.html`
- Day 10 SSR/PMREM patterns: `.claude/memory/agent-learnings/3d-design-specialist/2026-02-24--day10-ssr-n8ao-cinematic-product-shot.md`
