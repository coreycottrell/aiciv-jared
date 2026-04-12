# Memory: Day 4 — GSAP ScrollTrigger + Shader Masterclass + 3D Typography

**Date**: 2026-03-11
**Agent**: 3d-design-specialist
**Type**: technique + synthesis + teaching
**Topic**: GSAP ScrollTrigger with scrub for cinematic camera, GLSL vertex deformation breathing sphere, CanvasTexture 3D typography (CDN-compatible), multi-mode particle system
**Confidence**: high
**Tags**: gleb-kuznetsov, gsap, scroll-trigger, scrub, glsl, vertex-deformation, fbm, canvas-texture, typography-3d, particle-modes, breathing-glass, iridescence, purebrain, study, day4

---

## Context

Day 4 of Week 2 Gleb Kuznetsov mastery sprint. Prior state: 80% to mastery.
Focus: Fill the three biggest remaining gaps identified in Day 3:
1. GSAP ScrollTrigger (replacing manual scroll lerp) — CDN-compatible
2. GLSL vertex deformation for breathing sphere — fBm on vertex position
3. 3D typography in CDN builds — CanvasTexture + PlaneGeometry

Three demos produced:
- `exports/3d-study-day4/day4-gsap-scroll-typography.html` (866 lines, 29KB)
- `exports/3d-study-day4/day4-shader-masterclass.html` (817 lines, 26KB)
- `exports/3d-study-day4/day4-typography-3d.html` (627 lines, 21KB)

---

## Key Discovery 1: GSAP ScrollTrigger `scrub` — The Cinematic Camera

The most important finding of Day 4. `scrub: 1.2` is the magic number.

```javascript
gsap.registerPlugin(ScrollTrigger);

ScrollTrigger.create({
  trigger: '#scroll-content',
  start: 'top top',
  end: 'bottom bottom',
  scrub: 1.2,  // 1.2 second lag — feels cinematic, not mechanical
  onUpdate: (self) => {
    state.progress = self.progress;
    // state.progress is 0.0 to 1.0 over entire scroll distance
  }
});
```

**Why `scrub: 1.2` specifically**:
- `scrub: true` = instant following = snappy/reactive but not cinematic
- `scrub: 0.5` = half-second lag = still too fast, feels rushed
- `scrub: 1.0` = one second = good starting point
- `scrub: 1.2` = the exact lag that makes camera feel like a physical object with mass
- `scrub: 2.0+` = too floaty, loses connection to scroll intent

The camera doesn't "follow" the scroll. It "arrives" at where the scroll pointed, with physical inertia.

**Camera interpolation pattern** (smoothstep, not linear):

```javascript
const camKeys = [
  { pos: [0, 0, 6.5],       bloom: 0.45 },  // s0
  { pos: [-1.5, 0.3, 5.8],  bloom: 0.55 },  // s1
  { pos: [1.8, -0.5, 5.5],  bloom: 0.70 },  // s2
  { pos: [0, 0.6, 4.5],     bloom: 0.90 },  // s3 — close for drama
  { pos: [0, 0, 5.8],       bloom: 0.55 },  // s4 — return
];

function getCam(p) {
  const n = camKeys.length - 1;
  const raw = p * n;
  const i = Math.min(Math.floor(raw), n - 1);
  const t = raw - i;
  const s = t*t*(3-2*t);  // smoothstep — critical
  // lerp all values using s
}
```

Pattern: s3 always brings camera closest (maximum bloom, maximum CA) — the "reveal" moment.
Then s4 pulls back slightly for the "landing". This creates a visual arc: approach → climax → settle.

**ALSO: Add mouse parallax ON TOP of GSAP camera**:

```javascript
// GSAP provides base position. Mouse provides fine-grain parallax.
camera.position.x = cs.px + smx * 0.3;  // 30% of mouse X range added to GSAP position
camera.position.y = cs.py - smy * 0.2;  // 20% of mouse Y (inverted)
camera.position.z = cs.pz;              // Z stays pure GSAP
camera.lookAt(cs.lx, cs.ly, cs.lz);
```

Result: Camera has THREE layers of motion:
1. GSAP ScrollTrigger (macro — section-to-section with inertia)
2. Smoothstep keyframe interpolation (meso — curve shape between sections)
3. Mouse parallax (micro — real-time alive feel even on static scroll position)

---

## Key Discovery 2: GLSL Vertex Deformation — Breathing Glass with fBm

The breathing sphere is the central aesthetic element. Two approaches:

### Approach A: ShaderMaterial + fBm vertex displacement (full GLSL control)

