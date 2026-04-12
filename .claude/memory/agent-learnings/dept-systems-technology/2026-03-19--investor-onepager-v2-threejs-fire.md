# Investor One-Pager v2 — Three.js Fire + Bloom Build

**Date**: 2026-03-19
**Task**: Upgrade investors-onepager from GLSL WebGL fire shader to Three.js particle system with UnrealBloom
**Type**: operational + teaching

## What Was Built
- **File**: `exports/cf-pages-deploy/investors-onepager/index.html` (48KB, 622 lines)
- **Live URL**: https://purebrain-staging.pages.dev/investors-onepager/
- **Bypass URL**: https://purebrain-staging.pages.dev/investors-onepager/?open=1
- **Password**: purebrain2026 (also: pureinvestor2026, pt2026, puretech, puretechnology)

## Three.js Architecture
- **10,000 fire particles** — BufferGeometry with custom ShaderMaterial, AdditiveBlending
- **2,500 ember particles** — faster, more erratic, brighter glow
- **UnrealBloomPass** — strength 1.6, radius 0.5, threshold 0.08 (scroll-reactive)
- **5 glass orbs** — MeshPhysicalMaterial with transmission/thickness
- **3 volumetric light shafts** — CylinderGeometry, BackSide, AdditiveBlending
- **Grid floor** — GridHelper, sinks as user scrolls
- **3 PointLights** — flickering fire light (sin-based intensity variation)
- **ACESFilmicToneMapping** — toneMappingExposure 1.1

## Fire Particle Color Ramp
- t < 0.15: white-hot (1.0, 1.0, 0.85)
- t < 0.35: bright yellow-orange (1.0, 0.75, 0.15)
- t < 0.55: orange (1.0, 0.35, 0.04)
- t < 0.75: red-orange (0.85, 0.12, 0.01)
- t >= 0.75: dying ember (0.25, 0.02, 0.005)

## Key Patterns
- Fire particles spawn from y=-18 (bottom of viewport), wide spread x±16
- Turbulence: sin/cos applied per particle with unique phase offsets
- Scroll interactivity: bloom.strength and camera.y tied to scrollProgress
- Mouse parallax: camera.position.x/y lerped toward mouse position
- importmap + type="module" for Three.js ES module loading
- Particle system uses Float32Arrays for perf — no object allocation per frame

## Previous Version
- v1: GLSL fragment shader WebGL fire (flat, procedural noise) — 87KB
- v2: Three.js 3D particle system + bloom post-processing — 48KB (more efficient)

## Content Sourced From
- Fetched live from https://purebrain.ai/investors-v8/?open=1
- All stats, financials, team, divisions present

## Deploy
- Target: purebrain-staging
- Command: CLOUDFLARE_API_TOKEN=$(grep CF_PAGES_TOKEN .env | cut -d= -f2) npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain-staging --commit-dirty=true
- Verified: HTTP 200 on both gated and ?open=1 URL
