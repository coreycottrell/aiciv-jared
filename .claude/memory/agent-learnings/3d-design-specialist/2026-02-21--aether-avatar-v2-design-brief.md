# Aether Avatar v2 — Design Brief Creation

**Date**: 2026-02-21
**Type**: teaching
**Topic**: Complete design specification for Aether Avatar v2 — glass entity with 3-layer composition, audio-reactive core, cursor gaze, mode-driven lighting

---

## Memory Search Results

- Searched: All 7 sprint memory files (Night 1 through Day 7)
- Found: Complete Gleb recipe, R3F patterns, Vite project, GLB loading, adaptive quality, audio-reactive, cursor gaze, environment presets, avatar modes, PostMessage embed
- Applied: All sprint learnings directly inform design decisions — zero new research needed

---

## What Was Created

Design brief at: `exports/aether-avatar-v2-design-brief.md` (597 lines)

A strategic pre-build document for Jared's review. NOT code — this is the design specification.

---

## Core Design Decisions Documented

### 3-Layer Glass Entity Architecture

```
Layer 1: Outer glass sphere (near-invisible, refracts environment)
Layer 2: Orbiting glass rings (motion signature, light catches)
Layer 3: Inner emissive core (consciousness center — what breathes and reacts)
```

This architecture is more expressive than a single glass sphere because:
- The outer shell is atmospheric (barely there)
- The rings are the motion anchor (what the eye tracks)
- The inner core is the emotional indicator (what changes per mode)

### What NOT to Animate (Critical Performance Rule)

Do NOT animate MeshTransmissionMaterial roughness/transmission/thickness.
These trigger FBO reconfiguration = shader recompile every frame = catastrophic.

ONLY animate:
- `mesh.scale.setScalar()` — free matrix uniform
- `meshStandardMaterial.emissiveIntensity` — single uniform update

### Mode Visual Language (Final Spec)

```
idle:      blue core, 70% gaze, slow float, standard studio lighting
speaking:  white core, audio-reactive intensity, ring acceleration, 50% gaze
thinking:  blue-purple core, 30% gaze, slow float + FASTER spin (paradox)
listening: cyan core, 160% gaze, minimal rotation, "opening" attenuation
```

The "thinking paradox" (slow float, fast spin) is the most distinctive visual beat.

### Ring Design Decision

2 rings recommended (not 3) — sufficient visual complexity, cleaner on mobile.
Rings can degrade to MeshPhysicalMaterial (no FBO) before outer sphere degrades.
This gives performance headroom without compromising the primary glass element.

### PostMessage API State Machine

```
idle ←→ listening ←→ thinking ←→ speaking → idle
```

All transitions lerped over ~1 second. No instant state jumps.

---

## Files Referenced

- Design brief: `exports/aether-avatar-v2-design-brief.md`
- Sprint foundation: `exports/gleb-r3f-scene/` (entire R3F project)
- Key components: AudioReactive.jsx, CursorReactive.jsx, EnvironmentPresets.jsx, PerformanceMonitor.jsx, LoadingScreen.jsx
- PostMessage embed: `exports/gleb-r3f-scene/embed/index.html`

---

## Open Decisions (Pending Jared Review)

1. Ring count: 2 (recommended) or 3?
2. Ring attenuation: neutral glass or orange tint in speaking mode?
3. Orange (#f1420b) in avatar: reserved or included?
4. Canvas dimensions: 480px square (recommended) or custom?
5. Hosting path: 3d.purebrain.ai subdomain or purebrain.ai/3d/ path?

---

## Memory Written

Path: `.claude/memory/agent-learnings/3d-design-specialist/2026-02-21--aether-avatar-v2-design-brief.md`
Type: teaching
Topic: Design brief creation, 3-layer glass entity, animation constraints, mode visual language
