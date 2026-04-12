# Gleb Mastery Day 4 - GLB Loading, Spring Scroll, Code Splitting

**Date**: 2026-02-21
**Type**: teaching
**Topic**: Meshy GLB loading with glass override, framer-motion spring scroll bridge pattern, Vite code splitting

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/3d-design-specialist/` for all prior sprint learnings
- Found: Night 1 (complete Gleb recipe), Day 2 (R3F equivalence map), Day 3 (Vite project + MeshTransmissionMaterial)
- Applied: All prior params directly. Memory system continues to work. Zero rediscovery.

---

## Core Teaching 1: JSX MeshTransmissionMaterial vs Imperative Glass (Critical Gap)

This is the most important discovery from Day 4. There are TWO ways to get glass on a model:

```
OPTION A: JSX (for primitive geometry in scene graph)
<mesh>
  <sphereGeometry args={[1.2, 128, 128]} />
  <MeshTransmissionMaterial
    transmission={1}
    samples={8}           <- 8 FBO samples (Gleb quality)
    resolution={1024}     <- custom FBO resolution
    chromaticAberration={0.8}  <- material-level color split
  />
</mesh>
Result: ~100% Gleb glass quality

OPTION B: Imperative (for GLB traversal, outside JSX)
scene.traverse((child) => {
  if (child.isMesh) {
    child.material = new THREE.MeshPhysicalMaterial({
      transmission: 1,
      thickness: 0.8,
      ior: 1.5,
      // NO samples param (WebGL built-in only)
      // NO resolution param (no custom FBO)
      // NO material-level chromaticAberration
    })
  }
})
Result: ~90% Gleb glass quality
```

**When to use each**:
- Building custom geometry (sphere, box, torus): Use JSX `<MeshTransmissionMaterial>` always
- Loading GLB via useGLTF and traversing: Imperative is necessary (JSX can't be assigned to child.material)
- Future fix for GLB at 100% quality: Parse GLB node structure and reconstruct each mesh as JSX

---

## Core Teaching 2: framer-motion + R3F Bridge Pattern

framer-motion hooks live in DOM context. R3F useFrame lives in WebGL context. To bridge:

```javascript
// Step 1: Create MotionValues OUTSIDE Canvas (App.jsx)
function App() {
  const { scrollYProgress } = useScroll()
  const springScrollY = useSpring(scrollYProgress, {
    damping: 30,    // overdamped = no bounce on fast scroll
    stiffness: 100, // responsive tracking
    mass: 1,
  })

  return (
    <Canvas>
      {/* Step 2: Pass MotionValue as prop INTO Canvas */}
      <SpringScrollSphere springScrollY={springScrollY} />
    </Canvas>
  )
}

// Step 3: Derive transform MotionValues from spring
function SpringScrollSphere({ springScrollY }) {
  const rotY = useTransform(springScrollY, [0, 1], [0, Math.PI * 2])

  // Step 4: READ via .get() inside useFrame (not reactive, pulled per frame)
  useFrame(() => {
    meshRef.current.rotation.y = rotY.get()
  })
}
```

**Why .get() and not subscription**: MotionValues have `.subscribe()` but subscribing triggers React state updates which cause re-renders inside Canvas - catastrophic for 60fps. `.get()` in useFrame() pulls the current value synchronously without triggering any renders.

**Spring vs Lerp feel**:
- Lerp 8%: Moving average. No overshoot. Feels like signal smoothing.
- Spring damping=30: Physical deceleration with very slight overshoot. Feels like weighted cable.
- Spring damping=10: Visible bounce. Fun for demos, wrong for hero sections.

---

## Core Teaching 3: useGLTF Patterns

```javascript
import { useGLTF } from '@react-three/drei'

// Module level: start loading before component mounts
useGLTF.preload('/assets/model.glb')

function MyModel({ path }) {
  const { scene } = useGLTF(path)

  // MANDATORY: Wrap parent in Suspense
  // useGLTF throws a Promise during loading (Suspense mechanism)
  // Without Suspense wrapper in parent: app crashes during load
  return <primitive object={scene} />
}

// In parent:
<Suspense fallback={<FallbackComponent />}>
  <MyModel path="/assets/model.glb" />
