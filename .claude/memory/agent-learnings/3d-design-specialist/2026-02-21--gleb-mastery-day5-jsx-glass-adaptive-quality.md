# Gleb Mastery Day 5 - JSX Glass Quality Gap, Adaptive Quality, Loading Screen

**Date**: 2026-02-21
**Type**: teaching
**Topic**: JSX GLB mesh reconstruction for full MeshTransmissionMaterial quality, FPS-adaptive quality tiers, branded loading screen

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/3d-design-specialist/` for all prior sprint learnings
- Found: Night 1 (Gleb recipe), Day 2 (R3F equivalence), Day 3 (Vite project), Day 4 (GLB loading, spring scroll)
- Applied: All prior params directly. Memory compounds correctly. Night 1 lighting rig still in use.

---

## Core Teaching 1: JSX Reconstruction Pattern (The Quality Gap Solution)

**The problem**: `useGLTF` + `<primitive object={scene} />` with `THREE.MeshPhysicalMaterial` = ~90% Gleb quality. No custom FBO.

**The solution**: Extract mesh nodes from GLB scene graph. Reconstruct each as JSX.

```javascript
// Step 1: Extract descriptors from GLB scene
function extractMeshDescriptors(scene) {
  const descriptors = []
  scene.updateMatrixWorld(true)   // Must update before reading matrixWorld

  scene.traverse((child) => {
    if (child.isMesh && child.geometry) {
      descriptors.push({
        geometry: child.geometry.clone(), // Clone is cheap (shares typed arrays)
        matrix: child.matrixWorld.clone(), // World-space, not local
        name: child.name || `mesh_${descriptors.length}`,
      })
    }
  })
  return descriptors
}

// Step 2: Compute normalization (combine all world-space bounds)
function computeNormalization(descriptors, targetSize = 2.5) {
  const combinedBox = new THREE.Box3()
  descriptors.forEach(({ geometry, matrix }) => {
    geometry.computeBoundingBox()
    const transformed = geometry.boundingBox.clone().applyMatrix4(matrix)
    combinedBox.union(transformed)
  })
  const center = combinedBox.getCenter(new THREE.Vector3())
  const size = combinedBox.getSize(new THREE.Vector3())
  const maxDim = Math.max(size.x, size.y, size.z)
  return { centerOffset: center, scaleFactor: targetSize / maxDim }
}

// Step 3: Render each mesh as JSX with MeshTransmissionMaterial
function ReconstructedMesh({ descriptor, centerOffset, scaleFactor }) {
  const { geometry, matrix } = descriptor
  const position = new THREE.Vector3()
  const quaternion = new THREE.Quaternion()
  const scale = new THREE.Vector3()
  matrix.decompose(position, quaternion, scale)

  const normalizedPos = position.clone().sub(centerOffset).multiplyScalar(scaleFactor)
  const normalizedScale = scale.clone().multiplyScalar(scaleFactor)

  return (
    <mesh position={normalizedPos.toArray()} quaternion={quaternion.toArray()}
          scale={normalizedScale.toArray()} geometry={geometry}>
      {/* THIS is what makes Day 5 different from Day 4 */}
      <MeshTransmissionMaterial
        samples={8}           // 8 FBO samples = full Gleb refraction
        resolution={1024}     // 1024x1024 FBO
        chromaticAberration={0.8}  // Material-level (not just postprocessing)
        transmission={1}
        thickness={0.8}
        ior={1.5}
        backside={true}
      />
    </mesh>
  )
}
```

**Why world matrix**: GLBs have deep hierarchies. A child mesh may have local position [0,0,0] but world position [1.5, 0.3, -0.8] from ancestors. Using matrixWorld gives correct placement when flattening to JSX.

**Why geometry.clone()**: useGLTF caches the scene. Cloning prevents mutating cached geometry. Cost is near-zero (typed arrays shared by reference until modified).

---

## Core Teaching 2: FPS-Adaptive Quality Tiers

**Three tiers**:
```
TIER 0 HIGH: samples=8,  resolution=1024, dpr=[1,2],   full postprocessing
TIER 1 MID:  samples=4,  resolution=512,  dpr=[1,1.5], no ChromaticAberration
TIER 2 LOW:  samples=2,  resolution=256,  dpr=[1,1],   bloom only
```

**FPS measurement in useFrame**:
```javascript
export function FPSMeter({ onTierChange, currentTier }) {
  const fpsWindow = useRef([])   // Rolling 30-frame window

  useFrame((state) => {
    const delta = state.clock.getDelta()
    const fps = Math.min(Math.max(1/delta, 1), 120)  // Clamp outliers

    fpsWindow.current.push(fps)
    if (fpsWindow.current.length > 30) fpsWindow.current.shift()
    if (fpsWindow.current.length < 30) return  // Wait for full window

    const avgFPS = fpsWindow.current.reduce((a, b) => a + b, 0) / 30
    // Evaluate tier changes with hysteresis...
  })
}
```

**Hysteresis**:
```javascript
const DROP_STABILITY = 60   // 1 second below minFPS before downgrade
const RISE_STABILITY = 120  // 2 seconds above targetFPS before upgrade
```

Longer rise hysteresis prevents thrashing: downgrade fixes user experience; upgrade risks immediate re-degradation.

**Initial tier detection** (before FPS measurement warms up):
```javascript
function detectInitialTier() {
  const w = window.innerWidth
  if (w < 480) return QUALITY_TIERS.LOW
  if (w < 768) return QUALITY_TIERS.MID
  if (w < 1024) return QUALITY_TIERS.MID
  return QUALITY_TIERS.HIGH
}
```

---

## Core Teaching 3: Loading Screen Architecture

**Pattern**: Pure DOM overlay sits above Canvas. R3F signals readiness.

```jsx
// DOM component (renders instantly, before WebGL)
function LoadingOverlay({ isReady }) {
  // Fade on isReady=true, unmount after 900ms
}

