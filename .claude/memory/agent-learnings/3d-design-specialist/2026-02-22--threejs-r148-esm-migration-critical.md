# Three.js r148+ CDN Migration: Legacy Script Tags ALL 404

**Date**: 2026-02-22
**Type**: gotcha
**Confidence**: high
**Tags**: three-js, cdn, esm, importmap, webgl

---

## Context

Debugging three Aether avatar HTML files that showed blank/black scenes in Chrome. Loading screen dismissed but no 3D rendered. Multiple previous fix attempts (EffectComposer timing, pmremGenerator.dispose(), scene.environmentIntensity removal) had all failed.

---

## Discovery

**Three.js removed `build/three.min.js` and the entire `examples/js/` directory starting around r148 (released late 2023).**

At r0.161.0 (the version used in these files), ALL of these CDN paths return **404**:

- `https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.min.js` → 404
- `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/js/controls/OrbitControls.js` → 404
- `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/js/postprocessing/EffectComposer.js` → 404
- (ALL `examples/js/` paths 404)

The failures are **silent** in some browsers — no console error, THREE just never gets defined. The code then throws `ReferenceError: THREE is not defined` at the first usage, halting all scene setup. The canvas stays blank.

---

## Solution: ES Modules with Import Map

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
// ... rest of scene code
</script>
```

**Working CDN paths confirmed via WebFetch:**
- `https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js` → 200 OK
- `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/controls/OrbitControls.js` → 200 OK
- `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/postprocessing/EffectComposer.js` → 200 OK

---

## Gotcha: window.setMode for onclick Handlers

ES modules do NOT pollute global scope. If HTML has `onclick="setMode('idle')"`, the function must be explicitly exposed:

```javascript
// Inside <script type="module">
window.setMode = setMode;  // Required for onclick handlers to work
```

---

## Gotcha: No More Separate CopyShader / LuminosityHighPassShader

In the ESM build, `UnrealBloomPass` bundles its own shader dependencies. No separate `CopyShader.js` or `LuminosityHighPassShader.js` script tags needed.

---

## Gotcha: No More THREE.EffectComposer Namespace

In legacy builds: `new THREE.EffectComposer()`
In ESM builds: `new EffectComposer()` (imported directly)

Same for OrbitControls, RenderPass, UnrealBloomPass, ShaderPass.

---

## Performance Notes

ESM with import maps loads faster than legacy scripts because:
1. No global namespace pollution
2. Browser can cache individual modules
3. No need for separate shader dependency files

---

## Browser Compatibility

Import maps: Chrome 89+, Firefox 108+, Safari 16.4+, Edge 89+
Covers all modern browsers as of 2024+.

---

## Reference Files

- `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-v2-fixed.html`
- `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-proof-1-fixed.html`
- `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-proof-fixed.html`
- `/home/jared/projects/AI-CIV/aether/exports/avatar-debug-report.md`
