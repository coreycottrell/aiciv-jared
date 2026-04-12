# Memory: PURE Investor Experience v3 — Liquid Metal Avatar Final Build

**Date**: 2026-03-17
**Agent**: 3d-design-specialist
**Type**: technique + synthesis
**Topic**: Full PURE v3 investor page — liquid metal shader, Aether avatar, scroll-driven card emergence, IOR animation, particle aura
**Confidence**: high
**Tags**: three-js, investor-page, liquid-metal, avatar, glass, PURE, scroll-narrative, r0.161.0, purebrain, SMAA, bloom, particle-aura

---

## Memory Search Results

- Searched: prior 3d-design-specialist memories for "investor", "liquid metal", "avatar", "scroll"
- Found: `2026-03-17--investor-pure-experience-build.md` (v2 patterns), `2026-03-16--aether-avatar-investor-poc.md`, `2026-03-09--liquid-glass-scroll-narrative-day3.md`, `2026-03-17--gleb-training-session-overnight.md`
- Applied: All of the above. v3 incorporates v2 patterns + overnight training techniques.

---

## Context

Jared feedback on v2: "way too busy - hard to even read words in some places"
v3 brief: "single avatar... ethereal... liquid metal moving background... content emerges via scroll... sinks beneath liquid metal as next area appears... AETHEREAL - AETHER IS REAL... breathtaking"

Built and deployed: `/exports/cf-pages-deploy/investors-ask-aether-v3/index.html`
Deployed to: `https://de078faf.purebrain-staging.pages.dev/investors-ask-aether-v3/`
File size: 62KB, 1704 lines

---

## Architecture Summary

### Three.js Scene Architecture (same as v2, refined)

```
bgScene (ortho) → renderer.render() → not postprocessed
  └── Atmospheric gradient quad

mainScene → EffectComposer → Bloom + SMAA + OutputPass
  ├── Liquid metal surface (PlaneGeometry 26x26, 200 subdivisions)
  ├── Glow pool (billboard plane, AdditiveBlending)
  └── avatarGroup (everything follows this)
       ├── Outer shell (IcosahedronGeometry detail 5, transmission, iridescence)
       ├── Inner back-shell (higher IOR 1.72, BackSide)
       ├── Mid glass sphere (roughness 0.12, semi-frosted)
       ├── Emissive core (breathes with prime frequencies)
       ├── Halo (BackSide BasicMaterial, very low opacity)
       ├── Eye glows x2 (blink at sin(t * 3.1) > 0.988)
       ├── 10 orbiting hex prisms (fragmented brand elements)
       ├── Particle aura (1600 points, ShaderMaterial, AdditiveBlending)
       └── Avatar point light (drives glass illumination)
```

### Key Improvements Over v2

1. **Multi-layer glass avatar** (5 layers total):
   - Outer shell (DoubleSide, IOR 1.52 animated, iridescence 0.48)
   - Inner BackSide shell (IOR 1.72 — stronger refraction depth)
   - Mid glass (roughness 0.12 — frosted quality contrast)
   - Emissive core (breathes)
   - Halo (BackSide, 6% opacity — bloom suggestion)

2. **IOR animation** ("breathing refraction" — identified in overnight session):
   ```javascript
   shellMat.ior = 1.42 + 0.14 * Math.sin(t * 2.1 * FF[3]);
   ```
   Zero performance cost. The glass literally breathes in how it bends light.

3. **Particle aura** (NEW):
   1600 points in a radius band 0.95-1.80 around the avatar.
   ShaderMaterial with aSize/aPhase attributes.
   Gentle breathing motion per-particle via sin(uTime + aPhase).
   AdditiveBlending — brightens what's behind without opaque coverage.
   Makes the avatar feel like it has an energy field around it.

4. **Enhanced liquid metal fragment shader**:
   Added 4th cool fill light for depth.
   Added shimmer effect (sin(worldPos.x * 3.8 + uTime * 1.1) * sin(z) * 0.04)
   — looks like caustic light through water. Very subtle, very premium.
   Color scheme: deep blue-black base, warm white key, PureBrain blue fill, orange rim.

