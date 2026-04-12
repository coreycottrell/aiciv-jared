# Logo Deconstruction: String Art Hexagon → 3D Animatable Pieces

**Date**: 2026-03-20
**Agent**: 3d-design-specialist
**Type**: technique
**Confidence**: high
**Tags**: three-js, logo-deconstruction, string-art, hexagon, animation, decomposition, parametric

---

## Context

Task: Take the actual Pure Technology PNG icon (nested hexagonal spiral) and deconstruct it into individual geometric pieces that can be scattered in 3D space and animated back together — creating a cinematic assembly reveal.

The problem with v1: it used generic hexagons. v2 uses the REAL logo geometry recreated mathematically.

---

## What the PT Logo Actually Is

The Pure Technology icon is a **string art hexagon** — a classic parametric line art technique:

**Structure:**
1. **Border rings**: ~4 tightly spaced concentric hexagon outlines at the outer edge (creates the "frame" or border look)
2. **Interior rings**: ~5 more hexagon outlines radiating inward, getting progressively more orange
3. **String art blade fans**: The spiral vortex effect is created by 6 fan groups of parallel lines, one per hex side
4. **Void circle**: A solid black circle at the center, ~7-8% of outer hex radius

**How the string art vortex works:**
- For each of the 6 hex sides, take N evenly-spaced points along that side
- Each point on the outer side connects to a point on the **next inner hex** — but twisted
- The twist angle: inner hex is rotated by some amount relative to outer
- The endpoints are REVERSED: outer point at position `u` connects to inner point at `1-u`
- This reversal creates the "fan" / diagonal effect
- Stacking many levels with increasing twist creates the logarithmic spiral appearance

**Why it looks like a spiral (not just fans):**
Each consecutive ring level has a slightly larger twist angle. The outer blades connect nearly horizontally (small twist). The inner blades sweep dramatically (large twist). This progressive twist is what creates the vortex illusion.

**Color system:**
Linear interpolation from `#2a93c1` (outer blue) to `#f1420b` (inner orange) based on normalized radius position.

---

## Decomposition into Animatable Pieces

**15 pieces total:**
- 9 hexagon ring Line loops (4 border + 5 vortex interior)
- 6 blade fan LineSegments groups (one per hex side — the 6 sectors of the vortex)
- 1 void CircleGeometry disc

**Why 6 blade fans?**
The vortex naturally divides into 6 sectors (one per hex side). Each fan covers its sector's blades from outer edge to inner void. These 6 fans can scatter separately like "petals" and fly back together during assembly.

---

## Key Mathematical Parameters (tuned to match image)

```javascript
const BORDER_RINGS = 4;           // tight cluster at outer edge
const BORDER_SPACING = 0.027;     // normalized spacing between border rings
const VORTEX_RINGS = 5;           // interior rings
const VOID_R = 0.078;             // void radius as fraction of outer radius
const BLADES_PER_LEVEL = 38;      // line count per side per level
const TOTAL_SPIRAL_RADIANS = Math.PI * (5.0/3.0); // ~300° total vortex sweep
```

**Ring radius distribution:**
- Border rings cluster at outer edge (1.0, 0.972, 0.944, 0.916)
- Interior rings use logarithmic compression toward center
- Power curve `1.0 - pow(1.0 - t, 1.8)` matches the visual density

**Twist angle per level:**
- Border levels: small twist `PI/3 * 0.15` (short diagonal lines in border area)
- Vortex levels: `PI/3 + vortexFrac * TOTAL_SPIRAL_RADIANS / VORTEX_RINGS`

**Blade fan algorithm (per side):**
```javascript
// Outer endpoints on side S at position u
const ox = outerA.x + (outerB.x - outerA.x) * u;
// Inner endpoints at position (1-u) — REVERSAL creates the fan
const ix = innerA.x + (innerB.x - innerA.x) * (1-u);
```

---

## Three.js Implementation Notes

**Hex ring loops**: `THREE.Line` with `THREE.BufferGeometry` (7 points: 6 vertices + close)

**Blade fans**: `THREE.LineSegments` with `vertexColors: true` — color per vertex for smooth gradient

**Void disc**: `THREE.CircleGeometry` with `renderOrder: 5` (renders on top of lines)

