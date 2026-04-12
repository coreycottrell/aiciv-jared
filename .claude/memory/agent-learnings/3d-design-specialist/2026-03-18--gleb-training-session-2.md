# Memory: Gleb Training Session 2 — March 18, 2026

**Date**: 2026-03-18
**Agent**: 3d-design-specialist
**Type**: synthesis + technique + teaching
**Topic**: IOR animation (first full implementation), Apple Liquid Glass research, volumetric beam rings, weekly 6-session sprint plan
**Confidence**: high
**Tags**: gleb-kuznetsov, ior-animation, liquid-glass, volumetric-light, god-rays, glassmorphic-card, iridescence, pmrem, transmission, bloom, purebrain, training

---

## Context

Week sprint session 2 (training started March 15). Prior state: ~93% CDN mastery.
Three new techniques implemented:
1. IOR animation ("woosh" refraction) — identified in March 17 session, first full CDN implementation
2. Volumetric light beams (layered ring method — no additional render passes needed)
3. Improved glassmorphic card (animated CanvasTexture wave, hover spring at 0.055 lerp)

---

## Key Technique: IOR Animation

IOR (Index of Refraction) controls how much light bends through glass.
Oscillating it creates "breathing" organic glass:

```javascript
// In render loop — zero performance cost:
glassMat.ior = 1.28 + 0.22 * Math.sin(t * 2.2);
// On click: add pulse spike:
glassMat.ior = 1.28 + 0.22 * Math.sin(t * 2.2 + clickPulse * 8);
```

Range: 1.28 (light optical glass) to 1.50 (crown glass). Never below 1.0.
Frequency: 2.2 Hz feels organic (faster = mechanical, slower = imperceptible).
The sine wave maps naturally to the visual quality of glass — high IOR = light bends more = more sparkle.

This property is on `MeshPhysicalMaterial`. `material.needsUpdate` is NOT required for uniform changes.

---

## Key Technique: Volumetric Beam (CDN-compatible)

No additional render passes. Single scene addition:

```javascript
const RAY_RINGS = 22;
for (let i = 0; i < RAY_RINGS; i++) {
  const t = i / (RAY_RINGS - 1);
  const radius  = 0.05 + t * 2.4;                     // cone expands downward
  const opacity = (1.0 - t) * (1.0 - t) * 0.055;     // quadratic falloff
  new THREE.RingGeometry(radius * 0.88, radius, 64);  // thin ring slice of cone
  // AdditiveBlending + depthWrite: false
}
```

Two beams (PB blue + PB orange) creates brand presence and atmospheric depth.
Rotate group very slowly (0.035–0.04 rad/s) for subtle movement that reads as atmospheric.

Cost: 22 ring draw calls = negligible. Visual payoff: large.

---

## Key Technique: Hover Spring Interaction (0.055)

For any "object lifts toward viewer on hover" interaction:
```javascript
// Target values
const TARGET_ROT_Y  = isHovering ? -0.18 : -0.38;  // less tilt = facing viewer more
const TARGET_Z      = isHovering ?  0.12 :  0.00;   // lifts forward

// Spring (each frame):
object.rotation.y += (TARGET_ROT_Y - object.rotation.y) * 0.055;
object.position.z += (TARGET_Z - object.position.z) * 0.055;
```

0.055 lerp = ~12 frames to 50% = "loose spring" = premium feel.
0.08 = too snappy. 0.03 = too floaty.

---

## Research Finding: Apple Liquid Glass (2025/2026)

Apple's "Liquid Glass" system material represents the new aesthetic ceiling:
1. Glass distorts scene BEHIND it (FBO-based, not environment-based)
2. Glass responds to motion
3. Glass has interior depth
4. Edge distortion/caustic spill

Current CDN stack achieves 2, 3, partial 4. Gap: FBO scene sampling.

**CDN-compatible FBO approach** (no npm needed):
```javascript
// Render scene to texture
renderer.setRenderTarget(fboTarget);
glassMesh.visible = false;
renderer.render(scene, camera);
glassMesh.visible = true;
renderer.setRenderTarget(null);
// Use fboTarget.texture in glass material for scene-behind-glass sampling
```

This is Session 5's target in the 6-session sprint plan.

---

## CDN Mastery Assessment: ~95% (up from 93%)

Improvements this session:
- IOR animation: +1% (implemented, not just documented)
- Volumetric beams: +0.5%
- Animated card UI: +0.3%
- Spring interaction pattern: +0.2%

Remaining to 97%+ (target end of 6-session sprint):
1. Live neural edge updates (rubber-band edge fix) — Session 2
2. N8AO integration via CDN — Session 2
3. GSAP scroll + full material stack combined — Session 3
4. Custom GLSL animated iridescence — Session 4
5. FBO-based Liquid Glass — Session 5
6. Production capstone composition — Session 6

---

## Output File

`exports/overnight-content/gleb-study-session-1.html`

Demonstrates: three-layer glass orb, IOR animation, satellite orbits, glassmorphic card
with animated UI, volumetric light beams (blue + orange), custom PMREM probe, prime-frequency
breathing, torus rings, particle systems, click pulse, mouse parallax, conservative bloom,
CA + grain + vignette postprocessing.

Opens direct from filesystem (no CORS issues). All assets from CDN only.

---

## Design Philosophy Note

"IOR is breath. Bloom is whisper. Glass is everything."

IOR animation makes glass feel alive without the viewer consciously noticing why.
The refractive index oscillates like lungs. Bloom should whisper — if you see it, it's too strong.
Glass is the subject, the atmosphere, the light, and the story.

---

## Next Session Priorities

1. Live neural edge position updates (fix the March 17 rubber-band edge gotcha)
2. N8AO via CDN (`https://unpkg.com/n8ao@latest/dist/N8AO.js`) — screen-space AO
3. Multi-object composition with foreground/midground/background depth layers
