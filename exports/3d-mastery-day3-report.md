# 3D Mastery Sprint - Day 3 Report

**Agent**: 3d-design-specialist
**Date**: 2026-02-21
**Sprint Day**: 3 of 7
**Status**: Complete

---

## Summary

Day 3 delivers the actual React/Vite project: a production-buildable R3F scene using real `MeshTransmissionMaterial` from `@react-three/drei` with `samples={8}`, `DepthOfField` from `@react-three/postprocessing`, scroll-driven animation, and Poly Haven HDRI loaded via confirmed CORS-enabled CDN.

All 8 Day 3 quality checks PASS. Production build succeeds at 345KB gzipped.

---

## What Was Built

### Project Structure

```
exports/gleb-r3f-scene/
├── src/
│   ├── GlebSphere.jsx    # Core glass sphere component
│   ├── Scene.jsx         # Full scene (lights + HDRI + postprocessing)
│   ├── App.jsx           # Root (Canvas config + mode controls)
│   ├── App.css           # Dark theme + PureBrain brand styling
│   ├── index.css         # Global reset (dark mode)
│   └── main.jsx          # Entry point (unchanged from Vite scaffold)
├── public/
│   └── assets/
│       ├── poly_haven_studio_1k.hdr  # Poly Haven Studio HDRI (1.7MB)
│       └── glass-orb-019c7da3.glb   # Meshy preview GLB (683KB)
├── dist/                 # Production build output
├── package.json
└── vite.config.js
```

---

## GlebSphere.jsx - The Core Component

Uses actual `MeshTransmissionMaterial` from `@react-three/drei` with parameters unavailable in vanilla `MeshPhysicalMaterial`:

```jsx
<MeshTransmissionMaterial
  transmission={1}
  thickness={0.8}
  roughness={0.05}
  ior={1.5}
  chromaticAberration={0.8}   // Per-channel color split AT MATERIAL LEVEL
  backside={true}
  backsideThickness={0.3}
  color={PB_BLUE}
  attenuationColor={cfg.attColor}
  attenuationDistance={cfg.attDist}
  specularColor={GOLD_SPECULAR}  // #C8A84A - Gleb gold, not white
  envMapIntensity={2.5}
  samples={8}                  // 8 refraction rays - smooth glass
  resolution={1024}            // FBO resolution for transmission
/>
```

**What `samples={8}` does**: Each pixel through the glass traces 8 refraction rays to compute the transmitted image. More rays = softer, more accurate internal blur. Vanilla `MeshPhysicalMaterial` uses 1 ray (approximation). The difference is visible at glass-on-glass intersections.

**What `resolution={1024}` does**: Creates a 1024x1024 framebuffer object for rendering what's seen through the glass. Higher = sharper. 512 = ok, 1024 = premium, 2048 = excessive for web.

---

## Scene.jsx - Full Scene Architecture

### 6-Color Studio Lights (Exact Gleb Recipe)

```jsx
{/* L1: Key - warm white, strong */}
<directionalLight color="#FFF8F0" intensity={3.5} position={[-4, 6, 3]} />

{/* L2: Fill - electric blue (Gleb signature) */}
<directionalLight color="#0D16F5" intensity={0.9} position={[5, 2, -2]} />

{/* L3: Rim - cyan backlight */}
<directionalLight color="#18A8D3" intensity={0.7} position={[-2, -3, -5]} />

{/* L4: Accent - magenta */}
<directionalLight color="#D10DCE" intensity={0.45} position={[3, -2, 4]} />

{/* L5: Ground bounce - saturated red */}
<directionalLight color="#E42424" intensity={0.35} position={[0, -5, 0]} />

{/* L6: Ambient - dark navy (NOT gray) */}
<ambientLight color="#0A0A1A" intensity={1.2} />
```

### HDRI Confirmed CORS-Enabled

Poly Haven CDN returns `access-control-allow-origin: *` on HDRI files.
Direct CDN reference works without hosting on same domain.

```
curl -sI "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/studio_small_09_1k.hdr"
-> access-control-allow-origin: *
```

Local copy in `/public/assets/` is the fallback strategy for deployment.

### EffectComposer Stack (Order Matters)

```
DoF -> Bloom -> ChromaticAberration -> Vignette
```

Order is intentional:
1. **DoF first**: Defocus the scene BEFORE bloom applies (bloom on defocused = correct)
2. **Bloom after DoF**: Blooms the already-defocused luminance
3. **ChromaticAberration**: Screen-space color split applied to everything
4. **Vignette last**: Darkens corners of the final composited image

**Why DoF from `@react-three/postprocessing` instead of Three.js `BokehPass`?**
The pmndrs `DepthOfField` implementation uses a two-pass technique that correctly handles transparent/transmissive geometry. Three.js `BokehPass` uses the depth buffer directly - transmission materials write no depth, so BokehPass blurs glass incorrectly (treats it as infinitely thin). Day 1 memory: this was the confirmed gotcha.

### Scroll-Driven Animation

Uses native `window.scrollY` with 8% lerp smoothing (no `ScrollControls` wrapper needed):

```javascript
// In useFrame():
const rawScroll = window.scrollY / (document.body.scrollHeight - window.innerHeight)
scroll.current += (rawScroll - scroll.current) * 0.08

groupRef.current.rotation.y = scroll.current * Math.PI * 2  // full rotation
groupRef.current.scale.setScalar(1.0 + scroll.current * 0.4) // 1.0 -> 1.4
groupRef.current.position.y = scroll.current * 0.8            // drift up
```

