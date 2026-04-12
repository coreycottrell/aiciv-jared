# Three.js RoomEnvironment: Not in Core Export — Must Import from Addons

**Date**: 2026-03-12
**Type**: gotcha
**Confidence**: high

## The Bug

`THREE.RoomEnvironment` does NOT exist on the core `three` module export.

Files using:
```js
import * as THREE from 'three';
const roomEnv = new THREE.RoomEnvironment(); // FAILS silently — black canvas
```

This produces a black 3D canvas with no error visible to the user. The scene
initializes, the render loop runs, but `pmrem.fromScene()` receives `undefined`
so the environment map is never set. MeshPhysicalMaterial (transmission/glass)
needs `scene.environment` set or it renders flat/dark.

## The Fix

Add a named import from the addons path:

```js
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// Then use without THREE. prefix:
const roomEnv = new RoomEnvironment();
const envTex = pmrem.fromScene(roomEnv, 0.04);
pmrem.dispose();
scene.environment = envTex.texture;
```

## Which Three.js Items Require Addon Imports (Not in Core)

These are commonly confused as being on the THREE namespace:

| Class | Correct Import Path |
|-------|-------------------|
| `RoomEnvironment` | `three/addons/environments/RoomEnvironment.js` |
| `OrbitControls` | `three/addons/controls/OrbitControls.js` |
| `GLTFLoader` | `three/addons/loaders/GLTFLoader.js` |
| `DRACOLoader` | `three/addons/loaders/DRACOLoader.js` |
| `EffectComposer` | `three/addons/postprocessing/EffectComposer.js` |
| `UnrealBloomPass` | `three/addons/postprocessing/UnrealBloomPass.js` |
| `RenderPass` | `three/addons/postprocessing/RenderPass.js` |
| `ShaderPass` | `three/addons/postprocessing/ShaderPass.js` |
| `FontLoader` | `three/addons/loaders/FontLoader.js` |
| `TextGeometry` | `three/addons/geometries/TextGeometry.js` |

## What IS in the Core THREE Export

Things that correctly use `THREE.` prefix:
- `THREE.WebGLRenderer`
- `THREE.Scene`
- `THREE.PerspectiveCamera`
- `THREE.Mesh`
- `THREE.MeshPhysicalMaterial`
- `THREE.SphereGeometry`
- `THREE.BufferGeometry`
- `THREE.PMREMGenerator` (this is core)
- `THREE.Color`, `THREE.Vector3`, `THREE.Clock`
- All geometry primitives
- All core materials
- All core lights

## Symptom Pattern

"3D canvas is black, titles and nav render, but no 3D visible"

This symptom = JavaScript error thrown inside the module script block, which
halts execution before the render loop ever starts. Check browser console for:
`TypeError: THREE.RoomEnvironment is not a constructor`

Or the subtler version: scene renders but glass/transmission materials look
wrong (flat, no refraction) = `scene.environment` is null because pmrem setup
failed silently.

## Files Fixed

- `/home/jared/portal_uploads/from-portal/portal_20260312_152231_day4-shader-masterclass.html`
- `/home/jared/portal_uploads/from-portal/portal_20260312_152231_day4-typography-3d.html`

Both also copied to `/home/jared/projects/AI-CIV/aether/exports/3d-studies/`

## importmap Pattern (r148 CDN)

Both files use this correct importmap approach for Three.js r148:
```json
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.148.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.148.0/examples/jsm/"
  }
}
```

This maps `three/addons/` to the JSM examples directory which contains all
addon modules. The import syntax then works cleanly without full CDN URLs.
