<script type="module">
  import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js';
  import { EffectComposer }   from 'https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/postprocessing/EffectComposer.js';
  import { RenderPass }       from 'https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/postprocessing/RenderPass.js';
  import { UnrealBloomPass }  from 'https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/postprocessing/UnrealBloomPass.js';
  import { OutputPass }       from 'https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/postprocessing/OutputPass.js';

  // ─────────────────────────────────────────────────────────────────────────────
  // BRAND CONSTANTS
  // ─────────────────────────────────────────────────────────────────────────────
  const C_BLUE   = new THREE.Color(0x2a93c1);
  const C_ORANGE = new THREE.Color(0xe86020);
  const C_BG     = new THREE.Color(0x0a0e1a);
  const C_IDLE   = new THREE.Color(0x1a2840);

  // ─────────────────────────────────────────────────────────────────────────────
  // DEVICE DETECTION
  // ─────────────────────────────────────────────────────────────────────────────
  const isMobile   = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent) || window.innerWidth < 768;
  const isLowPower = isMobile;

  const NODE_COUNT      = isLowPower ? 160 : 280;
  const AMBIENT_COUNT   = isLowPower ? 800 : 1800;
  const MAX_PULSES      = isLowPower ? 60  : 120;
  const MAX_SPARKS      = isLowPower ? 300 : 600;
  const PIXEL_RATIO_MAX = isLowPower ? 1   : 2;

  // ─────────────────────────────────────────────────────────────────────────────
  // SCENE SETUP
  // ─────────────────────────────────────────────────────────────────────────────
  const container = document.getElementById('pb-canvas-container');
  let W = window.innerWidth;
  let H = window.innerHeight;

  const renderer = new THREE.WebGLRenderer({
    antialias: !isLowPower,
    alpha: false,
    powerPreference: isLowPower ? 'low-power' : 'high-performance'
  });
  renderer.setSize(W, H);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, PIXEL_RATIO_MAX));
  renderer.setClearColor(C_BG, 1);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = C_BG;
  scene.fog = new THREE.FogExp2(0x0a0e1a, isLowPower ? 0.045 : 0.038);

  function getInitialFOV() {
    const aspect = W / H;
    return aspect < 0.8 ? 70 : 55;
  }

  const camera = new THREE.PerspectiveCamera(getInitialFOV(), W / H, 0.1, 200);
  const CAMERA_Z = isLowPower ? 26 : 22;
  camera.position.set(0, 0, CAMERA_Z);
  camera.lookAt(0, 0, 0);

  // PMREM environment
  const pmremGenerator = new THREE.PMREMGenerator(renderer);
  pmremGenerator.compileCubemapShader();
  const probeScene = new THREE.Scene();
  const envKey  = new THREE.PointLight(0x4ab8ff, 6.0, 60);
  envKey.position.set(5, 8, 5);
  const envFill = new THREE.PointLight(0x2a93c1, 3.5, 40);
  envFill.position.set(-6, 2, 3);
  const envRim  = new THREE.PointLight(0xe86020, 1.2, 30);
  envRim.position.set(1, -2, -8);
  probeScene.add(envKey, envFill, envRim);
  const envTexture = pmremGenerator.fromScene(probeScene).texture;
  scene.environment = envTexture;
  pmremGenerator.dispose();

  // ─────────────────────────────────────────────────────────────────────────────
  // NEURAL NETWORK
  // ─────────────────────────────────────────────────────────────────────────────
  const CONNECTION_LIMIT = 4;
  const FIRE_DURATION    = 1.2;
  const PULSE_SPEED      = 2.8;

  class Neuron {
    constructor(id, position) {
      this.id = id; this.position = position;
      this.connections = []; this.fireTime = -999;
      this.fireIntensity = 0;
      this.baseColor = C_IDLE.clone(); this.currentColor = C_IDLE.clone();
    }
  }

  const neurons = [];

  function brainPosition() {
    const hemisphere = Math.random() > 0.5 ? 1 : -1;
    let x, y, z; let attempts = 0;
    do {
      const r = Math.cbrt(Math.random());
      const theta = Math.random() * Math.PI * 2;
      const phi   = Math.acos(2 * Math.random() - 1);
      x = r * 8.5 * Math.sin(phi) * Math.cos(theta) + hemisphere * 1.0;
      y = r * 5.0 * Math.cos(phi);
      z = r * 6.0 * Math.sin(phi) * Math.sin(theta);
      const distFromCenter = Math.sqrt(x * x + z * z);
      if (distFromCenter > 1.5 && Math.abs(y) < 5) break;
      attempts++;
    } while (attempts < 30);
    return new THREE.Vector3(x, y, z);
  }

  for (let i = 0; i < NODE_COUNT; i++) neurons.push(new Neuron(i, brainPosition()));

  for (let i = 0; i < NODE_COUNT; i++) {
    const ni = neurons[i];
    if (ni.connections.length >= CONNECTION_LIMIT) continue;
    const distances = [];
    for (let j = i + 1; j < NODE_COUNT; j++) {
      const nj = neurons[j];
      if (nj.connections.length >= CONNECTION_LIMIT) continue;
      const d = ni.position.distanceTo(nj.position);
      if (d < 6.5) distances.push({ j, d });
    }
    distances.sort((a, b) => a.d - b.d);
    for (const { j } of distances.slice(0, CONNECTION_LIMIT - ni.connections.length)) {
      const nj = neurons[j];
      if (nj.connections.length >= CONNECTION_LIMIT) continue;
      ni.connections.push(j); nj.connections.push(i);
    }
  }

  const neuronGeo = new THREE.SphereGeometry(0.12, isLowPower ? 8 : 12, isLowPower ? 6 : 8);
  const neuronMeshes = []; const neuronMaterials = [];

  for (let i = 0; i < NODE_COUNT; i++) {
    const mat = new THREE.MeshPhysicalMaterial({
      color: C_IDLE, emissive: C_IDLE.clone(), emissiveIntensity: 0.25,
      roughness: 0.15, metalness: 0.05,
    });
    const mesh = new THREE.Mesh(neuronGeo, mat);
    mesh.position.copy(neurons[i].position);
    const scale = 0.6 + Math.random() * 0.8;
    mesh.scale.setScalar(scale);
    scene.add(mesh); neuronMeshes.push(mesh); neuronMaterials.push(mat);
  }

  const edges = []; const edgeSet = new Set(); const edgeLookup = new Map();
  for (let i = 0; i < NODE_COUNT; i++) {
    for (const j of neurons[i].connections) {
      const key = Math.min(i, j) * 10000 + Math.max(i, j);
      if (!edgeSet.has(key)) {
        edgeSet.add(key);
        const edgeIndex = edges.length;
        edges.push([i, j]); edgeLookup.set(key, edgeIndex);
      }
    }
  }

  function getEdgeIndex(a, b) {
    const key = Math.min(a, b) * 10000 + Math.max(a, b);
    return edgeLookup.get(key) ?? -1;
  }

  const linePositions = new Float32Array(edges.length * 2 * 3);
  const lineColors    = new Float32Array(edges.length * 2 * 3);

  for (let e = 0; e < edges.length; e++) {
    const [i, j] = edges[e];
    const pi = neurons[i].position; const pj = neurons[j].position;
    linePositions[e*6+0]=pi.x; linePositions[e*6+1]=pi.y; linePositions[e*6+2]=pi.z;
    linePositions[e*6+3]=pj.x; linePositions[e*6+4]=pj.y; linePositions[e*6+5]=pj.z;
    const ir=0.08,ig=0.14,ib=0.22;
    lineColors[e*6+0]=ir; lineColors[e*6+1]=ig; lineColors[e*6+2]=ib;
    lineColors[e*6+3]=ir; lineColors[e*6+4]=ig; lineColors[e*6+5]=ib;
  }

  const lineGeo = new THREE.BufferGeometry();
  lineGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
  lineGeo.setAttribute('color',    new THREE.BufferAttribute(lineColors, 3));
  const lineMat = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.65, linewidth: 1 });
  const lineSegments = new THREE.LineSegments(lineGeo, lineMat);
  scene.add(lineSegments);

  // Pulse particles
  const pulses = [];
  const pulseGeo = new THREE.BufferGeometry();
  const pulsePositions = new Float32Array(MAX_PULSES * 3);
  const pulseColors    = new Float32Array(MAX_PULSES * 3);
  const pulseSizes     = new Float32Array(MAX_PULSES);
  pulseGeo.setAttribute('position', new THREE.BufferAttribute(pulsePositions, 3));
  pulseGeo.setAttribute('color',    new THREE.BufferAttribute(pulseColors, 3));
  pulseGeo.setAttribute('size',     new THREE.BufferAttribute(pulseSizes, 1));
  const pulseMat = new THREE.ShaderMaterial({
    uniforms: {},
    vertexShader: `attribute vec3 color; attribute float size; varying vec3 vColor;
      void main() { vColor = color; vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      gl_PointSize = size * (350.0 / -mvPosition.z); gl_Position = projectionMatrix * mvPosition; }`,
    fragmentShader: `varying vec3 vColor;
      void main() { vec2 uv = gl_PointCoord - 0.5; float d = dot(uv,uv); if(d>0.25) discard;
      float alpha = 1.0 - smoothstep(0.1,0.25,d); float core = 1.0 - smoothstep(0.0,0.12,d);
      vec3 fc = mix(vColor, vec3(1.0,1.0,0.95), core*0.7); gl_FragColor = vec4(fc, alpha*0.95); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, vertexColors: false,
  });
  const pulsePoints = new THREE.Points(pulseGeo, pulseMat);
  scene.add(pulsePoints);
  for (let i = 0; i < MAX_PULSES; i++) pulses.push({ active: false, edgeIndex: -1, t: 0, speed: 0, color: new THREE.Color(), fromIndex: -1, toIndex: -1 });

  function spawnPulse(edgeIndex, fromNeuron, toNeuron, color) {
    for (let i = 0; i < MAX_PULSES; i++) {
      if (!pulses[i].active) {
        const p = pulses[i];
        p.active=true; p.edgeIndex=edgeIndex; p.t=0;
        p.speed=0.6+Math.random()*0.5; p.color.copy(color); p.fromIndex=fromNeuron; p.toIndex=toNeuron;
        return;
      }
    }
  }

  // Ambient particles
  const ambientGeo = new THREE.BufferGeometry();
  const ambientPos = new Float32Array(AMBIENT_COUNT * 3);
  const ambientCol = new Float32Array(AMBIENT_COUNT * 3);
  const ambientSz  = new Float32Array(AMBIENT_COUNT);
  const ambientVel = new Float32Array(AMBIENT_COUNT * 3);
  for (let i = 0; i < AMBIENT_COUNT; i++) {
    const r = Math.cbrt(Math.random()) * 12;
    const theta = Math.random() * Math.PI * 2;
    const phi   = Math.acos(2 * Math.random() - 1);
    ambientPos[i*3+0] = r * Math.sin(phi) * Math.cos(theta);
    ambientPos[i*3+1] = r * 0.6 * Math.cos(phi);
    ambientPos[i*3+2] = r * Math.sin(phi) * Math.sin(theta);
    const t2 = Math.random();
    if (t2 < 0.85) { ambientCol[i*3+0]=0.05+Math.random()*0.1; ambientCol[i*3+1]=0.12+Math.random()*0.12; ambientCol[i*3+2]=0.25+Math.random()*0.2; }
    else           { ambientCol[i*3+0]=0.2+Math.random()*0.2;  ambientCol[i*3+1]=0.08+Math.random()*0.07; ambientCol[i*3+2]=0.01; }
    ambientSz[i] = 0.3 + Math.random() * 0.8;
    const speed = 0.003 + Math.random() * 0.008;
    const dTheta = Math.random() * Math.PI * 2;
    ambientVel[i*3+0]=Math.cos(dTheta)*speed; ambientVel[i*3+1]=(Math.random()-0.5)*speed*0.3; ambientVel[i*3+2]=Math.sin(dTheta)*speed;
  }
  ambientGeo.setAttribute('position', new THREE.BufferAttribute(ambientPos, 3));
  ambientGeo.setAttribute('color',    new THREE.BufferAttribute(ambientCol, 3));
  ambientGeo.setAttribute('size',     new THREE.BufferAttribute(ambientSz, 1));
  const ambientMat = new THREE.ShaderMaterial({
    uniforms: {},
    vertexShader: `attribute vec3 color; attribute float size; varying vec3 vColor; varying float vAlpha;
      void main() { vColor=color; vAlpha=0.18+size*0.08; vec4 mvPosition=modelViewMatrix*vec4(position,1.0);
      gl_PointSize=size*(280.0/-mvPosition.z); gl_Position=projectionMatrix*mvPosition; }`,
    fragmentShader: `varying vec3 vColor; varying float vAlpha;
      void main() { vec2 uv=gl_PointCoord-0.5; float d=dot(uv,uv); if(d>0.25) discard;
      float alpha=vAlpha*(1.0-smoothstep(0.05,0.25,d)); gl_FragColor=vec4(vColor,alpha); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const ambientPoints = new THREE.Points(ambientGeo, ambientMat);
  scene.add(ambientPoints);

  // Spark burst
  const sparkGeo = new THREE.BufferGeometry();
  const sparkPos  = new Float32Array(MAX_SPARKS * 3);
  const sparkCol  = new Float32Array(MAX_SPARKS * 3);
  const sparkSz   = new Float32Array(MAX_SPARKS);
  sparkGeo.setAttribute('position', new THREE.BufferAttribute(sparkPos, 3));
  sparkGeo.setAttribute('color',    new THREE.BufferAttribute(sparkCol, 3));
  sparkGeo.setAttribute('size',     new THREE.BufferAttribute(sparkSz, 1));
  const sparkMat = new THREE.ShaderMaterial({
    uniforms: {},
    vertexShader: `attribute vec3 color; attribute float size; varying vec3 vColor;
      void main() { vColor=color; vec4 mvPosition=modelViewMatrix*vec4(position,1.0);
      gl_PointSize=size*(400.0/-mvPosition.z); gl_Position=projectionMatrix*mvPosition; }`,
    fragmentShader: `varying vec3 vColor;
      void main() { vec2 uv=gl_PointCoord-0.5; float d=dot(uv,uv); if(d>0.25) discard;
      float alpha=pow(1.0-smoothstep(0.0,0.25,d),2.0); gl_FragColor=vec4(vColor,alpha); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const sparkPoints = new THREE.Points(sparkGeo, sparkMat);
  scene.add(sparkPoints);
  const sparks = [];
  for (let i = 0; i < MAX_SPARKS; i++) sparks.push({ active: false, pos: new THREE.Vector3(), vel: new THREE.Vector3(), life: 0, maxLife: 0, color: new THREE.Color() });

  function spawnSparks(origin, color, count = 6) {
    const isOrange = color.r > 0.6 && color.b < 0.3;
    const actualCount = isOrange ? Math.max(3, Math.floor(count * 0.6)) : count;
    let spawned = 0;
    for (let i = 0; i < MAX_SPARKS &#038;&#038; spawned < actualCount; i++) {
      if (!sparks[i].active) {
        const s = sparks[i]; s.active = true; s.pos.copy(origin);
        const speed = 0.04 + Math.random() * 0.12;
        s.vel.set((Math.random()-0.5)*speed, (Math.random()-0.5)*speed, (Math.random()-0.5)*speed);
        s.life = 0; s.maxLife = 0.4 + Math.random() * 0.6; s.color.copy(color); spawned++;
      }
    }
  }

  // Postprocessing
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(W, H),
    isLowPower ? 1.0 : 1.4,
    isLowPower ? 0.4 : 0.6,
    0.15
  );
  composer.addPass(bloomPass);
  composer.addPass(new OutputPass());

  // Mouse / touch parallax
  const mouse         = new THREE.Vector2(0, 0);
  const mouseWorld    = new THREE.Vector3(0, 0, 0);
  const raycaster     = new THREE.Raycaster();
  const mousePlane    = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
  const cameraTarget  = new THREE.Vector3(0, 0, CAMERA_Z);
  const cameraLookTarget = new THREE.Vector3(0, 0, 0);
  let lastMouseActivationTime = 0;
  const MOUSE_ACTIVATION_COOLDOWN = 0.08;

  function getClientXY(e) {
    if (e.touches &#038;&#038; e.touches.length > 0) return { x: e.touches[0].clientX, y: e.touches[0].clientY };
    return { x: e.clientX, y: e.clientY };
  }
  function onPointerMove(e) {
    const { x, y } = getClientXY(e);
    mouse.x = (x / window.innerWidth)  * 2 - 1;
    mouse.y = -(y / window.innerHeight) * 2 + 1;
    const parallaxX = isLowPower ? -1.0 : -1.8;
    const parallaxY = isLowPower ? -0.7 : -1.2;
    cameraTarget.x = mouse.x * parallaxX;
    cameraTarget.y = mouse.y * parallaxY;
    cameraTarget.z = CAMERA_Z;
    cameraLookTarget.x = mouse.x * 0.8;
    cameraLookTarget.y = mouse.y * 0.5;
  }
  window.addEventListener('mousemove',  onPointerMove);
  window.addEventListener('touchmove',  onPointerMove, { passive: true });
  window.addEventListener('touchstart', onPointerMove, { passive: true });

  // Neuron firing
  const firingQueue = [];

  function fireNeuron(neuronIndex, time, propagate = true, depth = 0, color = null) {
    const n = neurons[neuronIndex];
    if (time - n.fireTime < FIRE_DURATION * 0.7) return;
    n.fireTime = time;
    let fireColor;
    if (color)           { fireColor = color; }
    else if (depth === 0){ fireColor = C_BLUE; }
    else if (depth % 2 === 1) { fireColor = Math.random() < 0.6 ? C_ORANGE : C_BLUE; }
    else                 { fireColor = C_BLUE; }
    firingQueue.push({ index: neuronIndex, time, color: fireColor.clone() });
    const sparkCount = fireColor === C_ORANGE ? 3 + depth : 5 + depth * 2;
    spawnSparks(n.position, fireColor, sparkCount);
    if (propagate &#038;&#038; depth < 4) {
      const shuffled = [...n.connections].sort(() => Math.random() - 0.5);
      const propagateCount = Math.min(2 + Math.floor(Math.random() * 2), shuffled.length);
      for (let k = 0; k < propagateCount; k++) {
        const targetIndex = shuffled[k];
        const targetNeuron = neurons[targetIndex];
        const dist = n.position.distanceTo(targetNeuron.position);
        const travelTime = dist / PULSE_SPEED;
        const edgeIndex = getEdgeIndex(neuronIndex, targetIndex);
        if (edgeIndex >= 0) spawnPulse(edgeIndex, neuronIndex, targetIndex, fireColor);
        setTimeout(() => {
          const nextColor = fireColor === C_BLUE ? (Math.random() < 0.6 ? C_ORANGE : C_BLUE) : C_BLUE;
          fireNeuron(targetIndex, clock.getElapsedTime(), true, depth + 1, nextColor);
        }, travelTime * 1000);
      }
    }
  }

  function scheduleAmbientFire() {
    const neuronIndex = Math.floor(Math.random() * NODE_COUNT);
    const minDelay = isLowPower ? 300 : 200;
    const maxDelay = isLowPower ? 700 : 500;
    const delay = minDelay + Math.random() * (maxDelay - minDelay);
    setTimeout(() => {
      const initColor = Math.random() < 0.75 ? C_BLUE : C_ORANGE;
      fireNeuron(neuronIndex, clock.getElapsedTime(), true, 0, initColor);
      scheduleAmbientFire();
    }, delay);
  }

  function initialBurst() {
    for (let i = 0; i < 8; i++) {
      setTimeout(() => {
        const idx = Math.floor(Math.random() * NODE_COUNT);
        fireNeuron(idx, 0, true, 0, C_BLUE);
      }, i * 150);
    }
  }

  // Render loop
  const clock  = new THREE.Clock();
  const tmpV   = new THREE.Vector3();
  let isVisible = true;
  const _blueIdle = new THREE.Color(0x0d1a2d);

  function animate() {
    requestAnimationFrame(animate);
    if (!isVisible) return;

    const dt = clock.getDelta();
    const t  = clock.getElapsedTime();

    camera.position.lerp(cameraTarget, 0.025);
    camera.lookAt(cameraLookTarget);
    scene.rotation.y = Math.sin(t * 0.071) * 0.10 + Math.sin(t * 0.038) * 0.04;
    scene.rotation.x = Math.sin(t * 0.053) * 0.04 + Math.sin(t * 0.029) * 0.02;

    raycaster.setFromCamera(mouse, camera);
    raycaster.ray.intersectPlane(mousePlane, mouseWorld);

    if (t - lastMouseActivationTime > MOUSE_ACTIVATION_COOLDOWN) {
      const MOUSE_RADIUS = 4.0;
      for (let i = 0; i < NODE_COUNT; i++) {
        const n = neurons[i];
        tmpV.copy(n.position).applyMatrix4(scene.matrixWorld);
        const dx = tmpV.x - mouseWorld.x; const dy = tmpV.y - mouseWorld.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < MOUSE_RADIUS &#038;&#038; t - n.fireTime > FIRE_DURATION) {
          const prob = (1.0 - dist / MOUSE_RADIUS) * 0.25;
          if (Math.random() < prob) {
            const mouseColor = Math.random() < 0.7 ? C_BLUE : C_ORANGE;
            fireNeuron(i, t, true, 0, mouseColor);
            lastMouseActivationTime = t; break;
          }
        }
      }
    }

    // Update neuron materials
    for (let i = 0; i < NODE_COUNT; i++) {
      const n = neurons[i]; const mat = neuronMaterials[i];
      const age = t - n.fireTime;
      if (age < FIRE_DURATION) {
        let intensity;
        const rampUp = 0.3; const hold = 0.4; const rampDown = FIRE_DURATION - rampUp - hold;
        if (age < rampUp)             { intensity = age / rampUp; }
        else if (age < rampUp + hold) { intensity = 1.0; }
        else                          { intensity = 1.0 - (age - rampUp - hold) / rampDown; }
        intensity = Math.max(0, Math.min(1, intensity));
        const fc = firingQueue.find(f => f.index === i && f.time === n.fireTime);
        const fireColor = fc ? fc.color : C_BLUE;
        mat.emissive.copy(fireColor).multiplyScalar(intensity);
        mat.emissiveIntensity = 0.3 + intensity * 3.5;
        mat.color.lerpColors(C_IDLE, fireColor, intensity * 0.7);
      } else {
        const pulse = Math.sin(t * 0.8 + i * 0.3) * 0.5 + 0.5;
        mat.emissive.copy(_blueIdle);
        mat.emissiveIntensity = 0.1 + pulse * 0.08;
        mat.color.copy(C_IDLE);
      }
    }

    // Clean firing queue
    const QUEUE_TTL = FIRE_DURATION * 2;
    for (let i = firingQueue.length - 1; i >= 0; i--) {
      if (t - firingQueue[i].time > QUEUE_TTL) firingQueue.splice(i, 1);
    }

    // Update connection colors
    const colorsArr = lineGeo.attributes.color.array;
    for (let e = 0; e < edges.length; e++) {
      const [ai, bi] = edges[e];
      const na = neurons[ai]; const nb = neurons[bi];
      const ageA = t - na.fireTime; const ageB = t - nb.fireTime;
      const firedA = ageA < FIRE_DURATION; const firedB = ageB < FIRE_DURATION;
      let r, g, b;
      if (firedA || firedB) {
        const intensityA = firedA ? Math.max(0, 1.0 - ageA / FIRE_DURATION) : 0;
        const intensityB = firedB ? Math.max(0, 1.0 - ageB / FIRE_DURATION) : 0;
        const intensity = Math.max(intensityA, intensityB);
        r = 0.08 + intensity * 0.16; g = 0.14 + intensity * 0.45; b = 0.22 + intensity * 0.65;
      } else { r = 0.06; g = 0.10; b = 0.18; }
      colorsArr[e*6+0]=r; colorsArr[e*6+1]=g; colorsArr[e*6+2]=b;
      colorsArr[e*6+3]=r; colorsArr[e*6+4]=g; colorsArr[e*6+5]=b;
    }
    lineGeo.attributes.color.needsUpdate = true;

    // Update pulses
    const pPositions = pulseGeo.attributes.position.array;
    const pColors    = pulseGeo.attributes.color.array;
    const pSizes     = pulseGeo.attributes.size.array;
    for (let i = 0; i < MAX_PULSES; i++) {
      const p = pulses[i];
      if (!p.active) { pPositions[i*3]=9999; pSizes[i]=0; continue; }
      p.t += dt * p.speed;
      if (p.t >= 1.0) { p.active=false; pPositions[i*3]=9999; pSizes[i]=0; continue; }
      const fn = neurons[p.fromIndex]; const tn2 = neurons[p.toIndex];
      pPositions[i*3+0] = fn.position.x + (tn2.position.x - fn.position.x) * p.t;
      pPositions[i*3+1] = fn.position.y + (tn2.position.y - fn.position.y) * p.t;
      pPositions[i*3+2] = fn.position.z + (tn2.position.z - fn.position.z) * p.t;
      const pulseAge = p.t;
      pColors[i*3+0] = p.color.r + (1.0 - p.color.r) * pulseAge * 0.4;
      pColors[i*3+1] = p.color.g * (1.0 - pulseAge * 0.3);
      pColors[i*3+2] = p.color.b * (1.0 - pulseAge * 0.5);
      pSizes[i] = 2.5 + Math.sin(pulseAge * Math.PI) * 1.5;
    }
    pulseGeo.attributes.position.needsUpdate = true;
    pulseGeo.attributes.color.needsUpdate    = true;
    pulseGeo.attributes.size.needsUpdate     = true;

    // Update sparks
    const sPositions = sparkGeo.attributes.position.array;
    const sColors    = sparkGeo.attributes.color.array;
    const sSizes     = sparkGeo.attributes.size.array;
    for (let i = 0; i < MAX_SPARKS; i++) {
      const s = sparks[i];
      if (!s.active) { sPositions[i*3]=9999; sSizes[i]=0; continue; }
      s.life += dt;
      if (s.life >= s.maxLife) { s.active=false; sPositions[i*3]=9999; sSizes[i]=0; continue; }
      s.pos.x+=s.vel.x; s.pos.y+=s.vel.y; s.pos.z+=s.vel.z;
      s.vel.multiplyScalar(0.96);
      const lifeRatio = s.life / s.maxLife;
      sPositions[i*3+0]=s.pos.x; sPositions[i*3+1]=s.pos.y; sPositions[i*3+2]=s.pos.z;
      const brightness = Math.pow(1.0 - lifeRatio, 1.5);
      const hotCore = Math.max(0, 1.0 - lifeRatio * 3.0);
      sColors[i*3+0]=s.color.r*brightness+hotCore*0.8;
      sColors[i*3+1]=s.color.g*brightness+hotCore*0.7;
      sColors[i*3+2]=s.color.b*brightness+hotCore*0.4;
      sSizes[i]=(1.5+hotCore*2.0)*brightness;
    }
    sparkGeo.attributes.position.needsUpdate = true;
    sparkGeo.attributes.color.needsUpdate    = true;
    sparkGeo.attributes.size.needsUpdate     = true;

    // Update ambient particles
    for (let i = 0; i < AMBIENT_COUNT; i++) {
      ambientPos[i*3+0]+=ambientVel[i*3+0]; ambientPos[i*3+1]+=ambientVel[i*3+1]; ambientPos[i*3+2]+=ambientVel[i*3+2];
      const px=ambientPos[i*3+0]; const py=ambientPos[i*3+1]; const pz=ambientPos[i*3+2];
      const dist2 = Math.sqrt(px*px+(py/0.6)*(py/0.6)+pz*pz);
      if (dist2 > 13) { ambientVel[i*3+0]*=-0.8; ambientVel[i*3+1]*=-0.8; ambientVel[i*3+2]*=-0.8; }
    }
    ambientGeo.attributes.position.needsUpdate = true;

    composer.render();
  }

  // Resize
  function onResize() {
    W = window.innerWidth; H = window.innerHeight;
    camera.aspect = W / H;
    camera.fov = (W / H) < 0.8 ? 70 : 55;
    camera.updateProjectionMatrix();
    renderer.setSize(W, H);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, PIXEL_RATIO_MAX));
    composer.setSize(W, H);
    bloomPass.resolution.set(W, H);
  }
  window.addEventListener('resize', onResize);
  window.addEventListener('orientationchange', () => setTimeout(onResize, 200));

  // Click/tap burst
  function onTap(clientX, clientY) {
    const mx = (clientX / window.innerWidth)  * 2 - 1;
    const my = -(clientY / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(new THREE.Vector2(mx, my), camera);
    raycaster.ray.intersectPlane(mousePlane, mouseWorld);
    let minDist = Infinity; let nearestIdx = 0;
    for (let i = 0; i < NODE_COUNT; i++) {
      tmpV.copy(neurons[i].position).applyMatrix4(scene.matrixWorld);
      const dx = tmpV.x - mouseWorld.x; const dy = tmpV.y - mouseWorld.y;
      const d = Math.sqrt(dx*dx+dy*dy);
      if (d < minDist) { minDist = d; nearestIdx = i; }
    }
    fireNeuron(nearestIdx, clock.getElapsedTime(), true, 0, C_BLUE);
    spawnSparks(neurons[nearestIdx].position, C_BLUE, 20);
  }
  window.addEventListener('click',    (e) => onTap(e.clientX, e.clientY));
  window.addEventListener('touchend', (e) => {
    if (e.changedTouches.length > 0) onTap(e.changedTouches[0].clientX, e.changedTouches[0].clientY);
  }, { passive: true });

  document.addEventListener('visibilitychange', () => { isVisible = document.visibilityState === 'visible'; });

  // Launch
  initialBurst();
  scheduleAmbientFire();
  animate();
  console.log('[PureBrain Neural 3D] Invite landing — initialized');
  </script>