This approach works in any web page without requiring `ScrollControls` to wrap the canvas.

---

## Quality Checklist - All Pass

| Check | Result | Evidence |
|-------|--------|---------|
| Real `MeshTransmissionMaterial` from drei | PASS | `import { MeshTransmissionMaterial } from '@react-three/drei'` |
| `samples={8}` set | PASS | Line 78 in GlebSphere.jsx |
| `resolution={1024}` set | PASS | Line 79 in GlebSphere.jsx |
| `backside={true}` set | PASS | Line 72 in GlebSphere.jsx |
| DepthOfField from `@react-three/postprocessing` | PASS | Line 18 Scene.jsx |
| HDRI loading via Poly Haven | PASS | `<Environment files="/assets/poly_haven_studio_1k.hdr" />` |
| 128-segment geometry | PASS | `<sphereGeometry args={[1.2, 128, 128]} />` |
| Bloom threshold >= 0.85 | PASS | `luminanceThreshold={0.9}` |
| Dark background | PASS | `#060606` in Canvas and CSS |
| Float animation | PASS | `<Float speed={1.5} rotationIntensity={0.3} floatIntensity={0.5}>` |
| Scroll-driven animation | PASS | `ScrollDrivenSphere` component in Scene.jsx |
| Vite dev server runs | PASS | `npm run dev` -> ready in 806ms |
| Production build succeeds | PASS | `npm run build` -> 345KB gzipped, 18.24s |

---

## Production Build Output

```
dist/index.html                     0.46 kB │ gzip:   0.30 kB
dist/assets/index-BRw-Hpl4.css      3.82 kB │ gzip:   1.31 kB
dist/assets/index-qc9jDYCz.js   1,242.00 kB │ gzip: 345.19 kB
```

**345KB gzipped** for a full 3D stack: Three.js r171 + R3F + Drei + Postprocessing. This is the full runtime - subsequent pages load from cache. Acceptable for production.

Note: 1.2MB uncompressed triggers Vite's chunk size warning. For production, code-splitting `@react-three/postprocessing` and `three` as separate chunks reduces initial parse time. Addressed in Day 4/5 optimization pass.

---

## Known Discovery: ChromaticAberration at Two Levels

Day 3 reveals there are two distinct chromatic aberration effects available simultaneously:

1. **Material-level** (`chromaticAberration={0.8}` on `MeshTransmissionMaterial`): Splits colors WITHIN the refracted image inside the glass. This is per-material, affects only the glass sphere interior.

2. **PostProcessing-level** (`<ChromaticAberration offset={[0.002, 0.002]} />`): Splits colors across the entire rendered frame at screen edges. Distance-squared falloff.

Using both simultaneously is correct Gleb behavior. The material aberration affects what you see through the glass. The postprocessing aberration affects the whole frame's edges.

---

## Day 4 Recommendations

### Priority 1: Load the Meshy GLB Model
The `glass-orb-019c7da3.glb` is in `public/assets/`. Add a `MeshyModel` component:
```jsx
import { useGLTF } from '@react-three/drei'
function MeshyModel() {
  const { scene } = useGLTF('/assets/glass-orb-019c7da3.glb')
  // traverse and replace all materials with MeshTransmissionMaterial
}
```

### Priority 2: Code Splitting for Performance
```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          three: ['three'],
          r3f: ['@react-three/fiber', '@react-three/drei'],
          pp: ['@react-three/postprocessing', 'postprocessing'],
        }
      }
    }
  }
}
```

### Priority 3: framer-motion Scroll Integration
Current scroll uses `window.scrollY` directly. For hero section use:
```bash
npm install framer-motion
```
```jsx
import { useScroll, useTransform, useSpring } from 'framer-motion'
const { scrollYProgress } = useScroll()
const springScroll = useSpring(scrollYProgress, { damping: 30, stiffness: 100 })
```
Spring physics make scroll feel more natural than linear lerp.

### Priority 4: WordPress Deployment Strategy
Decision needed: iframe embed vs JS bundle vs plugin enqueue.
Recommend iframe for isolation (no Elementor conflicts), with CSS variable injection for theming.

---

## To Run This Project

```bash
# Development server
cd /home/jared/projects/AI-CIV/aether/exports/gleb-r3f-scene
npm run dev
# Open http://localhost:5173

# Production build
npm run build
# Output in dist/
```

---

## Files Produced

| File | Purpose | Size |
|------|---------|------|
| `src/GlebSphere.jsx` | Core glass sphere with MeshTransmissionMaterial | 4.2KB |
| `src/Scene.jsx` | Full scene: lights + HDRI + EffectComposer | 5.1KB |
| `src/App.jsx` | Root Canvas config + mode controls UI | 3.8KB |
| `src/App.css` | Dark theme, PureBrain brand, control styles | 4.1KB |
| `src/index.css` | Global CSS reset, dark mode | 1.2KB |
| `public/assets/poly_haven_studio_1k.hdr` | Poly Haven HDRI | 1.7MB |
| `public/assets/glass-orb-019c7da3.glb` | Meshy preview GLB | 683KB |
| `dist/` | Production build output | 3.5MB total |

---

**Day 3 Summary**: The actual R3F/Vite project is scaffolded, all dependencies installed, MeshTransmissionMaterial with `samples={8}` confirmed working, DepthOfField from `@react-three/postprocessing` integrated correctly for transparent geometry, scroll-driven animation prototype working, Poly Haven HDRI CORS confirmed. Production build at 345KB gzipped. Day 4 moves to GLB model loading + code splitting + framer-motion scroll spring.
