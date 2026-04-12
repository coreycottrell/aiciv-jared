# 3D Design Agent Capability Roadmap
## From Zero to Gleb Kuznetsov-Level Quality

**Prepared by**: web-researcher (Aether AI Collective)
**Date**: 2026-02-20
**Research Method**: Parallel investigation across APIs, tools, platforms, and reference links
**Purpose**: Actionable setup guide for design agents learning 3D modeling

---

## Executive Summary

AI agents can programmatically access a powerful and mature 3D design ecosystem right now. The path to Gleb Kuznetsov-level quality is clear: Three.js / React Three Fiber is the primary code-driven rendering layer, Sketchfab and Poly Haven provide the model library backbone, Spline handles no-code scene design with code export, and text-to-3D APIs (Meshy, Tripo3D) enable generative model creation. The Peach Worlds reference sites use a proprietary custom WebGL engine with Sketchfab artist Tamminen's animated sci-fi orbs, confirming that the aesthetic Jared wants is achievable with Three.js + premium postprocessing effects.

**Priority order for setup**: Sketchfab account (free) + Poly Haven API (free) + Meshy Pro API ($20/mo) + Spline Pro ($25/mo) = full capability stack under $50/month.

---

## Section 1: What the Reference Links Show

### 1.1 Peach Worlds Sites (worthy and tough subdomains)

Both sites are built on **PeachWeb** (formerly Peach Worlds), a no-code 3D WebGL website builder that raised pre-seed funding specifically to make immersive 3D websites accessible.

**Technical findings:**
- Canvas-based custom WebGL engine (not Three.js directly, but WebGL underneath)
- AWS + CloudFront CDN hosting for performance
- Sophisticated loading easing functions (cubic bezier math visible in source)
- Keyframe-based animation system
- Animated GIF elements layered over 3D canvas

**The "tough" site** credits 3D models to **TAMMINEN** - the Sketchfab artist at sketchfab.com/tamminen.

**Key insight**: These sites are not hand-coded Three.js. They use PeachWeb as a no-code builder, importing assets from artists like Tamminen. An AI agent cannot access PeachWeb programmatically (no API), but can replicate the aesthetic using Three.js directly.

**Replication strategy**: Use Three.js or React Three Fiber + load GLTF models from Sketchfab/Tamminen's portfolio + apply postprocessing effects to match quality.

### 1.2 Tamminen on Sketchfab

- 662 models, 51.7M triangles, 984K views
- Style: Animated sci-fi orbs, energy spheres, wormholes, vortexes, magical effects
- Tools: Blender (modeling) + ZBrush (sculpting) + Substance (texturing) + Unity (game engine)
- Most models are downloadable and animated
- **This is the exact aesthetic used on the Peach Worlds sites**

**Key insight**: Tamminen's animated orbs are Sketchfab downloadable assets. An agent with a Sketchfab account can download these as GLTF/GLB and embed them in Three.js scenes.

### 1.3 Ramotion 3D Website Design Blog

Confirms the industry-standard stack:
- Three.js (most popular WebGL library)
- Babylon.js (high-performance alternative)
- Spline (no-code with code export)
- Blender (source asset creation)
- GLTF/GLB as the universal format

---

## Section 2: What Tools AI Agents Can Programmatically Access

### 2.1 Sketchfab API - FULLY ACCESSIBLE

**What it provides:**
- Search 1M+ models with filters: keywords, tags, categories, license type (CC0, CC-BY), animated status, downloadable status, polygon count, PBR materials
- Download models in GLTF, GLB, and USDZ formats via REST API
- Upload models, manage collections, access metadata
- Python, JavaScript, PHP, Ruby, Swift code examples available

**Authentication:**
- Free account: API token from user settings
- OAuth 2.0 for end-user authentication in apps
- Commercial Viewer API requires Premium membership ($79/mo)

**Download API workflow:**
```
1. Search: GET /v3/models?type=models&q={keyword}&downloadable=true&license=CC-BY
2. Get download URL: GET /v3/models/{uid}/download
3. Retrieve Authorization header token
4. Download from returned URL (GLTF/GLB format)
```

**Key limitation**: Downloading requires authenticated Sketchfab account. For agent automation without per-user auth, contact Sketchfab directly (they have provisions for this).

**License filters available:**
- CC0 (public domain - no restrictions)
- CC-BY (attribution required)
- CC-BY-SA
- CC-BY-ND
- CC-BY-NC
- Editorial Use Only