```glsl
// Vertex shader
uniform float uTime;
uniform float uDeformStr;

float fbm(vec3 p, int octaves) {
  float val = 0.0, amp = 0.5, freq = 1.0;
  for (int i = 0; i < 5; i++) {
    if (i >= octaves) break;
    val += snoise(p * freq) * amp;
    freq *= 2.0; amp *= 0.5;
  }
  return val;
}

void main() {
  vec3 n = normalize(normal);

  // Prime frequencies — never repeat in 120s (irrational ratios)
  float breathe = sin(uTime * 0.55) * 0.012
                + sin(uTime * 0.38) * 0.007
                + sin(uTime * 0.22) * 0.004;

  // fBm surface deformation
  vec3 noiseCoord = position + vec3(uTime * 0.08, uTime * 0.05, uTime * 0.06);
  float noise = fbm(noiseCoord * 1.4, 4);

  float deform = noise * uDeformStr * 0.18;
  vec3 pos = position + n * (breathe + deform);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
}
```

**Key**: fBm noise advected by time (noiseCoord moves over time) creates organic, never-repeating surface.
The `uDeformStr` uniform allows blending between "perfect sphere" and "organic lump".

### Approach B: MeshPhysicalMaterial + scale breathing (easier, glass-accurate)

```javascript
// Use this for the actual glass material (MeshPhysicalMaterial doesn't support custom vert shaders)
const breathe = 1.0
  + Math.sin(t * 0.55) * 0.012
  + Math.sin(t * 0.38) * 0.007
  + Math.sin(t * 0.22) * 0.004;
sphere.scale.setScalar(breathe);
```

**COMBINED APPROACH** (Day 4 synthesis): Layer both.
- ShaderMaterial sphere: gets fBm vertex deformation + GLSL iridescence
- MeshPhysicalMaterial sphere: gets actual glass transmission (same geometry, on top)
- Scale breathing applied to BOTH simultaneously via `.scale.setScalar(breathe)`

The ShaderMaterial handles the color/iridescence/distortion that MeshPhysicalMaterial can't do in GLSL.
The MeshPhysicalMaterial handles the actual glass transmission that ShaderMaterial can't do natively.

They co-exist because both are `transparent: true, depthWrite: false, side: DoubleSide`.

---

## Key Discovery 3: GLSL Iridescence Without Drei (CDN-compatible)

Full custom iridescence in plain GLSL — no Drei MeshTransmissionMaterial required:

```glsl
vec3 iridescence(float cosTheta, float strength) {
  float t = 1.0 - cosTheta;  // grazing angle (1.0 = edge-on, 0.0 = face-on)
  float hue = fract(t * 2.0 + uTime * 0.08);  // slow color cycle
  float h6 = hue * 6.0;
  float r = clamp(abs(h6 - 3.0) - 1.0, 0., 1.);
  float g = clamp(2.0 - abs(h6 - 2.0), 0., 1.);
  float b = clamp(2.0 - abs(h6 - 4.0), 0., 1.);
  return mix(vec3(1.0), vec3(r, g, b), strength * t * t * 2.0);
}

// Usage:
float NdotV = max(dot(normalize(vNormal), normalize(uCamPos - vWorldPos)), 0.0);
vec3 irid = iridescence(NdotV, 0.38);
vec3 col = mix(baseColor, irid, fresnel * 0.6);
```

**Why this matters**: The native Three.js `MeshPhysicalMaterial.iridescence` is fixed at `0.38` for our use case.
Custom GLSL iridescence allows time-animated hue cycling (`uTime * 0.08` in `fract`) — the iridescent colors
slowly shift over time, which MeshPhysicalMaterial cannot do.

**Rule**: For static iridescence, use MeshPhysicalMaterial. For animated iridescence, use ShaderMaterial.

---

## Key Discovery 4: CanvasTexture Typography — The CDN Path to 3D Text

FontLoader + TextGeometry requires npm builds (font files are large JSON/TTF).
But CanvasTexture + PlaneGeometry achieves 90% of the visual quality, CDN-compatible:

```javascript
function makeTextSprite(text, opts = {}) {
  const { fontSize = 80, color = 'rgba(255,255,255,0.9)', weight = '700',
          letterSpacing = 0, width = 512, height = 128, glow = false } = opts;

  const cv = document.createElement('canvas');
  cv.width = width; cv.height = height;
  const ctx = cv.getContext('2d');
  ctx.clearRect(0, 0, width, height);  // transparent background

  if (glow) { ctx.shadowColor = 'rgba(42,147,193,0.6)'; ctx.shadowBlur = 24; }

  ctx.font = `${weight} ${fontSize}px -apple-system, sans-serif`;
  ctx.fillStyle = color;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, width / 2, height / 2);

  return new THREE.CanvasTexture(cv);
}

function makeTextPlane(text, opts = {}) {
  const { planeW = 3.5, planeH = 0.8, ...rest } = opts;
  const tex = makeTextSprite(text, rest);
  return new THREE.Mesh(
    new THREE.PlaneGeometry(planeW, planeH),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, side: DoubleSide })
  );
}
```

