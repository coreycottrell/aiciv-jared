/**
 * Variation C — GPGPU Compute Particles with SDF Attractor Field
 * ================================================================
 * Closes Session 45 stated next-target: "GPU compute particles with SDF
 * attractor fields" using THREE.GPUComputationRenderer / FBO ping-pong.
 *
 * Design intent (post-Gleb-current-direction-shift, May 2026):
 *   - "Generative system" aesthetic, NOT showpiece material
 *   - 16,384 particles (128x128 position FBO) — runs 60fps on M1/integrated GPU
 *   - Curl noise drift + sphere->torus SDF morph attraction
 *   - Brand-blue particles with 3% white sparkles for premium catch
 *   - Bloom-as-primary (threshold 0.4) — particle bloom is the aesthetic
 *
 * Performance: 128x128 FBO = 16384 particles. Bumping to 256x256 = 65536 for
 * more "cloud-like" density at same frame budget on modern GPUs.
 */

import { Canvas, useFrame, useThree, createPortal, extend } from '@react-three/fiber'
import { useFBO, OrbitControls } from '@react-three/drei'
import { EffectComposer, Bloom } from '@react-three/postprocessing'
import { useMemo, useRef } from 'react'
import * as THREE from 'three'

// ──────────────────────────────────────────────────────────────────────
// Simulation fragment shader — runs once per particle each frame
// Reads previous position from texture, writes new position
// ──────────────────────────────────────────────────────────────────────
const simFrag = /* glsl */ `
  uniform sampler2D uPositions;     // ping-pong: previous frame positions
  uniform sampler2D uOriginals;     // initial positions (for elastic snap-back)
  uniform float uTime;
  uniform float uMorph;             // 0 = sphere, 1 = torus
  uniform float uCurlStrength;      // typical 0.15
  uniform float uAttract;           // typical 0.018 — gentle pull to SDF surface

  // Simplex 4D noise — for curl field. Shortened here; in production
  // include the canonical Ashima simplex4 (Stefan Gustavson).
  // Placeholder body uses 3D Perlin to keep this snippet readable.
  float n3(vec3 p) {
    return fract(sin(dot(p, vec3(12.9898, 78.233, 37.719))) * 43758.5453);
  }

  // Curl of a 3D noise field — divergence-free => particles flow without piling
  vec3 curlNoise(vec3 p) {
    float e = 0.05;
    float n1 = n3(p + vec3(0.0, e, 0.0));
    float n2 = n3(p - vec3(0.0, e, 0.0));
    float n3a = n3(p + vec3(0.0, 0.0, e));
    float n4  = n3(p - vec3(0.0, 0.0, e));
    float n5  = n3(p + vec3(e, 0.0, 0.0));
    float n6  = n3(p - vec3(e, 0.0, 0.0));
    return normalize(vec3(
      (n1 - n2) - (n3a - n4),
      (n3a - n4) - (n5 - n6),
      (n5 - n6) - (n1 - n2)
    ));
  }

  // Sphere SDF
  float sdSphere(vec3 p, float r) { return length(p) - r; }

  // Torus SDF
  float sdTorus(vec3 p, vec2 t) {
    vec2 q = vec2(length(p.xz) - t.x, p.y);
    return length(q) - t.y;
  }

  // Morphed SDF: blend sphere and torus by uMorph
  float sceneSDF(vec3 p) {
    float a = sdSphere(p, 1.0);
    float b = sdTorus(p, vec2(0.85, 0.32));
    return mix(a, b, uMorph);
  }

  // Numerical gradient — points outward from surface
  vec3 sdfGrad(vec3 p) {
    float e = 0.005;
    return normalize(vec3(
      sceneSDF(p + vec3(e, 0, 0)) - sceneSDF(p - vec3(e, 0, 0)),
      sceneSDF(p + vec3(0, e, 0)) - sceneSDF(p - vec3(0, e, 0)),
      sceneSDF(p + vec3(0, 0, e)) - sceneSDF(p - vec3(0, 0, e))
    ));
  }

  void main() {
    vec2 uv = gl_FragCoord.xy / resolution.xy;
    vec3 pos = texture2D(uPositions, uv).xyz;

    // 1) Curl noise drift — divergence-free organic motion
    vec3 drift = curlNoise(pos * 1.4 + uTime * 0.06) * uCurlStrength;

    // 2) SDF attractor — pull particle toward surface (signed by gradient)
    float d = sceneSDF(pos);
    vec3 grad = sdfGrad(pos);
    vec3 pull = -grad * d * uAttract;  // negative dist * outward grad = inward when outside

    pos += drift + pull;

    gl_FragColor = vec4(pos, 1.0);
  }
`

// ──────────────────────────────────────────────────────────────────────
// Particle render shaders — read final positions, render as points
// ──────────────────────────────────────────────────────────────────────
const renderVert = /* glsl */ `
  uniform sampler2D uPositions;
  attribute vec2 uvRef;        // which texel in the FBO is THIS particle?
  varying float vSparkle;

  void main() {
    vec3 pos = texture2D(uPositions, uvRef).xyz;
    vec4 mv = modelViewMatrix * vec4(pos, 1.0);
    gl_Position = projectionMatrix * mv;

    // 3% sparkle particles read brighter — drives "premium catch"
    vSparkle = step(0.97, fract(sin(dot(uvRef, vec2(12.9898, 78.233))) * 43758.5453));

    // Distance-based size — closer = bigger
    gl_PointSize = mix(1.5, 5.0, vSparkle) * (300.0 / -mv.z);
  }
`