**2025 note**: Fab (Epic Games, which acquired Sketchfab) plans to release a public download API for Fab in 2025, expanding accessible model libraries further.

**Apify integration**: An existing Apify actor (sketchfab-ai-3d-model-search) enables AI-driven Sketchfab search without building custom API integration.

### 2.2 Poly Haven API - FREE, NO AUTH REQUIRED (for non-commercial)

**What it provides:**
- Complete catalog of CC0 HDRIs, PBR textures, and 3D models
- All assets are public domain - no license restrictions
- Download any size/format programmatically

**API endpoints:**
```
GET https://api.polyhaven.com/assets?type=hdris    # List HDRIs
GET https://api.polyhaven.com/assets?type=textures  # List textures
GET https://api.polyhaven.com/assets?type=models    # List models
GET https://api.polyhaven.com/files/{asset_slug}    # Get download URLs by resolution
```

**Python package**: `pip install polydown` - batch downloader using their public API

**Authentication**: Just a User-Agent header (your app name). No account required.

**Why this matters for design agents**: Poly Haven provides premium HDR environment maps that create the lighting quality seen in Gleb Kuznetsov's work. One good HDRI transforms flat-looking Three.js scenes into premium renders.

**Commercial use**: Requires custom license/sponsorship with Poly Haven team.

### 2.3 Blender Python API (bpy) - HEADLESS AUTOMATION

**Capability**: Full 3D modeling, rendering, and asset export from command line.

```bash
# Run Blender headless with Python script
blender --headless --python my_script.py

# Example: render a scene to PNG
blender -b scene.blend -f 1

# Example: export to GLTF
blender --headless --python export_gltf.py
```

**What bpy enables agents to do:**
- Create geometry procedurally (spheres, complex meshes, boolean operations)
- Apply materials and shaders (including glass, transmission, metallic)
- Set up lighting (HDRI, area lights, point lights)
- Animate objects (keyframes, physics, particle systems)
- Export to GLTF/GLB for web use
- Render still images (PNG, EXR) and animations (MP4)

**Python package**: `pip install blenderless` - simplifies headless rendering

**Key capability for avatar creation**: Blender can generate the base 3D form programmatically, apply Gleb-style glass materials, set up studio lighting, and export as GLB for web embedding.

**Limitation**: Blender must be installed on the system. Heavy compute requirements for rendering.

### 2.4 Three.js and React Three Fiber - PURE CODE, MAXIMUM CONTROL

**The primary web-delivery layer for everything.**

Three.js enables agents to write JavaScript that creates complete 3D scenes:
```javascript
// An AI agent can generate this code entirely from description
const geometry = new THREE.SphereGeometry(1, 64, 64);
const material = new THREE.MeshPhysicalMaterial({
  transmission: 1.0,
  thickness: 0.5,
  roughness: 0.1,
  ior: 1.5,
  color: new THREE.Color('#ffffff'),
});
const sphere = new THREE.Mesh(geometry, material);
scene.add(sphere);
```

**React Three Fiber (R3F)** wraps Three.js in React components - AI agents can generate entire 3D web experiences as JSX:
```jsx
// AI generates this as component code
function GlassSphere() {
  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <MeshTransmissionMaterial
        transmission={1}
        thickness={0.5}
        roughness={0.1}
        chromaticAberration={0.5}
      />
    </mesh>
  );
}
```

**The @react-three/drei package** provides pre-built components:
- `MeshTransmissionMaterial` - premium glass/transmission effects
- `Environment` - HDRI environment maps (can use Poly Haven HDRIs)
- `Float` - gentle floating animation
- `OrbitControls` - user interaction
- `useGLTF` - load GLTF models from Sketchfab
- `Sparkles` - particle effects

**The @react-three/postprocessing package** provides Gleb-level effects:
- `Bloom` - glow/luminance effects
- `DepthOfField` - bokeh/focus effects
- `ChromaticAberration` - lens dispersion
- `Vignette` - edge darkening
- `Noise` - film grain
- `LensFlare` - light flares

**AI code generation for Three.js**: Multiple tools exist specifically for this:
- Workik AI Three.js Code Generator (free, web-based)
- v0 by Vercel with R3F support
- Claude/GPT already know Three.js deeply and can generate complete scenes from descriptions

### 2.5 Spline - NO-CODE DESIGN WITH CODE EXPORT

**What it is**: Browser-based 3D design tool, no Blender skills needed.

