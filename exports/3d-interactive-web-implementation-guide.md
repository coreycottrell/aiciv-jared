# 3D Interactive Web Implementation Guide
## Voice-Reactive, Scroll-Driven, and Mouse-Interactive 3D for PureBrain.ai

**Author**: full-stack-developer agent
**Date**: 2026-02-20
**Context**: Implementation guide for Aether avatar and general 3D web interactions.
Built from real production code in `exports/avatar-fluid.html`.

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/full-stack-developer/` for "audio", "WebGL", "3D", "shader"
- Found:
  - `2026-02-19--webgl-glass-shader-overhaul.md` - Full WebGL raymarcher with audio-reactive uniforms
  - `2026-02-20--premium-glass-sphere-avatar.md` - Glass material + interior glow
  - `2026-02-20--gleb-kuznetsov-avatar-overhaul.md` - Studio environment + volumetric light
- Applying: All patterns from production `exports/avatar-fluid.html` where it demonstrates working Web Audio API + WebGL render loop

---

## SECTION 1: Voice-Reactive 3D (Priority Implementation)

### How It Works - The Signal Chain

```
Microphone → getUserMedia() → MediaStreamSource
    → AnalyserNode (FFT 256 bins)
    → getByteFrequencyData() → Float [0..255] array
    → Normalize → smooth lerp → float uniform
    → GLSL shader: pulse scale, glow intensity, morph target
```

The key insight: **Web Audio API does NOT give you raw audio - it gives you frequency magnitudes**. FFT analysis converts the time-domain signal into frequency bins (bass, mids, highs). Each bin is 0-255. You average or weight-sum them to get a single "loudness" value, or treat them separately for frequency-specific reactions.

### Step 1: Set Up Audio Context + Analyser

This is the exact pattern from our working `exports/avatar-fluid.html`:

```javascript
var audioCtx = null;
var analyser = null;
var audioLevel = 0;        // smoothed current value (0.0 to ~1.0)
var targetAudioLevel = 0;  // raw measured value

function initAudio() {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;             // 128 frequency bins (fftSize/2)
    analyser.smoothingTimeConstant = 0.8; // built-in smoothing (0=none, 1=freeze)
    analyser.minDecibels = -90;         // lower sensitivity floor
    analyser.maxDecibels = -10;         // upper ceiling
    analyser.connect(audioCtx.destination); // needed to keep it alive

    // Resume on user gesture (browser policy)
    if (audioCtx.state === 'suspended') audioCtx.resume();
    return audioCtx;
}

// Called when user clicks "Talk" / grants mic
function connectMicrophone(stream) {
    var source = audioCtx.createMediaStreamSource(stream);
    source.connect(analyser); // mic audio → analyser
    // Do NOT connect source → destination (would cause feedback/echo)
}
```

### Step 2: Request Mic Permission

```javascript
function startListening() {
    initAudio();
    navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        .then(function(stream) {
            connectMicrophone(stream);
            window._micStream = stream; // save ref for cleanup
        })
        .catch(function(err) {
            console.error('Mic denied:', err);
            // Show fallback UI
        });
}

function stopListening() {
    if (window._micStream) {
        window._micStream.getTracks().forEach(function(t) { t.stop(); });
        window._micStream = null;
    }
}
```

### Step 3: Read Audio in the Render Loop

**This runs every frame (~60fps). NEVER create new Uint8Array inside the loop - allocate once.**

```javascript
// Allocate ONCE outside render loop
var freqData = null;

function initFreqBuffer() {
    freqData = new Uint8Array(analyser.frequencyBinCount); // 128 bins
}

// Inside requestAnimationFrame render loop:
function updateAudioLevel() {
    if (!analyser || !freqData) return 0;

    analyser.getByteFrequencyData(freqData); // fills freqData in-place

    // Option A: Average all bins (overall loudness)
    var sum = 0;
    for (var i = 0; i < freqData.length; i++) sum += freqData[i];
    var rawLevel = (sum / freqData.length) / 255; // 0.0 to 1.0

    // Option B: Weighted by frequency band (voice = 85Hz-255Hz = bins 0-10 at 48kHz)
    // Bass (bins 0-4), Mids (bins 5-20), Treble (bins 21+)
    var bassSum = 0;
    for (var i = 0; i < 5; i++) bassSum += freqData[i];
    var bassLevel = (bassSum / 5) / 255;

    return rawLevel;
}

