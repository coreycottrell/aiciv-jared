# Meshy GLB Self-Contained HTML Viewer

**Date**: 2026-02-22
**Type**: technique
**Confidence**: high
**Tags**: three-js, gltf, glb, base64, importmap, esm, file-protocol, meshy, orbit-controls

---

## Context

Building a single-file self-contained HTML viewer for a Meshy-generated 5.2 MB GLB model.
Requirements: works on file:// protocol, no server needed, interactive rotation, PureBrain branding.

---

## Memory Search Applied

- Applied ESM importmap pattern from `2026-02-22--threejs-r148-esm-migration-critical.md`
- Applied OutputPass-last requirement from `2026-02-22--avatar-v2-proof-esm-build.md`
- Applied dt-cap pattern from `2026-02-22--avatar-v2-proof-esm-build.md`
- Applied procedural PMREMGenerator (no external HDRI) from `2026-02-22--avatar-v2-proof-esm-build.md`
- Zero rediscovery needed

---

## Core Pattern: Base64 GLB Embedding

To make a GLB work on file:// protocol without a server:

```python
# Python: convert GLB to base64
import base64
with open('model.glb', 'rb') as f:
    b64_data = base64.b64encode(f.read()).decode()
# b64_data is ~1.37x file size in characters
# 5.2 MB GLB → 7.3 MB base64 string → 7 MB HTML file (acceptable)
```

```javascript
// JS: decode base64 → Blob → URL
const GLB_B64 = `LONG_BASE64_STRING_HERE`;

function b64ToBlob(b64, mime) {
  const binary = atob(b64);
  const bytes  = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return new Blob([bytes], { type: mime });
}

const glbBlob = b64ToBlob(GLB_B64, 'model/gltf-binary');
const glbUrl  = URL.createObjectURL(glbBlob);

// Then load normally:
const loader = new GLTFLoader();
loader.load(glbUrl, (gltf) => {
  // ... add to scene
  URL.revokeObjectURL(glbUrl);  // free memory after GPU upload
});
```

### Size notes
- 5.2 MB GLB → 7.3 MB base64 → 7 MB HTML (total)
- Browser handles atob() synchronously in main thread (~100-200ms for 7MB)
- Revoke the blob URL after load — model data is in GPU memory, blob URL no longer needed

---

## Auto-Scale + Centre Pattern for Unknown GLB

Meshy models have unpredictable sizes (could be 0.1 units or 100 units).
Always auto-scale to a known viewport size:

```javascript
loader.load(glbUrl, (gltf) => {
  const model = gltf.scene;

  // Scale to fit
  const box    = new THREE.Box3().setFromObject(model);
  const size   = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z);
  const scale  = 2.0 / maxDim;    // target: 2 units max dimension
  model.scale.setScalar(scale);

  // Centre at origin (must recompute box after scaling)
  const box2   = new THREE.Box3().setFromObject(model);
  const centre = box2.getCenter(new THREE.Vector3());
  model.position.sub(centre);     // origin is now centre of model

  scene.add(model);
  controls.target.set(0, 0, 0);
  controls.update();
});
```

---

## Material Enhancement for Meshy Models

Meshy generates PBR materials that are often slightly flat.
Boost emissive intensity + env map intensity:

```javascript
model.traverse((child) => {
  if (child.isMesh && child.material) {
    // Boost any emissive colors (glow effects)
    if (child.material.emissive) {
      const em = child.material.emissive;
      if (em.r + em.g + em.b > 0.05) {
        child.material.emissiveIntensity = Math.min(
          (child.material.emissiveIntensity || 1.0) * 1.8, 4.0
        );
      }
    }
    // Ensure env map reflections are visible
    child.material.envMapIntensity = 1.6;
    child.material.needsUpdate = true;
  }
});
```

---

## Lighting Setup for Meshy Models (No External HDRI)

5-light setup that works with Meshy PBR materials without any external HDRI file:

```javascript
// Ambient: broad fill
scene.add(new THREE.AmbientLight(0xffffff, 0.6));

// Hemisphere: sky/ground gradient
scene.add(new THREE.HemisphereLight('#3a8fc4', '#0a0405', 0.9));

// Key: cool blue from top-left
const key = new THREE.DirectionalLight('#c8e8ff', 2.2);
key.position.set(-3, 4, 3);
scene.add(key);

// Fill: warm orange accent (PureBrain)
const fill = new THREE.DirectionalLight('#f1420b', 0.5);
fill.position.set(4, 1, -2);
scene.add(fill);

// Rim: back glow for silhouette
const rim = new THREE.DirectionalLight('#2a93c1', 1.0);
rim.position.set(0, -2, -5);
scene.add(rim);

// Point: colored glow beneath
const pt = new THREE.PointLight('#1a6fa0', 1.5, 10);
pt.position.set(0, -1.5, 1);
scene.add(pt);

// Procedural env map (glass reflections)
const pmrem = new THREE.PMREMGenerator(renderer);
const envScene = new THREE.Scene();
// Add 6 colored point lights at box positions...
const envTex = pmrem.fromScene(envScene).texture;
scene.environment = envTex;
setTimeout(() => pmrem.dispose(), 3000);
```

---

## Auto-Rotate with Resume Pattern

```javascript
controls.autoRotate      = true;
controls.autoRotateSpeed = 0.8;   // slow, dignified

let idleTimer = null;
renderer.domElement.addEventListener('pointerdown', () => {
  controls.autoRotate = false;
  clearTimeout(idleTimer);
});
renderer.domElement.addEventListener('pointerup', () => {
  clearTimeout(idleTimer);
  idleTimer = setTimeout(() => { controls.autoRotate = true; }, 4000);
});
```

---

## Gentle Idle Float Animation

```javascript
// In animate loop, after model loads:
if (model) {
  model.position.y = Math.sin(elapsed * 0.6) * 0.05;  // gentle bob, ~2s cycle
}
```

This makes the model feel alive without interfering with user orbit controls
(OrbitControls adds to position, so the bob is additive).

---

## Verification Checklist (All Pass)

- [x] importmap with unpkg three.module.js r0.161.0
- [x] GLTFLoader from three/addons/loaders/GLTFLoader.js
- [x] OrbitControls from three/addons/controls/OrbitControls.js
- [x] Base64 → Blob → URL pattern works on file://
- [x] Auto-scale and centre on load
- [x] OutputPass last in EffectComposer chain
- [x] Single requestAnimationFrame loop only
- [x] dt cap (Math.min(rawDt, 0.05))
- [x] Loading screen with progress updates
- [x] Auto-rotate with 4s idle resume
- [x] Dark background #060606
- [x] PureBrain branding in header
- [x] Material emissive boost + envMapIntensity
- [x] URL.revokeObjectURL after load

---

## Files Delivered

- `/home/jared/projects/AI-CIV/aether/exports/meshy-demo-viewer.html`
  - Size: 7.0 MB (5.2 MB GLB + HTML/CSS/JS overhead)
  - Base64 chars: 7,298,268
  - Total HTML lines: ~468

Sent to Jared via Telegram:
- Thumbnail photo (message ID 7833)
- HTML viewer file (message ID 7834, 7.3 MB)
- Explanation text (message ID 7837)

---

## Memory Written

Path: `.claude/memory/agent-learnings/3d-design-specialist/2026-02-22--meshy-glb-selfcontained-viewer.md`
Type: technique
Topic: Self-contained HTML viewer for Meshy GLB — base64 embedding, auto-scale, lighting, auto-rotate