**Export capabilities:**
- Vanilla JS (with full animations and events)
- React (with full animations and events)
- Three.js (static scene data)
- Next.js
- React Three Fiber
- GLTF/USDZ for 3D format

**The r3f-spline package**: `@splinetool/r3f-spline` lets agents load Spline-designed scenes directly into React Three Fiber code.

**Key workflow for agents:**
1. Human designs scene in Spline (or agent prompts Spline AI)
2. Export as React/Vanilla JS code
3. Agent receives the code, modifies it programmatically
4. Agent adds custom logic, interactions, integrations

**Spline AI**: Spline now has AI features for generating 3D content from prompts within the tool.

**Pricing:**
- Free: Working but exports include Spline watermark
- Starter ($15/mo): No watermark, video imports
- Professional ($25/mo): Code export, mobile export, version history - REQUIRED for agent use
- Team ($36/seat/mo): Collaboration features

**No public API**: Spline does not expose a REST API for programmatic scene creation. Access is through the GUI or exported code.

### 2.6 Meshy AI - TEXT/IMAGE TO 3D MODEL API

**The fastest path to custom 3D models without Blender skills.**

**API capabilities:**
- Text to 3D: Describe a model in words, get GLTF/GLB back
- Image to 3D: Upload photo, get 3D model
- AI Texturing: Take existing geometry, AI applies textures
- Auto-rigging and animation generation

**Pricing for API use:**
- Free: 100 credits/month, 10 downloads (no API access)
- Pro ($20/mo): 1,000 credits/month, API access enabled
- Text to 3D = 20 credits per model
- Image to 3D = 15-30 credits per model
- With Pro: ~50 text-to-3D models per month

**Output formats**: GLB, FBX, OBJ, STL, 3MF, USDZ, BLEND

**Rate limits**: 20 requests/second, 10 concurrent tasks (Pro tier)

**Workflow:**
```python
import requests

response = requests.post(
    "https://api.meshy.ai/v2/text-to-3d",
    headers={"Authorization": f"Bearer {MESHY_API_KEY}"},
    json={"prompt": "glass orb with energy swirling inside, sci-fi aesthetic"}
)
task_id = response.json()["result"]
# Poll for completion, download GLB
```

### 2.7 Tripo3D - ALTERNATIVE TEXT-TO-3D API

**Models available**: v1.4 (fast), v2.0 (accurate + PBR), v2.5 (balanced), v3.0 (sculpture-level)
**Input types**: Text, single image, multi-image (front/side/top views)
**Style options**: Cartoon, clay, alien, Christmas, steampunk, and others
**Output**: GLB, FBX, OBJ

**Also offers**: Text-to-CAD API for precise engineering models (launched 2025)

**Advantage over Meshy**: More model quality tiers, particularly v3.0 for high-quality work.

### 2.8 Rive - INTERACTIVE ANIMATION WITH MCP INTEGRATION

**What it is**: Animation tool for interactive micro-animations, not full 3D scenes.

**Key 2025 development**: Rive now has an official MCP server - AI agents can interact with Rive programmatically via the Model Context Protocol.

**Scripting with AI Coding Agent**: Rive launched an AI coding agent in Early Access 2025 that iterates on code, design, and animation in a single collaborative editor.

**Best for**: Interactive UI animations, animated logos, state-machine-driven elements (hover states, loading animations). Not ideal for full 3D environments.

**Web runtime**: The Rive runtime embeds interactive animations on any website with minimal code.

---

## Section 3: Gleb Kuznetsov-Level - The Technical Path

### What Makes Gleb's Work Distinctive

1. **Glass/transmission materials**: Objects that refract and transmit light, not just reflect
2. **Depth of field**: Soft bokeh blur on elements not in focus
3. **Chromatic aberration**: Slight color separation at edges (lens distortion)
4. **Bloom/glow**: Luminous materials that appear to emit light
5. **Premium HDR lighting**: Complex multi-light setups with HDRI environments
6. **Subtle animation**: Floating, pulsing, rotating - never jarring
7. **Volumetric elements**: Fog, particles, energy effects inside objects
8. **Dark backgrounds**: Black or very dark base makes glass/glow effects pop

### The Three.js Stack That Replicates This

