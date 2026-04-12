# Avatar 3D Debug Report

**Date**: 2026-02-22
**Agent**: 3d-design-specialist
**Status**: ROOT CAUSE FOUND AND FIXED

---

## Root Cause: Three.js r148+ Removed `build/three.min.js` and `examples/js/`

Every previous fix attempt was treating symptoms, not the disease. The actual problem:

**Three.js r0.161.0 does not ship `build/three.min.js` OR `examples/js/` at all.**

These paths were **permanently removed** starting around r148. All legacy `<script src>` tags in the files returned **404 Not Found** silently — no console error in some browsers, no THREE global defined, and the entire 3D scene never initializes.

### Verified CDN 404s (r0.161.0)

| URL | Status |
|-----|--------|
| `https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.min.js` | **404** |
| `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/js/controls/OrbitControls.js` | **404** |
| `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/js/postprocessing/EffectComposer.js` | **404** |
| `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/js/postprocessing/UnrealBloomPass.js` | **404** |
| `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/js/shaders/CopyShader.js` | **404** |
| `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/js/shaders/LuminosityHighPassShader.js` | **404** |

### Working CDN Paths (r0.161.0)

| URL | Status |
|-----|--------|
| `https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js` | **200 OK** |
| `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/controls/OrbitControls.js` | **200 OK** |
| `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/postprocessing/EffectComposer.js` | **200 OK** |
| `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/postprocessing/RenderPass.js` | **200 OK** |
| `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/postprocessing/UnrealBloomPass.js` | **200 OK** |
| `https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/postprocessing/ShaderPass.js` | **200 OK** |

---

## Why Previous Fixes Did Not Work

All previous attempts modified the JavaScript logic (EffectComposer loop timing, pmremGenerator.dispose(), scene.environmentIntensity, etc.) but the **scripts never loaded in the first place**. No THREE global existed. The browser hit the `new THREE.Color()` call and threw `ReferenceError: THREE is not defined`, halting all execution before any scene setup occurred.

The loading screen dismissed after 8 seconds (safety timeout) but nothing was behind it because zero 3D code ran.

---

## The Fix: ES Modules with Import Map

The correct approach for Three.js r148+ is **ES modules with an import map**:

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
</script>
```

Key changes from the broken approach:
1. `build/three.min.js` → `build/three.module.js` (ESM build)
2. `examples/js/` → `examples/jsm/` (ESM addons)
3. No more `THREE.OrbitControls`, `THREE.EffectComposer` etc. — classes are imported directly
4. `<script>` → `<script type="module">` for the application code
5. CopyShader.js and LuminosityHighPassShader.js no longer needed as separate includes — they're bundled into UnrealBloomPass automatically in the ESM build

---

## Important: onclick Handlers and ES Module Scope

ES modules have their own scope — functions defined inside `<script type="module">` are NOT automatically global. The HTML buttons use `onclick="setMode('idle')"` which requires `setMode` to be on `window`.

Fix applied in all three files:
```javascript
// Inside the module, explicitly expose to window:
window.setMode = setMode;
```

---

## Files Fixed

| File | Status |
|------|--------|
| `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-v2-fixed.html` | Fixed |
| `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-proof-1-fixed.html` | Fixed |
| `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-proof-fixed.html` | Fixed |

---

## Browser Compatibility Note

Import maps are supported in:
- Chrome 89+ (March 2021)
- Firefox 108+ (December 2022)
- Safari 16.4+ (March 2023)
- Edge 89+

This covers all modern browsers Jared would be using. No polyfill needed.

---

## Memory Written

This diagnosis is being captured as a 3d-design-specialist memory for future reference.

**Key lesson**: When using Three.js r148+, NEVER use legacy `<script src>` tags pointing to `build/three.min.js` or `examples/js/`. Always use ES modules with import maps pointing to `build/three.module.js` and `examples/jsm/`.
