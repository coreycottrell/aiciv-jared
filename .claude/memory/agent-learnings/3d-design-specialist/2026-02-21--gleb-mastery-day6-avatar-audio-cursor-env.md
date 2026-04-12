# Gleb Mastery Day 6 - Avatar Mode: Audio-Reactive, Cursor Gaze, Environment Presets

**Date**: 2026-02-21
**Type**: teaching
**Topic**: Avatar foundation: Web Audio API reactivity, cursor gaze illusion, environment presets with lerp transitions, combined avatar mode API

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/3d-design-specialist/` for all sprint learnings
- Found: Night 1 (complete Gleb recipe), Day 2 (R3F equivalence), Day 3 (Vite project), Day 4 (GLB + spring), Day 5 (JSX quality gap, adaptive quality, loading screen)
- Applied: All prior quality parameters, Float architecture, MeshTransmissionMaterial settings, FBO cost model

---

## Core Teaching 1: Web Audio API Frequency Band Architecture

**The full chain:**
```
getUserMedia() → MediaStream → MediaStreamSource → AnalyserNode → getByteFrequencyData()
```

**FFT parameters that determine frequency resolution:**
```javascript
const FFT_SIZE = 2048      // Must be power of 2
const SAMPLE_RATE = 44100  // Standard CD quality
const BIN_WIDTH = SAMPLE_RATE / FFT_SIZE  // ~10.77 Hz per frequency bin
// Result: 1024 bins covering 0-22050 Hz
```

**Why 2048 FFT size:**
- Frequency resolution = sampleRate / fftSize = 10.77 Hz/bin
- Time resolution = fftSize / sampleRate = 46.4ms latency
- These trade off: higher fftSize = better frequency resolution, worse temporal response
- For speech reactivity: 2048 is the right balance (distinguishes bass/mid/high clearly)

**Band definitions that map to visual properties:**
```javascript
const BANDS = {
  subBass:  { lo: freqToBin(20),   hi: freqToBin(60) },    // Breathing, body
  bass:     { lo: freqToBin(60),   hi: freqToBin(250) },   // Voice fundamental
  midLow:   { lo: freqToBin(250),  hi: freqToBin(500) },   // Formants (vocal resonances)
  midHigh:  { lo: freqToBin(500),  hi: freqToBin(2000) },  // Articulation, consonants
  highMid:  { lo: freqToBin(2000), hi: freqToBin(4000) },  // Presence, clarity
  presence: { lo: freqToBin(4000), hi: freqToBin(8000) },  // Sibilants (s, sh sounds)
}
```

**What to animate with each band:**
- bass → sphere scale (fundamental energy)
- midHigh → inner glow (articulation = thought)
- presence → chromatic aberration, shimmer (high-frequency = sparkle)

---

## Core Teaching 2: Synthetic Audio Engine (the "no mic" fallback)

**Why synthetic audio matters:**
- Demos need to work without mic permission
- Development happens without speaking
- Controlled tests need reproducible amplitude patterns

**Speech simulation approach:**
```javascript
// Three layers of modulation create realistic speech feel:
// 1. Burst envelope (syllable timing: 150-500ms bursts)
//    burstProgress < 0.2: fast attack (20% of cycle)
//    burstProgress >= 0.2: slow decay (80% of cycle)
// 2. Phoneme detail: sin(t * 12) = 12Hz oscillation on top of burst
// 3. Sibilants: intermittent (only when sin(t*5) > 0.6)

this.speechCycleLength = 0.15 + Math.random() * 0.35  // 150-500ms random bursts
```

**Formant simulation (why frequency distribution matters):**
Real voice has vocal tract resonances (formants) that create bell-curve amplitude
shapes across frequency ranges. We simulate with `Math.sin(midPos * Math.PI)` which
creates a bell shape across the midLow band. This makes synthetic audio feel like
real speech when mapped to glass transmission colors.

---

## Core Teaching 3: Why MeshTransmissionMaterial Roughness Cannot Be Animated

**Critical gotcha for audio reactivity:**

The tempting approach is to animate `roughness` in response to high-frequency audio:
```javascript
// DON'T DO THIS:
outerRef.current.material.roughness = 0.05 + highFreqAmp * 0.3
```

**Why it breaks:**
`MeshTransmissionMaterial` uses `roughness` to configure FBO sampling spread.
Any change to `roughness` triggers an internal shader recompile + FBO reconfigure.
This happens EVERY FRAME if roughness is animated. At 60fps = 60 shader recompiles/second.
Catastrophic performance.

**What you CAN animate cheaply:**
- `mesh.scale.setScalar(x)` - transforms a matrix uniform, virtually free
- `material.emissiveIntensity` (on meshStandardMaterial, not on MeshTransmission) - updates one uniform
- `mesh.position.x / .y` - free transform
- `material.opacity` on standard materials - one uniform

**The safe architecture:**
- Glass sphere: scale only (MeshTransmissionMaterial = reference stays unchanged)
- Inner core: emissiveIntensity only (meshStandardMaterial = standard uniform update)
- NO roughness, NO transmission, NO thickness animation

---

## Core Teaching 4: Cursor Gaze Illusion Architecture

**Why it works psychologically:**
The "gaze effect" is not eye contact. The sphere has no eyes. But a subtle rotation
toward the cursor creates the felt sense of an entity noticing you. This is enough
for avatar presence.

**The two-group composition pattern:**
```
scene
  └── gazeGroup (cursor rotation applied here)
      └── Float (orbital float - handles its own transform)
          └── outerMesh (glass sphere + idle rotation from useFrame)
          └── innerMesh (emissive core + audio reactivity)
