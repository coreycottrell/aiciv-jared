# Aether Avatar Proof - Single-File Three.js Architecture

**Date**: 2026-02-21
**Type**: teaching
**Topic**: Complete Gleb-level single HTML file with Three.js CDN, no build step, all sprint mastery applied

---

## Memory Search Results

- Searched: All 7 prior sprint files (Night 1 through Day 7)
- Found: Complete recipe stack - all parameters used directly
- Applied: 100% of sprint learnings in one file

---

## Core Teaching: Single-File Three.js with CDN

The full sprint R3F scene can be replicated in vanilla Three.js with CDN scripts:

```html
<!-- Three.js CDN stack for postprocessing -->
<script src="https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.161.0/examples/js/controls/OrbitControls.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.161.0/examples/js/postprocessing/EffectComposer.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.161.0/examples/js/postprocessing/RenderPass.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.161.0/examples/js/postprocessing/ShaderPass.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.161.0/examples/js/postprocessing/UnrealBloomPass.js"></script>
```

**What vanilla Three.js provides vs R3F:**
- MeshPhysicalMaterial = closest to MeshTransmissionMaterial (transmission, thickness, ior, attenuationColor)
- UnrealBloomPass = same as R3F @react-three/postprocessing Bloom
- ShaderPass = custom GLSL effects (ChromaticAberration, Vignette)
- PMREMGenerator = procedural environment map (replaces Poly Haven HDRI for self-contained files)

---

## Architecture Applied

### All 7 Sprint Learnings Used

1. **Night 1** - Complete Gleb recipe: 6-light studio rig (exact colors), MeshPhysicalMaterial params, bloom threshold=0.75, vignette, chromatic aberration shaders
2. **Day 2** - R3F equivalence: MeshPhysicalMaterial.transmission replaces MeshTransmissionMaterial
3. **Day 3** - Geometry density: SphereGeometry(1.2, 128, 128) mandatory for transmission
4. **Day 4** - Orbital mechanics: rings counter-rotate at different speeds
5. **Day 5** - Emissive inner core as bloom bait, haze sphere for glow
6. **Day 6** - SyntheticAudioEngine (full 200-line class), cursor gaze with gazeGroup, mode color/intensity system
7. **Day 7** - Loading screen pattern (DOM overlay + ready signal), PostMessage architecture reference

### Key Parameters (Production-Verified)

```javascript
// Glass outer shell
MeshPhysicalMaterial({
  transmission: 1.0,
  thickness: 0.8,
  roughness: 0.05,
  ior: 1.5,
  envMapIntensity: 2.5,
  side: THREE.DoubleSide,    // = backside: true equivalent
  attenuationColor: PB_BLUE,
  attenuationDistance: 0.5,
  clearcoat: 0.3,
})

// Inner core (bloom bait)
MeshStandardMaterial({
  emissiveIntensity: 6.0,  // High = bloom trigger
  roughness: 1.0,          // Diffuse, not specular
})

// Bloom
UnrealBloomPass(size, 0.6 strength, 0.5 radius, 0.75 threshold)
```

### Synthetic Audio Engine

The full SyntheticAudioEngine class (from Day 6) creates realistic speech-profile amplitudes with:
- Burst envelope (syllable timing: 150-500ms)
- Phoneme detail (12Hz oscillation)
- Formant simulation (bell curve across midLow band)
- Sibilants (intermittent high-freq bursts when sin(t*5) > 0.6)

Mode-specific profiles: idle (breathing), speaking (speech bursts), thinking (pulse), listening (quiet breath)

---

## Gotchas: Playwright/Headless Rendering

**Problem**: SwiftShader software renderer (headless Chromium) doesn't fully render:
- MeshPhysicalMaterial.transmission (requires floating-point WebGL textures)
- EffectComposer postprocessing (bloom especially)

**Result**: Screenshots in headless mode show the dark atmosphere (correct) but sphere is nearly invisible.

**Solution**: The file is designed for real browsers. Open in Chrome/Firefox where hardware WebGL is available.

**Playwright evaluate() TDZ issue**: `const` variables in the page's top-level script scope are NOT accessible via `page.evaluate()` in some Playwright versions (strict mode isolation). Use `var` for any globals that need external manipulation, OR just describe this is a real-browser file.

---

## Loading Screen Architecture (Self-Contained)

```javascript
// Two-phase animation: simple loop for first N frames, full loop after
let readyFrames = 0;
function animateWithReady() {
  requestAnimationFrame(animateWithReady);
  // ... minimal render ...
  readyFrames++;
  if (readyFrames >= 4) {
    document.getElementById('loading-screen').classList.add('hidden');
    animate();  // switch to full loop
    return;     // stop this loop
  }
}
animateWithReady();
```

This cleanly separates loading state from full scene state without React's Suspense.

---

## Environment Without Poly Haven HDRI

For self-contained files, PMREMGenerator + a ShaderMaterial env sphere works:

```javascript
const envScene = new THREE.Scene()
// Add ShaderMaterial sphere with gradient (top=electric blue, bottom=dark red)
// Add point lights to env scene for reflections
const envTexture = new THREE.PMREMGenerator(renderer).fromScene(envScene).texture
scene.environment = envTexture
scene.environmentIntensity = 1.5
```

This provides specular reflections that glass transmission picks up, even without HDRI.

---

## File Delivered

- Path: `exports/aether-avatar-proof.html`
- Size: 39KB, 1250 lines, zero dependencies beyond CDN
- Sent to Jared via Telegram: 2026-02-21

## Memory Written

Path: `.claude/memory/agent-learnings/3d-design-specialist/2026-02-21--aether-avatar-proof-single-file.md`
Type: teaching
Topic: Single-file Three.js architecture combining all 7 sprint learnings
