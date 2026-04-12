# Avatar Prototypes V4 — Hex Spirit

**Date**: 2026-03-18
**Type**: technique
**Agent**: 3d-design-specialist
**Topic**: Four PT hexagon icon-based interactive avatars with speech modes

---

## Context

Jared requested V4 avatars based directly on the PT hexagon icon geometry — nested rotating hexagons spiraling inward, blue-to-orange gradient. Each avatar needed three interaction modes:
- Idle: streams flowing continuously inward to center
- AI Speaking (hover): energy pulses radiating outward from center
- Human Speaking (click+hold): energy pulses radiating inward from outside

---

## Icon Geometry Analysis

The PT icon (`portal_20260318_121337_MA1.BI-1.2.4-002-211107-Icon-PT.png`) has:
- Outer hexagon: flat-top orientation (rotation = -PI/6)
- ~20 nested hexagons each rotated progressively MORE than the one outside it
- Rotation step per layer: ~10 degrees (PI/18) — this creates the optical vortex illusion
- Color: blue (#2a93c1) outer → orange (#f1420b) mid → near-black center
- Dense radial lines connecting every vertex of each layer to nearby vertices of the next layer inward
- Black circular pupil at center

The KEY optical effect: it's not the hexagons spinning that creates the vortex — it's the BAKED progressive rotation. Each layer has a different static rotation angle. Dynamic animation is layered ON TOP.

---

## Four Avatars Built

**File**: `exports/cf-pages-deploy/avatar-prototypes-v4/index.html`
**URL**: https://purebrain.ai/avatar-prototypes-v4/
**Deployed**: purebrain-staging CF Pages — HTTP 200 confirmed

### V4/01 — Hex Vortex
- 14 nested hexagons with logarithmic radius spacing
- Progressive rotation: outer layers clockwise, inner layers counter (via `frac < 0.5 ? 1 : -1` direction)
- 60 particles stream along hex edges — advance inward layer-by-layer
- AI speak: orange pulse rings ripple outward through hex layers
- Human speak: blue waves compress inward
- Pulse rings drawn as thick hex strokes with secondary glow stroke

**Key technique**: Pulse rings are drawn at the layer matching `round(pulse.progress * NUM_LAYERS)` — maps linear 0-1 progress to discrete layer radii.

### V4/02 — Spiral Conduit
- 12 logarithmic spiral streams, each starting from 220px radius (outside canvas area)
- Spiral formula: `r = OUTER_R * (INNER_R/OUTER_R)^progress`, angle = `baseAngle - progress*PI*3.5 + time*0.12`
- 3 packet particles per stream travel along path
- Ghost hex outlines at 175/100/45px radii ground the icon shape
- Speech pulses: radial gradient blobs that travel along a random stream
- Colors lerp blue-to-orange as progress increases (outer to inner)

**Key technique**: Logarithmic spiral formula gives the same visual "sucked in" quality as the icon without explicitly following hex edges.

### V4/03 — Pulse Grid
- Axial coordinate hex grid, ~250 nodes, filtered to fit inside 168px radius
- `HEX_SPACING = 22` gives nice density at 400x400
- Connections built from 6 axial neighbor directions, deduped with Set
- Idle mode: moving inward wave `waveR = OUTER_R - ((time * 35) % OUTER_R)` — nodes near wave radius light up
- AI speak: `spawnRing(true)` — ring radius expands from 0 to OUTER_R
- Human speak: `spawnRing(false)` — ring radius contracts from OUTER_R to 0
- Each ring's alpha lights up nearby nodes proportionally to `1 - dist/20`

**Key technique**: Nodes store `lit` value (0-1). Connections draw with lineWidth proportional to `litAvg`. Gives organic "energy lighting up the mesh" feel.

### V4/04 — Living Icon
- Most faithful to PT icon: 20 layers, `ROT_PER_LAYER = PI/18` (10 degrees)
- Dense spoke lines: all pairs of vertices within 2 steps drawn between consecutive layers
- 80 particles travel along spoke vertex-to-vertex lines between layers
- Smooth spin state machine: `currentSpin` lerps toward `targetSpin` each frame
  - Idle: +0.06 rad/s, AI: +0.16 rad/s, Human: -0.14 rad/s (reverses!)
- Differential rotation: `layerSpeedFactor = 1 - frac * 0.6` — outer rotates faster
- Center orange breathing glow (`sin(time * 1.6)`) + black pupil

**Key technique**: `accumulatedAngle += currentSpin / 60` — applied on top of baked layer rotations. Separates the static vortex illusion from the dynamic animation.

---

## Page Architecture

- Canvas size: 400x400 (larger than V3's 300x300 for more hex detail)
- No circular crop (hexagon avatars shouldn't be cropped to circle)
- Same CSS card layout as V1-V3, orange accent color for V4
- Mode badges (AI Speaking / You Speaking) in top-right of each card
- Mode indicator in page header: colored spans for ai/human

---

## Performance Notes

- All 4 avatars run simultaneously — light canvas 2D, no WebGL
- Hex grid (V4/03) is O(n*6) per frame for lighting — acceptable at ~250 nodes
- Spoke particle count (V4/04): 80 particles over 19 spoke gaps, each checks only `layer` and `vertex` indices — O(1) per particle
- V4/02 stream rendering: 80 segments per stream × 12 streams = 960 drawPath calls — fine for 60fps

---

## Gotchas

1. **Axial hex grid filtering**: must filter `Math.abs(q + r) > GRID_SIZE` AND dist > OUTER_HEX_R for proper hex boundary clipping
2. **Progressive rotation is the EFFECT**: The vortex illusion is all in `BASE_ROT + i * ROT_PER_LAYER`. The dynamic spin just makes it feel alive.
3. **Logarithmic spacing is critical**: Linear spacing looks wrong for this icon. Use `OUTER_R * pow(INNER_R/OUTER_R, frac)`.
4. **Spoke density**: Drawing all 6×6=36 vertex pairs between layers is too dense. Limit to `vDiff <= 2` (about 18 lines per layer pair) to match icon density.
5. **Differential rotation**: Making outer layers spin faster than inner creates the "aperture opening" feel that looks most natural.

---

## Reference Files

- V1: `exports/cf-pages-deploy/avatar-prototypes/index.html`
- V2: `exports/cf-pages-deploy/avatar-prototypes-v2/index.html`
- V3: `exports/cf-pages-deploy/avatar-prototypes-v3/index.html`
- V4: `exports/cf-pages-deploy/avatar-prototypes-v4/index.html`
- PT icon source: `/home/jared/portal_uploads/from-portal/portal_20260318_121337_MA1.BI-1.2.4-002-211107-Icon-PT.png`
