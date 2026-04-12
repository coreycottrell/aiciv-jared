# Voice-Reactive & Scroll-Driven 3D Web - Implementation Guide

**Date**: 2026-02-20
**Type**: teaching
**Topic**: Complete implementation patterns for audio-reactive WebGL, scroll-driven 3D, cursor interaction, and WordPress/Elementor embedding

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/full-stack-developer/` for "audio", "WebGL", "3D", "scroll"
- Found: webgl-glass-shader-overhaul.md, premium-glass-sphere-avatar.md, gleb-kuznetsov-avatar-overhaul.md
- Applied: Exact production code from `exports/avatar-fluid.html` as ground truth

---

## Key Patterns Documented

### 1. Web Audio API Signal Chain

```
Mic → getUserMedia → MediaStreamSource → AnalyserNode (fftSize=256) → getByteFrequencyData → normalize → lerp → uniform
```

**Critical**: Allocate `Uint8Array` ONCE outside render loop. Never inside.
**Critical**: `source.connect(analyser)` NOT `source.connect(destination)` - prevents feedback.
**Critical**: AudioContext must be created/resumed after user gesture (browser policy).

### 2. Audio Smoothing Pattern

```javascript
audioLevel += (targetAudioLevel - audioLevel) * 0.12; // 12% per frame = 0.2s lag at 60fps
if (rawLevel < 0.01) targetAudioLevel *= 0.95; // slow decay when quiet
```

This is the exact pattern in our production avatar. It feels "organic" vs jittery.

### 3. Frequency Band Mapping

- Sub-bass (20-80Hz): bins 0-4 → good for impact/scale shake
- Voice fundamental (85-255Hz): bins 5-15 → good for mouth/face morph
- Mids (255Hz-3kHz): → glow, emission
- Highs (3-8kHz): → sparkle, shimmer
- Overall average: → general reactivity

### 4. Scroll-Driven Architecture Choice

Two approaches:
- **GSAP ScrollTrigger + Three.js**: Better for WordPress/Elementor (no build step, CDN)
- **React Three Fiber ScrollControls**: Better for React SPA builds

Key scroll pattern: `sticky` CSS + IntersectionObserver + GSAP `scrub:1`

### 5. Elementor Embedding Rules

1. Use `three.min.js` (NOT ES module) for Elementor HTML widget
2. Load GLTFLoader separately via CDN (script tag, not import)
3. Always include WebGL capability check before initializing
4. Always include CSS fallback img (display:none initially)
5. Use IntersectionObserver to pause rendering off-screen
6. Cap pixelRatio at 2 (`Math.min(devicePixelRatio, 2)`)

### 6. Production Avatar Architecture

Our avatar uses raw WebGL (not Three.js) because:
- Raymarched SDF sphere = no GLB needed (mathematically perfect sphere)
- Full GLSL control impossible in Three.js material system
- Zero load time (no asset fetch)

For Meshy GLB models → use Three.js
For procedural geometry → raw WebGL + GLSL

### 7. State Machine + Audio Combined

```glsl
// Smooth state blending:
float sMix = clamp(1.0 - abs(uState - 1.0), 0.0, 1.0); // peaks at speaking
float tMix = clamp(1.0 - abs(uState - 2.0), 0.0, 1.0); // peaks at thinking

// Audio amplifies effects within current state:
float glowStrength = 0.9 + uAudioLevel * 0.6 * sMix;
```

---

## Files Produced

- `/home/jared/projects/AI-CIV/aether/exports/3d-interactive-web-implementation-guide.md`
  - Complete implementation guide with working code patterns
  - All 4 sections: voice-reactive, scroll-driven, mouse interaction, WordPress embedding
  - 50-line quick start example included

---

## Gotchas for Future Reference

- Elementor HTML widgets cannot use ES module `type="importmap"` or `type="module"` reliably - use UMD builds
- Web Audio API `analyser.fftSize` must be power of 2 (256, 512, 1024)
- `frequencyBinCount` = fftSize / 2 (so 256 fftSize = 128 bins)
- `getByteFrequencyData` fills 0-255. `getFloatFrequencyData` fills -Infinity to 0 dB
- GSAP ScrollTrigger `scrub: 1` = 1 second lag (feels smoother than `scrub: true`)
- Three.js GLTFLoader (old) vs GLTFLoader (ESM) - Elementor requires old `examples/js/` path
- WebGL context loss: always listen for `webglcontextlost` event in production
- Mobile: single-channel refraction, 40 ray march steps max, mediump float