// Smooth the signal so it doesn't jitter (lerp = linear interpolation)
function render() {
    var rawLevel = updateAudioLevel();

    // Only update if significant (filter background noise)
    if (rawLevel > 0.01) targetAudioLevel = rawLevel;

    // Smooth: 12% per frame toward target = ~0.2s lag at 60fps
    audioLevel += (targetAudioLevel - audioLevel) * 0.12;

    // Decay: when quiet, slowly fade back to 0
    if (rawLevel < 0.01) targetAudioLevel *= 0.95;

    // Pass to WebGL shader
    gl.uniform1f(uAudioLevel, audioLevel);

    // ... draw
    requestAnimationFrame(render);
}
```

### Step 4: Frequency Band Extraction (Advanced)

For fine-grained control - different bands drive different visual effects:

```javascript
function getFrequencyBands() {
    analyser.getByteFrequencyData(freqData);

    var nyquist = audioCtx.sampleRate / 2; // typically 24000Hz
    var binHz = nyquist / freqData.length;  // Hz per bin

    // Voice fundamental: 85-255Hz
    var voiceBinStart = Math.floor(85 / binHz);
    var voiceBinEnd   = Math.ceil(255 / binHz);

    // Sub-bass punch: 20-80Hz
    var subBassEnd = Math.ceil(80 / binHz);

    // High presence: 3000-8000Hz
    var hiStart = Math.floor(3000 / binHz);
    var hiEnd   = Math.ceil(8000 / binHz);

    function avgRange(start, end) {
        var s = 0;
        for (var i = start; i <= end; i++) s += freqData[i];
        return (s / (end - start + 1)) / 255;
    }

    return {
        subBass:   avgRange(0, subBassEnd),            // 20-80Hz  → scale/shake
        voice:     avgRange(voiceBinStart, voiceBinEnd), // 85-255Hz → face morph
        mids:      avgRange(voiceBinEnd, hiStart),      // 255-3kHz → glow
        highs:     avgRange(hiStart, hiEnd),            // 3-8kHz   → sparkle
        overall:   avgRange(0, freqData.length - 1)    // overall   → size
    };
}
```

### Step 5: Connect Audio to a WebGL Shader (Our Production Pattern)

This is exactly how `exports/avatar-fluid.html` does it:

**In GLSL (vertex or fragment shader):**
```glsl
uniform float uAudioLevel; // 0.0 to ~1.0

// Example: pulse sphere radius
float sphereRadius = 0.985 + uAudioLevel * 0.12;

// Example: audio ripple on surface
float audio = uAudioLevel;
if (audio > 0.15) {
    float r = length(p);
    float ripple = sin(r * 10.0 - t * 4.0) * (audio - 0.15) * 0.004;
    p += normal * ripple;
}

// Example: interior glow brightens with voice
float coreGlow = exp(-coreDist / 0.22) * 0.85 * (1.0 + audio * 0.8);

// Example: concentric wave rings from core
float waveR = 0.2 + sin(t * 6.0 + audio * 8.0) * 0.08 * audio;
float wavePulse = exp(-abs(coreDist - waveR) / 0.03) * audio * 0.8;
```

**In JavaScript (upload uniform each frame):**
```javascript
// Set up once after compiling shader:
uAudioLevel = gl.getUniformLocation(program, 'uAudioLevel');

// Each frame:
gl.uniform1f(uAudioLevel, audioLevel);
```

### Step 6: Voice-Reactive with Three.js + GLB Model

This is the pattern for Meshy-generated `.glb` files:

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// --- Scene Setup ---
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(600, 600);
document.getElementById('canvas-container').appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
camera.position.set(0, 0, 4);

// --- Load GLB ---
const loader = new GLTFLoader();
let model = null;
let mixer = null;

loader.load('/path/to/your-model.glb', (gltf) => {
    model = gltf.scene;
    scene.add(model);

    // Center and scale model
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    model.position.sub(center);
    const size = box.getSize(new THREE.Vector3()).length();
    model.scale.multiplyScalar(2.0 / size);

    // Set up animation mixer if model has animations
    if (gltf.animations.length > 0) {
        mixer = new THREE.AnimationMixer(model);
        const action = mixer.clipAction(gltf.animations[0]);
        action.play();
    }
});

// --- Audio Setup ---
let audioCtx, analyser, freqData, micStream;
let audioLevel = 0, targetAudioLevel = 0;

async function initMicrophone() {
    audioCtx = new AudioContext();
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    analyser.connect(audioCtx.destination);
    freqData = new Uint8Array(analyser.frequencyBinCount);

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    micStream = stream;
    const source = audioCtx.createMediaStreamSource(stream);
    source.connect(analyser);

    return stream;
}

// --- Lights ---
const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
scene.add(ambientLight);

const keyLight = new THREE.DirectionalLight(0xffffff, 2.0);
keyLight.position.set(-2, 3, 2);
scene.add(keyLight);

const rimLight = new THREE.DirectionalLight(0x2a93c1, 0.8);
rimLight.position.set(2, -1, -2);
scene.add(rimLight);

// --- Render Loop ---
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const delta = clock.getDelta();
    const elapsed = clock.getElapsedTime();

    // Update audio level
    if (analyser && freqData) {
        analyser.getByteFrequencyData(freqData);
        let sum = 0;
        for (let i = 0; i < freqData.length; i++) sum += freqData[i];
        const raw = (sum / freqData.length) / 255;
        if (raw > 0.01) targetAudioLevel = raw;
        else targetAudioLevel *= 0.95;
    }
    audioLevel += (targetAudioLevel - audioLevel) * 0.12;

    // Apply audio to model
    if (model) {
        // Pulse scale
        const pulse = 1.0 + audioLevel * 0.08;
        model.scale.setScalar((2.0 / modelSize) * pulse);

        // Gentle idle rotation
        model.rotation.y += delta * 0.3;

        // Audio-reactive Y wobble
        model.rotation.x = Math.sin(elapsed * 2) * audioLevel * 0.15;
        model.rotation.z = Math.cos(elapsed * 1.7) * audioLevel * 0.1;

        // Color/emission shift (if model material supports it)
        model.traverse((child) => {
            if (child.isMesh && child.material) {
                // Emissive intensity scales with audio
                if (child.material.emissive) {
                    child.material.emissiveIntensity = 0.2 + audioLevel * 1.5;
                }
                // Rim light color shifts toward orange when speaking
                rimLight.color.setHSL(
                    0.55 - audioLevel * 0.4, // blue → orange
                    0.8 + audioLevel * 0.2,
                    0.5
                );
            }
        });
    }

    // Update animations
    if (mixer) mixer.update(delta);

    renderer.render(scene, camera);
}

animate();

// --- Morph Targets (for models with blend shapes) ---
// Meshy models may export morph targets for facial expressions
function applyMorphTargets(mesh, audioLevel) {
    if (!mesh.morphTargetDictionary) return;

    // Example: "viseme_O" mouth open = speech
    const openIdx = mesh.morphTargetDictionary['viseme_O'];
    if (openIdx !== undefined) {
        mesh.morphTargetInfluences[openIdx] = audioLevel * 2.0;
    }

    // Example: "jawOpen" for talking
    const jawIdx = mesh.morphTargetDictionary['jawOpen'];
    if (jawIdx !== undefined) {
        mesh.morphTargetInfluences[jawIdx] = Math.min(audioLevel * 3.0, 1.0);
    }
}
</script>
```

