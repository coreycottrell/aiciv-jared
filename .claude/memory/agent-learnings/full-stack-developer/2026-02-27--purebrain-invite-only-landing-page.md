# PureBrain Invite-Only Landing Page Build

**Date**: 2026-02-27
**Type**: operational
**Topic**: Self-contained invite landing page with Three.js neural network fullscreen background

## What Was Built

`/home/jared/projects/AI-CIV/aether/exports/purebrain-invite-only.html` — 1,786 lines, 70KB

Complete self-contained invite-only landing page for purebrain.ai featuring:
- Fullscreen Three.js neural network brain (extracted from purebrain-frontend-3d.html lines 13862-14461)
- Glassmorphism content sections scrolling over 3D background
- Live countdown timer to 2026-03-05T04:59:59Z (March 4 EOD Eastern)
- 25 spots indicator with filled/empty dot visualization
- 4-tier pricing section (Awakened $79, Bonded $149 RECOMMENDED, Partnered $499, Unified $999)
- Michael Hancock testimonial
- Page load stagger animation (850ms brain fade → content in)
- Intersection Observer scroll reveals

## Z-Index Architecture

- `#pb-canvas-container`: position fixed, inset 0, z-index 0 — THREE.js canvas always behind
- `#pb-vignette`: position fixed, inset 0, z-index 1, pointer-events none — radial gradient darkening
- `#pb-page`: position relative, z-index 2 — scrollable content over brain

## Three.js Extraction Pattern

Source file: `docs/from-telegram/purebrain-frontend-3d.html`
- Importmap block: lines 2269-2277
- Canvas div: `<div id="pb-canvas-container">` at line 2991
- Three.js module script: lines 13862-14461 (removed login overlay pause/resume logic)
- Key change: Removed `checkLoginVisibility()` function and login-state gating — brain always runs

## Key Adaptations from Original

1. **Removed login-overlay gating** — original paused brain when `loginOverlay.classList.contains('hidden')`. New version always renders.
2. **Removed tap exclusion zone** — original excluded clicks on `.pb-login-card`. New version fires bursts everywhere.
3. **Adjusted ambient fire timing** — maxDelay 400ms → 500ms for slightly calmer ambient on landing page

## File Paths

- Output: `/home/jared/projects/AI-CIV/aether/exports/purebrain-invite-only.html`
- Source: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/purebrain-frontend-3d.html`
- Drive folder: 1QaBu0gO7__my-AziZ2WD_PAuhkfLjQoN (purebrain.ai HTML files)

## All CTA Links

All 6 CTA buttons → `https://purebrain.ai/pay-test-2/?bypass=invited`
