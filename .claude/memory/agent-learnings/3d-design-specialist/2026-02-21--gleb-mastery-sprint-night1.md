# Gleb Kuznetsov Mastery Sprint - Night 1

**Date**: 2026-02-21
**Type**: teaching
**Topic**: Complete Gleb Kuznetsov aesthetic recipe for Three.js/R3F replication

---

## Memory Search Results

- Searched: Previous full-stack-developer memories for "glass", "avatar", "WebGL", "Gleb"
- Found: Three phases of GLSL avatar work (premium-glass-sphere, gleb-kuznetsov-avatar-overhaul)
- Found: ui-ux-designer Gleb forensic analysis
- Applied: All Phase 3 learnings to inform Three.js (non-raymarcher) implementation

---

## Core Discovery: Two Paradigms

**GLSL Raymarcher** (current avatar-fluid.html): Gleb-level ALREADY. Don't replace.
**React Three Fiber + MeshTransmissionMaterial**: The path for new scene elements.

These are COMPLEMENTARY, not competing. Use each for its strength:
- Raymarcher: Custom avatar with full shader control
- R3F: Product showcases, homepage backgrounds, embed scenes

---

## The Complete Gleb Recipe (Technical)

### Glass Material Parameters
```javascript
transmission: 1.0          // MUST be 1.0 for glass
thickness: 0.8             // Refraction depth
roughness: 0.05            // Nearly smooth (0 = mirror, 1 = frosted)
ior: 1.5                   // Real glass IOR
chromaticAberration: 0.8   // Per-channel color split (artistic, not physical)
backside: true             // MANDATORY - shows internal reflections
attenuationColor: '#2a93c1' // Beer's law glass tint color
attenuationDistance: 0.5   // Lower = stronger tint
envMapIntensity: 2.5       // HDRI reflection strength
samples: 8                 // Refraction quality
```

### Geometry - NEVER go below 128 segments for transmission
```javascript
SphereGeometry(1.2, 128, 128)  // 128 segments = smooth glass silhouette
// 32 segments through glass = visible facets = looks like mistake
```

### Post-Processing Stack (ALL required)
```
1. UnrealBloom: threshold=0.85, strength=0.35, radius=0.4
   threshold 0.85 = ONLY truly bright emissive elements bloom
   DO NOT go below 0.8 = nuclear look
2. DepthOfField: subtle (focusDistance=0.015, maxblur=0.003)
3. ChromaticAberration: 0.002 screen-space (stronger at edges)
4. Vignette: offset=0.5, darkness=0.8
5. FXAA anti-aliasing
```

### Lighting: 6-Color Studio (Mandatory)
```
L1 Key:   #FFF8F0 warm white, intensity 3.5, upper-left
L2 Fill:  #0D16F5 electric blue, intensity 0.9 (Gleb signature)
L3 Rim:   #18A8D3 cyan, intensity 0.7
L4 Accent: #D10DCE magenta, intensity 0.45
L5 Ground: #E42424 saturated red, intensity 0.35
L6 Ambient: #0A0A1A dark navy (not gray!)
+ Poly Haven Studio 1k HDRI as scene.environment
```

### The "Light vs Object" Test
```
PASS: Glass sphere transmits colored light from colored environment
FAIL: Glass sphere only reflects surroundings (roughness too high)

PASS: Inner content is a diffuse emitter (roughness=1, emissiveIntensity=3+)
FAIL: Inner content has visible geometry with specular highlights
```

### Gold Specular (Gleb Signature)
```
NOT white (#ffffff)
USE gold (#C8A84A = vec3(0.784, 0.659, 0.290))
White speculars = generic demo
Gold speculars = premium product render
```

### Animation Rules
```
Float: sin(t * 0.8) * 0.12 on Y + sin(t * 0.5) * 0.05 on X
       Multiple frequencies = organic, not mechanical
Rotation: 0.12 rad/s idle (barely perceptible)
Mouse follow: 4% lerp per frame = weighted, not snappy
Rings: counter-rotate at different speeds for visual interest
```

### Background
```
#060606 (NOT #000000 - slightly blue-black)
CSS colored light bleed: electric blue upper-right, magenta lower-left
The glass casts colored light into the background
```

---

## Tools Validated

### Poly Haven API
- URL: https://api.polyhaven.com/files/{slug}
- Studio HDRI: `poly_haven_studio`
- 1k version: 1.7MB, fast load, good enough for web
- Downloaded to: exports/3d-assets/poly_haven_studio_1k.hdr

### Meshy API
- API works (mode: "preview" for fast iteration)
- New generation submitted: task 019c7da3 (glass orb)
- Previous successful: task 019c7c18 (glowing orb)
- Meshy generates SHAPE not MATERIAL - always apply MeshTransmissionMaterial after

### Three.js Prototype
- Path: exports/gleb-glass-prototype.html
- Uses: MeshPhysicalMaterial + 6-light studio + UnrealBloomPass + ChromaticAberration shader + Vignette shader + FXAA
- HDRI: attempts CDN load, falls back to procedural colored environment
- Mode system: idle/blue/orange/hologram

---

## Gotchas Learned

1. BokehPass from Three.js addons doesn't work well with transmission materials
   (DoF blurs the glass incorrectly). R3F postprocessing DepthOfField handles better.

2. ChromaticAberration as a postprocessing pass is nearly free GPU cost.
   Material-level chromaticAberration in MeshTransmissionMaterial is more expensive.
   Use both for different effects.

3. Bloom is 60% of GPU cost in typical post-processing stack.
   If performance issues: reduce bloom samples or strength, not geometry.

4. HDRI fails cross-origin. Solution: host HDRI on same domain as scene,
   OR use the PMREMGenerator procedural fallback (colored environment spheres).

5. `mode: "preview"` Meshy = ~5 minutes, fewer credits. `mode: "refine"` on preview result = better quality.

---

## Context
- Full report: to-jared/overnight/3d-gleb-mastery-progress-2026-02-21.md
- Prototype: exports/gleb-glass-prototype.html
- HDRI: exports/3d-assets/poly_haven_studio_1k.hdr
- 7-day roadmap: day 1 complete, day 2 = R3F component build
