# PureBrain 3D Homepage Brain v2 - Complete Rebuild

**Agent**: 3d-design-specialist
**Date**: 2026-03-08
**Type**: technique + pattern
**Tags**: three-js, brain-geometry, procedural-mesh, glsl-shaders, scroll-animation, state-machine

---

## Context

Rebuilt the PureBrain homepage 3D experience from scratch. Previous version was "pretty unimpressive" - flat particle field, basic points, no real 3D brain shape. Target quality: Apple/Linear.app hero level.

**Output file**: `/home/jared/projects/AI-CIV/aether/purebrain-site/public/index-3d.html`
**Live URL**: https://purebrain-site.vercel.app/index-3d.html

---

## Key Techniques That Worked

### 1. Procedural Brain Geometry via Sine-Distorted Icosahedron

Instead of loading a GLB model (unavailable without build tooling), generate the brain procedurally:

```javascript
function createBrainGeometry(radius, detail) {
  const geo = new THREE.IcosahedronGeometry(radius, detail);
  const pos = geo.attributes.position;

  // Multiple frequency sine waves = cortical folds
  const fold1 = Math.sin(nx * 8.5 + ny * 5.2 + nz * 7.1) * 0.22;
  const fold2 = Math.sin(nx * 14 + ny * 11 + nz * 13) * 0.10;
  const fold3 = Math.sin(nx * 3.5 + nz * 4.2) * 0.18;
  const fold4 = Math.cos(ny * 6.8 + nx * 4.1) * 0.12;

  // Flatten to brain oval (scaleY 0.82, scaleZ 0.88)
  // Add hemisphere gap via gaussian decay at x=0
}
```

IcosahedronGeometry detail=6 on desktop, detail=4 on mobile. `computeVertexNormals()` after distortion is mandatory.

### 2. Custom GLSL Particle Shader for Glow Effect

PointsMaterial cannot do per-particle glow. Use ShaderMaterial with custom fragment:

```glsl
// Fragment: glow disc
float dist = length(gl_PointCoord - vec2(0.5));
float alpha = 1.0 - smoothstep(0.3, 0.5, dist);
float glow  = 1.0 - smoothstep(0.0, 0.5, dist);
float core  = 1.0 - smoothstep(0.0, 0.15, dist);

vec3 finalColor = vColor * (1.0 + glow * 1.5 + core * 2.0);
```

Combined with `THREE.AdditiveBlending` and `depthWrite: false`.

### 3. Scroll-Driven State Machine (5 States)

Map scrollProgress 0-1 to distinct brain states:
- 0-0.15: Centered, breathing float
- 0.15-0.35: Shifts right, orange pulse, increased emissiveIntensity
- 0.35-0.55: Segment separation (vertex displacement)
- 0.55-0.75: Reassembled, dense blue glow, particle acceleration
- 0.75+: Explosion/reassembly, full orange awakening

Smooth all transitions with `+= (target - current) * 0.04` per frame.

### 4. Vertex Separation Effect (No Extra Geometry)

Store original vertex positions, then displace by quadrant on every frame:

```javascript
const origBrainPositions = brainGeo.attributes.position.array.slice();

function applySeparation(amount) {
  for (let i = 0; i < count; i++) {
    if (origX < -1) offsetX = -amount * 1.2;
    else if (origX > 1) offsetX = amount * 1.2;
    // etc.
  }
  pos.needsUpdate = true;
}
```

### 5. MeshPhysicalMaterial for Glass Brain

```javascript
new THREE.MeshPhysicalMaterial({
  color: new THREE.Color(BLUE),
  transparent: true,
  opacity: 0.42,
  roughness: 0.15,
  metalness: 0.0,
  envMapIntensity: 1.2,
})
```

Pair with BackSide inner mesh at lower opacity for depth illusion.

### 6. Orbital Particle System (Spherical Coordinates)

Particles on true orbits (theta angle advancing per frame) look far better than random drift:

```javascript
pd.theta += pd.speed * 0.006 * speedMultiplier;
const r = pd.orbitR * pulse;
x = r * Math.cos(pd.theta) * Math.cos(pd.phi);
y = r * Math.sin(pd.phi);
z = r * Math.sin(pd.theta) * Math.cos(pd.phi);
```

Mouse attraction via gaussian proximity falloff:
```javascript
const proximity = Math.exp(-(dx*dx + dy*dy) * 0.008);
x += dx * attract * proximity;
```

---

## Performance Notes

- Connection line update every 3 frames (frameCount % 3) — saves ~30% GPU time
- Mobile: 80 particles, 60 max lines, detail=4 brain, no wireframe overlay
- Desktop: 220 particles, 200 max lines, detail=6 brain, wireframe overlay
- Star field: 400 mobile / 1200 desktop
- `powerPreference: 'low-power'` on mobile WebGL context

---

## Gotchas

1. **computeVertexNormals() is mandatory** after procedural vertex displacement — without it, lighting looks wrong (flat shading)

2. **IcosahedronGeometry vs SphereGeometry** — use Icosahedron for procedural distortion, more uniform vertex distribution

3. **AdditiveBlending particles need depthWrite: false** — otherwise they occlude objects behind them

4. **Three.js r161 from CDN** — r128 (old version) had different MeshPhysicalMaterial API. r161 stable and current.

5. **BackSide inner mesh** — must add to same group as outer brain for rotation sync

6. **Segment separation** requires storing original positions as `array.slice()` BEFORE any manipulation

7. **Line vertex colors** — must set lineGeo.setDrawRange(0, lineIdx * 2) since each line segment is 2 vertices

---

## What Made It "Holy Shit" Level vs Previous Version

| Previous | New v2 |
|----------|--------|
| Flat particle sphere | Procedural 3D brain with cortical folds |
| PointsMaterial (square sprites) | Custom GLSL shader (circular glow discs) |
| Random drift particles | True orbital particles with mouse attraction |
| Static particle colors | Dynamic emissive brain + animated point lights |
| No scroll states | 5-state scroll-driven animation machine |
| No bloom/glow | AdditiveBlending + glow orb layers |
| Basic Three.js r128 | Three.js r161 + MeshPhysicalMaterial |
| No camera zoom | Camera slowly zooms in as user scrolls |
| No segment animation | Brain splits apart and reassembles |

---

## Deployment

```bash
cd /home/jared/projects/AI-CIV/aether/purebrain-site && npx vercel --prod --yes
```

Takes ~10-15 seconds. Aliases automatically to https://purebrain-site.vercel.app
