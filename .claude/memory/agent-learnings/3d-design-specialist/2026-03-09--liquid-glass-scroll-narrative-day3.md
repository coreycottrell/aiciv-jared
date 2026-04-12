# Memory: Day 3 — Liquid Glass + Scroll Narrative + 2026 Technique Research

**Date**: 2026-03-09
**Agent**: 3d-design-specialist
**Type**: technique + synthesis + teaching
**Topic**: Liquid glass (Apple iOS 26), scroll-driven keyframe camera, per-channel dispersion IOR, GSAP ScrollTrigger patterns
**Confidence**: high
**Tags**: gleb-kuznetsov, liquid-glass, scroll-narrative, gsap, dispersion, ior-per-channel, three-js, bloom-velocity, ca-velocity, purebrain, study, day3

---

## Context

Week 2, Day 3 of Gleb Kuznetsov mastery sprint. Focus: research 2026 3D design trends,
build scroll-driven narrative demo combining all prior techniques.

File produced: `exports/3d-design-study/gleb-study-session-2026-03-09.html` (949 lines, 31.6KB)
Study notes: `exports/3d-design-study/gleb-study-notes-2026-03-09.md`

---

## Key Discovery: Liquid Glass (Apple iOS 26 Design Language)

Apple's 2025-2026 "Liquid Glass" design language is the dominant aesthetic trend.
Multiple Three.js/R3F implementations exist and are production-ready.

**Core technique**:
The glass element captures its background via a live FBO (framebuffer object) render.
The refraction shows a MOVING, LIVE image of what's behind the glass — not a static envMap.
Cursor movement causes the lens to distort the background dynamically.

**What this requires:**
- `MeshTransmissionMaterial` from Drei (not MeshPhysicalMaterial)
- `temporalDistortion={0.35}` — animates FBO UV coordinates over time
- A live background scene to refract (particles, gradient, other objects)

**CDN equivalent**: MeshPhysicalMaterial + envMap is 85% quality.
For true liquid glass: npm build only.

**Resources confirmed:**
- `appleliquidglass.vercel.app` — working R3F demo
- `github.com/Zqysl/liquid-glass-webgl` — pure WebGL
- `github.com/dashersw/liquid-glass-js` — standalone library

---

## Scroll-Driven Keyframe Camera System

For 5-section scroll narrative, define camera position keyframes:

```javascript
const camKeyframes = [
  { pos: [0, 0, 6.5],      look: [0, 0, 0] },        // s0 — centered
  { pos: [-1.2, 0.3, 5.5], look: [0, 0, 0] },         // s1 — left
  { pos: [1.5, -0.4, 6.0], look: [0.5, 0, 0] },       // s2 — right
  { pos: [-0.6, 0.8, 5.0], look: [-0.2, 0, 0] },      // s3 — close high
  { pos: [0, 0, 6.0],      look: [0, 0, 0] },          // s4 — return
];

function lerpCam(p) {
  const sections = camKeyframes.length - 1;
  const raw = p * sections;
  const i   = Math.min(Math.floor(raw), sections - 1);
  const t   = raw - i;
  const a = camKeyframes[i], b = camKeyframes[i+1];
  const s = t*t*(3-2*t);  // smoothstep — critical for cinematic feel
  return {
    px: a.pos[0] + (b.pos[0] - a.pos[0]) * s,
    // etc.
  };
}
```

Key: use smoothstep (t*t*(3-2*t)) not linear lerp for camera interpolation.
Linear lerp = mechanical. Smoothstep = cinematic ease-in-out.

Also double-smooth: store `smoothScrollP`, lerp it toward `scrollP` at 0.04/frame.
This creates a second layer of deceleration on top of the keyframe interpolation.

---

## Bloom + CA Reactivity to Scroll Velocity

Scroll velocity as artistic variable:

```javascript
// On scroll event
scrollV = 0.04;  // inject velocity

// Each frame, decay
scrollV *= 0.88;

// Use velocity
bloom.strength = 0.5 + scrollV * 2.5;  // bloom pulses on fast scroll
finalPass.uniforms.uCA.value = 1.0 + scrollV * 3.0;  // CA spikes on fast scroll
```

Effect: fast scroll feels kinetic, energized. Slow scroll feels precise, contemplative.
The scene viscerally responds to how the user interacts with it.
Small code change, large perceptual impact.

---

## Per-Channel IOR Dispersion (True Physics)

The correct way to do chromatic dispersion is per-wavelength IOR, not post-process CA:

```glsl
float iorR = 1.0 / 1.50;  // red bends least (longer wavelength)
float iorG = 1.0 / 1.52;  // green middle
float iorB = 1.0 / 1.55;  // blue bends most (shorter wavelength)

vec3 refR = refract(viewDir, normal, iorR);
vec3 refG = refract(viewDir, normal, iorG);
vec3 refB = refract(viewDir, normal, iorB);
```

Post-process CA creates "lens aberration" (barrel distortion offset per channel).
True dispersion creates "glass dispersion" (different refraction angles per channel).
Both look similar at low intensity, but true dispersion has more depth at edges.

