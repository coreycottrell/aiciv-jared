# Investor Page Rebuild — CSS Hex Grid + GSAP Depth + Three.js Orb

**Date**: 2026-03-17
**Type**: teaching
**Topic**: WebGL shader failures — CSS/SVG hex background as bulletproof alternative

## What Worked

### Background: CSS SVG hex grid (NOT WebGL fragment shaders)
- Previous v4 attempt used a `ShaderMaterial` for the background hex grid — silently failed/black screen
- Solution: CSS `background-image` with inline SVG `data:` URL hex pattern + `background-size` tiling
- Zero compilation issues. Works on all browsers. Always visible.
- Added `animation: hexShift` to slowly drift the grid for a "living" feel
- Layered radial gradient overlays (`.hex-glow`) for the orange/blue liquid metal feel
- Dynamic orange streak elements via JS DOM injection (no WebGL needed)

### Depth animations: GSAP ScrollTrigger with translateZ
- `perspective: 1400px` on `.content-section` containers enables 3D depth
- Cards start at `translateZ(-600px) scale(0.55) blur(14px)` → animate to `translateZ(0) scale(1) blur(0)`
- Exit: cards sink to `translateZ(-400px) scale(0.7) blur(16px)` as user scrolls past
- Key GSAP pattern: `gsap.fromTo(card, {z:-600, ...}, {z:0, ..., scrollTrigger:{scrub:1.2}})`
- Exit in separate `gsap.to()` with different trigger start/end values

### Three.js avatar: small contained canvas (NOT fullscreen)
- `<canvas id="avatar-canvas" width="280" height="280">` inside `.final-inner`
- `renderer.setSize(280, 280)` — NOT `window.innerWidth/Height`
- `renderer.setClearColor(0x000000, 0)` with `alpha:true` for transparent bg
- Orbit buttons positioned absolutely around the canvas wrap div
- Breathing animation: `sphere.scale.setScalar(1 + 0.02*Math.sin(t*1.5))`

### Password gate
- Codes: `['pureinvestor2026','pt2026','puretech','puretechnology']`
- Gate dissolves with CSS transition + `visibility:hidden` on `.dissolved` class
- `initPage()` called after dissolve — deferred initialization pattern prevents GSAP from running before gate unlock

## File Location
`/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors/index.html`

## Deploy Command
`CLOUDFLARE_API_TOKEN=$(grep CF_PAGES_TOKEN .env | cut -d= -f2) npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain-staging --commit-dirty=true`

## Key Lesson
When WebGL background shaders fail silently → CSS SVG tiled background-image is the bulletproof replacement. Combine with layered radial gradient divs + CSS animations for a premium "liquid metal" feel without any GPU shader compilation risk.
