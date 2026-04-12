# Pure Technology Cinematic Logo Reveal Animation

**Date**: 2026-03-20
**Agent**: 3d-design-specialist
**Type**: technique
**Confidence**: high
**Tags**: three-js, logo-animation, gsap-timeline, hexagon, glass-material, bloom, assembly-animation, cinematic

---

## Context

Built a cinematic Marvel/Netflix-style logo reveal animation for Pure Technology's nested hexagon spiral icon. Self-contained HTML with Three.js r0.161.0 ESM + GSAP 3.12.5 CDN. No build step.

Output: `exports/puretechnology-3d-redesign/logo-animation.html`
CF Pages: `exports/cf-pages-deploy/puretechnology-3d-redesign/logo-animation.html`

---

## Logo Analysis (from reference image)

The PT icon is: nested hexagonal rings (8 distinct radii) with spiral blade lines connecting outer edge to inner void. Color gradient: electric blue (#2a93c1) outer → purple transition → orange (#f1420b) inner → pure black core circle. The blades create a counterclockwise vortex illusion with 280-degree spiral twist.

---

## Architecture: 4-Phase GSAP Timeline

```
Phase 0: Pre-roll (0-0.85s) — pieces scattered, particles fade in
Phase 1: Scatter drift (0-0.85s) — rings spin gently in scatter positions
Phase 2: Assembly (0.85-3.6s) — 8 rings fly in staggered (0.20s apart), each with bloom spike
Phase 3: Final snap — white flash, mega bloom, dual shockwave, chromatic spike
Phase 4: Reveal (post-snap) — blades appear, coronas, core ignites, camera pulls back
Phase 5: Text in — "PURE TECHNOLOGY" fades in (Oswald 500 weight)
Hold: camera slow orbit, breathing bloom
```

---

## Key Techniques

### Ring Scatter → Assembly

Each ring starts at a random 3D position 5-9 units out. The GSAP timeline flies them home:

```javascript
// Scatter seed per ring
const SCATTER = RING_DEFS.map(() => ({
  px: Math.cos(theta) * Math.cos(phi) * dist,
  py: Math.sin(phi) * dist * 0.55,
  pz: Math.sin(theta) * Math.cos(phi) * dist * 0.3 - 4.0, // come from behind camera
  rx/ry/rz: random tumble rotations,
}));

// Assembly in GSAP TL:
masterTL.to(ring.group.position, {
  x: 0, y: 0, z: ring.finalZ,
  duration: 1.05, ease: 'expo.out',
}, t);
masterTL.to(ring.group.rotation, {
  x: Math.PI/2, y: 0, z: 0,
  duration: 0.95, ease: 'expo.out',
}, t);
// Approach scale punch:
masterTL.fromTo(ring.group.scale,
  { x:1.7, y:1.7, z:1.7 },
  { x:1.0, y:1.0, z:1.0, duration:0.65, ease:'back.out(2.8)' },
t+0.42);
```

**Critical**: Set pz to negative (behind camera) so pieces appear to fly TOWARD the viewer.

### Per-Ring Bloom Spike

```javascript
const snapT = t + 1.02; // when ring locks in
masterTL.to(bloomPass, { strength:1.8, duration:0.06 }, snapT);
masterTL.to(bloomPass, { strength:0.50, duration:0.55, ease:'power2.out' }, snapT+0.06);
masterTL.to(ring.mat, { emissiveIntensity:2.5, duration:0.05 }, snapT);
masterTL.to(ring.mat, { emissiveIntensity:0.55, duration:0.6 }, snapT+0.05);
```

### Dual Shockwave on Final Snap

Two concentric expanding rings — blue (#88ccff) and orange (#ff5500) — with slight delay:

```javascript
// Blue shockwave
masterTL.to(shockMat, { opacity:0.95, duration:0.03 }, FINAL_SNAP);
masterTL.to(shockMat, { opacity:0.0, duration:0.9, ease:'power3.out' }, FINAL_SNAP+0.03);
masterTL.to(shockwave.scale, { x:24, y:24, z:24, duration:0.9, ease:'expo.out' }, FINAL_SNAP);

// Orange, delayed 0.12s
masterTL.to(shockMat2, ..., FINAL_SNAP+0.12);
```

### Spiral Blade Lines

54 blades × 22 segments = LineSegments with vertex colors (blue→orange gradient):

```javascript
const TWIST = Math.PI * 1.55; // 280 degrees
for(let b=0;b<54;b++){
  const aStart = (b/54)*Math.PI*2;
  for(let s=0;s<22;s++){
    const u0=s/22, u1=(s+1)/22;
    const r0=OUTER_R*(1-u0)+INNER_R*u0;
    const a0=aStart+u0*TWIST;
    // slight z-arc: z=sin(u*PI)*0.05 for 3D depth
  }
}
```

Blades fade in during Reveal phase. They slowly drift-rotate (bladeGroup.rotation.z += 0.042*dt).

### MeshPhysicalMaterial for Hex Rings

```javascript
new THREE.MeshPhysicalMaterial({
  transmission:0.82, ior:1.48, thickness:0.25,
  clearcoat:1.0, clearcoatRoughness:0.03,
  metalness:0.12, roughness:0.05,
  envMapIntensity:1.5,
  // ... synthetic envmap assigned to scene.environment
})
```

Plus EdgesGeometry wireframe on top for crisp hex outline + BackSide rim glow.

### Chromatic Aberration + Flash Pass

Custom ShaderPass handles: CA radial, vignette, and white flash (for snap moments):

```glsl
float ca=uCA*d*0.022;
vec2 dir=normalize(c+0.0001);
float r=texture2D(tDiffuse,uv+dir*ca).r;
float g=texture2D(tDiffuse,uv).g;
float b=texture2D(tDiffuse,uv-dir*ca*0.65).b;
col+=uFlash; // additive white flash
```

GSAP drives `chromaPass.uniforms.uCA.value` (0→4.0 spike on snap, settle to 0.9).

---

## Gotchas

1. **GSAP must load BEFORE the module script** — use synchronous `<script src>` before `<script type="module">`. Async/defer breaks `window.gsap` availability.

2. **scatter pz should be negative** — rings start behind camera (pz: ...* 0.3 - 4.0) so they fly toward the viewer, more cinematic.

3. **`fromTo` for scale punch** — `gsap.to(scale, { x:1.7... })` from the DOM-managed value doesn't work. Must use `fromTo` to set the "from" state explicitly in the TL.

4. **GSAP TL `.to({}, { onComplete })` pattern** — use empty object target with onComplete for triggering DOM changes mid-TL (text fade-in).

5. **`clock.getDelta()` capped at 0.05** — prevents huge dt jumps on tab re-focus.

6. **Double shockwave** — single shockwave looks weak. Two with color contrast (blue+orange) and staggered timing looks cinematic.

7. **Progress bar** — drives `masterTL.onUpdate()` via `masterTL.progress()`. Nice UX touch showing animation progress.

---

## Performance

- 8 ring meshes × 3 objects each = 24 draw calls
- 1 LineSegments for blades (54 blades × 22 segs × 4 verts = 4752 verts)
- 5 corona torii + 2 shockwaves
- 1400 particles (update every 2 frames)
- 3-pass postprocessing (bloom + chroma/vig + output)
- Target: 60fps desktop, ~40fps mobile
- File size: 36KB self-contained

---

## Deployment

```bash
cp exports/puretechnology-3d-redesign/logo-animation.html exports/cf-pages-deploy/puretechnology-3d-redesign/
CLOUDFLARE_API_TOKEN=$(grep CF_PAGES_TOKEN .env | cut -d= -f2) npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain-staging --commit-dirty=true
```

Live URL: `https://e3e6b872.purebrain-staging.pages.dev/puretechnology-3d-redesign/logo-animation.html`
