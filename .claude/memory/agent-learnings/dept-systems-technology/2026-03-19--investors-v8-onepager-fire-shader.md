# Investors V8 One-Pager: Fire Shader Build

Date: 2026-03-19
Type: operational | technique

## What Was Built

Output: exports/cf-pages-deploy/investors-v8-onepager/index.html
Source: exports/cf-pages-deploy/investors-v8/index.html
Lines: 1021 (vs 2902 in source — 65% reduction)

## One-Pager Architecture
- Single scrolling page (no section nav, no GSAP ScrollTrigger)
- CSS grid layout: 2-column main-grid, full-width rows for tables/team
- Glassmorphism cards (backdrop-filter blur 24px)
- All investor content: Hero+Stats, Problem/Solution, Differentiator, Why Now, Business Model, Market, Revenue Table, The Raise, Returns, Team, CTA

## WebGL Fire Shader Architecture
- Raw WebGL (no Three.js needed for fullscreen quad shader)
- Vertex: passthrough quad -1 to 1
- Fragment:
  - 5-octave FBM (fractal Brownian motion) for base turbulence
  - 2-pass domain warping (q then r then final f) for organic shape
  - 3 fire columns (0.35, 0.5, 0.65 x positions) blended with Gaussian width
  - firePalette: #080a12 → deep crimson → #f1420b → amber/gold → hot white
  - 18 procedural ember sparks (hash-based position, phase, speed)
  - Diffuse ember glow (lower 40%)
  - Heat shimmer lines (sin-based, fire-masked)
  - Atmospheric smoke (fbm upper region, blue-dark tint)
  - Tone map: col / (col + 0.85) + gamma 0.88
- Scroll reactivity: intensity uniform increases 0.18 per scroll event, decays 0.006/frame
- Vignette: radial-gradient overlay div above canvas

## Password Gate
Same passwords as v8: pureinvestor2026, pt2026, puretech, puretechnology
?open=1 bypass + sessionStorage('pt_investor_auth')

## Deployment
Project: purebrain-staging
URL: https://purebrain-staging.pages.dev/investors-v8-onepager/
Deploy hash: c504edbb

## Key Lesson
Raw WebGL (no Three.js) is perfectly adequate for fullscreen fragment shaders.
Avoids importmap complexity and loads faster. Use FS pattern: fullscreen quad
with TRIANGLE_STRIP(4 verts), all work in fragment shader.
