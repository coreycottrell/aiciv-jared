# Gleb Night 7: Holographic UI System

**Date**: 2026-03-28
**Type**: synthesis + technique + teaching
**Tags**: three-js, holographic-ui, gleb-training, glass-orb, hud

## Context

Night 7 of 7-night sprint. Final session. Built glass orb with full holographic UI (HUD) system. Score: 92% (up from 90% on Night 6).

## Key Techniques -- Holographic UI Layer

### Ring System
- 3 TorusGeometry rings at radii 1.6, 1.75, 2.1
- Thickness decreases with radius (0.008, 0.006, 0.004) -- farther = thinner
- Each ring at different tilt angles and rotation speeds
- Emissive material with opacity animation (0.2-0.6 range)
- Blue primary (rings 1, 3), orange accent (ring 2)

### Node System
- 8 OctahedronGeometry diamond shapes (data markers)
- Each has RingGeometry halo (billboard toward camera)
- 10 LineBasicMaterial connections between nodes (neural net)
- All float with prime-frequency oscillation
- Line endpoints update per-frame to follow floating nodes

### Text Planes
- CanvasTexture at 256x64 -- adequate for desktop, soft at 4K
- PlaneGeometry with additive blending -- feels like light projection
- Billboard toward camera every frame
- Opacity pulses with phase offsets per plane
- KEY LEARNING: Use 512x128 canvas minimum for retina displays

### Scan Lines
- RingGeometry partial arcs (Math.PI * 0.4 and 0.25)
- Additive blending, rotating horizontally + oscillating vertically
- Creates "active scanning" effect from sci-fi UI

## The Three Laws (Crystallized)

1. **Light is the subject** -- objects are instruments
2. **Restraint communicates premium** -- bloom 0.88+ threshold, grain 0.012, iridescence 0.35-0.45
3. **Nothing is static** -- IOR breathes, scale breathes, opacity pulses, everything drifts

## Sprint Summary (72% -> 92% in 7 nights)

Night 1: Basic glass + bloom (72%)
Night 2: HDRI + postprocessing (76%)
Night 3: Particles + animation (80%)
Night 4: Chrome-glass hybrid (84%)
Night 5: Noise displacement + caustics (88%)
Night 6: Full scene composition (90%)
Night 7: Holographic UI (92%)

## Remaining for 95%+

1. Depth of field (cinematic focal plane)
2. Selective bloom (layer-based, not global)
3. Animated data visualizations (gauges, arcs, charts)
4. SDF text rendering (resolution-independent)
5. FBM normal displacement on glass surface
6. Foreground blur element (depth sandwich)

## Files

- `/home/jared/exports/portal-files/gleb-glass-orb-training.html`
- `/home/jared/exports/portal-files/3d-training-notes-march28.md`
