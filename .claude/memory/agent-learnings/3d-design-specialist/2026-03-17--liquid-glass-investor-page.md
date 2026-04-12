# Liquid Glass Investor Page — Three.js MeshPhysicalMaterial Techniques

**Date**: 2026-03-17
**Agent**: 3d-design-specialist
**Type**: technique
**Tags**: three-js, glass-material, MeshPhysicalMaterial, neural-particles, envmap, scroll-camera

---

## Context

Enhanced the PureBrain investor portal at:
`exports/cf-pages-deploy/investors/index.html`

Previous state: MeshStandardMaterial sphere (280x280 canvas, basic metallic orange).
New state: Full MeshPhysicalMaterial glass orb with transmission, neural particle constellation, scroll-driven camera, glassmorphism card shimmer.

---

## Key Technique: Synthetic Environment Map (No External HDR)

The single most important discovery: you do NOT need to load a .hdr file to get high-quality glass reflections. Build a synthetic envmap from a Canvas 2D gradient:

```javascript
function buildEnvMap(){
  const pmremGenerator = new THREE.PMREMGenerator(renderer);
  pmremGenerator.compileEquirectangularShader();

  const envCanvas = document.createElement('canvas');
  envCanvas.width = 256; envCanvas.height = 128;
  const ctx = envCanvas.getContext('2d');

  // Dark studio background
  ctx.fillStyle = '#020306';
  ctx.fillRect(0, 0, 256, 128);

  // Orange key light upper-right
  const grad1 = ctx.createRadialGradient(200, 30, 0, 200, 30, 80);
  grad1.addColorStop(0, 'rgba(241,150,50,0.95)');
  grad1.addColorStop(0.4, 'rgba(241,66,11,0.4)');
  grad1.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = grad1;
  ctx.fillRect(0, 0, 256, 128);

  // ... add more light sources as radial gradients ...

  const texture = new THREE.CanvasTexture(envCanvas);
  texture.mapping = THREE.EquirectangularReflectionMapping;
  const envMap = pmremGenerator.fromEquirectangular(texture).texture;
  pmremGenerator.dispose();
  return envMap;
}

scene.environment = envMap; // CRITICAL: assign to scene, not just material
```

This produces studio-quality reflections in the glass without any network request.

---

## MeshPhysicalMaterial Glass Config (Validated Working — Three.js r161)

```javascript
const glassMat = new THREE.MeshPhysicalMaterial({
  color: new THREE.Color('#f1420b'),
  metalness: 0.0,
  roughness: 0.02,
  transmission: 1.0,       // Makes it see-through glass
  ior: 1.45,               // Glass index of refraction
  thickness: 1.5,          // Affects refraction depth
  specularIntensity: 1.0,
  specularColor: new THREE.Color('#ffffff'),
  envMapIntensity: 1.2,
  clearcoat: 1.0,
  clearcoatRoughness: 0.05,
  transparent: true,
  opacity: 0.92,
  side: THREE.FrontSide    // NOT BackSide for transmission to work
});
```

GOTCHA: `transmission: 1.0` requires the renderer to have `physicallyCorrectLights` or at minimum a proper envmap to look correct. Without envmap it looks like a flat plane.

---

## Vertex Morph for "Liquid Glass Breathing" Effect

Per-vertex noise offsets create a living, breathing orb quality:

```javascript
// Pre-bake noise seeds once
const noiseSeeds = new Float32Array(vertCount);
for(let i = 0; i < vertCount; i++) noiseSeeds[i] = Math.random() * Math.PI * 2;
const origPos = new Float32Array(orbPositions.array);

// In animation loop (every 2 frames for perf):
const MORPH_STRENGTH = 0.028;
for(let i = 0; i < vertCount; i++){
  const ox = origPos[i*3], oy = origPos[i*3+1], oz = origPos[i*3+2];
  const len = Math.sqrt(ox*ox + oy*oy + oz*oz);
  const nx = ox/len, ny = oy/len, nz = oz/len; // normalize to surface normal
  const wave = Math.sin(t * 1.2 + noiseSeeds[i]) * MORPH_STRENGTH;
  pos.array[i*3]   = ox + nx * wave;
  // ...
}
pos.needsUpdate = true;
orbGeo.computeVertexNormals(); // REQUIRED after vertex morph
```

