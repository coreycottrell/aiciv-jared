# Aether Animated Voice-Reactive Avatar V1

**Date**: 2026-03-09
**Type**: technique
**Agent**: 3d-design-specialist
**Topic**: Voice-reactive Three.js avatar with Web Audio API and PostMessage integration

---

## Context

Built Aether's animated avatar from 6 reference files. Jared's favorites were:
- `hex-cube-day1.html` — RoundedBox isometric cube as primary form, Web Audio API wiring
- `gleb-study-session-2026-03-09.html` — dual-layer glass, fBm background shader, SMAA

Key insight: **hex-cube-day1** had the most sophisticated architecture and was already prototyping Web Audio. That was the correct base.

---

## What Was Built

**File**: `exports/avatars/aether-avatar-animated-v1.html`

Single self-contained HTML file (1200 lines, 43KB):
- Three.js r0.161.0 via CDN importmap (cdn.jsdelivr.net — more reliable than unpkg for large files)
- RoundedBoxGeometry from three/addons (requires separate import)
- Full postprocessing: UnrealBloom + ChromaticAberration + Vignette + OutputPass

---

## Architecture Decisions

### 1. Geometry: RoundedBox at Isometric Angle

```javascript
const HEX_ROT_X = -35.264 * Math.PI / 180;  // arctan(1/sqrt(2))
const HEX_ROT_Y =  45.000 * Math.PI / 180;
// RoundedBoxGeometry(1.32, 1.32, 1.32, 8, 0.082)
```

Key: A cube viewed from its vertex diagonal shows a hexagonal face. This is the "hex cube" aesthetic Jared likes. Chamfer 0.082 is the sweet spot — soft enough for glass refraction, distinct enough to read as cube not sphere.

### 2. Web Audio API — Real Voice Reactivity

Three audio input paths:
1. **Mic input** — `navigator.mediaDevices.getUserMedia` → analyser
2. **External audio node** — `window.avatarAudio.connectAudioNode(node)` for TTS output
3. **Amplitude injection** — `window.avatarAudio.feedAmplitude(0.0-1.0)` for non-Web-Audio TTS
4. **Synthetic fallback** — SynthAudio class when no real audio available

The avatar automatically uses real audio when available (>0.02 threshold), else falls back to synthetic.

### 3. PostMessage API Contract

Compatible with existing production avatar:
- `{ type: 'SET_MODE', mode: 'idle|speaking|thinking|listening' }`
- `{ type: 'SET_AUDIO_AMPLITUDE', value: 0.0-1.0 }` — NEW for voice reactivity
- `{ type: 'START_MIC' }` / `{ type: 'STOP_MIC' }` — NEW
- `{ type: 'PING' }` → responds with `{ type: 'PONG', mode, micActive, version, features }`
- Emits `{ type: 'READY', version: 'animated-v1', features: [...] }` on load

### 4. Procedural Environment Map

Six-light PMREMGenerator from an envScene with a gradient sky dome. Much better than canvas-based equirectangular approach because it generates true cube map reflections (critical for the isometric face glass).

```javascript
// Six env lights in envScene (not main scene)
{ c: '#FFF8F0', i: 72, p: [-3,  5,  3] }  // warm white key
{ c: '#0D16F5', i: 30, p: [ 4,  2, -3] }  // electric blue fill
{ c: '#18A8D3', i: 20, p: [-4, -1,  2] }  // cyan rim
{ c: '#D10DCE', i: 14, p: [ 2, -3, -2] }  // magenta accent
{ c: '#C8A84A', i: 18, p: [ 1,  3, -1] }  // gold specular
{ c: '#E44224', i: 14, p: [ 0, -5,  1] }  // orange underlight
```

### 5. Multi-Frequency Float

Three independent sine waves at prime-ratio frequencies. No two axes ever sync within a 2-minute window. This is what makes the avatar feel like it's breathing.

```javascript
// Three float frequencies — organic, never synchronize
float: { f1: 0.55, a1: 0.095, f2: 0.37, a2: 0.030, f3: 0.21, a3: 0.018 }
```

---

## Performance Gotchas

1. **CDN choice matters**: `cdn.jsdelivr.net` is more reliable than `unpkg.com` for Three.js module loads. unpkg sometimes 404s on the addons path.

2. **RoundedBoxGeometry import**: Must import from `three/addons/geometries/RoundedBoxGeometry.js` separately from THREE. Cannot destructure from `three`.

3. **pmrem.compileCubemapShader()** not `compileEquirectangularShader()` — use the right one for envScene approach.

4. **OutputPass must be last** in the EffectComposer chain in r0.161.0. Otherwise SRGB output is broken.

5. **HexMesh rotation baked into mesh, not group**: The isometric rotation must be on the mesh itself (with `rotation.order = 'YXZ'`). The continuous Y rotation in the animation loop adds to the base `HEX_ROT_Y`. If you put the base rotation on the group, the animation loop rotation competes incorrectly.

6. **AudioContext must be created on user gesture** (browser autoplay policy). The mic button and mode buttons both call `audioCtx.resume()` on click.

---

## Mode Color Mapping

| Mode | Inner Core | Ring | Bloom |
|------|-----------|------|-------|
| idle | blue #2a93c1 | blue | 0.45 |
| speaking | white | orange #f1420b | 0.90 |
| thinking | violet #7b4fc9 | violet | 0.48 |
| listening | cyan #18A8D3 | cyan | 0.58 |

---

## Future Improvements

1. Add `RoomEnvironment` from three/addons for better glass reflections (requires no external file)
2. Consider `SMAAPass` for better anti-aliasing on the glass edges
3. `ThicknessMap` texture on hexMat could make the glass look more volumetric
4. Depth of field (ShaderPass with DoF kernel) would push this to Gleb level
5. The fBm background shader from gleb-study-session would enhance depth

---

## Delivery

- File: `/home/jared/projects/AI-CIV/aether/exports/avatars/aether-avatar-animated-v1.html`
- Sent to Telegram: message_id 22345
- Size: 43KB / 1200 lines
- Standalone + iframe-embeddable
- Background: #080a12 (matches site-wide dark bg rule)