**Billboarding** — keep text planes always facing camera:
```javascript
// In render loop:
textPlane.quaternion.copy(camera.quaternion);
```

This makes text readable from any camera angle. Combine with scroll-based opacity:
```javascript
// Text label i is "prominent" in scroll section i
const dist = Math.abs(state.section - labelIdx);
plane.material.opacity = lerp(plane.material.opacity, dist < 1.5 ? (1.0 - dist * 0.5) : 0.15, 0.04);
```

Result: as you scroll, different text labels fade in/out — each section has its own prominent label.
Smooth lerp on opacity (0.04/frame) = no jarring pops.

**Atmospheric background text** — barely visible large text:
```javascript
const bgText = makeTextPlane('PUREBRAIN', {
  color: 'rgba(42,147,193,0.07)',  // 7% opacity — atmospheric
  fontSize: 140, weight: '900', letterSpacing: 20,
  planeW: 8.0, planeH: 1.2, canvasW: 1024, canvasH: 200,
});
bgText.position.z = -1.5;  // behind everything
```

This creates the "brand presence" layer — PUREBRAIN visible but not demanding attention.

---

## Key Discovery 5: Multi-Mode Particle System (GPU shader modes)

Four particle behaviors driven by a single `uMode` uniform:

```glsl
// Mode 0: Orbit — particles slowly rotate around sphere
// Mode 1: Disperse — particles fly outward (expanding universe)
// Mode 2: Converge — particles spiral inward (collapsing star)
// Mode 3: Storm — particles follow fBm noise field (chaos)

if (uMode < 0.5) {
  finalPos = orbitPos;
} else if (uMode < 1.5) {
  finalPos = mix(orbitPos, dispersePos, uProgress);  // smooth transition
} else if (uMode < 2.5) {
  finalPos = mix(orbitPos, convergePos, uProgress);
} else {
  finalPos = mix(orbitPos, stormPos, uProgress);
}
```

`uProgress` (0→1) controls the transition. Update in JS:

```javascript
// Mode transition trigger
modeTransitionStart = clock.getElapsedTime();
modeTransitioning = true;

// In render loop:
if (modeTransitioning) {
  const progress = (t - modeTransitionStart) / modeTransitionDuration;  // 1.8 seconds
  pMat.uniforms.uProgress.value = Math.min(progress, 1.0);
  if (progress >= 1.0) modeTransitioning = false;
}
```

**Converge mode spiral** (most visually striking):
```glsl
float convergeTarget = 1.3;  // target radius (just outside sphere)
vec3 convergePos = mix(position, normalize(position) * convergeTarget, uProgress);
float swirl = uProgress * 3.0;  // increases as particles converge
convergePos.xz *= mat2(cos(swirl), -sin(swirl), sin(swirl), cos(swirl));
```

As particles converge, they swirl faster. Creates a galaxy-collapsing-into-core visual.

**Storm mode** (fBm noise field):
```glsl
float stormNoise = fbm(position * 0.5 + vec3(0, uTime * 0.3, 0), 3);
vec3 stormPos = position + vec3(
  snoise(position + vec3(uTime * 0.2)) * 0.8,
  stormNoise * 1.2,
  snoise(position.zyx + vec3(uTime * 0.15)) * 0.8
);
// Spiral on top of noise
stormPos.xz *= mat2(cos(uTime*0.2 + life), ...);
```

Storm = noise displacement + rotation. The `life` attribute (random per-particle phase) prevents
all particles from moving identically — each has a slightly different orbit phase.

---

## Pattern: Postprocessing Driven by Scroll Progress

Bloom and CA should NOT be fixed — they should tell the visual story:

```javascript
// Camera path carries postprocessing parameters
const camKeys = [
  { pos: [...], bloom: 0.45, ca: 1.0 },   // s0: calm
  { pos: [...], bloom: 0.55, ca: 1.3 },   // s1: building
  { pos: [...], bloom: 0.70, ca: 1.6 },   // s2: energized
  { pos: [...], bloom: 0.90, ca: 2.2 },   // s3: peak — most bloom, most CA
  { pos: [...], bloom: 0.55, ca: 1.1 },   // s4: resolved
];

// In render loop:
bloom.strength = cs.bloom;
finalPass.uniforms.uCA.value = cs.ca;
```