// R3F component inside Canvas (signals after N rendered frames)
function ReadySignal({ onReady, warmupFrames = 3 }) {
  const count = useRef(0)
  useFrame(() => {
    count.current++
    if (count.current >= warmupFrames) onReady()
  })
  return null
}
```

**Timeline**:
- t=0ms: LoadingOverlay renders (DOM, instant)
- t=100-400ms: WebGL initializes, scene renders
- t=500ms: Frame 3 completes, ReadySignal fires
- t=500-1300ms: 800ms CSS opacity transition
- t=1300ms: LoadingOverlay unmounts

**CSS animations over JS timers** for loading animation: run on compositor thread (smooth while JS parses Three.js). Zero cleanup needed on unmount.

---

## Core Teaching 4: FBO Cost Model for Glass

`MeshTransmissionMaterial` creates ONE WebGLRenderTarget per component instance.

With resolution=1024, samples=8:
- Each glass object = 8 extra scene renders per frame
- 2 glass objects = 16 extra renders
- 10 glass objects = 80 extra renders (impossible on mobile)

**Optimization options**:
- TIER 1: samples=4, resolution=512 = 4x fewer GPU operations per glass object
- TIER 2: samples=2, resolution=256 = 16x fewer
- For multiple glass objects in one scene: share FBO (requires custom shader)

For avatar use case (single glass sphere): TIER 0 is fine on desktop, TIER 1 on mobile.

---

## Core Teaching 5: Responsive Canvas Pattern

```javascript
function useCanvasHeight() {
  const w = window.innerWidth
  if (w < 480) return 340
  if (w < 768) return 400
  if (w < 1024) return 460
  return 560
}
```

Why smaller canvas on mobile:
- Fewer pixels = cheaper to render (quadratic reduction: half width + half height = 4x fewer pixels)
- Portrait orientation means 560px canvas = nearly full viewport
- Mobile users engage less with 3D (no hover, smaller screen)

---

## Gotchas Discovered Day 5

1. **ReadySignal was in LoadingScreen.jsx, not PerformanceMonitor.jsx**: Import error caught at build. Always check which file exports what. Rollup gives a clear "X is not exported by Y" error.

2. **`useEffect` for adaptive quality must not run during loading**: FPS is artificially low during scene initialization (GPU is busy with first renders + HDRI loading). Pass `enabled={isSceneReady}` to useAdaptiveQuality to prevent premature downgrade.

3. **useFrame getDelta() includes time since last call**: If JS was paused (tab hidden, GPU stall), getDelta() returns a huge value. Always clamp: `Math.min(Math.max(fps, 1), 120)`.

4. **matrix.decompose() order is (position, quaternion, scale)**: Not (position, rotation, scale). Three.js uses quaternions internally. decompose gives the THREE.Quaternion, which R3F mesh accepts directly via `quaternion={q.toArray()}`.

---

## Files

- MeshyModelJSX.jsx: `exports/gleb-r3f-scene/src/MeshyModelJSX.jsx`
- PerformanceMonitor.jsx: `exports/gleb-r3f-scene/src/PerformanceMonitor.jsx`
- LoadingScreen.jsx: `exports/gleb-r3f-scene/src/LoadingScreen.jsx`
- Day 5 report: `exports/3d-mastery-day5-report.md`

## Days 6-7 Recommendations

1. **Tripo3D API for higher base mesh quality**: Meshy glass orb is decent; Tripo3D v3.0 produces sculpture-level geometry. Test with the text-to-3D endpoint and compare mesh density.

2. **Voice-reactive animation**: Wire audio amplitude to `innerIntensity` and `scale` in GlebSphere. The architecture is ready (mode system exists). Just need amplitude data from Web Audio API.

3. **Cursor proximity interaction**: When cursor is near the canvas, increase `rotationIntensity` and `floatIntensity` in Float component. Creates a magnetic attraction feel.

4. **WordPress iframe + postMessage integration test**: Build the actual iframe embed and test postMessage mode switching from a test WordPress page.