</Suspense>
```

**useGLTF advantages over useLoader(GLTFLoader, ...)**:
1. Includes Draco decompressor (handles compressed GLBs automatically)
2. Caches loaded model (second `useGLTF(samePath)` returns cached version instantly)
3. `preload()` starts fetch before component mounts

---

## Core Teaching 4: GLB Auto-Centering (Two-Pass Required)

```javascript
// Wrong (one-pass):
const box = new THREE.Box3().setFromObject(scene)
scene.position.sub(box.getCenter(new THREE.Vector3()))  // centers
scene.scale.setScalar(2.5 / maxDim)                     // scales BUT re-offsets!

// Correct (two-pass):
const box = new THREE.Box3().setFromObject(scene)
const center = box.getCenter(new THREE.Vector3())
const size = box.getSize(new THREE.Vector3())
const maxDim = Math.max(size.x, size.y, size.z)

scene.position.sub(center)                              // center first
scene.scale.setScalar(2.5 / maxDim)                    // then scale

// After scaling, model is off-center again. Re-center:
const newBox = new THREE.Box3().setFromObject(scene)
scene.position.sub(newBox.getCenter(new THREE.Vector3()))
```

Two-pass is required because scaling a translated object multiplies the translation offset.

---

## Core Teaching 5: Vite Code Splitting for 3D

```javascript
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          three: ['three'],
          r3f: ['@react-three/fiber', '@react-three/drei'],
          pp: ['@react-three/postprocessing', 'postprocessing'],
          motion: ['framer-motion'],
        },
      },
    },
  },
})
```

Result:
```
three:  188 kB gzip (cached separately - changes rarely)
r3f:    156 kB gzip (cached separately - changes rarely)
pp:      21 kB gzip (postprocessing effects)
motion:  12 kB gzip (framer-motion)
app:      4 kB gzip (YOUR code - changes often, tiny chunk)
```

**The real benefit**: When you update your app code, only the 4 kB app chunk is re-fetched. Three.js (188 kB) stays cached. Without splitting, any change invalidates the entire 345 kB bundle.

**Note**: Vite warns about chunks > 500 kB (uncompressed). `three.js` is 725 kB uncompressed = 188 kB gzipped. This is acceptable for web 3D. Suppressing the warning: `build.chunkSizeWarningLimit: 1000`.

---

## WordPress 3D Embed: Decision Table

| Embed Method | CSS Isolation | JS Isolation | Update Speed | Best For |
|--------------|---------------|--------------|-------------|----------|
| iframe | Full | Full | Instant | Production |
| Elementor HTML widget (bundle) | Partial | None | Plugin deploy | Testing |
| WP plugin enqueue | Partial | None | Plugin deploy | Custom |

**Always use iframe for production**. Elementor CSS resets, potential React conflicts, and CSP headers all make direct JS injection unreliable.

**PostMessage pattern for chatbot-to-3D integration**:
```javascript
// Parent page (WordPress) → child iframe (3D scene)
iframe.contentWindow.postMessage(
  { type: 'SET_MODE', mode: 'speaking' },
  'https://3d.purebrain.ai'
)

// 3D scene listens:
window.addEventListener('message', (event) => {
  if (event.origin !== 'https://purebrain.ai') return // SECURITY CHECK
  if (event.data?.type === 'SET_MODE') setMode(event.data.mode)
})
```

---

## Gotchas

1. **Suspense is mandatory for useGLTF**: No wrapper = app throws during load. Always add.

2. **Two-pass normalization**: Center, then scale, then re-center. One-pass leaves model off-center.

3. **MotionValues via .get() not .subscribe()**: Subscription triggers React renders inside Canvas. Always use `.get()` in `useFrame()`.

4. **Material dispose on traverse**: Always `child.material.dispose()` before assigning new material. GPU memory leak otherwise.

5. **manualChunks only for static imports**: Dynamic `import()` already splits automatically. manualChunks affects only top-level static imports.

---

## Files

- MeshyModel.jsx: `exports/gleb-r3f-scene/src/MeshyModel.jsx`
- ScrollScene.jsx: `exports/gleb-r3f-scene/src/ScrollScene.jsx`
- vite.config.js: `exports/gleb-r3f-scene/vite.config.js`
- WordPress strategy: `exports/wordpress-3d-embed-strategy.md`
- Day 4 report: `exports/3d-mastery-day4-report.md`

## Day 5 Recommendation

Close the JSX glass quality gap on GLB models:
- Parse GLB `scene.children` to find mesh nodes
- Reconstruct each mesh in JSX using `<mesh geometry={node.geometry}><MeshTransmissionMaterial .../></mesh>`
- This gives full `samples={8}` quality on Meshy-loaded models
- Alternatively: Try Tripo3D v3.0 for higher base mesh quality