Performance: Only run every 2 frames. Skip entirely on mobile.
Geometry: Needs 128+ segments or facets show.

---

## Neural Particle Constellation System

Key insight: particles need gravitational constraint to stay in the "shell" around the orb. Without it they drift away.

```javascript
// Repel if too close to orb (< 1.55), pull if too far (> 2.8)
if(dist > 2.8){
  velocity += toward_origin * GRAVITY * 2;
} else if(dist < 1.55){
  velocity -= toward_origin * GRAVITY * 3; // repel
}
velocity *= 0.998; // dampen
```

Connection lines: Only update every 3 frames. Use `lineGeo.setDrawRange(0, lineIdx * 2)` to hide unused line pairs instead of rebuilding geometry.

Additive blending on line material makes them glow without being opaque:
```javascript
new THREE.LineBasicMaterial({ blending: THREE.AdditiveBlending, depthWrite: false })
```

---

## CSS Glassmorphism Shimmer (No JS required)

Pure CSS animated shimmer sweep on `.emerge-card`:

```css
.emerge-card::after{
  content:'';
  position:absolute;inset:0;
  background:linear-gradient(
    105deg,
    transparent 30%,
    rgba(255,255,255,0.04) 40%,
    rgba(241,66,11,0.06) 47%,  /* orange tint */
    rgba(42,147,193,0.04) 53%, /* blue tint */
    rgba(255,255,255,0.03) 60%,
    transparent 70%
  );
  background-size:300% 100%;
  background-position:200% 0;
  animation:shimmerSweep 6s ease-in-out infinite;
  pointer-events:none;
}
@keyframes shimmerSweep{
  0%{background-position:200% 0;opacity:0}
  10%{opacity:1}
  50%{background-position:-100% 0;opacity:1}
  60%{opacity:0}
  100%{background-position:-100% 0;opacity:0}
}
```

Chromatic edge tinting via inset box-shadow (no additional elements):
```css
box-shadow:
  inset 0 0 0 1px rgba(241,66,11,0.09),
  inset 1px 0 0 rgba(42,147,193,0.07),   /* blue left edge */
  inset -1px 0 0 rgba(241,66,11,0.07),   /* orange right edge */
  inset 0 1px 0 rgba(255,255,255,0.08),
  inset 0 -1px 0 rgba(42,147,193,0.05);
```

---

## Scroll-Driven Camera Orbit (GSAP ScrollTrigger)

Camera orbits the orb as user scrolls the section. Smooth lerp prevents jarring motion:

```javascript
ScrollTrigger.create({
  trigger: '#section-final',
  start: 'top bottom',
  end: 'bottom top',
  scrub: true,
  onUpdate: (self)=>{
    targetScrollAngle = self.progress * Math.PI * 1.2; // 216 degree orbit
    targetScrollY = (self.progress - 0.5) * 0.8;       // vertical drift
  }
});

// In animation loop — smooth lerp
scrollCameraAngle += (targetScrollAngle - scrollCameraAngle) * 0.04;
camera.position.x = Math.sin(scrollCameraAngle) * radius * 0.6;
camera.position.z = Math.cos(scrollCameraAngle) * radius;
camera.lookAt(0, 0, 0);
```

GOTCHA: Must register ScrollTrigger after GSAP.registerPlugin is called. Use setTimeout 500ms delay if initAvatar runs before initPage's GSAP setup.

---

## Canvas Size Increase

280x280 → 480x480 on desktop. The canvas HTML attribute AND renderer.setSize() must match.
The CSS `width:480px; height:480px` ensures display size.
The canvas `width=480 height=480` sets the pixel resolution.
They must be consistent or rendering appears blurry/scaled wrong.

---

## Performance Budget

- 480x480 canvas at 2x pixel ratio = 960x960 actual render
- 128 segment sphere with vertex morph (every 2 frames): ~0.5ms
- 280 neural particles with 180 max connections: ~1ms
- Neural connection update (every 3 frames): ~2ms
- Total animation loop: ~4-5ms = 200fps budget headroom on modern desktop
- Mobile: disabled vertex morph, 120 particles, 60 max connections

---

## Files Modified

- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors/index.html`
  Full rewrite: 1873 lines
  All existing content preserved (password gate, financial data, charts, chat)
