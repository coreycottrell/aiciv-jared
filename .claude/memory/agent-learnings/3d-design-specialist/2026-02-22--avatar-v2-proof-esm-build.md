# Aether Avatar v2 Proof-of-Concept — ESM Build

**Date**: 2026-02-22
**Type**: teaching
**Confidence**: high
**Tags**: three-js, esm, importmap, glass-material, avatar, behavioral-modes

---

## Context

Building the Avatar v2 proof-of-concept as a single self-contained HTML file. Requirements:
- Vanilla Three.js ESM r0.161.0 (no React)
- Works on file:// protocol
- Multilayer glass entity (outer sphere + 2 orbiting torus rings + emissive core)
- 4 behavioral modes with smooth transitions
- Cursor gaze tracking (lerped)
- Bloom + Vignette postprocessing
- Auto-demo cycle that stops on user interaction

---

## Memory Search Applied

Searched all 3d-design-specialist memories before building. Applied:
- ESM importmap pattern from `2026-02-22--threejs-r148-esm-migration-critical.md`
- Single rAF loop (no dual loop) from `2026-02-21--threejs-legacy-avatar-rendering-fixes.md`
- Mode definitions from `2026-02-21--gleb-mastery-day6-avatar-audio-cursor-env.md`
- Ring architecture from `2026-02-21--aether-avatar-v2-build-complete.md`
- OutputPass last requirement from `2026-02-22--glsl-noise-gpu-particles-caustics.md`

---

## Architecture Decisions

### Glass Material: MeshPhysicalMaterial (not MeshTransmissionMaterial)

MeshTransmissionMaterial is a Drei/R3F abstraction. In vanilla Three.js, the closest
equivalent is `MeshPhysicalMaterial` with `transmission: 1.0`:

```javascript
const outerMat = new THREE.MeshPhysicalMaterial({
  transmission:    1.0,    // full glass
  thickness:       0.8,    // refraction depth
  roughness:       0.05,   // near-mirror smooth
  ior:             1.5,    // real glass IOR
  specularColor:   new THREE.Color('#C8A84A'),  // gold specular (Gleb signature)
  specularIntensity: 1.0,
  transparent:     true,
  depthWrite:      false,  // glass must not write depth
});
```

Two sphere meshes for glass: FrontSide + BackSide (separate meshes, separate materials).
This creates internal reflections visible through the glass without backside: true param.

### Ring Orbital System

```javascript
// Groups handle orbital plane tilt
const ringGroup1 = new THREE.Group();
ringGroup1.add(ring1);  // ring has its own tilt offset inside the group

// Rotation in animate loop:
ring1Angle += workRingSpeed0 * dt;  // use dt, not elapsed (frame-rate independent)
ringGroup1.rotation.set(RING1_TILT.x, ring1Angle, RING1_TILT.z);

// Extra rocking for life:
ring1.rotation.x = RING1_TILT.x + Math.sin(elapsed * 0.5) * 0.04;
```

Two rings: ring1 at 32-degree tilt (radius 1.55), ring2 at -45-degree tilt (radius 1.38).
Different speeds: 0.30 rad/s and -0.20 rad/s in idle mode, both scale with mode.

### Emissive Core: Scale-and-Intensity Only

Never animate roughness or transmission on glass materials (shader recompile cost).
Only safe animations:
- `mesh.scale.setScalar()` on outer sphere
- `coreMat.emissiveIntensity` on MeshStandardMaterial core
- `mesh.rotation` (uniform update, trivial)

### Gaze System

```javascript
// Normalised cursor to [-1,1]
document.addEventListener('mousemove', (e) => {
  cursorNorm.x = (e.clientX / window.innerWidth  - 0.5) * 2;
  cursorNorm.y = (e.clientY / window.innerHeight - 0.5) * 2;
});

// Per frame:
const gazeRange = 0.28 * workGazeMult;  // ~16deg max, mode-scaled
gazeTarget.x = -cursorNorm.y * gazeRange;
gazeTarget.y =  cursorNorm.x * gazeRange;
gazeCurrent.x += (gazeTarget.x - gazeCurrent.x) * 0.05;  // 5% lerp = organic
gazeCurrent.y += (gazeTarget.y - gazeCurrent.y) * 0.05;

// Apply to root group (all elements move together)
avatarGroup.rotation.x = gazeCurrent.x;
avatarGroup.rotation.y = gazeCurrent.y;
```

Mode-specific gaze multipliers: idle 0.7, speaking 0.5, thinking 0.3, listening 1.6.

### Mode Transitions

