# Premium Glass Sphere Avatar - Phase 2 Overhaul

**Date**: 2026-02-20
**Type**: technique
**Topic**: Complete rewrite following ui-ux-designer spec - Gleb-inspired single light, pure sphere, icosahedral interior

## What Was Built

Complete rewrite of `exports/avatar-fluid.html` fragment shaders (desktop + mobile) following the 705-line design spec from ui-ux-designer. Previous version was technically complex but visually muddy. This version focuses on restraint, one dominant light, and premium glass materials.

## Key Design Philosophy

"Let the darkness do half the work." - Gleb Kuznetsov approach:
- ONE key light (not four competing ones)
- Pure sphere SDF (not hex-prism blend)
- No liquid pool, no orbital particles, no light rays
- 55-60% canvas coverage, offset upward
- Internal icosahedron visible THROUGH the glass

## What Was Removed (All Causing Visual Mud)

1. Liquid metal pool (`smin(base, liquid, ...)`) - made it geological
2. 8 orbital particles (loop) - cheap effect, broke premium feel
3. 6 volumetric light rays (loop) - "trying to look impressive"
4. `sdHexPrism` SDF blend - hex moved INSIDE as icosahedron
5. L2, L3, L4 light sources - one key + one fill is all you need
6. Core glow (`exp(-length(p)*3.5)`) - was the source of muddy orange everywhere
7. bgRing1, bgRing2 concentric rings - clutter on clean background
8. Macro fbm deformation (deformAmt=0.025+audio*0.14) - made glass look like asteroid

## What Was Added

### 1. Pure Sphere SDF
```glsl
float sphere = length(p) - sphereRadius; // breathing: 0.985 to 1.005
float scratch = fbm(p * 28.0 + t * 0.005) * 0.003;  // micro only
float fingerprint = fbm(p * 8.0) * 0.0015;            // even subtler
```

### 2. Icosahedron Interior (`sdIcosahedronEdge`)
- Full 12-vertex icosahedron implementation
- Checks all 30 edges (adjacency threshold 1.18 for unit sphere verts)
- Edge glow: `smoothstep(0.06, 0.0, edgeDist) * 0.85`
- Slow rotation: 78s base speed, 28s in thinking state (0.08 vs 0.22 rad/s)
- Tilted 23.5 degrees from vertical (like Earth) for visual variety
- Gold accent on 4 key vertices (`#c8a84a`)
- Micro-particle cloud (12 particles, 0.006-0.010 sz, slow drift)
- Thinking: lighthouse scan beam rotating inside

### 3. Single Key Light Studio
```glsl
vec3 keyDir = normalize(vec3(-0.8, 1.4, 0.6));  // spec exact
float keyLobe = pow(max(0.0, dot(dir, keyDir)), 8.0); // soft softbox, not 18
```
Key: near-white 3.5 intensity. Fill: cool blue 0.15 intensity. Rim: state-color 0.4.

### 4. Real Glass Fresnel
```glsl
float f0 = 0.04;  // real glass value (not IOR-derived)
float fresnel = f0 + (1.0 - f0) * pow(1.0 - NdotV, 5.0);
// Center: 4% reflection, 96% transmission
// Edge: ~100% reflection = mirror silhouette = glass "money shot"
```

### 5. Chromatic Dispersion IOR (N-BK7 optical glass)
```glsl
float iorR = 1.5110;  // red: least bent
float iorG = 1.5168;  // green: reference
float iorB = 1.5220;  // blue: most bent = blue fringe at edges
```

### 6. Beer's Law Absorption
```glsl
vec3 absorption = exp(-vec3(0.08, 0.04, 0.02) * thickness);
// Red absorbed most, blue least = natural glass blue tint at depth
```

### 7. Post-Processing Improvements
- Bloom threshold: 0.85 (was 0.45 - was blooming everything)
- Two-pass: wide at 0.15 intensity, sparkle at 0.35 only for lum > 1.2
- Gamma: 0.91 (was 0.86 - preserves shadow drama)
- Vignette: `smoothstep(0.50, 1.05, length(uv)*1.05)` wider/softer
- Film grain: 0.003 (was 0.009), only on bright regions
- Chromatic aberration: screen-space at silhouette, 0.008 strength
- Caustic projection behind sphere: simulated focusing on background

### 8. Camera
- 45-second orbit (2*PI/45.0 rad/s)
- Sine drift: `camAngle += sin(t*0.07)*0.06` for non-mechanical path
- Distance 2.6 (closer than 2.85) so sphere fills 55-60% canvas
- Target y=0.06 (sphere offset slightly upward, 47% from top)
- Sphere micro-drift: 3-axis snoise * 0.015

### 9. State Colors (Exact Spec Values)
- Idle: #2a93c1 interior, #5bb8d4 rim, #1a4d7a tint
- Speaking: #f1420b interior, #ff7a3d hot core, #e8621a rim, #6b2200 tint
- Thinking: #7b4fc9 interior, #9b6fe0 scan beam, #5a2a9a rim, #2a0a5a tint

## Mobile Shader
- Simplified icosahedron: 6 key vertices only (no 30-edge check)
- No exit march for refraction (single-channel)
- 40 steps max, mediump float
- Same key light, same Fresnel f0=0.04, same state colors
- Same post-processing values (0.91 gamma, 0.85 bloom, wider vignette)

## File Changed
`/home/jared/projects/AI-CIV/aether/exports/avatar-fluid.html`

## Server
`https://89.167.19.20:8765` via `tools/avatar_chat_server.py`
Restart: `pkill -f avatar_chat_server.py && source venv/bin/activate && nohup python3 tools/avatar_chat_server.py >> logs/avatar_chat_server.log 2>&1 &`

## GLSL Gotchas for Future Reference
- WebGL GLSL doesn't allow variable-length loop bounds (constants only)
- `for (int i = 0; i < 12; i++)` is fine, must be compile-time constant
- Array declarations in GLSL: `vec3 v[12]; v[0] = ...; v[1] = ...;` (no initializer list in WebGL 1.0)
- Cannot break/continue nested loops efficiently - use `minD = min(minD, ...)` pattern
- mediump float is 16-bit: avoid large values, precision loss shows in normals
- `snoise()` uses many temporaries - can hit mediump register limit on some mobile GPUs

## Visual Impact Order (from spec Part 10)
Did all phases:
1. Removals (liquid, particles, rays, core glow, extra lights) - biggest impact
2. Pure sphere + micro-only noise
3. Real f0=0.04 Fresnel + Beer's law absorption
4. Icosahedral interior geometry
5. Screen-space chromatic aberration
6. Post-processing tuning (bloom 0.85, gamma 0.91, grain 0.003)