### Particle System that Reacts to Voice

```javascript
// Create particle geometry
const PARTICLE_COUNT = 500;
const positions = new Float32Array(PARTICLE_COUNT * 3);
const velocities = [];

for (let i = 0; i < PARTICLE_COUNT; i++) {
    // Random sphere distribution
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const r = 1.2 + Math.random() * 0.3;
    positions[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = r * Math.cos(phi);
    velocities.push(new THREE.Vector3(
        (Math.random() - 0.5) * 0.01,
        (Math.random() - 0.5) * 0.01,
        (Math.random() - 0.5) * 0.01
    ));
}

const particleGeo = new THREE.BufferGeometry();
particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

const particleMat = new THREE.PointsMaterial({
    color: 0x2a93c1,
    size: 0.02,
    transparent: true,
    opacity: 0.7,
    blending: THREE.AdditiveBlending
});

const particles = new THREE.Points(particleGeo, particleMat);
scene.add(particles);

// In render loop:
function updateParticles(audioLevel) {
    const pos = particles.geometry.attributes.position.array;
    const audioBoost = 1.0 + audioLevel * 3.0; // particles fly outward with voice
    const originScale = 1.2; // rest radius

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        const ix = i * 3, iy = i * 3 + 1, iz = i * 3 + 2;

        // Push outward from center when audio is loud
        const len = Math.sqrt(pos[ix]**2 + pos[iy]**2 + pos[iz]**2);
        const targetR = (originScale + audioLevel * 0.5) + Math.random() * 0.1;
        const factor = (targetR / len - 1) * 0.05;
        pos[ix] += pos[ix] * factor + velocities[i].x;
        pos[iy] += pos[iy] * factor + velocities[i].y;
        pos[iz] += pos[iz] * factor + velocities[i].z;

        // Contain particles
        const newLen = Math.sqrt(pos[ix]**2 + pos[iy]**2 + pos[iz]**2);
        if (newLen > 2.0) {
            pos[ix] *= 1.5 / newLen;
            pos[iy] *= 1.5 / newLen;
            pos[iz] *= 1.5 / newLen;
        }
    }
    particles.geometry.attributes.position.needsUpdate = true;

    // Size and opacity react to audio
    particleMat.size = 0.015 + audioLevel * 0.03;
    particleMat.opacity = 0.5 + audioLevel * 0.5;
}
```

### How Talking Avatar Services Work (D-ID, HeyGen Pattern)

Services like D-ID/HeyGen work differently from what we're building - they render video server-side and stream it. For our use case (real-time reactive avatar without pre-rendered video), the pattern is:

1. **Get audio stream** (mic or TTS audio playback)
2. **Analyze in real-time** with Web Audio API FFT
3. **Drive blend shapes / morph targets** using frequency data
4. **Map phonemes** to viseme states (optional - requires phoneme detection)

For the Aether sphere avatar specifically, we skip blend shapes entirely and use **shader uniforms** to drive visual state - this is simpler and more visually striking than mesh deformation.

---

## SECTION 2: Scroll-Driven 3D

### Approach A: GSAP ScrollTrigger + Three.js (Recommended for WordPress/Elementor)