```javascript
// Store prev + current mode, reset modeT to 0 on switch
function setMode(mode) {
  prevMode    = currentMode;
  currentMode = mode;
  modeT       = 0;
}

// Per frame lerp with smoothstep easing
modeT = Math.min(modeT + dt * 1.1, 1.0);  // ~0.9s full transition
const t = smoothstep(0, 1, modeT);
workCoreIntensity = lerp(src.coreIntensity, dst.coreIntensity, t);
// ... all other properties
workCoreColor.lerp(dst.coreColor, 0.045);  // THREE.Color lerp is per-frame
```

### Postprocessing Stack (CRITICAL ORDER)

```javascript
composer.addPass(new RenderPass(scene, camera));        // 1. render scene
composer.addPass(bloomPass);                            // 2. selective bloom
composer.addPass(vignettePass);                         // 3. vignette (custom ShaderPass)
composer.addPass(new OutputPass());                     // 4. ALWAYS LAST
```

OutputPass MUST be last in r0.161.0. Without it, colors are wrong gamma/washed out.

### Procedural Environment Map

No HDRI file (file:// can't load external HDRIs with fetch). Instead, PMREMGenerator
from a procedural scene with 6 colored PointLights:

```javascript
const pmremGenerator = new THREE.PMREMGenerator(renderer);
const envScene = new THREE.Scene();
// 6 colored lights at extreme positions (box arrangement)
const envTexture = pmremGenerator.fromScene(envScene).texture;
scene.environment = envTexture;
setTimeout(() => pmremGenerator.dispose(), 2000);  // deferred dispose
```

Glass materials use `envMapIntensity: 3.5` to compensate (no scene-level intensity).
Never use `scene.environmentIntensity` — it crashes legacy builds silently.

### Auto-Demo Cycle Pattern

```javascript
let demoActive = true;
const DEMO_MODES = ['idle', 'listening', 'thinking', 'speaking'];

function nextDemoMode() {
  if (!demoActive) return;
  demoCycleIdx = (demoCycleIdx + 1) % DEMO_MODES.length;
  setMode(DEMO_MODES[demoCycleIdx]);
  demoTimer = setTimeout(nextDemoMode, 5000);
}

// 4s initial delay, then 5s per mode
setTimeout(nextDemoMode, 4000);

// Stop on user button click
document.querySelectorAll('.mode-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    demoActive = false;
    clearTimeout(demoTimer);
  });
});
```

---

## Gotchas Found

**Gotcha 1: Re-parenting meshes under avatarGroup after creation**
Must do: create meshes → add to scene → then remove from scene and add to group.
Or: add directly to group from the start (cleaner pattern going forward).

**Gotcha 2: BackSide sphere must have slightly smaller radius**
If front and back glass spheres are same radius, they z-fight. Inner backside at 1.19
(vs outer at 1.20) eliminates z-fighting.

**Gotcha 3: sparkPosAttr.needsUpdate = true is mandatory**
Every frame after updating particle positions, this flag must be set.
Missing it = frozen particles despite code executing.

**Gotcha 4: dt cap prevents spiral of death**
`const dt = Math.min(clock.getDelta(), 0.05)` caps frame time to 50ms.
Without this, a tab switch creates a huge dt spike (tab was away for 30 seconds)
that animates everything by 30 seconds in one frame = broken state.

---

## Quality Verification Checklist (All PASS)

- [x] importmap with three.module.js ESM CDN path
- [x] OutputPass is last in composer chain
- [x] Single requestAnimationFrame call
- [x] window.setMode exposed for onclick handlers
- [x] MeshPhysicalMaterial with transmission: 1.0
- [x] 128-segment spheres (no visible facets through glass)
- [x] Two torus rings, counter-rotating at different speeds
- [x] Emissive core (scale + intensity only, never roughness)
- [x] Cursor gaze with 5% lerp per frame
- [x] All 4 modes (idle, listening, thinking, speaking)
- [x] PostMessage API (SET_MODE, PING/PONG, READY)
- [x] Gold specular (#C8A84A)
- [x] No scene.environmentIntensity (known crash)
- [x] PureBrain blue (#2a93c1) throughout

---

## File Delivered

Path: `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-v2-proof.html`
Size: 924 lines, 32KB
Sent: Telegram message ID 7802 (confirmed delivery)

---

## Memory Written

Path: `.claude/memory/agent-learnings/3d-design-specialist/2026-02-22--avatar-v2-proof-esm-build.md`
Type: teaching
Topic: Avatar v2 proof-of-concept — ESM importmap, MeshPhysicalMaterial glass, 4-mode state machine, gaze system