**Hex orientation**: Pointy-top hexagon (vertex at top/bottom), achieved via `Math.PI/6` rotation offset

**Z-depth**: `Z_STEP = 0.010` per ring gives subtle 3D depth that catches light from camera angle

**Postprocessing stack** (Three.js ESM r0.161.0):
1. `RenderPass`
2. `UnrealBloomPass` (strength 0.4, radius 0.55, threshold 0.80)
3. Custom `ShaderPass` (chromatic aberration + vignette + flash)
4. `OutputPass` (MUST be last)

---

## Animation Architecture (GSAP Timeline)

**Phase 0** (0–1.2s): Fade in all pieces at scatter positions (opacity 0 → 0.6)

**Phase 1** (1.2s): Ring assembly, outermost first, 0.20s stagger
- Fly to (0,0,0), exit tumble rotation → flat
- Scale punch: 1.6x → 1.0x with back.out(2.4) easing
- Each snap triggers bloom spike (1.3 strength, 0.05s, then decay)

**Phase 2** (2.7s): Blade fan assembly, 0.13s stagger per fan

**Phase 3**: Void disc arrives last

**Final Snap**: Mega bloom (3.2), white flash, chromatic spike (6.5), orange glow ignites, camera pulls back

**Hold state**: Gentle z-rotation + breathing wobble + mouse parallax + breathing bloom

---

## Side-by-Side Comparison Feature

The file includes a 2D canvas recreation of the logo using the same math, drawn with the HTML Canvas 2D API. Clicking "Compare" overlays this against the original PNG loaded from the portal uploads path.

This lets Jared verify the mathematical recreation matches the original before watching the 3D animation.

The Canvas 2D version runs the exact same algorithm as the Three.js version — same parameters, same math — just using `ctx.lineTo()` instead of `THREE.BufferGeometry`.

---

## Gotchas

1. **Ring radius overlap bug**: When `OUTER_BORDER_RINGS` rings are calculated and interior rings start at the same radius, you get duplicate rings at the same position. Fix: interior rings use `(i - OUTER_BORDER_RINGS + 1) / (NUM_RINGS - OUTER_BORDER_RINGS)` (offset by 1) so the first interior ring starts INSIDE the last border ring.

2. **Hex orientation**: The logo image uses pointy-top hexagon orientation. Apply `Math.PI/6` extra rotation to all hexagon vertex calculations.

3. **GSAP synchronous load**: GSAP `<script src>` MUST come before `<script type="module">`. If you use async/defer, `window.gsap` is undefined when the module runs.

4. **`fromTo` for scale punch**: Use `TL.fromTo(group.scale, {x:1.6,y:1.6,z:1.6}, {x:1.0,...})` — do NOT use `TL.to()` for the "from" state, as GSAP won't track it correctly from within a timeline.

5. **LineSegments vs Line**: For blade fans (pairs of vertices), use `LineSegments`. For closed hexagon loops, use `Line` with the last vertex duplicating the first.

6. **Scatter pz negative**: Set starting z to `-4.8` (behind the camera at z=5.5) so pieces fly TOWARD the viewer during assembly. This is more cinematic than pieces flying in from the sides.

---

## This as a Service Pattern

This skill — logo deconstruction — can be applied to any geometric logo:
1. Analyze what geometric primitives compose the logo (rings, lines, triangles, arcs)
2. Determine if it's string art, parametric curves, or pure geometry
3. Build each identified piece as an independent Three.js object
4. Scatter + animate back together with GSAP

**Works best for**: Logos that are geometric / constructive (built from mathematical shapes)
**Harder for**: Organic logos with freeform paths (would need SVG conversion step)
**For SVG logos**: Load SVG, extract `<path>` elements, extrude each path with `THREE.ExtrudeGeometry`, animate the extruded pieces

---

## File Reference

- Build: `/home/jared/projects/AI-CIV/aether/exports/puretechnology-3d-redesign/logo-animation-v2.html`
- CF Deploy: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/puretechnology-3d-redesign/logo-animation-v2.html`
- Live URL: `https://7913f6a5.purebrain-staging.pages.dev/puretechnology-3d-redesign/logo-animation-v2.html`
- Original logo: `/home/jared/portal_uploads/from-portal/portal_20260320_231816_MA1.BI-1.2.4-002-211107-Icon-PT.png`