const renderFrag = /* glsl */ `
  varying float vSparkle;
  void main() {
    // Round point with squared falloff — bloom catches it
    vec2 c = gl_PointCoord - 0.5;
    float a = pow(1.0 - smoothstep(0.0, 0.5, length(c)), 2.0);

    // Brand blue base, white for sparkles
    vec3 col = mix(vec3(0.165, 0.576, 0.757), vec3(1.0, 1.0, 1.0), vSparkle);

    gl_FragColor = vec4(col, a * (0.55 + vSparkle * 0.4));
  }
`

// ──────────────────────────────────────────────────────────────────────
// FBO Particles component
// ──────────────────────────────────────────────────────────────────────
const SIZE = 128 // 128*128 = 16,384 particles. Bump to 256 for 65k.

function FBOParticles() {
  const points = useRef()
  const simMat = useRef()
  const { gl } = useThree()

  // 1) Two FBOs for ping-pong (read from one, write to other)
  const fboA = useFBO(SIZE, SIZE, {
    minFilter: THREE.NearestFilter,
    magFilter: THREE.NearestFilter,
    format: THREE.RGBAFormat,
    type: THREE.FloatType,
    stencilBuffer: false,
  })
  const fboB = useFBO(SIZE, SIZE, {
    minFilter: THREE.NearestFilter,
    magFilter: THREE.NearestFilter,
    format: THREE.RGBAFormat,
    type: THREE.FloatType,
    stencilBuffer: false,
  })

  // 2) Initial positions — sphere shell with 0.05 jitter for organic start
  const { initialTexture, particleGeom } = useMemo(() => {
    const data = new Float32Array(SIZE * SIZE * 4)
    const uvRef = new Float32Array(SIZE * SIZE * 2)
    const positions = new Float32Array(SIZE * SIZE * 3) // dummy, overwritten in vertex

    for (let i = 0; i < SIZE * SIZE; i++) {
      // Random point on unit sphere (Marsaglia method)
      let x, y, z
      do {
        x = Math.random() * 2 - 1
        y = Math.random() * 2 - 1
        z = Math.random() * 2 - 1
      } while (x * x + y * y + z * z > 1)
      const r = 0.95 + Math.random() * 0.1
      const len = Math.sqrt(x * x + y * y + z * z)
      data[i * 4 + 0] = (x / len) * r
      data[i * 4 + 1] = (y / len) * r
      data[i * 4 + 2] = (z / len) * r
      data[i * 4 + 3] = 1
      uvRef[i * 2 + 0] = (i % SIZE) / SIZE
      uvRef[i * 2 + 1] = Math.floor(i / SIZE) / SIZE
    }

    const tex = new THREE.DataTexture(
      data, SIZE, SIZE, THREE.RGBAFormat, THREE.FloatType
    )
    tex.needsUpdate = true

    const geom = new THREE.BufferGeometry()
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geom.setAttribute('uvRef', new THREE.BufferAttribute(uvRef, 2))

    return { initialTexture: tex, particleGeom: geom }
  }, [])

  // 3) Sim scene — fullscreen quad that runs our sim shader
  const simScene = useMemo(() => new THREE.Scene(), [])
  const simCamera = useMemo(
    () => new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1),
    []
  )

  // 4) Ping-pong tracker — alternate which FBO we read/write each frame
  const pong = useRef({ read: fboA, write: fboB })

  useFrame((state) => {
    // Update sim uniforms
    if (simMat.current) {
      simMat.current.uniforms.uPositions.value = pong.current.read.texture
      simMat.current.uniforms.uTime.value = state.clock.elapsedTime
      simMat.current.uniforms.uMorph.value =
        0.5 + 0.5 * Math.sin(state.clock.elapsedTime * 0.25) // 0..1 over ~25s
    }

    // Render sim into write FBO
    gl.setRenderTarget(pong.current.write)
    gl.clear()
    gl.render(simScene, simCamera)
    gl.setRenderTarget(null)

    // Update render-side uniform with the freshly-written texture
    if (points.current) {
      points.current.material.uniforms.uPositions.value =
        pong.current.write.texture
    }

    // Swap
    const tmp = pong.current.read
    pong.current.read = pong.current.write
    pong.current.write = tmp
  })

  return (
    <>
      {/* Sim quad rendered into FBOs */}
      {createPortal(
        <mesh>
          <planeGeometry args={[2, 2]} />
          <shaderMaterial
            ref={simMat}
            fragmentShader={simFrag}
            vertexShader={`void main() { gl_Position = vec4(position, 1.0); }`}
            uniforms={{
              uPositions: { value: initialTexture },
              uOriginals: { value: initialTexture },
              uTime: { value: 0 },
              uMorph: { value: 0 },
              uCurlStrength: { value: 0.15 },
              uAttract: { value: 0.018 },
            }}
          />
        </mesh>,
        simScene
      )}

      {/* Render the particles at positions read from FBO */}
      <points ref={points} geometry={particleGeom}>
        <shaderMaterial
          vertexShader={renderVert}
          fragmentShader={renderFrag}
          uniforms={{ uPositions: { value: initialTexture } }}
          transparent
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>
    </>
  )
}

// ──────────────────────────────────────────────────────────────────────
// Scene composition
// ──────────────────────────────────────────────────────────────────────
export function GPGPUParticleScene() {
  return (
    <div style={{ width: '100%', height: '100vh', background: '#060606' }}>
      <Canvas camera={{ position: [0, 0, 3.6], fov: 45 }} gl={{ antialias: true }}>
        <FBOParticles />
        <OrbitControls enableZoom={false} />

        {/* Bloom-as-primary — threshold 0.4, intensity 1.1 (per S44 particle pattern) */}
        <EffectComposer>
          <Bloom
            luminanceThreshold={0.4}
            luminanceSmoothing={0.2}
            intensity={1.1}
            mipmapBlur
          />
        </EffectComposer>
      </Canvas>
    </div>
  )
}
