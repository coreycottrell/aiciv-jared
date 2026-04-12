# Gleb Mastery Day 3 - Vite R3F Production Project

**Date**: 2026-02-21
**Type**: teaching
**Topic**: Scaffolding real React/Vite R3F project with MeshTransmissionMaterial + postprocessing

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/3d-design-specialist/` for all prior sprint learnings
- Found: Night 1 recipe (glass params, 6-light studio, animation), Day 2 R3F equivalence map
- Found: Meshy refinement workflow (preview 668KB = web-ready)
- Applied: ALL parameters directly. Zero rediscovery. Memory system working exactly as designed.

---

## Core Teaching: Real MeshTransmissionMaterial vs Vanilla

This is the key insight Day 3 makes concrete:

```
Vanilla THREE.MeshPhysicalMaterial    @react-three/drei MeshTransmissionMaterial
--------------------------------------------
transmission: 1.0                     transmission={1}
thickness: 0.8                        thickness={0.8}
(no samples param)                    samples={8}     <- 8 refraction rays
(single FBO, fixed)                   resolution={1024}  <- FBO resolution control
(no material-level aberration)        chromaticAberration={0.8}  <- per-channel split
~90% of Gleb quality                  ~100% of Gleb quality
```

**The remaining 10% difference** is all in `samples` and `resolution`. Higher samples = softer, more accurate refraction of background objects seen through glass. This is especially visible when multiple glass objects overlap.

---

## Discovery: Poly Haven CDN CORS Confirmed

```bash
curl -sI "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/studio_small_09_1k.hdr"
# -> access-control-allow-origin: *
```

Poly Haven CDN serves ALL HDRIs with `access-control-allow-origin: *`.
No need to host HDRI on same domain. Direct CDN reference works in browser.

```jsx
// This works directly in any browser (no CORS error):
<Environment files="https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/studio_small_09_1k.hdr" />
```

BUT: Local copy in public/assets/ is still preferred for production (no external dependency,
faster load if CDN varies, works offline). Keep CDN as fallback option.

---

## Discovery: DepthOfField Ordering in EffectComposer

Order of effects in EffectComposer is significant. The correct Gleb order:

```jsx
<EffectComposer multisampling={4}>
  <DepthOfField />          // 1st: defocus scene before bloom
  <Bloom />                 // 2nd: bloom the defocused image
  <ChromaticAberration />   // 3rd: screen-edge color split
  <Vignette />              // 4th: dark corners on final composite
</EffectComposer>
```

If Bloom comes before DoF: bloomed halos get blurred by DoF = muddy look.
If ChromaticAberration before Vignette: aberration affects vignetted dark area = correct.

---

## Discovery: Two-Level ChromaticAberration

Gleb uses chromatic aberration at TWO levels simultaneously:

1. **Material level**: `chromaticAberration={0.8}` on `MeshTransmissionMaterial`
   - Splits colors within the refracted image INSIDE the glass
   - Only affects the glass sphere's internal content
   - This is the "looking through a prism" effect

2. **PostProcessing level**: `<ChromaticAberration offset={[0.002, 0.002]} />`
   - Splits colors across the entire rendered frame
   - Distance-squared falloff (edges more than center)
   - Applied to the whole scene including background

Both together = physically real feel. Material aberration = what you see THROUGH glass.
PostProcess aberration = what the CAMERA LENS does.

---

## Scroll Animation Without ScrollControls Wrapper

`@react-three/drei`'s `ScrollControls` requires the canvas to be inside its wrapper.
This limits flexibility when embedding in existing web pages.

Better pattern for web integration:

```javascript
// In useFrame() - reads native window scroll, smoothed with lerp
const scroll = useRef(0)

useFrame(() => {
  const maxScroll = document.body.scrollHeight - window.innerHeight
  const rawScroll = maxScroll > 0 ? window.scrollY / maxScroll : 0
  scroll.current += (rawScroll - scroll.current) * 0.08  // 8% lerp

  // Now use scroll.current (0-1) to drive transforms
  groupRef.current.rotation.y = scroll.current * Math.PI * 2
})
```

This works in ANY web page without ScrollControls wrapping the Canvas.
8% lerp = smooth but responsive. 4% = very sluggish. 15% = snappy.

---

## Vite Build: Package Sizes

Full R3F + postprocessing stack:
```
dist/assets/index-*.js   1,242.00 kB uncompressed
                            345.19 kB gzipped
```

345KB gzipped is acceptable for a 3D scene. Comparison:
- Three.js alone: ~150KB gzipped
- R3F adds: ~40KB gzipped
- Drei adds: ~80KB gzipped
- Postprocessing adds: ~75KB gzipped

For optimization, code-split with rollupOptions.manualChunks:
```javascript
manualChunks: {
  three: ['three'],
  r3f: ['@react-three/fiber', '@react-three/drei'],
  pp: ['@react-three/postprocessing', 'postprocessing'],
}
```
This defers non-critical chunks and allows parallel loading.

---

## Day 4 Next Steps

1. Load Meshy GLB via `useGLTF` from drei - traverse and replace materials
2. Code splitting via `vite.config.js` manualChunks
3. `framer-motion` scroll spring for more natural scroll feel
4. WordPress embed strategy decision (iframe vs bundle vs plugin)

---

## Files

- Main project: `exports/gleb-r3f-scene/`
- GlebSphere.jsx: `exports/gleb-r3f-scene/src/GlebSphere.jsx`
- Scene.jsx: `exports/gleb-r3f-scene/src/Scene.jsx`
- App.jsx: `exports/gleb-r3f-scene/src/App.jsx`
- Day 3 report: `exports/3d-mastery-day3-report.md`
- Production build: `exports/gleb-r3f-scene/dist/`
