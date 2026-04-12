# Memory: Portal Login Neural Network Background

**Date**: 2026-02-24
**Type**: teaching
**Agent**: full-stack-developer
**Topic**: Replacing mesh gradient + particle system with canvas neural network visualization

## Task

Swap the purebrain-portal-login background (animated mesh gradient CSS + floating particle canvas + orb div) with a pure JS canvas neural network effect. Zero text/content changes.

## What Was Replaced

**Before** (3 separate bg elements):
- `.pb-bg` div — CSS `::before`/`::after` mesh gradient with `meshDrift` keyframes
- `#pb-particles` canvas — simple floating particle system (55 particles)
- `.pb-orb-wrap` div — large 420px glowing orb with glass highlight + neural lines

**After** (single element):
- `#pb-neural-canvas` — full-background canvas with full JS neural network system

## Neural Network Architecture

### 3-Layer Depth System
- Layer 0 (back): 50 nodes, radius ~1.0px, opacity 0.18, slow drift
- Layer 1 (mid): 45 nodes, radius ~1.6px, opacity 0.32, medium drift
- Layer 2 (front): 35 nodes, radius ~2.4px, opacity 0.55, faster drift

Total: ~130 nodes. Well within 100-150 target range for 60fps.

### Color Distribution
- 55% dim-white `(200,210,230)` — forms the ambient neural mass
- 27% blue `(42,147,193)` — PureBrain brand blue
- 18% orange `(241,66,11)` — PureBrain brand orange

### Connections (Synaptic Lines)
- Pre-computed edge list on init and every 90 frames
- Max connection distance: 180px (scales well on all screen sizes)
- Max 4 connections per node (performance cap)
- Line opacity fades with distance; boosted slightly when adjacent nodes fire
- Color inherits from the colored node in the pair (falls back to blue/orange)

### Signal Pulses (18 concurrent)
- Each pulse travels along a pre-computed edge from one node to another
- Position interpolated 0→1 along edge with `Math.sin(t * PI)` fade in/out at endpoints
- Speed randomized ±50% around base speed for organic feel
- Bright core dot (radius 2.2px) + soft radial glow (3.5x radius)
- On reaching end of edge: immediately respawned on a new random edge

### Neuron Firing
- Each frame: 0.06% chance per node to fire (`fireChance: 0.0006`)
- Fire sets `n.fire = 1.0`, decays at 0.04/frame (~25 frames = ~0.4s burst)
- Visual effect: node opacity multiplied by `firePeak` (3.0x), halo radius expands 3x
- Edges connected to firing nodes get extra opacity

### Background
- Solid `#0a0a0a` fill (replaces mesh gradient)
- Two ambient radial glows: blue upper-left, orange lower-right
- Central pulsing radial glow (replaces orb presence, sine-animated)

## Performance Patterns

### Edge Rebuild Cadence
Edges are rebuilt every 90 frames, not every frame. Nodes drift slowly so stale edges are acceptable for 1.5s. Full rebuild is O(n²) but with n=130 and layer adjacency filtering, it completes fast.

### No Heap Allocations in Hot Path
- `drawBackground()`, `drawEdges()`, `drawPulses()`, `drawNodes()` all use indexed loops
- Pulse respawn creates a new object but only 18 pulses means ~1/18 chance per frame = rare
- No Array methods (forEach, map) in the animation loop

### visibilitychange
Added `document.addEventListener('visibilitychange', ...)` to pause rAF when tab hides.

### prefers-reduced-motion
Static single frame rendered (background + edges + nodes), no animation loop started.

## File Locations

- Source: `docs/from-telegram/purebrain-portal-login - updated.html`
- Output: `exports/purebrain-portal-login-neural.html`

## Critical Constraint: Zero Text Changes

ALL of these were preserved verbatim:
- `id="loginOverlay"`, `id="loginAicivName"`, `id="loginSecret"`, `id="loginButton"`, `id="loginError"`
- `function handleLogin()` interface
- All visible text strings: headlines, subtext, button labels, footer tagline
- All CSS classes on card/form/footer elements

The ONLY structural changes:
1. Removed `.pb-bg` div, `#pb-particles` canvas, `.pb-orb-wrap` div from HTML
2. Added `<canvas id="pb-neural-canvas">` in their place
3. Replaced all background-related CSS sections with `#pb-neural-canvas` positioning CSS
4. Replaced particle JS with neural network JS

## Verification Commands

```bash
# All IDs present
for id in loginOverlay loginAicivName loginSecret loginButton loginError; do
  grep -q "id=\"$id\"" file.html && echo "FOUND $id" || echo "MISSING $id"
done

# Old bg elements absent
grep -c "pb-bg\|pb-orb-wrap\|pb-particles\|meshDrift\|orbFloat" file.html

# New canvas present
grep "pb-neural-canvas" file.html
```
