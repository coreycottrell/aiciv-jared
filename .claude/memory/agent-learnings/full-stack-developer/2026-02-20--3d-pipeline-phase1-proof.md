# 3D Interactive Pipeline - Phase 1 Proof

**Date**: 2026-02-20
**Type**: technique
**Topic**: End-to-end Three.js pipeline: Sketchfab GLB → glass materials → HDRI → bloom → mouse/scroll interaction → standalone HTML

---

## What Was Built

`/home/jared/projects/AI-CIV/aether/exports/3d-interactive-demo.html`

Complete standalone interactive 3D demo proving the full pipeline works without a build step.

## Pipeline Proof

```
Sketchfab GLB (ZIP format)
  → Python: extracted scene.gltf + scene.bin, embedded bin as base64 data URI
  → GLTFLoader: loaded self-contained GLB
  → MeshPhysicalMaterial: applied glass override to all meshes
  → RGBELoader: loaded Poly Haven HDRI
  → EffectComposer + UnrealBloomPass: postprocessing
  → Mouse listener: tilt with 4% lerp per frame
  → Scroll listener: scrollProgress [0..1] drives rotation + camera Z
  → Procedural IcosahedronGeometry fallback if GLB fails
  → Standalone HTML via importmap + CDN (no build step)
```

## Critical Discovery: Sketchfab GLBs Are ZIP Files

The Tamminen Energy Orb `.glb` downloaded from Sketchfab is actually a ZIP archive containing:
- `license.txt`
- `scene.gltf` (GLTF JSON, 30KB)
- `scene.bin` (binary geometry, 501KB)

**To convert to a real self-contained GLB:**
```python
import zipfile, io, json, base64, struct

with open('tamminen-energy-orb.glb', 'rb') as f:
    data = f.read()

with zipfile.ZipFile(io.BytesIO(data)) as z:
    gltf_bytes = z.read('scene.gltf')
    bin_bytes  = z.read('scene.bin')
    gltf = json.loads(gltf_bytes)

# Embed bin as data URI inside gltf JSON
bin_b64 = base64.b64encode(bin_bytes).decode()
gltf['buffers'][0]['uri'] = f'data:application/octet-stream;base64,{bin_b64}'

# Build proper GLB binary
gltf_json_str = json.dumps(gltf)
json_bytes = gltf_json_str.encode('utf-8')
json_pad = (4 - len(json_bytes) % 4) % 4
json_bytes += b' ' * json_pad

total_len = 12 + 8 + len(json_bytes)
header    = struct.pack('<III', 0x46546C67, 2, total_len)
json_chunk = struct.pack('<II', len(json_bytes), 0x4E4F534A) + json_bytes
glb_bytes = header + json_chunk

with open('energy-orb-selfcontained.glb', 'wb') as f:
    f.write(glb_bytes)
```

Result: 672KB self-contained GLB (bin was 501KB raw → embedded as base64 becomes ~668KB in JSON → packed to GLB is still large because base64 adds 33% overhead).

**Takeaway**: For Phase 2, compress GLB with `gltf-transform optimize --compress draco`. The Tamminen orb has 12 meshes and 1 animation - very rich for glass layering.

## HDRI from Poly Haven

API call to get file list: `GET https://api.polyhaven.com/files/studio_small_09`

Direct 1K HDR download URL: `https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/studio_small_09_1k.hdr`

Files are ~1.6MB at 1K resolution. Saves to `exports/3d-models/studio.hdr`.

**Three.js HDRI setup:**
```javascript
const rgbeLoader = new RGBELoader();
rgbeLoader.load('path/to/file.hdr', (texture) => {
    texture.mapping = THREE.EquirectangularReflectionMapping;
    scene.environment = texture;
    // DO NOT set scene.background = texture if you want dark bg
});
```

## Glass Material - MeshPhysicalMaterial Config

The premium glass config:
```javascript
new THREE.MeshPhysicalMaterial({
    color: 0xd0eeff,
    transmission: 1.0,      // full transmission = see-through glass
    thickness: 0.8,         // controls how much light bends inside
    roughness: 0.02,        // very smooth = mirror-like
    metalness: 0.0,
    ior: 1.5,               // glass IOR (water=1.33, diamond=2.4)
    reflectivity: 0.5,
    envMapIntensity: 2.5,
    transparent: true,
    side: THREE.DoubleSide,
});
```