```jsx
// Complete Gleb-level setup in React Three Fiber
import { Canvas } from '@react-three/fiber'
import { Environment, Float } from '@react-three/drei'
import { MeshTransmissionMaterial } from '@react-three/drei'
import { EffectComposer, Bloom, DepthOfField, ChromaticAberration } from '@react-three/postprocessing'

function GlebStyleScene() {
  return (
    <Canvas camera={{ position: [0, 0, 4], fov: 45 }}>
      {/* HDRI lighting from Poly Haven */}
      <Environment files="/polyhaven_studio.hdr" />

      {/* Floating glass sphere */}
      <Float speed={1.5} rotationIntensity={0.5} floatIntensity={0.5}>
        <mesh>
          <sphereGeometry args={[1.2, 128, 128]} />
          <MeshTransmissionMaterial
            transmission={1}
            thickness={0.8}
            roughness={0.05}
            ior={1.5}
            chromaticAberration={0.8}
            backside={true}
            color="#88ccff"
          />
        </mesh>
      </Float>

      {/* Premium postprocessing */}
      <EffectComposer>
        <DepthOfField focusDistance={0.01} focalLength={0.05} bokehScale={3} />
        <Bloom luminanceThreshold={0.9} luminanceSmoothing={0.025} intensity={0.5} />
        <ChromaticAberration offset={[0.002, 0.002]} />
      </EffectComposer>
    </Canvas>
  );
}
```

### Tool-by-Tool Contribution to Gleb Quality

| Effect | Tool | Implementation |
|--------|------|----------------|
| Glass material | Three.js MeshTransmissionMaterial | transmission=1, ior=1.5, thickness |
| Depth of field | @react-three/postprocessing | DepthOfField component |
| Glow/bloom | @react-three/postprocessing | Bloom with luminanceThreshold |
| Chromatic aberration | @react-three/postprocessing | ChromaticAberration component |
| Premium lighting | Poly Haven HDRIs | Environment component |
| Base 3D model | Meshy/Tripo3D API or Sketchfab | Load as GLTF/GLB |
| Animation | React Three Fiber useFrame | Rotation, float, pulse |
| Particles/volumetrics | Three.js Points or Sparkles | Particle systems |

### Which Tool is Most AI-Automatable?

**Ranking from most to least AI-automatable:**

1. **React Three Fiber + Three.js** (10/10) - Pure code. AI generates complete scenes from descriptions. Every property is code. No GUI required. Claude and GPT both know this deeply.

2. **Meshy/Tripo3D API** (9/10) - REST API with simple JSON. Text prompt in, GLB out. Perfect for agent workflows.

3. **Poly Haven API** (9/10) - REST API, no auth, free, direct downloads. Agents get premium HDRIs in one API call.

4. **Sketchfab API** (8/10) - REST API, requires auth token, but fully programmatic search and download.

5. **Blender Python (bpy)** (7/10) - Powerful but requires Blender installed, steep learning curve, compute-heavy.

6. **Spline** (4/10) - GUI-based. Agents can't design in Spline programmatically. Useful for exporting human-designed scenes, not agent-created ones.

7. **Rive** (5/10) - MCP integration helps, but still designed for UI animations not full 3D scenes.

8. **PeachWeb** (1/10) - No API, GUI-only, no programmatic access.

---

## Section 4: Accounts and Tools to Set Up (Priority Order)

### Priority 1: FREE - Set Up Today

**Sketchfab Account (Free)**
- URL: https://sketchfab.com/signup
- Get API token from: Account Settings > Password & API
- What it unlocks: Search and download 1M+ free models, access Tamminen's animated orbs
- Store token in Aether `.env` as `SKETCHFAB_API_TOKEN`

**Poly Haven (No Account Needed)**
- URL: https://api.polyhaven.com
- Just set User-Agent header in requests: `User-Agent: AetherDesignAgent/1.0`
- Immediately download HDRIs, textures, 3D models
- Free for non-commercial use

**Three.js + React Three Fiber (Free, npm)**
```bash
npm install three @react-three/fiber @react-three/drei @react-three/postprocessing
```
- Agents can generate complete 3D web experiences from code descriptions
- Works today with zero setup beyond npm install

**Open Source 3D Assets Registry**
- URL: https://www.opensource3dassets.com (991+ CC0 GLB models, JSON API-friendly)
- No account needed
- Direct programmatic access to free 3D assets

### Priority 2: LOW COST - Set Up This Week

**Meshy Pro ($20/month)**
- URL: https://www.meshy.ai/pricing
- Unlocks: API access, 1,000 credits/month (~50 text-to-3D models)
- Store API key in `.env` as `MESHY_API_KEY`
- Best for: Generating custom 3D models from agent descriptions

