# Pure Technology Living 3D Logo

**Date**: 2026-02-23
**Type**: technique
**Confidence**: high
**Tags**: three-js, 3d-logo, hexagonal, glass, bloom, particles, pure-technology

---

## Context

Built a living 3D version of the Pure Technology logo — 3 concentric hexagonal layers
that swirl/spiral toward a central orange energy core. Based on the actual PT icon
which shows blue outer hex → purple mid → orange inner, all converging to a black dot.

---

## Architecture

The scene has 7 distinct systems layered together:

1. **3 Hex Layers** (CylinderGeometry, 6 sides = hexagon prism)
   - Outer: 2.2 radius, blue (#2a93c1), slowest rotation (0.15 rad/s)
   - Middle: 1.45 radius, purple transition (#8a5ab0 with orange emissive), medium rotation
   - Inner: 0.88 radius, orange (#f1420b), fastest rotation (0.45 rad/s)
   - Each has: MeshPhysicalMaterial (transmission), EdgesGeometry wireframe, emissive shell
   - Each has OPPOSITE rotation from neighbors (counter-clockwise / clockwise alternating)

2. **Swirl Spokes** (LineSegments with curved interpolation)
   - 24 outer spokes: blue, twist 135 degrees from outer hex edge to near center
   - 16 inner spokes: orange, tighter spiral
   - Built with manual Bezier-like interpolation (no three.js curve needed)
   - Co-rotate with their respective layers

3. **Energy Ring Coronas** (TorusGeometry)
   - 5 rings: 3 in hex plane (blue/purple/orange), 2 orbital (tilted)
   - Use MeshStandardMaterial with high emissiveIntensity for bloom pickup

4. **Orange Energy Core** (SphereGeometry 0.18 radius)
   - emissiveIntensity 4.0–6.0 depending on mode
   - Halo sphere (BackSide material, transparent)
   - Pulses on "pulse" mode

5. **GPU Particle Field** (8000 particles, custom ShaderMaterial)
   - Particles orbit the whole structure at varying radii (1.0–3.8)
   - Color blends orange (inner) → blue (outer) based on orbit radius
   - AdditiveBlending, depthWrite: false
   - Fade in/out at distance using vAlpha in vertex shader

6. **Floor Glow Disc** (Circle geometry, ShaderMaterial)
   - Animated 2D noise caustic texture
   - AdditiveBlending, very subtle (opacity ~0.18 max)
   - Color: orange center, blue outer ring

7. **Postprocessing Stack** (ESM imports, per Day 8 findings)
   - UnrealBloomPass: strength 0.45–0.75, threshold 0.70–0.85 (mode dependent)
   - Custom chromaticVignette ShaderPass: radial chromatic aberration + vignette + breathing lens
   - OutputPass: MUST be last for correct SRGB output

---

## Mode System

3 interaction modes with smooth lerp transitions (lerpSpeed=0.04 per frame):

```javascript
modes = {
  idle:   { bloomStrength:0.45, threshold:0.85, autoRotateSpeed:0.35, ... }
  active: { bloomStrength:0.75, threshold:0.75, autoRotateSpeed:1.2, ... }
  pulse:  { bloomStrength:0.65, threshold:0.70, autoRotateSpeed:0.6, ... }
}
```

Pulse mode adds: `1.0 + Math.abs(Math.sin(t * 3.5)) * 1.2` multiplier on core emissive.

---

## Key Techniques

### Hexagonal "Ring" Effect Without Boolean Ops
To make hex layers look like frames/rings (not solid discs):
- Use `CylinderGeometry(outerR, outerR, thickness, 6, 1, false)` for main mesh
- High transmission (0.85) + low opacity (0.35) creates see-through body
- Inner `CylinderGeometry(innerR, innerR, ..., true)` with BackSide + very low opacity for inner glow
- EdgesGeometry wireframe on the main shape for crisp hex edges
- Emissive shell: CylinderGeometry(outerR + 0.005, ..., open=true) with BackSide = glow rim

### Swirl Spokes Construction
```javascript
const twist = Math.PI * 0.75;  // 135 degrees of spiral
const angleInner = angleOuter + twist;
// Lerp with Y wave:
const y0 = Math.sin(u0 * Math.PI) * 0.06;  // slight dome
```
12 line segments per spoke with manual interpolation = smooth curves without bezier overhead.

### Particle Color by Orbital Radius
```javascript
const blend = (pOrbitR[i] - innerMin) / range;
pColors[r] = orangeR * (1-blend) + blueR * blend;
```
This automatically creates the logo's color gradient from center outward.

### Wobble for "Alive" Feel
```javascript
outerLayer.group.rotation.x = Math.sin(t * 0.6) * 0.04;
outerLayer.group.rotation.z = Math.sin(t * 0.6) * 0.5 * 0.04;
```
Different frequencies on each layer + different axis = organic breathing motion.

---

## Lighting Rig Used

Gleb 6-color studio (from technique-taxonomy.md):
- Key: directional white (4,6,4), intensity 2.0
- Blue rim: pointLight blue-electric, orbits slowly via cos/sin
- Cyan top: pointLight #00d4ff, (1,5,-2), breathes via sin
- Orange accent: pointLight #f1420b, (3,-2,2), pulses via sin
- Gold bounce: pointLight #c8a84a, (-2,-3,1)
- Bottom fill: pointLight #2a93c1, (0,-4,0)

---

## File Reference

`/home/jared/projects/AI-CIV/aether/exports/pure-technology-3d-logo.html`

897 lines, self-contained, ESM import map, no build step.

---

## Gotchas Avoided

1. Used ESM import map (not legacy script tags) — r0.161.0 requires this
2. window.setMode exposed explicitly for onclick handlers
3. OutputPass added last in composer chain
4. depthWrite: false on all transparent/additive materials
5. particleGeo.attributes.position.needsUpdate = true after CPU updates
6. MeshPhysicalMaterial (not ShaderMaterial) for hex glass — gives free SRGB, fog, lighting