**Transmission requires `renderer.physicallyCorrectLights = true`.**

## Mouse Tilt Pattern (Verified Working)

```javascript
let targetRotX = 0, targetRotY = 0;
let currentRotX = 0, currentRotY = 0;

document.addEventListener('mousemove', (e) => {
    const nx = (e.clientX / window.innerWidth)  * 2 - 1; // -1 to +1
    const ny = (e.clientY / window.innerHeight) * 2 - 1;
    targetRotY =  nx * 0.28;  // max 16 degrees
    targetRotX = -ny * 0.18;  // max ~10 degrees
});

// In render loop (4% lerp = ~0.6s lag for smooth feel):
currentRotX += (targetRotX - currentRotX) * 0.04;
currentRotY += (targetRotY - currentRotY) * 0.04;
model.rotation.x = currentRotX;
model.rotation.y += delta * IDLE_ROT_Y; // idle rotation still runs
```

## Scroll-Driven Pattern

```javascript
let scrollProgress = 0;
window.addEventListener('scroll', () => {
    const docH = document.documentElement.scrollHeight - window.innerHeight;
    scrollProgress = docH > 0 ? window.scrollY / docH : 0;
}, { passive: true });

// In render loop:
camera.position.z = CONFIG.CAM_Z - scrollProgress * 0.6; // camera moves forward
rimLight.color.lerpColors(BLUE, ORANGE, scrollProgress * 0.6); // color shift
```

## Postprocessing Stack (CDN, No Build)

```javascript
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass }     from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass }     from 'three/addons/postprocessing/OutputPass.js';

const composer   = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(new THREE.Vector2(w, h), 0.7, 0.4, 0.85));
composer.addPass(new OutputPass());

// In render loop: composer.render() NOT renderer.render()
```

**Bloom config**: strength=0.7, radius=0.4, threshold=0.85. Higher threshold means only true highlights bloom (not muddy everything).

## Procedural Glass Sphere Fallback

Built from IcosahedronGeometry (cleaner than SphereGeometry for glass):
```javascript
// Outer shell
new THREE.Mesh(new THREE.IcosahedronGeometry(1.0, 4), glassMat)
// Inner core
new THREE.Mesh(new THREE.IcosahedronGeometry(0.52, 3), innerMat)
// Wire frame (low subdivision)
new THREE.Mesh(new THREE.IcosahedronGeometry(0.76, 1), wireMat)
// Ring pair (TorusGeometry)
```

## Files Created

- `/home/jared/projects/AI-CIV/aether/exports/3d-interactive-demo.html` (1232 lines, standalone)
- `/home/jared/projects/AI-CIV/aether/exports/3d-models/energy-orb-selfcontained.glb` (672KB, self-contained)
- `/home/jared/projects/AI-CIV/aether/exports/3d-models/studio.hdr` (1.6MB, Poly Haven CC0)

## How to Serve

The demo MUST be served via HTTP (not file:///) for importmap + HDRI to work:
```bash
cd /home/jared/projects/AI-CIV/aether/exports
python3 -m http.server 8888
# Open: http://localhost:8888/3d-interactive-demo.html
```

## Phase 2 Next Steps

1. **Draco compression** - Run `gltf-transform optimize` on the GLB to reduce from 672KB → ~120KB
2. **Depth of Field** - Add `BokehPass` or `SSAOPass` to the composer stack
3. **Audio reactivity** - Wire up the Web Audio API pattern from the implementation guide
4. **Custom glass GLSL** - Replace MeshPhysicalMaterial with raw ShaderMaterial for Fresnel + chromatic dispersion (see `2026-02-19--webgl-glass-shader-overhaul.md`)
5. **Multiple models** - Test pipeline on Meshy-generated GLBs (see `meshy-glass-orb-test.glb`)

## Performance Notes

- Pixel ratio capped at 2x: `Math.min(window.devicePixelRatio, 2)`
- Particle system uses `BufferGeometry.attributes.position.needsUpdate = true` (mutates in place, no GC)
- Background particles are CSS/DOM (free GPU cycles for Three.js)
- Press `P` in-browser to show FPS + draw call HUD
