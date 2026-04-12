# Investor One-Pager 3D Build — 2026-03-19

**Type**: operational + teaching
**Task**: Build password-gated investor one-pager with Three.js 3D fire/nebula background

## What Was Built

- **File**: `exports/cf-pages-deploy/investors-onepager-3d/index.html`
- **Live URL**: https://purebrain-staging.pages.dev/investors-onepager-3d/
- **Bypass URL**: https://purebrain-staging.pages.dev/investors-onepager-3d/?open=1

## Passwords

- Primary: `purebrain2026`
- Fallbacks: `pureinvestor2026`, `pt2026`, `puretech`, `puretechnology`
- Session storage key: `pt_investor_v2_auth`

## 3D Architecture (Three.js 0.160.1 from CDN)

1. Particle vortex: 5,000 pts (2,200 mobile), fire/plasma color palette
2. Icosahedra: 12 glass wireframe crystals, float+rotate animations
3. Neural lines: BufferGeometry LineSegments connecting sampled particles within distance threshold
4. Glow orbs: 4 SphereGeometry meshes with AdditiveBlending pulse
5. Camera drift: Slow sin/cos orbit for parallax feel
6. Scroll reactivity: scrollIntensity multiplies animation speed

## Deploy

- Deploy target: purebrain-staging (not purebrain)
- CF_PAGES_TOKEN is Pages-only — no zone access for cache flush — new deployment ID auto-invalidates

## Prior Art

- investors-v8-onepager/index.html — older GLSL fire shader, flat 2D WebGL
- Jared wanted "more fire 3D crazy" — Three.js scene is significantly more spectacular
