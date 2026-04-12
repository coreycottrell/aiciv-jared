# Three.js: RoomEnvironment is NOT in core THREE namespace

**Date**: 2026-02-22
**Type**: gotcha
**Confidence**: high
**Tags**: three-js, esm, environment, pmremgenerator

---

## Bug

`gleb-meshy-showcase-day2.html` used `new THREE.RoomEnvironment()` in the HDRI fallback path.

`RoomEnvironment` is NOT exported from the `three` core module (`build/three.module.js`).

It lives in: `three/addons/environments/RoomEnvironment.js`

When the HDR file fails to load (CORS, local file protocol, missing file), the fallback fires and throws:

```
TypeError: THREE.RoomEnvironment is not a constructor
```

This crashes the entire `buildScene()` function silently, leaving both canvases black with the loading spinner frozen.

---

## Fix

Add the import at the top of the `<script type="module">` block:

```javascript
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
```

Then use the imported class directly (not `THREE.RoomEnvironment`):

```javascript
const envRT = pmremGenerator.fromScene(new RoomEnvironment(), 0.04);
```

CDN URL confirmed 200: `https://cdn.jsdelivr.net/npm/three@0.162.0/examples/jsm/environments/RoomEnvironment.js`

---

## Why This Is Tricky

The HDRI primary load path works fine. Only the ERROR CALLBACK fires `RoomEnvironment`. So if your HDR file loads successfully (e.g., running from a local server with assets present), you never hit this bug. It only manifests when:

- Opening the file via `file://` protocol (most common when sharing HTML files)
- HDR file path is wrong or missing
- CORS blocks the HDR load

Since `file://` is the most common way Jared opens showcase files, this bug hits every time.

---

## Related

Three.js classes NOT in core that people commonly assume are:
- `RoomEnvironment` - addons/environments/RoomEnvironment.js
- `OrbitControls` - addons/controls/OrbitControls.js
- `GLTFLoader` - addons/loaders/GLTFLoader.js
- `EffectComposer` - addons/postprocessing/EffectComposer.js

Rule: if it's not a geometry, material, light, camera, renderer, or math helper, it's probably in addons.

---

## File Fixed

- Original: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/gleb-meshy-showcase-day2.html`
- Fixed: `/home/jared/projects/AI-CIV/aether/exports/gleb-meshy-showcase-day2-fixed.html`