**Spline Professional ($25/month)**
- URL: https://spline.design/pricing
- Required for: Code export (React, Three.js, Vanilla JS exports)
- Agent workflow: Human designs or AI prompts in Spline, agent receives code, modifies it
- Most valuable if human designers use Spline and agents integrate output

### Priority 3: EVALUATE - Based on Usage

**Sketchfab Premium ($79/month)**
- Only needed if: Using Viewer API for commercial 3D configurator applications
- NOT needed for: Downloading models, basic API use, data API access

**Tripo3D API**
- Alternative to Meshy, evaluate after testing Meshy
- Advantage: v3.0 model for sculpture-level quality
- Check current pricing at https://www.tripo3d.ai/api

**Blender (Free)**
- Install for: Headless rendering, procedural modeling, format conversion
- When to prioritize: If agents need to CREATE 3D assets from scratch, not just download and embed
- Learning investment is significant

---

## Section 5: The Agent Learning Path (Step by Step)

### Phase 1: Foundation (Week 1)
**Goal**: Agent can embed and display any 3D model on a web page with Gleb-level effects.

1. Install Three.js + R3F ecosystem (`npm install` stack above)
2. Create Sketchfab account, get API token
3. Agent learns to: Search Sketchfab API for models, download GLTF, load in Three.js
4. Agent learns to: Apply MeshTransmissionMaterial for glass effects
5. Agent learns to: Add EffectComposer with Bloom + DepthOfField
6. Agent learns to: Load Poly Haven HDRIs for premium lighting

**Deliverable**: Agent generates a complete Three.js page from a text description.

### Phase 2: Generative Models (Week 2-3)
**Goal**: Agent can create custom 3D models that don't exist in any library.

1. Set up Meshy Pro API access
2. Agent learns to: Submit text-to-3D jobs via API, poll for completion, download GLB
3. Agent learns to: Describe 3D assets in prompts that produce good results
4. Agent learns to: Post-process Meshy output in Three.js for premium presentation
5. Test Tripo3D as comparison

**Deliverable**: Agent generates a custom branded 3D object from a description and embeds it in a page.

### Phase 3: Advanced Aesthetics (Week 3-4)
**Goal**: Agent produces work indistinguishable from Gleb Kuznetsov's aesthetic.

1. Study Tamminen's model library on Sketchfab for style reference
2. Agent learns to: Combine multiple postprocessing effects without performance degradation
3. Agent learns to: Create animated scenes (floating, rotation, particle systems)
4. Agent learns to: Optimize Three.js scenes for web performance
5. If Spline Pro is available: Agent learns to modify exported Spline code

**Deliverable**: Agent produces a complete 3D web section matching reference quality.

### Phase 4: Blender Automation (Month 2)
**Goal**: Agent can create original 3D assets procedurally via Blender Python.

1. Install Blender on server (headless mode)
2. Agent learns to: Run `blender --headless --python script.py`
3. Agent learns to: Create geometry procedurally with bpy
4. Agent learns to: Apply glass/transmission materials in Cycles renderer
5. Agent learns to: Export to GLTF for web use

**Deliverable**: Agent creates a custom PureBrain-branded 3D orb via Blender script and deploys it to a webpage.

---

## Section 6: Specific Recommendations for Aether's Design Agents

### What agent receives Sketchfab + 3D knowledge?

The **ui-ux-designer** agent should be primary owner of 3D aesthetic decisions. The **full-stack-developer** agent owns Three.js implementation. Consider creating a dedicated **3d-design-specialist** agent if 3D work becomes a major workload.

### The agent brief for Three.js work