**Dependencies:**
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.4/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.4/ScrollTrigger.min.js"></script>
```

**HTML Structure:**
```html
<!-- Wrapper that GSAP pins -->
<div id="scroll-container" style="height: 400vh; position: relative;">
    <!-- Sticky canvas wrapper -->
    <div id="canvas-sticky" style="
        position: sticky;
        top: 0;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    ">
        <canvas id="scroll-canvas" width="600" height="600"></canvas>
    </div>
</div>
```

**JavaScript - GSAP ScrollTrigger + Three.js:**
```javascript
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// Three.js setup
const renderer = new THREE.WebGLRenderer({
    canvas: document.getElementById('scroll-canvas'),
    antialias: true,
    alpha: true
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(600, 600);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
camera.position.set(0, 0, 5);

// Scroll progress tracker (0 = top, 1 = bottom of scroll section)
let scrollProgress = 0;

// Define keyframes for model transform at each scroll %
const keyframes = [
    // scrollProgress 0.0: model at start state
    { progress: 0.0, rotY: 0,         rotX: 0,         posZ: 0,   scale: 1.0 },
    // 0.25: rotated 90 degrees
    { progress: 0.25, rotY: Math.PI/2, rotX: 0.2,       posZ: 0.5, scale: 1.1 },
    // 0.5: showing back of model
    { progress: 0.5,  rotY: Math.PI,   rotX: 0,         posZ: 0,   scale: 1.2 },
    // 0.75: 270 degrees
    { progress: 0.75, rotY: Math.PI*1.5, rotX: -0.2,    posZ: 0.5, scale: 1.1 },
    // 1.0: full rotation back to start, elevated
    { progress: 1.0,  rotY: Math.PI*2, rotX: 0,         posZ: 0,   scale: 1.0 }
];

// Interpolate between keyframes
function getScrollState(progress) {
    // Find surrounding keyframes
    let prev = keyframes[0], next = keyframes[keyframes.length - 1];
    for (let i = 0; i < keyframes.length - 1; i++) {
        if (progress >= keyframes[i].progress && progress <= keyframes[i+1].progress) {
            prev = keyframes[i];
            next = keyframes[i+1];
            break;
        }
    }
    const t = (progress - prev.progress) / (next.progress - prev.progress);
    const ease = t < 0.5 ? 2*t*t : -1+(4-2*t)*t; // ease in-out quad

    return {
        rotY:  prev.rotY  + (next.rotY  - prev.rotY)  * ease,
        rotX:  prev.rotX  + (next.rotX  - prev.rotX)  * ease,
        posZ:  prev.posZ  + (next.posZ  - prev.posZ)  * ease,
        scale: prev.scale + (next.scale - prev.scale) * ease
    };
}

// GSAP ScrollTrigger
ScrollTrigger.create({
    trigger: '#scroll-container',
    start: 'top top',
    end: 'bottom bottom',
    scrub: 1,           // smooth scrub (1 = 1 second lag)
    onUpdate: (self) => {
        scrollProgress = self.progress;
    }
});

// Load model
let model;
const loader = new GLTFLoader();
loader.load('/path/to/model.glb', (gltf) => {
    model = gltf.scene;
    scene.add(model);
    // Center model
    const box = new THREE.Box3().setFromObject(model);
    model.position.sub(box.getCenter(new THREE.Vector3()));
});

// Lights
scene.add(new THREE.AmbientLight(0xffffff, 0.4));
const mainLight = new THREE.DirectionalLight(0xffffff, 2.0);
mainLight.position.set(5, 10, 7);
scene.add(mainLight);

// Render loop
function animate() {
    requestAnimationFrame(animate);

    if (model) {
        const state = getScrollState(scrollProgress);
        model.rotation.y = state.rotY;
        model.rotation.x = state.rotX;
        model.position.z = state.posZ;
        model.scale.setScalar(state.scale);
    }

    renderer.render(scene, camera);
}
animate();
```

### Approach B: React Three Fiber with ScrollControls

**For React-based builds (not WordPress/Elementor):**

```bash
npm install @react-three/fiber @react-three/drei three gsap
```

```jsx
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { ScrollControls, Scroll, useScroll, useGLTF } from '@react-three/drei';
import { useRef } from 'react';

function ModelOnScroll({ url }) {
    const { scene } = useGLTF(url);
    const ref = useRef();
    const scroll = useScroll(); // gives scroll.offset (0 to 1)

    useFrame(() => {
        if (!ref.current) return;
        const t = scroll.offset; // 0 = top, 1 = bottom

        // Rotate full circle as user scrolls
        ref.current.rotation.y = t * Math.PI * 2;

        // Elevate model in second half of scroll
        ref.current.position.y = t > 0.5 ? (t - 0.5) * 2 : 0;

        // Breathe scale
        const breathe = 1 + Math.sin(t * Math.PI) * 0.1;
        ref.current.scale.setScalar(breathe);
    });

    return <primitive ref={ref} object={scene} scale={1.5} />;
}

export default function ScrollScene() {
    return (
        <div style={{ height: '400vh' }}>
            <Canvas
                style={{ position: 'sticky', top: 0, height: '100vh' }}
                camera={{ position: [0, 0, 5], fov: 45 }}
            >
                <ambientLight intensity={0.5} />
                <directionalLight position={[5, 10, 7]} intensity={2} />

                <ScrollControls pages={4} damping={0.1}>
                    <Scroll>
                        <ModelOnScroll url="/model.glb" />
                    </Scroll>

                    {/* HTML content that scrolls alongside */}
                    <Scroll html>
                        <div style={{ position: 'absolute', top: '120vh', left: '10%', color: 'white' }}>
                            <h2>Feature One</h2>
                        </div>
                        <div style={{ position: 'absolute', top: '220vh', left: '60%', color: 'white' }}>
                            <h2>Feature Two</h2>
                        </div>
                    </Scroll>
                </ScrollControls>
            </Canvas>
        </div>
    );
}
```

### Apple-Style Product Reveal Pattern

The Apple pattern uses scroll to play through a pre-baked animation timeline:

```javascript
// Load model with animations from Blender/Meshy
loader.load('/model.glb', (gltf) => {
    model = gltf.scene;
    scene.add(model);

    if (gltf.animations.length > 0) {
        mixer = new THREE.AnimationMixer(model);
        animAction = mixer.clipAction(gltf.animations[0]);
        animAction.play();
        animAction.paused = true; // We control time manually

        // Total animation duration
        const duration = animAction.getClip().duration;

        // Scroll controls time position in animation
        ScrollTrigger.create({
            trigger: '#scroll-section',
            start: 'top top',
            end: 'bottom bottom',
            scrub: true,
            onUpdate: (self) => {
                // Set animation time based on scroll progress
                mixer.setTime(self.progress * duration);
            }
        });
    }
});
```

---

## SECTION 3: Mouse / Cursor Interaction

### Raycasting for Hover Detection

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let hoveredObject = null;

// Convert mouse position to normalized device coordinates (-1 to +1)
function onMouseMove(event) {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width)  * 2 - 1;
    mouse.y = -((event.clientY - rect.top)  / rect.height) * 2 + 1;
}
window.addEventListener('mousemove', onMouseMove);

// In render loop:
function checkRaycast() {
    raycaster.setFromCamera(mouse, camera);

    const intersects = raycaster.intersectObjects(scene.children, true); // true = recursive

    if (intersects.length > 0) {
        const hit = intersects[0].object;
        if (hoveredObject !== hit) {
            // Restore previous
            if (hoveredObject) hoveredObject.material.emissiveIntensity = 0;
            hoveredObject = hit;
            // Highlight hovered part
            hit.material.emissiveIntensity = 0.5;
            renderer.domElement.style.cursor = 'pointer';
        }
    } else {
        if (hoveredObject) {
            hoveredObject.material.emissiveIntensity = 0;
            hoveredObject = null;
        }
        renderer.domElement.style.cursor = 'default';
    }
}
```

### Cursor-Follow Tilt (Billboard Effect)

This is used for the "avatar looks at cursor" effect. Very smooth with lerp:

```javascript
let targetRotX = 0, targetRotY = 0;
let currentRotX = 0, currentRotY = 0;

function onMouseMove(event) {
    const rect = renderer.domElement.getBoundingClientRect();
    const nx = ((event.clientX - rect.left) / rect.width)  * 2 - 1; // -1 to 1
    const ny = ((event.clientY - rect.top)  / rect.height) * 2 - 1; // -1 to 1

    // Convert to rotation angles (max 15 degrees = 0.26 rad)
    targetRotY = nx * 0.26;
    targetRotX = -ny * 0.15;
}
window.addEventListener('mousemove', onMouseMove);

// In render loop:
function updateCursorFollow() {
    // Smooth follow (4% per frame = ~0.6s lag at 60fps)
    currentRotX += (targetRotX - currentRotX) * 0.04;
    currentRotY += (targetRotY - currentRotY) * 0.04;

    if (model) {
        model.rotation.x = currentRotX;
        model.rotation.y = currentRotY;
    }
}
```

### Click to Select Part + Trigger Animation

```javascript
renderer.domElement.addEventListener('click', (event) => {
    // Raycast at click position
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);

    if (intersects.length > 0) {
        const hitObject = intersects[0].object;
        const hitName = hitObject.name || hitObject.parent?.name;

        // Trigger specific animation based on what was clicked
        if (hitName === 'Head' || hitName.includes('head')) {
            triggerAnimation('headNod');
        } else if (hitName === 'Body' || hitName.includes('body')) {
            triggerAnimation('spin360');
        }

        // Visual feedback - flash color
        const originalColor = hitObject.material.color.clone();
        hitObject.material.color.setHex(0x2a93c1);
        setTimeout(() => {
            hitObject.material.color.copy(originalColor);
        }, 300);
    }
});

function triggerAnimation(name) {
    if (!mixer || !model) return;
    // Find clip by name
    const clip = THREE.AnimationClip.findByName(allClips, name);
    if (clip) {
        const action = mixer.clipAction(clip);
        action.reset().setLoop(THREE.LoopOnce).play();
    }
}
```

### Cursor Particle Trail

```javascript
const TRAIL_LENGTH = 40;
const trail = [];
const trailGeo = new THREE.BufferGeometry();
const trailPositions = new Float32Array(TRAIL_LENGTH * 3);
trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));

const trailMat = new THREE.LineBasicMaterial({
    color: 0x2a93c1,
    transparent: true,
    opacity: 0.5
});
const trailLine = new THREE.Line(trailGeo, trailMat);
scene.add(trailLine);

function updateTrail(mouseX, mouseY) {
    // Unproject mouse to 3D space at z=0 plane
    const vec = new THREE.Vector3(mouseX, mouseY, 0.5);
    vec.unproject(camera);
    vec.sub(camera.position).normalize();
    const distance = -camera.position.z / vec.z;
    const pos = camera.position.clone().add(vec.multiplyScalar(distance));

    trail.unshift({ x: pos.x, y: pos.y, z: pos.z });
    if (trail.length > TRAIL_LENGTH) trail.pop();

    for (let i = 0; i < TRAIL_LENGTH; i++) {
        const p = trail[i] || trail[trail.length - 1] || { x: 0, y: 0, z: 0 };
        trailPositions[i * 3]     = p.x;
        trailPositions[i * 3 + 1] = p.y;
        trailPositions[i * 3 + 2] = p.z;
    }
    trailGeo.attributes.position.needsUpdate = true;
}
```

---

## SECTION 4: Embedding in WordPress / Elementor

### Method 1: Elementor HTML Widget (Recommended for Quick Deploy)

**Step 1**: In Elementor, drag in an HTML widget.

**Step 2**: Paste this structure:

```html
<!-- 3D Scene Container -->
<div id="pb-3d-wrapper" style="width:100%;max-width:600px;margin:0 auto;position:relative;">
    <!-- Fallback for no-WebGL (static image) -->
    <img id="pb-3d-fallback"
         src="/wp-content/uploads/avatar-fallback.png"
         style="display:none;width:100%;border-radius:12px;"
         alt="Aether AI Avatar" />

    <!-- Canvas (hidden until WebGL confirmed) -->
    <canvas id="pb-3d-canvas" style="width:100%;border-radius:12px;display:none;"></canvas>
</div>

<!-- Load Three.js with importmap workaround for Elementor (no native support) -->
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<!-- Load GLTFLoader separately when not using modules -->
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/loaders/GLTFLoader.js"></script>

<script>
(function() {
    'use strict';

    var canvas = document.getElementById('pb-3d-canvas');
    var fallback = document.getElementById('pb-3d-fallback');

    // WebGL capability check
    function checkWebGL() {
        try {
            var testCanvas = document.createElement('canvas');
            return !!(testCanvas.getContext('webgl') || testCanvas.getContext('experimental-webgl'));
        } catch(e) { return false; }
    }

    if (!checkWebGL()) {
        fallback.style.display = 'block';
        return;
    }

    canvas.style.display = 'block';

    // Intersection Observer: only animate when in viewport
    var isVisible = false;
    var observer = new IntersectionObserver(function(entries) {
        isVisible = entries[0].isIntersecting;
    }, { threshold: 0.1 });
    observer.observe(canvas);

    // Three.js scene
    var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
    var containerWidth = canvas.parentElement.offsetWidth;
    renderer.setSize(containerWidth, containerWidth); // square
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
    camera.position.z = 4;

    scene.add(new THREE.AmbientLight(0xffffff, 0.5));
    var dirLight = new THREE.DirectionalLight(0xffffff, 2.0);
    dirLight.position.set(5, 10, 7);
    scene.add(dirLight);

    var model = null;
    var loader = new THREE.GLTFLoader();

    // Lazy load model only when in viewport
    var modelLoaded = false;
    function loadModelWhenReady() {
        if (modelLoaded || !isVisible) return;
        modelLoaded = true;

        loader.load(
            '/wp-content/uploads/your-model.glb',
            function(gltf) {
                model = gltf.scene;
                var box = new THREE.Box3().setFromObject(model);
                model.position.sub(box.getCenter(new THREE.Vector3()));
                var size = box.getSize(new THREE.Vector3()).length();
                model.scale.multiplyScalar(2.5 / size);
                scene.add(model);
            },
            undefined,
            function(error) {
                console.warn('GLB load failed, showing fallback');
                canvas.style.display = 'none';
                fallback.style.display = 'block';
            }
        );
    }

    var startTime = performance.now();

    function animate() {
        requestAnimationFrame(animate);

        // Skip rendering when not visible (save CPU/GPU)
        if (!isVisible) return;

        loadModelWhenReady();

        var t = (performance.now() - startTime) / 1000;

        if (model) {
            model.rotation.y = t * 0.4; // slow idle rotation
        }

        renderer.render(scene, camera);
    }
    animate();

    // Handle resize
    window.addEventListener('resize', function() {
        var w = canvas.parentElement.offsetWidth;
        renderer.setSize(w, w);
    });

})();
</script>
```

### Method 2: WordPress Plugin Custom Script (For Complex Interactions)

Add to your custom plugin or child theme `functions.php`:

```php
// In your custom plugin file:
function purebrain_enqueue_3d_scripts() {
    // Only load on pages that need it
    if (!is_page('home') && !is_page('purebrain')) return;

    wp_enqueue_script(
        'three-js',
        'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js',
        array(),
        '0.160.0',
        true // load in footer
    );

    wp_enqueue_script(
        'gltf-loader',
        'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/loaders/GLTFLoader.js',
        array('three-js'),
        '0.160.0',
        true
    );

    wp_enqueue_script(
        'purebrain-3d-avatar',
        plugin_dir_url(__FILE__) . 'js/avatar-3d.js',
        array('three-js', 'gltf-loader'),
        '1.0.0',
        true
    );

    // Pass PHP variables to JS
    wp_localize_script('purebrain-3d-avatar', 'PB3D', array(
        'modelUrl'    => content_url('/uploads/aether-avatar.glb'),
        'fallbackUrl' => content_url('/uploads/avatar-fallback.png'),
        'apiUrl'      => rest_url('purebrain/v1/')
    ));
}
add_action('wp_enqueue_scripts', 'purebrain_enqueue_3d_scripts');
```

**Then in your Elementor HTML widget, just place the container:**
```html
<div id="pb-3d-avatar-root" data-model="aether" style="width:100%;height:500px;"></div>
```

### Performance Considerations

**Critical rules for production:**

| Issue | Problem | Solution |
|-------|---------|---------|
| Frame rate | 3D kills battery on mobile | Target 30fps on mobile, 60fps desktop |
| Model size | Large GLBs = slow load | Compress with `gltf-transform optimize --compress` |
| Offscreen rendering | Wastes GPU when not visible | IntersectionObserver to pause rendering |
| Pixel ratio | 3x on iPhone = 9x work | Cap at `Math.min(devicePixelRatio, 2)` |
| WebGL context loss | Browser can kill context | Listen for `webglcontextlost` event |

```javascript
// WebGL Context Loss Handler (critical for production)
canvas.addEventListener('webglcontextlost', function(event) {
    event.preventDefault();
    // Show CSS fallback
    canvas.style.display = 'none';
    fallback.style.display = 'block';
    console.warn('WebGL context lost - showing fallback');
}, false);

canvas.addEventListener('webglcontextrestored', function() {
    // Reinitialize renderer and reload scene
    canvas.style.display = 'block';
    fallback.style.display = 'none';
    initScene(); // your setup function
}, false);
```

**Mobile Fallback Pattern (from our production implementation):**
```javascript
// Check mobile BEFORE initializing WebGL
var isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
var MAX_CANVAS_SIZE = isMobile ? 380 : 600;
var PIXEL_RATIO = isMobile ? 1 : Math.min(window.devicePixelRatio, 2);

// Use simpler shader/geometry on mobile
if (isMobile) {
    // Load low-poly version of model
    loader.load('/model-mobile.glb', ...);
} else {
    loader.load('/model-desktop.glb', ...);
}
```

---

## SECTION 5: Putting It All Together - The Aether Sphere Pattern

Our production avatar (`exports/avatar-fluid.html`) uses **raw WebGL with GLSL shaders instead of Three.js** because:

1. Raymarched SDF = no GLB file needed (sphere is computed mathematically)
2. Full shader control = impossible to do with Three.js material system
3. No dependency on model loading - instant render

For Meshy GLB models, Three.js is the right tool. For procedural geometry with complex glass shaders, raw WebGL gives more control.

**The complete audio-reactive state machine** (our production implementation):

```javascript
// Avatar states
var state = 'idle'; // idle | listening | thinking | speaking
var stateTargets = {
    idle:      0.0,
    speaking:  1.0,
    thinking:  2.0,
    listening: 1.5
};

function setAvatarState(newState) {
    state = newState;
    targetStateFloat = stateTargets[newState] || 0;
}

// State transitions triggered by voice/API events:
// - User clicks mic → setAvatarState('listening')
// - Speech detected → stays 'listening' with high audioLevel
// - Message sent to API → setAvatarState('thinking')
// - API response arrives, TTS starts → setAvatarState('speaking')
// - TTS finishes → setAvatarState('idle')

// In render loop, state blends smoothly:
currentStateFloat += (targetStateFloat - currentStateFloat) * 0.06;
// Upload to shader: gl.uniform1f(uState, currentStateFloat);
```

**GLSL responds to state + audio simultaneously:**
```glsl
uniform float uState;     // 0=idle, 1=speaking, 2=thinking (can be fractional)
uniform float uAudioLevel; // 0.0 to 1.0

// Derive smooth blend values
float sMix = clamp(1.0 - abs(uState - 1.0), 0.0, 1.0); // peak at state=1 (speaking)
float tMix = clamp(1.0 - abs(uState - 2.0), 0.0, 1.0); // peak at state=2 (thinking)

// State-specific visual effects
vec3 stateColor = mix(
    mix(IDLE_COLOR, SPEAKING_COLOR, sMix),
    THINKING_COLOR,
    tMix
);

// Audio amplifies interior brightness in speaking state
float glowStrength = 0.9 + uAudioLevel * 0.6 * sMix;
```

---

## Libraries Reference

| Library | Use Case | CDN |
|---------|---------|-----|
| Three.js | 3D scene, GLB loading | `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js` |
| GLTFLoader | Load .glb files | `https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/loaders/GLTFLoader.js` |
| GSAP | Scroll animation tweening | `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.4/gsap.min.js` |
| ScrollTrigger | GSAP scroll plugin | `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.4/ScrollTrigger.min.js` |
| audiomotion-analyzer | Pre-built FFT visualization | `https://cdn.jsdelivr.net/npm/audiomotion-analyzer@4/dist/audiomotion-analyzer.js` |
| Web Audio API | Built into browser | No CDN needed |
| @react-three/fiber | React + Three.js | npm only |
| @react-three/drei | Three.js helpers for R3F | npm only |

### audiomotion-analyzer (Quickest Path to Audio Visualization)

If you want fast results without writing FFT code yourself:

```javascript
import AudioMotionAnalyzer from 'audiomotion-analyzer';

const audioMotion = new AudioMotionAnalyzer(
    document.getElementById('visualizer-container'),
    {
        source: document.getElementById('audio-element'),
        height: 300,
        mode: 1,         // bars
        gradient: 'prism',
        showPeaks: false,
        smoothing: 0.8
    }
);

// Access raw frequency data for Three.js
const analyser = audioMotion.analyser;
const dataArray = new Uint8Array(analyser.frequencyBinCount);
// Then use in your render loop as shown above
```

---

## Quick Start: Voice-Reactive Sphere in 50 Lines

This is the minimum viable implementation for our Aether sphere use case:

```html
<!DOCTYPE html>
<html>
<head>
<style>
    body { margin:0; background:#050510; display:flex; align-items:center; justify-content:center; height:100vh; }
    canvas { border-radius:50%; }
    button { position:fixed; bottom:20px; padding:12px 24px; background:#2a93c1; color:#fff; border:none; border-radius:6px; cursor:pointer; font-size:1rem; }
</style>
</head>
<body>
<canvas id="c" width="400" height="400"></canvas>
<button onclick="toggle()">Talk to Aether</button>
<script>
var c = document.getElementById('c');
var ctx = c.getContext('2d');
var audioCtx, analyser, freqData, stream;
var level = 0, target = 0, listening = false;
var t = 0;

function toggle() {
    if (listening) {
        stream && stream.getTracks().forEach(t=>t.stop());
        listening = false;
    } else {
        audioCtx = new AudioContext();
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        analyser.connect(audioCtx.destination);
        freqData = new Uint8Array(analyser.frequencyBinCount);
        navigator.mediaDevices.getUserMedia({audio:true}).then(s=>{
            stream = s;
            audioCtx.createMediaStreamSource(s).connect(analyser);
            listening = true;
        });
    }
}

function draw() {
    requestAnimationFrame(draw);
    t += 0.016;

    if (analyser && freqData) {
        analyser.getByteFrequencyData(freqData);
        var sum = 0;
        for (var i=0;i<freqData.length;i++) sum+=freqData[i];
        target = (sum/freqData.length)/255;
    }
    level += (target - level) * 0.12;
    target *= 0.95;

    // Draw sphere
    ctx.clearRect(0,0,400,400);
    var r = 160 + level*30;
    var grd = ctx.createRadialGradient(170,160,10,200,200,r);
    grd.addColorStop(0, `rgba(${Math.round(42+level*200)},147,193,${0.9+level*0.1})`);
    grd.addColorStop(0.5, `rgba(20,80,130,0.8)`);
    grd.addColorStop(1, 'rgba(5,5,16,0)');
    ctx.beginPath();
    ctx.arc(200,200,r,0,Math.PI*2);
    ctx.fillStyle = grd;
    ctx.fill();

    // Pulse rings
    if (level > 0.1) {
        for (var i=1;i<=3;i++) {
            var pr = r + i*20 + Math.sin(t*4)*5;
            var alpha = Math.max(0,(level-0.1)*0.5/i);
            ctx.beginPath();
            ctx.arc(200,200,pr,0,Math.PI*2);
            ctx.strokeStyle = `rgba(42,147,193,${alpha})`;
            ctx.lineWidth = 2;
            ctx.stroke();
        }
    }
}
draw();
</script>
</body>
</html>
```

---

## Verification Notes

This guide is based on:
- Production code in `/home/jared/projects/AI-CIV/aether/exports/avatar-fluid.html`
- Working Web Audio API + WebGL implementation (audio-reactive uniforms verified)
- Speech recognition + mic stream integration tested and working
- All GLSL patterns extracted from actual compiled/running shaders
- Elementor HTML widget deployment pattern from multiple prior sessions

Code patterns marked as "production" are extracted from running code, not hypothetical.
Code patterns marked as "example" are standard Three.js/WebGL patterns that follow official documentation.
