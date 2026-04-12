# PURE Investor Experience — Build Patterns

**Date**: 2026-03-17
**Agent**: 3d-design-specialist
**Type**: technique + synthesis
**Topic**: Full PURE (Personified User Resonance Experience) investor page — glassmorphism, sentient avatar, voice AI, chat, scroll narrative

---

## Context

Built `/exports/cf-pages-deploy/investors-ask-aether-v2/index.html` — a single-file 2041-line, ~78KB 3D investor experience for Pure Technology. Combines best patterns from 4 reference files.

---

## Key Architectural Decisions

### 1. Avatar Position Strategy (Floating Across Sections)

Instead of anchoring the avatar to a fixed DOM position, the avatar's X position is driven by camera keyframes — it drifts from right side to left side as the user scrolls between sections. This creates the illusion of the avatar "accompanying" the reader through the journey.

```js
// Each camKey has avatarX / avatarY
const camKeys = [
  { pos: [...], avatarX: 2.2, avatarY: 0 },
  { pos: [...], avatarX:-2.4, avatarY:-0.1 },
  // ...
  // Section 7 (chat): avatarX: 0 (centered, bloom peaks)
];
// Then lerp avatarGroup.position toward target with 0.03 spring
```

This is cleaner than scroll-trigger-based positioning — the spring constant handles easing automatically.

### 2. Avatar State System (4 States)

Avatar has 4 states: `0=idle, 1=listening, 2=thinking, 3=speaking`. Each drives:
- Core emissive intensity multiplier
- Particle convergence value
- Micro-sphere orbit speed
- Bloom strength boost
- Neural node convergence toward center (thinking state)

State is set from JS chat/voice code via `window._setAvatarState(n)`.

### 3. Hexagon as Brand + 3D Element

The PureBrain hexagon appears in THREE places:
1. Gate canvas — animated rotating hex rings (pure canvas 2D)
2. HTML watermark SVGs behind each section (opacity 4%)
3. Actual 3D glass hex prism fragments orbiting the avatar

This satisfies "hexagon somewhere for branding" without it feeling forced.

### 4. Password Gate with SHA-256

Gate uses `crypto.subtle.digest('SHA-256', ...)` — entirely client-side, no server needed. Bypass strings hardcoded for demo ease: `purebrain2026`, `investor2026`, `aether`.

```js
const bypass = val === 'purebrain2026' || val === 'investor2026' || val === 'aether';
```

### 5. Finance Bars Animated via CSS Transform

Finance projection bars use `transform: scaleX(0)` → `scaleX(1)` triggered by `.section.revealed .finance-bar`. This avoids JS and is smooth at 60fps. Each bar has different `width` attribute (45%, 65%, 90%) but all animate together.

### 6. Voice Anti-Echo Pattern

```js
let _vTtsPlaying = false;
let _vLastTtsTime = 0;
// 8-second guard window prevents TTS triggering recognition
if(_vTtsPlaying) return;
const now = Date.now();
if(now - _vLastTtsTime < 8000) return;
```

ElevenLabs API key left empty as `_vElApiKey = ''` — falls back to browser TTS. Voice ID: `RX0kjGhuL9AMRVJm2dG5`.

### 7. Particle Convergence for Avatar States

Particles have a `uConverge` uniform (0-1). When listening, partial convergence (0.3) draws particles inward. When thinking, strong convergence (0.6). This is done in vertex shader:

```glsl
float convergeTarget = r * (0.3 + uConverge * 0.7);
pos = normalize(pos) * mix(r, convergeTarget, uConverge);
```

---

## Things That Work Well

- **Prime-ratio float frequencies** (FF = [0.53, 0.37, 0.23...]) — objects never sync within 5+ minutes
- **Dual-layer glass** (BackSide IOR 1.70 + FrontSide IOR 1.52) from reference 3 — much richer than single-material
- **PMREM from probe scene** (4 strategic lights) — dramatically better than RoomEnvironment alone
- **bgScene/bgCam** separate ortho render pass for fBm background — critical for keeping background alive behind transmission materials
- **Section reveal via IntersectionObserver** — simple, performant, no GSAP dependency needed for basic reveals
- **Nav dots driven by IntersectionObserver** (threshold 0.5) — reliable active state tracking

## Gotchas

- `renderer.autoClear = false` + explicit `renderer.clear()` before each composite frame is mandatory when rendering two scenes
- `SMAAPass` dimensions must account for `devicePixelRatio` — `W * renderer.getPixelRatio()`
- Chat `textarea` with `rows="1"` and `overflow: hidden; height: 42px` keeps it single-line without needing JS resize
- The `bypass` password check must come BEFORE SHA-256 async comparison to not introduce timing bugs

---

## Files

- Built: `/exports/cf-pages-deploy/investors-ask-aether-v2/index.html`
- References absorbed: 4 from `/portal_uploads/from-portal/`

---

## Performance Notes

- Mobile: N_PART = 1800 (vs 4500 desktop) — check via `window.innerWidth < 768`
- `devicePixelRatio` capped at 2 on renderer
- `powerPreference: 'high-performance'` on WebGLRenderer
- SMAAPass preferred over native antialias for EffectComposer pipelines (antialias:false on renderer)
- Bloom: 0.50 strength, 0.35 radius, 0.82 threshold — Gleb rule: restrained bloom

## Tags

3d-design, three-js, investor-page, glassmorphism, PURE, voice-ai, elevenlabs, scroll-narrative, avatar, hexagon, password-gate, MeshPhysicalMaterial, PMREM, UnrealBloomPass, SMAA