```

**Why Float must be INSIDE gazeGroup, not outside:**
Float from `@react-three/drei` manages its own group transform via useFrame.
If we try to apply cursor rotation to the same object Float controls, we fight.
By wrapping Float in gazeGroup, we apply cursor rotation to the parent.
Float animates inside. The rotations compose via matrix multiplication. Correct.

**Lerp parameters for organic gaze:**
```javascript
trackingRatio: 0.2     // Cursor at +1 → sphere rotates 0.3 rad (not 1:1)
rotationSmooth: 0.05   // Very slow lerp = reluctant gaze (feels weighted, not robotic)
scaleSmooth: 0.08      // Slightly faster = proximity response feels alive
innerOffset: 0.04      // Very slow inner core shift = subliminal light source movement
```

**Mode-specific intensity multipliers:**
```
idle:      0.7  (present but not focused)
speaking:  0.5  (focused on speech, less gaze)
thinking:  0.3  (distracted, reduced tracking)
listening: 1.6  (maximum tracking = looking toward you)
```

---

## Core Teaching 5: Environment Preset Lerp via Light Ref Mutation

**The problem with React state for light values:**
If we stored current light colors/intensities in React state, every frame of lerp
would trigger a re-render (setState). 60 re-renders/second = thrashing.

**Solution: THREE.js refs + useFrame + throttled React state sync:**
```javascript
// Light values stored in useRef (no re-renders during lerp)
const lightState = useRef({
  key: { color: new THREE.Color('#FFF8F0'), intensity: 3.5 },
  // ...
})

// THREE.js light refs (direct DOM-equivalent mutation)
const keyRef = useRef()

useFrame(() => {
  // Lerp color (THREE.Color.lerp() is in-place, linear RGB)
  stateLight.color.lerp(targetColor, lerpFactor)
  // Lerp intensity
  stateLight.intensity += (targetIntensity - stateLight.intensity) * lerpFactor
  // Apply to THREE.js light (no React re-render)
  keyRef.current.color.copy(stateLight.color)
  keyRef.current.intensity = stateLight.intensity
})
```

**For bloom params (needs React state because EffectComposer is declarative):**
Use a throttled callback: only call setState at most 10x/second (100ms intervals).
```javascript
const lastBloomUpdate = useRef(0)
if (now - lastBloomUpdate.current > 100) {
  lastBloomUpdate.current = now
  setBloomParams(lerped)
}
```

**THREE.Color.lerp() is in LINEAR RGB space:**
Hex colors are in gamma-encoded sRGB. THREE.Color stores in linear RGB internally.
When you `new THREE.Color('#FF0000')`, it converts sRGB → linear.
`color.lerp(target, t)` interpolates in linear space.
Result: physically correct color blending (no grey band between complementary colors).

---

## Core Teaching 6: Avatar Mode Visual Design System

**Mode color/glow/behavior table:**
```
idle:      innerColor=PB_BLUE,   intensity=3.0, floatSpeed=1.5, idleRot=0.002
           (breathing, neutral, minimal reactivity)

speaking:  innerColor='#ffffff', intensity=6.0, floatSpeed=2.0, idleRot=0.003
           ringPulse=true, (maximum audio reactivity, bright white core)

thinking:  innerColor=PB_BLUE,   intensity=2.5, floatSpeed=0.8, idleRot=0.005
           attColor='#8866AA' (purple tint = contemplative state)
           (slow deliberate float, reduced glow, faster spin = mental activity)

listening: innerColor='#00D4FF', intensity=3.5, floatSpeed=1.2, idleRot=0.001
           attColor='#00D4FF' (cyan = open, receptive)
           (very slow rotation, active cursor tracking, thin glass)
