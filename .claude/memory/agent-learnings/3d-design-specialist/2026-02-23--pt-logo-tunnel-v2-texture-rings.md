# Pure Technology Logo Tunnel V2 - Texture Ring Approach

**Date**: 2026-02-23
**Type**: technique
**Confidence**: high
**Tags**: three-js, tunnel-animation, logo-animation, texture-rings, additive-blending, phase-state-machine

---

## Context

Built V2 of the PT logo tunnel animation after Jared's feedback that V1 "doesn't look like our logo at all."
The key fix: embed the ACTUAL logo PNG as base64 data URI and use it as a texture on every ring in the tunnel.

---

## Logo Visual Analysis

The PT logo is:
- Hexagonal outer frame with multiple concentric blue hex outlines
- Swirling spiral lines that transition blue (outer) -> orange/red (inner center)
- The spiral creates a VORTEX feel - it already looks like a tunnel/depth effect
- Small black circle at the very center (the void)
- Black background

This shape is PERFECT for a tunnel: each "ring" in the tunnel IS the logo, receding to infinity.

---

## Technical Approach: Logo Texture Rings

Core technique: 80 PlaneGeometry meshes, each:
- Textured with the actual logo PNG (loaded from base64 data URI embedded in HTML)
- Positioned along Z axis from -910 to -10 (depth)
- Each rotated by 0.09 radians more than the previous (cumulative spiral)
- Color tinted: blue (far) -> purple (mid) -> orange (near)
- Opacity: 0.08 (far) -> 0.63 (near)
- blending: THREE.AdditiveBlending (essential - makes overlapping look luminous not solid)

```javascript
const mat = new THREE.MeshBasicMaterial({
  map: logoTexture,
  transparent: true,
  opacity: opacity,
  depthWrite: false,
  blending: THREE.AdditiveBlending,  // CRITICAL
  color: ringColor,  // Tint applied ON TOP of texture
});
```

The tint color changes the logo's appearance per ring while the base texture remains the same.
AdditiveBlending means multiple overlapping logo-rings GLOW rather than obscure each other.

---

## Size Scaling Formula

Rings further away need to be physically larger to counteract perspective:
```javascript
const depth = Math.abs(z);
const ringSize = BASE_SIZE * (depth / 60.0);
```
This keeps their apparent on-screen size consistent = infinite tunnel feel.

---

## Animation: Tunnel Scroll (No Camera Movement)

Instead of moving the camera (which caused issues with ortho/looping), move the tunnelGroup:
```javascript
// Phase 2: tunnel flight
tunnelGroup.position.z = 20 + travel * TUNNEL_LENGTH * 1.1;
```
Camera stays at origin. This is simpler and loops cleanly.

---

## 6-Phase State Machine

```
Phase 0 (0-2.8s):   Hero logo appears on black — recognizable, still
Phase 1 (2.8-5.2s): Logo spins + shrinks (viewer pulled toward center)
Phase 2 (5.2-9.5s): TUNNEL FLIGHT — rings scroll past, drill spin, speed lines
Phase 3 (9.5-11.5s): Orange core explosion — emerging from the other side
Phase 4 (11.5-14.5s): Logo reforms, spinning back in from -360deg rotation
Phase 5 (14.5-16.0s): Hold, then loop
Total: 16 seconds
```

Key: each phase modifies tunnelGroup.position.z and heroMat.opacity independently.
Clean separation of concerns per phase.

---

## Postprocessing Stack (ESM, r0.161.0)

```javascript
// UnrealBloom: threshold 0.78 prevents the logo texture from overexposing
const bloomPass = new UnrealBloomPass(res, 0.6, 0.4, 0.78);

// Custom ShaderPass: chromatic aberration (ramps 0.0015 -> 0.0105 during tunnel)
// + vignette + flicker during tunnel phase
```

The aberration adds physical feel: edges of logo refract slightly, like looking through a lens.

---

## Hero Logo Plane

Separate Mesh from tunnel rings — positioned at z=-28, size 20x20.
During Phase 0/4/5: full opacity, stationary.
During Phase 1: spins (rotation.z), scales down (0.35x), moves closer (+14 on z).
This creates the "being sucked in" effect without complex physics.

---

## Speed Lines During Tunnel

250 LineSegments, radial pattern, inner = orange, outer = blue:
```javascript
// Inner point near center
linePositions[i*6+0] = Math.cos(angle) * innerR;  // innerR = 0.05 to 0.25
// Outer tip
linePositions[i*6+3] = Math.cos(angle) * outerR;  // outerR = 2.5 to 11.5
```
AdditiveBlending, opacity animated 0 -> 0.3 -> 0 across phases.

---

## Base64 Embedding for Self-Contained File

```python
import base64
with open('logo.png', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()
logo_data_uri = f'data:image/png;base64,{b64}'
# Store in JS variable, pass to TextureLoader.load()
```

The PT logo is ~3MB PNG -> 4MB base64 -> 3.8MB total HTML file.
Works completely standalone, no server needed.

---

## Gotchas

1. **GLSL in Python heredoc**: curly braces in GLSL conflict with Python .format() / f-string.
   Solution: use f-string but double-escape all JS object braces `{{}}` while GLSL braces stay single.

2. **textureLoader.load() is async** - use `await new Promise(resolve => textureLoader.load(url, resolve))`
   so texture is ready before building rings. Requires `<script type="module">`.

3. **Tint color on top of texture**: `MeshBasicMaterial.color` multiplies with the texture.
   Use white (0xffffff) for no tint, blue/orange for colored versions.
   Setting color to black hides the texture entirely.

4. **depthWrite: false is essential** for all transparent/additive materials to avoid z-fighting
   when many planes overlap.

---

## File Reference

`/home/jared/projects/AI-CIV/aether/exports/pure-technology-3d-logo-v2.html`
3.8 MB, self-contained, requires Chrome/Firefox with internet for Three.js CDN.