5. **Scroll hint show delay**:
   "Scroll to explore" hint appears 2s after hero reveal via CSS transition.
   Not there on load (gate is up) — appears naturally after gate dissolves.

---

## Gotchas Hit / Avoided

### Avoided: Outer IcosahedronGeometry needs detail >= 4 for smooth transmission
Using detail 5 (2562 vertices). At detail 3 (642 verts) the glass facets show.
RULE: detail >= 4 for any IcosahedronGeometry that will receive transmission.

### Avoided: aura ShaderMaterial needs depthWrite: false
Points at distance could clip against the glass shell.
AdditiveBlending + depthWrite: false = they always add light, never cut geometry.

### Avoided: metal surface normal calculation
The finite-difference normal calc in vertex shader ONLY uses the primary fBm layer
(not ripples/details). This is intentional — ripple normals are too chaotic and
create specular noise. The primary wave normal is clean chrome-like.

### New gotcha found: camera.position.clone() for uniform initial value
```javascript
uCamPos: { value: camera.position.clone() }
// NOT: uCamPos: { value: camera.position }
```
If you pass camera.position directly (not cloned), the uniform IS camera.position —
updates automatically, which is what you want in animate() with .copy().
But the INITIAL value would be (0,0,0) before camera is positioned.
Use .clone() for initial value to capture starting position.
Then in animate(): metalUniforms.uCamPos.value.copy(camera.position)

### Verified: dissolveGate() defined after triggerRipple() — both hoisted in same module scope
ES module `function` declarations are hoisted within the module. No closure issues.

---

## Content Sections (Investor Flow)

1. **HERO** — "Meet Aether, Your AI Co-CEO" — full viewport, avatar center stage
2. **VISION** — PURE model explanation (Personified User Resonance Experience)
3. **OPPORTUNITY** — $52B market, 4-stat grid (blue gradient numbers)
4. **PRODUCT** — 4 feature cards with dot indicators
5. **RAISE** — $750K seed, 4 raise blocks (orange), fund allocation bars
6. **ASK AETHER** — Chat interface, avatar responds with state changes

### Password bypass codes (dev/demo):
- `purebrain2026`, `investor2026`, `aether`, `pure2026`, `aethereal`

---

## Performance Profile

- Metal surface: PlaneGeometry 26x26, 200 subdivisions = 200x200 = 40K quads
  Mobile: 80 subdivisions = 6400 quads
- Avatar: 5 mesh objects + 10 frags + 1600 particle points
- Postprocessing: EffectComposer → RenderPass → UnrealBloomPass → SMAAPass → OutputPass
- Bloom: 0.42 strength, 0.32 radius, 0.82 threshold (conservative)
- Target: 60fps desktop, 30fps+ mobile

---

## Scroll Ripple Map

| Section | Ripple Position | Meaning |
|---------|----------------|---------|
| 1 Vision | (-4.2, 1.8) | Content rises from left-back |
| 2 Opportunity | (4.2, -1.6) | Content rises from right-front |
| 3 Product | (0, 0) | Center emergence |
| 4 Raise | (-4.0, -1.2) | Left-front emergence |
| 5 Chat | (0, 2.2) | Center-back emergence |

---

## CSS Scroll Transition Pattern

Cards use three states:
- Default: `opacity: 0; transform: translateY(90px) scale(0.965)`
- `.emerged`: `opacity: 1; transform: translateY(0) scale(1)` — emerges from below
- `.sinking`: `opacity: 0; transform: translateY(-56px) scale(0.965)` — sinks upward

"Sinking" is applied when card.getBoundingClientRect().bottom < 0 (scrolled past viewport top).
This creates the "sinking back into the metal" effect as content passes.

Emerge transition: `cubic-bezier(0.16,1,0.3,1)` — spring easing
Sink transition: `cubic-bezier(0.4,0,0.6,1)` — fast ease-in for snappy disappearance

---

## Files

- `/exports/cf-pages-deploy/investors-ask-aether-v3/index.html` — 62KB, 1704 lines, self-contained
- Deployed to CF Pages staging: `https://de078faf.purebrain-staging.pages.dev/investors-ask-aether-v3/`
