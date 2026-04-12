# Portal Light Mode: Particle Network Background Injection

**Date**: 2026-03-20
**Type**: operational
**Topic**: Replaced gradient orbs + hex grid with Particle Network variant in portal light mode canvas

## What Was Done

Replaced the existing light mode background IIFE in `/home/jared/purebrain_portal/portal-pb-styled.html` with the Particle Network variant from the approved prototype.

**Source**: `/home/jared/purebrain_portal/light-mode-bg-prototype.html` — Variant 1 (Particle Network)
**Target script block**: Lines ~17527+ in portal-pb-styled.html

## Architecture of the New Animation

Two-layer system on `#pb-light-canvas`:

**Layer 1 — Ambient Gradient Orbs** (kept from prototype, not the old portal orbs):
- 5 orbs: 2 blue, 2 orange, 1 lavender
- Very low opacity (0.03-0.055), slow sinusoidal drift
- Sit beneath the particle layer as a color wash

**Layer 2 — Particle Network**:
- Particle count: min(floor(W*H / 14000), 90) — density-capped
- Colors: 70% LAVENDER (100,120,210), 22% BLUE (#2a93c1), 8% ORANGE (#f1420b)
- Connection lines between particles within min(W,H) * 0.22 px
- Line alpha: (1 - dist/linkDist) * 0.07 — very subtle
- Each particle has independent oBase, oPhase, oSpeed for breathing opacity

## What Was Preserved (Lifecycle Wrappers)
- MutationObserver on body.classList — starts/stops on .light-mode toggle
- visibilitychange listener — pauses when tab is hidden
- resize handler with debounce
- start() / stop() lifecycle functions
- Initial check for body.classList.contains('light-mode') on page load

## What Was Removed
- Old orbs array (7 orbs using color: [r,g,b] format)
- buildDotPattern() — offscreen canvas hex grid
- dotCanvas / dotCtx offscreen canvas machinery

## Key Technical Notes
- The edit was done with Python str.replace() since file is 17,699 lines (too large for Edit tool)
- Old portal had _dpr capped at 1.5 — new code caps at 2.0 (matches prototype)
- t0 timing: uses elapsed = now - t0 (resets on start/resume)
- initNetwork() called on every resize — particles re-seeded when window resizes

## Portal Restart
- Portal runs via python3 portal_server.py on port 8097
- Verified via curl localhost:8097/ — Particle Network, initNetwork, drawNetwork all present

## Files Changed
- /home/jared/purebrain_portal/portal-pb-styled.html — light mode animation script block replaced