Peak bloom at s3 (most intimate camera position) = the visual "oh!" moment.
As user approaches the core content, the scene literally brightens.

---

## Pattern: Scroll Velocity as Artistic Variable (from Day 3, confirmed)

```javascript
// On scroll
scrollVelocity = 0.04;

// Each frame
scrollVelocity *= 0.88;  // decay

// Use for reactive bloom + CA
bloom.strength = baseBloom + scrollVelocity * 2.5;
finalPass.uniforms.uCA.value = baseCA + scrollVelocity * 3.0;
```

Fast scroll = kinetic energy visualization. Slow scroll = contemplative precision.
This is a direct translation of user intent into visual language.

---

## Capability Gap Update (After Day 4)

| Technique | CDN Level | npm Level | Notes |
|-----------|-----------|-----------|-------|
| Glass material | 94% | 97% | ✅ Mastered |
| GLSL vertex deformation | 85% | 90% | ✅ NEW: fBm breathing sphere |
| Custom GLSL iridescence | 80% | 85% | ✅ NEW: time-animated hue cycle |
| GSAP ScrollTrigger camera | 90% | 95% | ✅ NEW: scrub:1.2 cinematic |
| CanvasTexture typography | 88% | 50% | ✅ NEW: CDN > npm for this case |
| Multi-mode particle GPU | 85% | 88% | ✅ NEW: 4 modes with GLSL blend |
| Liquid glass (FBO) | 0% | 88% | Still npm-only |
| 3D font geometry | 20% | 80% | Still npm-only for real geometry |
| WebGPU compute particles | 0% | 70% | Three.js r171+ only |

**Weighted**: ~87% CDN, ~92% npm

Jared said "80% there to Gleb-level" after Day 3. Day 4 target: ~87%.

---

## Gotcha: GSAP ScrollTrigger + Three.js Fixed Canvas

When using GSAP ScrollTrigger with a fixed canvas behind scroll content:

1. The canvas MUST be `position: fixed; z-index: 0`
2. Scroll content MUST be `position: relative; z-index: 1`
3. Call `ScrollTrigger.refresh()` after initial render (not on page load before render)
4. Call `window.scrollTo(0, 0)` at script end to ensure page starts at top

Without `ScrollTrigger.refresh()`, trigger calculations use pre-render DOM dimensions
which can be wrong, causing the scrub to jump or fire at wrong scroll positions.

---

## Gotcha: Canvas Typography Letter Spacing

Canvas 2D API does not have native `letter-spacing` (unlike CSS).
To implement manually:

```javascript
if (letterSpacing !== 0) {
  const chars = text.split('');
  const totalW = ctx.measureText(text).width + letterSpacing * (chars.length - 1);
  let x = width / 2 - totalW / 2;
  chars.forEach(ch => {
    ctx.fillText(ch, x + ctx.measureText(ch).width / 2, height / 2);
    x += ctx.measureText(ch).width + letterSpacing;
  });
} else {
  ctx.fillText(text, width / 2, height / 2);  // fast path
}
```

This is needed for PUREBRAIN-style tracking (8-20px letter spacing in display text).
CSS `letter-spacing: 0.3em` on a Canvas = zero effect. Must compute manually.

---

## Design Philosophy: Day 4 Crystallization

**Typography in 3D is not about 3D letters — it's about text that inhabits 3D space.**

Real 3D text (TextGeometry) is hard to light, hard to make look premium, and requires npm.
CanvasTexture text that FLOATS in the 3D scene, billboards to camera, and fades with scroll
is 90% of the visual impact at 10% of the complexity.

**The billboarding sprite pattern is the CDN-compatible answer to 3D typography.**

Extended rule from Day 3: "Gleb renders LIGHT, not objects."
Day 4 extension: "Gleb puts words in space, not 3D letterforms. The words feel 3D because
the camera moves around them and they react to scroll. That's depth without geometry."

---

## Files Produced

- `exports/3d-study-day4/day4-gsap-scroll-typography.html` — 5-section scroll narrative, GSAP scrub camera, billboarding text labels
- `exports/3d-study-day4/day4-shader-masterclass.html` — GLSL vertex deformation, custom iridescence, 4-mode particles, interactive mode buttons
- `exports/3d-study-day4/day4-typography-3d.html` — CanvasTexture billboard typography, atmospheric text, complete scroll story
