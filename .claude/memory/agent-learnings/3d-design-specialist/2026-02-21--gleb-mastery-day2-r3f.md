# Gleb Mastery Day 2 - R3F Architecture Reference

**Date**: 2026-02-21
**Type**: teaching
**Topic**: R3F GlebSphere in vanilla Three.js - complete equivalence map + post-processing implementation

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/3d-design-specialist/` for night 1 learnings
- Found: Night 1 recipe (glass params, 6-light studio, animation frequencies, Meshy workflow)
- Found: Meshy refinement task status (019c7e93 = SUCCEEDED, 1.7MB)
- Applied: All night 1 parameters directly. No rediscovery needed. Memory worked.

---

## Core Teaching: R3F to Vanilla Three.js Equivalence Map

This map lets you build R3F scenes in vanilla Three.js for CDN delivery, then trivially port to R3F later.

```
R3F                                          Vanilla Three.js
-----------------------------------------------------------------------
<Canvas camera={{position:[0,0,4], fov:45}}  new THREE.PerspectiveCamera(45, w/h, 0.1, 100)
                                             camera.position.set(0,0,4)

<sphereGeometry args={[1.2, 128, 128]} />    new THREE.SphereGeometry(1.2, 128, 128)

<MeshTransmissionMaterial                    new THREE.MeshPhysicalMaterial({
  transmission={1}                             transmission: 1.0,
  thickness={0.8}                              thickness: 0.8,
  roughness={0.05}                             roughness: 0.05,
  ior={1.5}                                    ior: 1.5,
  chromaticAberration={0.8}                    // handled by post-processing ShaderPass
  backside={true}                              side: THREE.DoubleSide,
  color="#88ccff"                              color: new THREE.Color(0x88ccff),
  attenuationColor="#2a93c1"                   attenuationColor: new THREE.Color(0x2a93c1),
/>                                             attenuationDistance: 0.5,
                                               specularColor: new THREE.Color(0xC8A84A),
                                               envMapIntensity: 2.5,
                                               transparent: true, depthWrite: false
                                             })

<Float speed={1.5} floatIntensity={0.5}>     // Float group with useFrame-equivalent animation:
                                             floatY = sin(t*0.8)*0.12 + sin(t*0.5)*0.05
                                             floatX = sin(t*0.6)*0.04 + cos(t*0.35)*0.02

useFrame({ mouse }) =>                       canvas.addEventListener('mousemove', ...)
  mesh.rotation.y = mouse.x * 0.3           + lerp with 4% factor per frame

<Environment files="studio.hdr" />          new RGBELoader().load(path, callback)
                                             + PMREMGenerator.fromEquirectangular(texture)

<EffectComposer>                             new EffectComposer(renderer)
  <Bloom                                     + new UnrealBloomPass(size, strength, radius, threshold)
    luminanceThreshold={0.85}
    intensity={0.35}
    radius={0.4} />

  <ChromaticAberration                       Custom ShaderPass with GLSL:
    offset={[0.002,0.002]} />                  abb = aberrationStrength * dist^2 * 3.0
                                               R = sample(uv - dir*abb*1.2).r
                                               G = sample(uv).g
                                               B = sample(uv + dir*abb*1.0).b

  <Vignette offset={0.5} darkness={0.8} />  Combined in same ShaderPass:
                                               vignette = 1.0 - smoothstep(0.5, 0.5+0.8, dist)
</EffectComposer>
```

---

## Key Discovery: ChromaticAberration GLSL Implementation

The R3F `ChromaticAberration` uses a screen-space offset. The equivalent GLSL:

```glsl
vec2 center = vec2(0.5);
vec2 offset = vUv - center;
float dist = length(offset);

// Key: dist^2 falloff means aberration is VERY subtle near center,
// pronounced only at extreme edges. This matches Gleb's aesthetic.
float abb = aberrationStrength * dist * dist * 3.0;
vec2 dir = normalize(offset + 0.0001);  // +epsilon avoids normalize(0,0)

float r = texture2D(tDiffuse, vUv - dir * abb * 1.2).r;
float g = texture2D(tDiffuse, vUv).g;                    // green = no shift
float b = texture2D(tDiffuse, vUv + dir * abb * 1.0).b;
```

With `aberrationStrength = 0.0018`, this creates subtle chromatic fringing at edges.
At center of screen: effectively 0. At corners: ~0.005 pixel offset. Feels physically real.

---

## Meshy Workflow: Final Confirmed Parameters

### Production Decision
- **Use PREVIEW model (683KB) for web delivery** - identical visual quality after glass material override
- **REFINED model (1.7MB)** = only needed if Meshy's generated textures matter (non-glass use case)
- Glass transmission overrides ALL Meshy materials anyway, so UV quality from refinement = unused

### GLB Loading Pattern
```javascript
const gltfLoader = new GLTFLoader()
gltfLoader.load(glbPath, (gltf) => {
  const model = gltf.scene

  // ALWAYS traverse and override materials for glass use case
  model.traverse((child) => {
    if (child.isMesh) {
      child.material = createGlassMaterial()
    }
  })

  // Auto-center and normalize scale
  const box = new THREE.Box3().setFromObject(model)
  const center = box.getCenter(new THREE.Vector3())
  const size = box.getSize(new THREE.Vector3())
  const maxDim = Math.max(size.x, size.y, size.z)
  model.position.sub(center)               // center
  model.scale.setScalar(2.5 / maxDim)      // normalize to ~2.5 units
})
```

---

## Mode System Pattern (Applicable to Avatar)

```javascript
const modeColors = {
  idle:     { innerIntensity: 3.0, bloomStrength: 0.35 },
  blue:     { innerIntensity: 4.5, bloomStrength: 0.55 },
  orange:   { innerIntensity: 4.0, bloomStrength: 0.50 },
  speaking: { innerIntensity: 6.0, bloomStrength: 0.70,
              pulse: true }  // add sin-based scale fluctuation
}

// Smooth lerp transitions (NOT instant jumps)
// In useFrame or requestAnimationFrame:
innerMat.emissiveIntensity = lerp(current, target, 0.05)  // 5% per frame = ~1 sec transition
```

---

## Known Gotcha: HDRI Serving

| Context | HDRI Status |
|---------|-------------|
| `file://` protocol | FAILS (cross-origin) |
| `python3 -m http.server` | WORKS |
| WordPress CDN | WORKS (same domain) |
| Cross-domain CDN | FAILS unless CORS headers |

**Solution for deployment**: Place HDRI in WordPress uploads, serve via same domain.

---

## Day 3 Next Steps (Critical Path)

1. `npm create vite@latest` - actual React project
2. `npm install @react-three/fiber @react-three/drei @react-three/postprocessing`
3. Build `GlebSphere.jsx` using actual `<MeshTransmissionMaterial samples={8} />`
4. Test DepthOfField from `@react-three/postprocessing` (handles transmission correctly)
5. Research Poly Haven CORS headers for direct CDN HDRI reference

---

## Files

- Main scene: `exports/gleb-r3f-day2.html`
- Meshy showcase: `exports/gleb-meshy-showcase-day2.html`
- Report: `exports/3d-mastery-day2-report.md`
- Refined GLB: `exports/3d-models/glass-orb-refined-019c7e93.glb`
