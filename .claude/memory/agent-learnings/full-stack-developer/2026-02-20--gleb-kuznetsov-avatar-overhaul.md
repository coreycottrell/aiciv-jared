# Gleb Kuznetsov / Milkinside Avatar Overhaul - Phase 3

**Date**: 2026-02-20
**Type**: technique
**Topic**: Complete rewrite applying ui-ux-designer's Gleb forensic analysis - multi-light colored environment, volumetric glow, gold specular, no surface noise

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/full-stack-developer/` for "avatar", "glass", "WebGL"
- Found: `2026-02-19--webgl-glass-shader-overhaul.md` and `2026-02-20--premium-glass-sphere-avatar.md`
- Found: `ui-ux-designer/2026-02-20--gleb-kuznetsov-sphere-visual-analysis.md` (forensic guide)
- Applied: All 7 changes from the ui-ux-designer's priority list

---

## What Changed (vs Phase 2)

### Removed
1. **Icosahedron wireframe** - replaced with volumetric glow (`interiorLight()`)
2. **Single studio key light** - replaced with 6-light colored environment
3. **Ice-white specular** `vec3(0.910, 0.953, 1.0)` - replaced with gold `#C8A84A`
4. **FBM surface noise** (`scratch`, `fingerprint`) - removed entirely, zero noise
5. **Micro-particle cloud** - removed (was "WebGL demo" signal)
6. **Scanning beam geometry** - replaced with soft volumetric energy plane
7. **45-second obvious orbit** - replaced with 90-second near-imperceptible orbit

### Added
1. **6-light colored studio environment** (`studioEnv()` with L1-L8)
   - L1: Warm white key (upper left, exponent 6)
   - L2: Electric blue #0D16F5 fill (upper right, exponent 4)
   - L3: Violet #5a0e8a ambient (lower front, exponent 2) - state-shifts to red when speaking
   - L4: Magenta #D10DCE accent (right lower, exponent 10) - shifts to red #E42424 when speaking
   - L5: Cyan #18A8D3 rim (back right, exponent 12) - shifts to electric blue when thinking
   - L6: Red #E42424 hot zone (bottom back, exponent 5) - intensifies when speaking
   - L7: Hot orange-white flood (speaking state only)
   - L8: Cool blue (thinking state only)

2. **Volumetric interior glow** (`interiorLight()`)
   - Core emitter: `exp(-dist/0.22) * 0.85` - concentrated center
   - Orbiting secondary: `exp(-dist²/0.05) * 0.45` - 12-second orbit
   - Corona band: tilted 23.5° (Earth axial tilt), slow pulse
   - Speaking: hot white/orange eruption with audio-reactive rings
   - Thinking: soft rotating volumetric scan plane (not geometry)

3. **Gold specular** `vec3(0.784, 0.659, 0.290)` = `#C8A84A`
   - Tight: shininess 480, intensity 5.5
   - Soft halo: shininess 40, warm near-white `(0.88, 0.80, 0.78)`
   - Speaking: shifts toward hotter gold `#FFB830`

4. **Gleb background treatment**
   - Base: `#020204` equivalent (blue-black void, NOT pure black)
   - Light bleed: electric blue upper-right, magenta lower-right, cyan around sphere
   - State bleed: orange atmospheric glow when speaking, blue when thinking

5. **Post-processing tuning**
   - Bloom threshold: 0.80 (was 0.85) - selective, not aggressive
   - Gamma: 0.90 (was 0.91) - richer shadows
   - Vignette: starts at 0.45 (was 0.50) - wider frame
   - Grain: 0.0012 max, ONLY in pure black areas (was 0.003 in midtones)

---

## The "Light vs Object" Principle (from ui-ux-designer)

The key insight: Gleb renders LIGHT, not OBJECTS.
- Wrong: Glass sphere containing geometric interior (icosahedron, particles)
- Right: Glass sphere as LENS for colored light environment

The icosahedron showed "a thing inside a ball" = toy
The volumetric glow shows "a ball of pure light" = artwork

---

## Gleb Color Palette (from forensic analysis)

| Color | Hex | Use |
|-------|-----|-----|
| `#020204` | Background void | Near-black with blue tint |
| `#3C0E4E` | Deep violet | Idle secondary emitter |
| `#0D16F5` | Electric blue | Light 2, thinking dominant |
| `#E42424` | Saturated red | Light 6, speaking accent |
| `#D10DCE` | Magenta | Light 4, idle accent |
| `#18A8D3` | Cyan | Light 5, rim |
| `#C8A84A` | Gold | SPECULAR HIGHLIGHT (mandatory) |

---

## File Changed

`/home/jared/projects/AI-CIV/aether/exports/avatar-fluid.html`

## Server

`https://89.167.19.20:8765` via `tools/avatar_chat_server.py`
Restart: `pkill -f avatar_chat_server.py && source venv/bin/activate && nohup python3 tools/avatar_chat_server.py >> logs/avatar_chat_server.log 2>&1 &`

---

## GLSL Notes for Future Reference

- `snoise()` renamed `mod289v3`/`mod289v4` functions to avoid collision between desktop/mobile (no namespace in GLSL)
- State-dependent environment lights: mix colors inside `studioEnv()` based on sMix/tMix uniforms
- `interiorLight()` takes exitP (point inside sphere at glass exit) as input
- Mobile shader: 4-light environment (skip L5-L6 magenta/red for budget), single-channel refraction, simplified `interiorLight` inline

## Verification

- Server running at `https://89.167.19.20:8765`
- `curl -sk https://89.167.19.20:8765/ | grep "goldSpec"` returns `vec3(0.784, 0.659, 0.290)` ✓
- `curl -sk https://89.167.19.20:8765/ | grep "icosahedron"` returns only comment "Replaces icosahedron completely." ✓
- `curl -sk https://89.167.19.20:8765/ | grep "0D16F5"` returns electric blue light ✓
- `curl -sk https://89.167.19.20:8765/ | grep "scratch"` returns only the "NO surface noise" comment ✓