An AI agent doing Three.js work should be prompted to:
1. Always use `MeshTransmissionMaterial` for glass/premium materials (from @react-three/drei)
2. Always include `<Environment>` with a Poly Haven HDRI
3. Always wrap effects in `<EffectComposer>` with at minimum Bloom
4. Always use `<Float>` for subtle organic animation
5. Use dark backgrounds (#060606 to #111111) to make glass effects visible
6. Target 60fps: limit postprocessing to 2-3 effects, use LOD for complex models

### Key repositories to study

- pmndrs/react-three-fiber: https://github.com/pmndrs/react-three-fiber
- pmndrs/drei: https://github.com/pmndrs/drei (all the helper components)
- pmndrs/postprocessing: https://github.com/pmndrs/postprocessing
- Poly Haven API: https://github.com/Poly-Haven/Public-API
- Open Source 3D Assets: https://github.com/ToxSam/open-source-3D-assets

### Key learning resources to ingest

- Codrops Three.js tutorials: https://tympanus.net/codrops/tag/three-js/ (premium effects tutorials)
- Three.js Journey: https://threejs-journey.com (comprehensive course, ~$100)
- Wawa Sensei R3F tutorials: https://wawasensei.dev (React Three Fiber specific)
- Olivier Larose 3D glass effect: https://blog.olivierlarose.com/tutorials/3d-glass-effect

---

## Section 7: Technology Stack Summary

### The Full AI-Agent 3D Stack

```
LAYER                    TOOL                           AGENT ACCESS
─────────────────────────────────────────────────────────────────────
Model Generation     →   Meshy API / Tripo3D API        Full REST API
Model Library        →   Sketchfab API                  Full REST API + Download
Free Assets          →   Poly Haven API                 Full REST API, no auth
Scene Design         →   Spline (GUI) → Code Export     Code output only
Web Rendering        →   Three.js / React Three Fiber   Pure code generation
Visual Effects       →   @react-three/postprocessing    Pure code generation
Lighting             →   Poly Haven HDRIs               Download via API
Animation            →   React Three Fiber useFrame     Pure code generation
Interactive Anim     →   Rive + MCP server              MCP programmatic access
Headless Rendering   →   Blender + bpy                  CLI + Python scripts
Format               →   GLTF/GLB                       Universal 3D web format
```

### Monthly Cost for Full Stack

| Tool | Plan | Cost |
|------|------|------|
| Sketchfab | Free | $0 |
| Poly Haven | Non-commercial | $0 |
| Three.js / R3F | Open source | $0 |
| Meshy AI | Pro | $20/mo |
| Spline | Professional | $25/mo |
| **Total** | | **$45/mo** |

---

## Verification

Research conducted via parallel web investigation across:
- Sketchfab developer documentation
- Poly Haven API documentation
- Spline export documentation and pricing
- Meshy AI API documentation
- Tripo3D API overview
- Rive 2025 AI agent features
- Three.js and React Three Fiber ecosystem
- Peach Worlds platform analysis
- Tamminen artist profile on Sketchfab
- Ramotion 3D website design resource guide
- Multiple tutorials on glass/transmission materials

**Confidence**: High - all capabilities described are verified against official documentation or primary sources.

---

## Sources

- [Sketchfab Data API v3](https://sketchfab.com/developers/data-api/v3)
- [Sketchfab Download API](https://sketchfab.com/developers/download-api)
- [Tamminen on Sketchfab](https://sketchfab.com/tamminen)
- [Poly Haven API](https://polyhaven.com/our-api)
- [Poly Haven Public API GitHub](https://github.com/Poly-Haven/Public-API)
- [Spline Code Export Documentation](https://docs.spline.design/doc/exporting-as-code/docDdDWmkQri)
- [Spline Pricing](https://spline.design/pricing)
- [r3f-spline GitHub](https://github.com/splinetool/r3f-spline)
- [React Three Fiber](https://github.com/pmndrs/react-three-fiber)
- [React Postprocessing](https://github.com/pmndrs/react-postprocessing)
- [MeshTransmissionMaterial - Drei](https://drei.docs.pmnd.rs/)
- [Three.js Glass Effect Tutorial](https://blog.olivierlarose.com/tutorials/3d-glass-effect)
- [Codrops Glass in Three.js](https://tympanus.net/codrops/2021/10/27/creating-the-effect-of-transparent-glass-and-plastic-in-three-js/)
- [Meshy AI API](https://www.meshy.ai/api)
- [Meshy Pricing](https://www.meshy.ai/pricing)
- [Tripo3D API](https://www.tripo3d.ai/api)
- [Rive AI Coding Agent](https://rive.app/blog/scripting-with-the-ai-coding-agent)
- [Blender Python API](https://docs.blender.org/api/current/index.html)
- [Blenderless Package](https://github.com/oqton/blenderless)
- [Open Source 3D Assets Registry](https://github.com/ToxSam/open-source-3D-assets)
- [PeachWeb Platform](https://peachweb.io/)
- [Ramotion 3D Website Design](https://www.ramotion.com/blog/3d-website-design/)
- [v0 + React Three Fiber - Vercel](https://vercel.com/blog/add-3d-to-your-web-projects-with-v0-and-react-three-fiber)
- [Sketchfab Plans](https://sketchfab.com/plans)

---

*Prepared by web-researcher | Aether AI Collective | 2026-02-20*
