# investors-v8: Fluid Core Avatar — Iframe Final Fix
**Date**: 2026-03-19
**Type**: teaching + operational

## Root Cause of All Previous Failures

Multiple WebGL contexts on a single page conflict. The investors-v8 page already runs a
full Navier-Stokes simulation on #liquid-canvas (the background). A second Navier-Stokes
instance on #fluidCanvas (avatar) causes GPU context exhaustion or silent black rendering.
No amount of timing fixes (window.load, requestAnimationFrame, DOMContentLoaded) resolves
a fundamental GPU resource conflict — only isolation does.

## The Working Solution: iframe + 100vmin

Approach: Isolate the avatar WebGL context completely in an iframe pointing to /fluid-core.

### investors-v8/index.html changes:
1. Removed entire FLUID-CORE AVATAR CSS block (~87 lines)
   — ::before/::after ring pseudo-elements, fluidRingRotate keyframes, .fluid-container,
     #fluidCanvas, .avatar-sigil, sigilPulse, state classes all deleted
2. Replaced avatar inner HTML with clean iframe:
     <iframe id="fluid-core-iframe" src="/fluid-core"
       style="position:absolute;inset:0;width:100%;height:100%;border:none;pointer-events:auto;"
       allow="autoplay" loading="eager" scrolling="no"></iframe>
3. Removed the avatar Navier-Stokes script block (~1600 chars minified JS)
4. Kept #aether-avatar-wrap CSS but: removed ring pseudo-elements, added overflow:hidden

### fluid-core/index.html changes:
1. Added ?size=N URL param support (DOMContentLoaded sets avatar-wrapper inline size)
2. Changed .avatar-wrapper from width:200px;height:200px to width:100vmin;height:100vmin
   — makes the avatar FILL the iframe viewport regardless of iframe dimensions
3. Added overflow:hidden to body — prevents scrollbars in the iframe

## Key Insight: 100vmin

100vmin = 100% of the smaller viewport dimension. In a square iframe (280x280 or 200x200),
vmin == vw == vh, so the avatar always fills the iframe exactly. No dark borders, no clipping.
The ring, fluid, Ae sigil, glass overlay — all render correctly at any size.

## Critical Anti-Pattern: CSS ::before/::after on parent of iframe

If you put ring pseudo-elements on the PARENT div that contains the iframe, you get TWO
rings — one from the parent CSS and one from inside the iframe. Remove ALL pseudo-elements
from the parent. Let the ring come from inside the iframe only.

## File Locations
- exports/cf-pages-deploy/investors-v8/index.html
- exports/cf-pages-deploy/fluid-core/index.html

## Verification
- Deploy: 2 files uploaded to purebrain-staging CF Pages
- Deployment: https://c2f0a599.purebrain-staging.pages.dev
- Live check: https://purebrain.ai/investors-v8/?open=1

## Pattern: When Multiple WebGL Contexts Conflict
Use an iframe. It is the only reliable fix. The iframe gets its own renderer process
with isolated GPU contexts. No CSS trick, timing hack, or shared canvas workaround
will fix GPU resource exhaustion on the same page.
