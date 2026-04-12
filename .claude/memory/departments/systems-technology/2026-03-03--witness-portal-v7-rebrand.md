# Witness Portal v7 Rebrand

**Date**: 2026-03-03
**Type**: pattern
**Topic**: Applying v7 PureBrain branding to Witness portal

## Task
Rebrand witness portal (portal-pb-styled.html, 37KB) to exactly match PureBrain 3D Login v7 (890KB).

## Key Extractions from v7 Reference

### Fonts
- Heading: `'Oswald'` (Google Fonts, weights 400-700)
- Body: `'Plus Jakarta Sans'` (Google Fonts, weights 300-700)
- Mono: `'JetBrains Mono'` (Google Fonts)

### Color Palette
- `--bright-orange: #f1420b`
- `--orange: #ed6626`
- `--light-blue: #2a93c1`
- `--dark-blue: #3a60ab`
- `--black: #0a0a0a` / `--bg-deep: #080a12`
- Card bg: `rgba(20, 20, 20, 0.97)` or for login overlay: `rgba(10, 10, 10, 0.82)`

### PureBrain Wordmark (CRITICAL)
```html
<span class="pb-pure">PUREBR</span><span class="pb-brain">AI</span><span class="pb-brain-n">N</span><span class="pb-ai">.ai</span>
```
- `pb-pure`: `#2a93c1` (blue)
- `pb-brain`: `#f1420b` (orange)
- `pb-brain-n`: `#2a93c1` (blue)
- `pb-ai`: `rgba(255,255,255,0.6)` (white/transparent)

### Login Card
- Glassmorphism: `backdrop-filter: blur(32px) saturate(1.6)`
- Card bg: `rgba(10, 10, 10, 0.82)`
- Border: `rgba(255, 255, 255, 0.09)`
- Multi-shadow: orange + blue glow combo
- Top edge gradient bar: orange → blue → transparent
- Entry animation: `pbCardMaterialize` (translateY 24px + scale 0.97)

### Auth Button
- Gradient: `linear-gradient(105deg, #f1420b 0%, #ed6626 30%, #2a93c1 70%, #3a60ab 100%)`
- Shimmer effect via `::after` pseudo-element
- `font-family: Oswald`, uppercase, letter-spacing

### Footer
- Glow bar: orange → blue gradient horizontal line
- Inner bg: blue/orange radial gradient
- Pulsing glow animation
- Tagline: Oswald font, gradient text (orange → blue), drop-shadow filter

### 3D Neural Background
- Three.js 0.161.0 via CDN importmap
- ES module: `import * as THREE from 'three'`
- `EffectComposer` + `UnrealBloomPass` + `OutputPass`
- Brain-shaped neuron distribution, blue/orange firing pulses
- Showed ONLY during login (body.login-active) — hidden after auth

## Implementation Pattern
1. Keep ALL original portal JS (auth, WebSocket, status, chat, terminal) intact
2. Add `class="login-active"` to body on page load — removed on successful auth
3. `#pb-canvas-container` shown via `body.login-active #pb-canvas-container { display: block }`
4. Canvas pauses when `auth-overlay.style.display === 'none'`
5. All sidebar nav, panels, mobile nav preserved unchanged functionally

## Output File
`/home/jared/projects/AI-CIV/aether/exports/purebrain-portal-rebranded.html` (82KB, 2055 lines)

## Verification
29/29 checks passed — all v7 branding elements present + all portal functionality preserved.
