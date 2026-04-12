# Portal Welcome Hero — 3D WebGL Neural Network

**Date**: 2026-03-16
**Type**: teaching
**Agent**: full-stack-developer

## What Was Done

Replaced the 2D canvas neural network in the portal welcome hero (`#panel-chat` background)
with the full 3D Three.js WebGL neural network from `portal_20260316_220004_purebrain-frontend-3dwloginv7.html`.

## Key Architecture

### Problem: ES modules + dynamic DOM creation
The `renderWelcomeHero()` function runs in a normal `<script>` tag (non-module).
Three.js requires `import` statements which only work in `<script type="module">`.
A module cannot directly call non-module functions synchronously before DOMContentLoaded.

### Solution: Deferred bridge pattern
1. `startAetherCanvas(container)` in non-module code does:
   - If `window.__startWelcome3D` is defined → call it immediately
   - Else → store container in `window.__welcome3DQueue`
2. The module script at bottom of `<body>` defines `window.__startWelcome3D = initWelcome3D`
3. Module also checks `window.__welcome3DQueue` at startup and processes any queued call

### DOM Layout Change
Old: `.welcome-hero` was `position:absolute; top:50%; left:50%; transform:translate(-50%,-50%)`
     containing a 600×600 `<canvas>` with 2D neural net

New: `.welcome-hero` is `position:absolute; inset:0` (fills entire panel)
     - `#welcome-3d-container` inside: `position:absolute; inset:0` receives WebGL renderer
     - `.welcome-hero__labels` wrapper: `position:relative; z-index:1` for text above 3D canvas

### Renderer Configuration
- Alpha: true, clearColor: #080a0f (portal --bg), clearAlpha: 0.92
- EffectComposer with UnrealBloomPass
- Slightly lower node counts than login version (220 vs 280 desktop) to share GPU budget
- Cleanup triggered when `#welcomeHero` is removed from DOM (no leak)

## Files Changed
- `/home/jared/purebrain_portal/portal-pb-styled.html`
  - CSS lines ~1981-2048: welcome hero styles rewritten
  - JS lines ~8825-8887: `renderWelcomeHero()` creates div container instead of canvas
  - JS lines ~8880-8887: `startAetherCanvas()` replaced with bridge stub
  - Old 2D code renamed to `_startAetherCanvas_2D_REMOVED` (dead code, kept for reference)
  - New `<script type="module">` block at end (~lines 16280-16792): full 3D implementation

## Patterns Learned
- Module/non-module bridge via `window.__startWelcome3D` + queue pattern works well
- When Three.js 3D fills a panel (not full-screen), use `container.offsetWidth/Height`
  with fallback to `panel-chat` element size
- `alpha: true` on renderer + semi-transparent clearColor lets panel dark bg show subtly
- The cleanup function must cancel rAF AND remove event listeners to prevent memory leaks
- `scheduleAmbientFire` must check `document.getElementById('welcomeHero')` to self-terminate
