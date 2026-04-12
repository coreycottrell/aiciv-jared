# Three.js Legacy Build: Avatar Rendering Root Causes & Fixes

**Date**: 2026-02-21
**Type**: gotcha
**Topic**: Three.js r0.161.0 examples/js/ legacy build — two critical bugs causing black screen

---

## Context

Fixing three avatar HTML files that showed loading screen dismissing (after 8s timeout) but no 3D object rendering. Just black canvas. Files use Three.js r0.161.0 via jsdelivr CDN with `examples/js/` scripts (not ES modules).

---

## Bug 1: `scene.environmentIntensity` Does Not Exist in Legacy Build

**Severity**: Critical — silently crashes entire scene setup

**What happened**:
```javascript
const envTexture = pmremGenerator.fromScene(envScene).texture;
scene.environment = envTexture;
scene.environmentIntensity = 1.5;  // THIS LINE CRASHES
pmremGenerator.dispose();
```

`scene.environmentIntensity` was added to Three.js but the `examples/js/` legacy minified build does NOT expose this property setter. Assigning to it throws a TypeError in strict mode, halting all subsequent setup code. The renderer, lights, geometry, and composer are never set up. The 8s timeout fires, removes the loading screen, and reveals a black canvas because nothing was ever built.

**Fix**:
Remove `scene.environmentIntensity` entirely. Increase `envMapIntensity` on materials instead (already present on MeshPhysicalMaterial). This achieves the same effect without breaking anything.

```javascript
// WRONG:
scene.environmentIntensity = 1.5;

// RIGHT: set on material instead
const outerMat = new THREE.MeshPhysicalMaterial({
  envMapIntensity: 3.0,  // compensates for no scene-level intensity
  ...
});
```

---

## Bug 2: Dual requestAnimationFrame Loop Kills EffectComposer

**Severity**: Critical — produces black output even if setup succeeds

**What happened in the proof files**:
```javascript
function animateWithReady() {
  requestAnimationFrame(animateWithReady);  // <-- schedules NEXT frame FIRST
  // ... render work ...
  readyFrames++;
  if (readyFrames >= 4) {
    loadingScreen.classList.add('hidden');
    clock.getDelta(); // reset
    animate();  // <-- starts SECOND loop
    return;     // <-- only stops THIS frame callback, not the queued rAF
  }
}
```

`requestAnimationFrame(animateWithReady)` is called at the TOP of the callback. When `readyFrames >= 4`, `animate()` starts its own `requestAnimationFrame(animate)` loop. The `return` stops the current execution but the NEXT `animateWithReady` frame is already queued by the rAF at the top. Now TWO loops run every frame, each calling `composer.render()`. The EffectComposer cannot handle concurrent renders — it produces black/garbage output.

**Fix**: Single unified animation loop that handles its own ready state:

```javascript
let readyFrames = 0;
let loadingHidden = false;

function animate() {
  requestAnimationFrame(animate);  // single loop, always

  // Handle loading screen dismissal inline
  if (!loadingHidden) {
    readyFrames++;
    if (readyFrames >= 4) {
      loadingHidden = true;
      document.getElementById('loading-screen').classList.add('hidden');
    }
  }

  // ... all animation work ...
  composer.render();
}

animate();  // single call to start
```

---

## Bug 3: Immediate pmrem.dispose() May Race with GPU Upload

**Severity**: Medium — may cause white/corrupted env reflections on glass

**What happened**:
```javascript
const envTexture = pmremGenerator.fromScene(envScene).texture;
scene.environment = envTexture;
scene.environmentIntensity = 1.5;  // crash here (bug 1)
pmremGenerator.dispose();  // called immediately
```

Even if bug 1 were fixed, `pmremGenerator.dispose()` called synchronously after `fromScene()` can race with the GPU uploading the processed texture, especially on slower hardware.

**Fix**: Defer dispose with setTimeout:
```javascript
const envTexture = pmremGenerator.fromScene(envScene).texture;
scene.environment = envTexture;
setTimeout(function() { pmremGenerator.dispose(); }, 2000);
```

---

## Summary Pattern

When Three.js files with `examples/js/` scripts show blank/black canvas despite loading screen dismissing:

1. Check for `scene.environmentIntensity` — REMOVE IT, use `envMapIntensity` on materials
2. Check for multiple `requestAnimationFrame` loops — collapse to ONE
3. Check for immediate `pmremGenerator.dispose()` — DEFER with setTimeout
4. When in doubt, add `try/catch` around scene setup to surface silent TypeError crashes

---

## Files Fixed

- `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-v2-fixed.html`
- `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-proof-1-fixed.html`
- `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-proof-fixed.html`

## Memory Written

Path: .claude/memory/agent-learnings/3d-design-specialist/2026-02-21--threejs-legacy-avatar-rendering-fixes.md
Type: gotcha
Topic: Three.js legacy build black screen — environmentIntensity crash + dual rAF loop