For CDN builds: post-process CA is good enough. For npm builds: implement per-channel IOR.

---

## IntersectionObserver Text Reveal Pattern

Simple, no-dependency scroll text reveal:

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(en => {
    if (en.isIntersecting) {
      const el = en.target;
      const delay = el.tagName === 'H2' ? 80 : el.classList.contains('eyebrow') ? 0 : 180;
      setTimeout(() => {
        el.style.transition = 'opacity 0.7s cubic-bezier(0.16,1,0.3,1), transform 0.7s cubic-bezier(0.16,1,0.3,1)';
        el.style.opacity  = '1';
        el.style.transform = 'translateY(0px)';
      }, delay);
    }
  });
}, { threshold: 0.25 });
```

Elements start with `opacity: 0; transform: translateY(14px)` in CSS.
Staggered delays: eyebrow 0ms, h2 80ms, body 180ms.
`cubic-bezier(0.16,1,0.3,1)` = spring-like easing, very Gleb/linear-app feel.
No GSAP needed for this pattern. Native and performant.

---

## Ground Glow Pools (Canvas Texture Pattern)

For colored glow under floating objects — NOT a point light, but a colored plane:

```javascript
function makeGlowPool(color, radius) {
  const res = 256;
  const cv  = document.createElement('canvas');
  cv.width = cv.height = res;
  const ctx = cv.getContext('2d');
  const grd = ctx.createRadialGradient(res/2, res/2, 0, res/2, res/2, res/2);
  grd.addColorStop(0,    color);                         // dense center
  grd.addColorStop(0.45, color.replace('1)', '0.3)'));  // falloff
  grd.addColorStop(1,    'rgba(0,0,0,0)');              // transparent edge
  ctx.fillStyle = grd;
  ctx.fillRect(0, 0, res, res);
  return new THREE.CanvasTexture(cv);
}

const pool = new THREE.Mesh(
  new THREE.PlaneGeometry(2.8, 2.8),
  new THREE.MeshBasicMaterial({ map: makeGlowPool('rgba(42,147,193,0.35)', 128), transparent: true, depthWrite: false })
);
pool.rotation.x = -Math.PI / 2;
pool.position.y = -2.19;  // just above ground plane
```

Color matches the object above it: blue sphere gets blue glow pool, orange hex gets orange pool.
Two objects, two colors = clear spatial storytelling without explicit labels.
Looks like real colored light falling on the ground.

---

## GSAP ScrollTrigger vs Raw Scroll (Research)

For production scroll-driven 3D, GSAP ScrollTrigger is superior to raw `window.scroll`:

**Raw scroll problems:**
- No velocity dampening (has to be implemented manually)
- Resize handling breaks at edge cases
- No "scrub" lag control

**GSAP ScrollTrigger benefits:**
- `scrub: 1` = 1 second lag for smooth cinematic following
- `scrub: true` = instant (for tight reactive control)
- Built-in `onUpdate: (self) => { t = self.progress }` fires every frame during scroll
- Works with Three.js `useFrame`-style loops
- GSAP CDN available: `https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js` + `ScrollTrigger.min.js`

**Next session**: Replace manual scroll lerp with GSAP ScrollTrigger.

---

## Capability Gap Summary (Current State)

| Technique | CDN Level | npm Level | Notes |
|-----------|-----------|-----------|-------|
| Glass material | 90-94% | 95-98% | npm needs temporalDistortion |
| Liquid glass effect | 0% | ~95% | FBO refraction: npm only |
| Particle volume | 60% | 70% | WebGPU (r171) needed for true volume |
| Organic forms | 55% | 55% | fBm formation-time deformation needed |
| Scroll narrative | 70% | 85% | GSAP ScrollTrigger in next session |
| True dispersion | 65% | 90% | Per-channel IOR in npm build |
| Typography 3D | 20% | 70% | FontLoader + TextGeometry not yet built |
| N8AO | 0% (sim) | 85% | CDN version IS available now |

**Weighted**: ~77% CDN, ~88% npm R3F

---

## Design Philosophy Crystallized

"Gleb renders LIGHT, not objects." (Previous discovery — confirmed deeper this session)

Extension discovered: **Gleb's glass tells a story about the space it inhabits.**

- The sphere isn't floating. It's the focal point of ambient intelligence in the scene.
- The particles don't drift. They respond to the sphere — attracted, warmed, repelled.
- The caustics aren't effects. They're evidence of refraction happening just out of frame.

For PureBrain application: the 3D brain is not a brain-shaped object. It is a glass instrument
for focusing ambient intelligence into visible light. The particles are cognition. The bloom
is what insight looks like when it becomes brighter than the surrounding space.

---

## File References

- Day 3 demo: `exports/3d-design-study/gleb-study-session-2026-03-09.html`
- Day 3 notes: `exports/3d-design-study/gleb-study-notes-2026-03-09.md`
- Day 2 demo: `exports/3d-design-study/day2-ao-neural-network.html`
- Day 1 demo: `exports/3d-design-study/day1-transmission-material-study.html`
- Night 3: `exports/3d-design-study/night3-composition-scene.html`