```

**The rationale:**
- Speaking: white glow = all frequencies present = voice activated
- Thinking: slower float, faster spin = paradox of stillness+activity
- Listening: slowest rotation = waiting (movement = talking, stillness = listening)
- Listening: cyan = water/air color codes = open to receiving

---

## Core Teaching 7: Synthetic Audio → Synthetic Avatar Connection

**The MOST IMPORTANT architectural lesson of Day 6:**

The SyntheticAudioEngine.setMode() + useAudioAnalyzer.setAvatarMode() creates a
direct link between the avatar's behavioral state and the audio simulation.

When you set `avatarMode = 'speaking'`:
1. React state updates → AvatarSphere renders with speaking config
2. setAnalyzerMode('speaking') → SyntheticAudioEngine.mode = 'speaking'
3. SyntheticAudioEngine.tick() generates speech-profile amplitudes
4. AudioReactiveCore reads those amplitudes → scale + glow animate

**Without a microphone**, the avatar STILL speaks convincingly because the synthetic
engine generates realistic speech amplitude patterns for the 'speaking' mode.

This architecture means:
- Demo works offline (no mic)
- Testing is deterministic (no random mic input)
- Mic adds realism but is optional, not required

**This is the foundation for the Aether avatar:** synthetic audio can power
default idle/thinking/listening states, while actual voice input powers speaking.

---

## Gotchas Discovered Day 6

**Gotcha 1: AudioContext requires user gesture**
```javascript
// AudioContext creation often blocked before user interaction:
// "AudioContext was not allowed to start"
// Solution: Create AudioContext inside startMic() which is called from button click
// Never create AudioContext at module load or useEffect (blocked by browser policy)
```

**Gotcha 2: smoothingTimeConstant affects responsiveness**
```javascript
this.analyser.smoothingTimeConstant = 0.8
// 0.8 = 80% of previous frame, 20% of new frame
// Too high (0.95): sphere barely moves even to loud audio
// Too low (0.3): sphere jerks unnervingly on every syllable
// 0.8 is the sweet spot for organic speech response
```

**Gotcha 3: Float + cursor rotation composition**
If you apply cursor rotation to the same mesh that Float controls via useFrame,
the rotations fight each frame. Float wins (it runs every frame after your code).
Fix: wrap Float in a gazeGroup, apply cursor rotation to gazeGroup.

**Gotcha 4: Bloom state throttling is required**
`onBloomChange` fires every frame during lerp. Without throttling to 100ms,
React re-renders 60x/second during preset transitions. Always throttle callbacks
that originate from useFrame.

**Gotcha 5: THREE.Color.lerp() modifies in-place**
```javascript
// WRONG (creates garbage):
const lerped = currentColor.clone().lerp(targetColor, factor)

// RIGHT (mutates in place, no allocation):
stateLight.color.lerp(new THREE.Color(targetCfg.color), factor)
// But "new THREE.Color()" creates allocation every frame!

// BEST: create target color once, reuse:
const targetColor = new THREE.Color(targetCfg.color)
stateLight.color.lerp(targetColor, factor)
// But still creates one object per light per frame...
// For 6 lights at 60fps = 360 Color objects/sec = minor GC pressure
// Acceptable for 6 lights; use caching for 20+ lights
```

---

## Files Created Day 6

- AudioReactive.jsx: `exports/gleb-r3f-scene/src/AudioReactive.jsx`
  (SyntheticAudioEngine, AudioAnalyzer, useAudioAnalyzer, AudioReactiveCore)
- CursorReactive.jsx: `exports/gleb-r3f-scene/src/CursorReactive.jsx`
  (useCursorReactive, CursorReactiveDriver)
- EnvironmentPresets.jsx: `exports/gleb-r3f-scene/src/EnvironmentPresets.jsx`
  (PRESET_CONFIGS, useEnvironmentPreset, PresetLights, PresetSelectorUI)
- AvatarSphere.jsx: `exports/gleb-r3f-scene/src/AvatarSphere.jsx`
  (AVATAR_MODE_CONFIGS, AvatarSphereInner/AvatarSphere, AvatarRing)
- Scene.jsx: UPDATED - avatar displayMode, PresetLights, env preset wiring
- App.jsx: UPDATED - avatar controls, audio source toggle, env selector, mode API
- App.css: UPDATED - avatar overlay, preset buttons, audio controls

## Build Output Day 6

```
dist/assets/index-BiZMQsJj.js  40.31 kB gzip: 11.81 kB  (app: +0.5KB gzip from Day 5)
dist/assets/pp-D4hu7zPD.js     87.12 kB gzip: 20.89 kB  (unchanged)
dist/assets/r3f-GDf76nXz.js   493.21 kB gzip: 155.67 kB (unchanged)
dist/assets/three-DrdX3_7U.js 724.98 kB gzip: 187.65 kB (unchanged)
```

Total gzip: ~387 KB (only +2KB from all Day 6 additions).
Web Audio API is built into the browser - zero bundle cost.

## Day 7 Recommendations

1. **Connect actual microphone to speaking mode**: Test the full chain: real mic → voice → sphere scale
2. **Tripo3D API for avatar mesh**: The glass sphere works but for the REAL Aether avatar,
   we want a custom organic form. Tripo3D text-to-3D for "abstract AI consciousness orb"
3. **Scroll-driven avatar state**: Map scroll position to avatarMode transitions
   (scroll down = idle → thinking → speaking progression)
4. **WordPress iframe embed**: Build the actual iframe with postMessage API so
   the avatar can be embedded on purebrain.ai and controlled from page JS
5. **Performance test avatar mode**: The combined audio+cursor+float adds 3 useFrame
   callbacks. Verify still 60fps on mid-range laptop.
