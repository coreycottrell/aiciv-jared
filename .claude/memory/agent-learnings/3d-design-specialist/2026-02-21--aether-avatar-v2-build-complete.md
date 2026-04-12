# Aether Avatar v2 — Build Complete

**Date**: 2026-02-21
**Type**: teaching
**Topic**: Full production build of Aether Avatar v2 — standalone HTML + R3F components. Jared's 5 decisions applied.

---

## Memory Search Results

- Searched: All 8 prior sprint files (Night 1 through Day 7 + design-brief + proof-single-file)
- Found: Complete architecture — all parameters used directly, zero rediscovery
- Applied: 100% of sprint learnings, both standalone HTML and R3F Vite project

---

## What Was Built

### Deliverable 1: Standalone HTML (primary shareable)

**Path**: `exports/aether-avatar-v2.html`
**Size**: 1470 lines, ~50KB, zero build step
**Tech**: Three.js v0.161.0 CDN + vanilla JS

**All 5 Jared decisions implemented**:
1. 3 rings (not 2) — ring configs in `RING_CONFIGS` array
2. Ring color: orange in speaking, glass blue in idle/thinking/listening — `MODES[mode].ringColor`
3. Orange spark particles: `OrangeSparkParticles` class — 120 particles close-in orbit, `sparkMat.opacity` lerps 0→0.75 in speaking
4. 480px square canvas — `CANVAS_SIZE = 480`, camera aspect ratio 1:1
5. PostMessage API ready — `SET_MODE`, `PING`/`PONG` wired, `ALLOWED_ORIGINS` configured

**Key architecture decisions**:
- Demo auto-cycle: modes cycle every 5s starting at 3s delay (stops on user interaction)
- 9 audio bars (vs 7 in proof): center 3 are orange class
- Double loading ring (outer blue + inner orange counter-rotating) — more premium than single
- All mode transitions lerped at 0.045/frame (≈1s at 60fps)

### Deliverable 2: R3F Components (Vite project)

**New files**:
- `src/AetherCore.jsx` — Inner emissive core + haze + orange spark particles
- `src/AetherRings.jsx` — 3-ring orbital system with mode-adaptive color/opacity/speed
- `src/AetherAvatarV2.jsx` — Main component, wires all layers + audio + cursor

**Modified files**:
- `src/Scene.jsx` — Added `import { AetherAvatarV2 }`, added `avatar-v2` displayMode
- `src/App.jsx` — Added `avatar-v2` to DISPLAY_MODES array, defaulted to it, fixed isAvatarMode check

**Build result**: Clean — 0 errors, 0 warnings
```
dist/assets/index-Dhoxmxv2.js    47.23 kB │ gzip:  13.60 kB  (+6.4KB from 3 new components)
dist/assets/three-CaGg4_Cu.js   724.99 kB │ gzip: 187.66 kB  (unchanged)
dist/assets/r3f-BRxq3son.js     493.21 kB │ gzip: 155.67 kB  (unchanged)
Total: ~389 kB gzip
Build time: 16.59s
```

---

## Architecture Decisions Validated

### Ring Color Strategy (Jared decision #2)

Ring color is stored as a THREE.Color ref and lerped per frame:
```javascript
const smoothColor = useRef(PB_BLUE.clone())
// In useFrame:
smoothColor.current.lerp(RING_MODE_COLORS[avatarMode], 0.045)
ring.material.color.copy(smoothColor.current)
ring.material.emissive.copy(smoothColor.current)
```

This gives smooth 1-second transitions between ring colors when mode switches.

### Orange Spark Particles Architecture

```javascript
// Particles start invisible, lerp to 0.75 opacity in speaking mode
sparkMat.opacity = lerp(sparkMat.opacity, cfg.sparkActive ? 0.75 : 0.0, 0.08)

// Per-particle orbit animation
for (let i = 0; i < SPARK_COUNT; i++) {
  sparkAngles[i] += sparkSpeeds[i] * sparkSpeedMult
  posAttr.setXYZ(i, cos * radius, elevation + vertOsc, sin * radius)
}
posAttr.needsUpdate = true
```

Key: `sparkSpeedMult` = 1.0 in speaking, 0.4 in other modes (particles slow down but don't disappear when switching modes — makes transition smoother).

### Demo Auto-Cycle Pattern

```javascript
const DEMO_MODES = ['idle', 'listening', 'thinking', 'speaking']
// Cycles every 5s starting after 3s initial delay
// Stops on any user interaction (button click, key press, mode row click)
// Useful for demos where Jared shows the avatar to someone without clicking
```

### 480px Square Canvas + Centered Layout

```html
<div id="wrap"> <!-- fixed full-screen, flex center -->
  <div id="canvas-wrap"> <!-- 480x480, z-index 1 -->
    <canvas id="gl-canvas"></canvas>
  </div>
</div>
```

Camera aspect ratio: 1:1 (square). Camera FOV: 42 degrees (slightly tighter than the 45 in the sprint project, compensates for the square viewport).

---

## What Makes v2 Different from Proof File

| Feature | Proof (v1) | Avatar v2 |
|---------|-----------|-----------|
| Ring count | 4 (including orange ring always) | 3 (with mode-adaptive color) |
| Orange sparks | None | 120 particles, speaking-only |
| Canvas | Full-screen | 480px square, centered |
| Loading screen | Single ring | Dual counter-rotating rings |
| Audio bars | 7 bars | 9 bars (center 3 orange) |
| Demo cycle | None | Auto-cycles modes for demos |
| Ring color | Fixed (blue/gold/white/orange) | Mode-adaptive (blue ↔ orange lerp) |

---

## Gotchas (new in this build)

**Gotcha 1: Square canvas aspect ratio**
Camera needs `aspect: 1` for 480x480. React Three Fiber handles this automatically
from the Canvas size, but vanilla Three.js `PerspectiveCamera(45, w/h, 0.1, 100)`
needs `aspect: 1` explicitly for a square canvas.

**Gotcha 2: postMessage `'null'` origin for file:// protocol**
Already known from Day 7, reapplied here. Must check:
```javascript
if (origin === 'null') return true  // file:// development
```

**Gotcha 3: posAttr.needsUpdate = true is mandatory for particle systems**
If you forget `needsUpdate = true` after updating BufferAttribute XYZ, particles freeze.
Every particle update loop must end with this.

**Gotcha 4: Demo cycle stops working after page visibility change**
If user tabs away, clock.getDelta() returns a large value on return.
Cap dt: `const dt = Math.min(clock.getDelta(), 0.05)` — prevents spiral of death.
(Applied in the animate loop.)

---

## Files Created/Modified

**Created**:
- `exports/aether-avatar-v2.html` (1470 lines, standalone)
- `exports/gleb-r3f-scene/src/AetherCore.jsx` (inner core + sparks)
- `exports/gleb-r3f-scene/src/AetherRings.jsx` (3-ring system)
- `exports/gleb-r3f-scene/src/AetherAvatarV2.jsx` (main component)
- This memory file

**Modified**:
- `exports/gleb-r3f-scene/src/Scene.jsx` (added avatar-v2 import + display mode)
- `exports/gleb-r3f-scene/src/App.jsx` (added to DISPLAY_MODES, defaulted to avatar-v2)

---

## Memory Written

Path: `.claude/memory/agent-learnings/3d-design-specialist/2026-02-21--aether-avatar-v2-build-complete.md`
Type: teaching
Topic: Production build of Aether Avatar v2 — all 5 Jared decisions applied, standalone + R3F
