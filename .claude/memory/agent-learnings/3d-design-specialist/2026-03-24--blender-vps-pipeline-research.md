---
type: synthesis
topic: Blender headless on VPS — pipeline research complete
date: 2026-03-24
---

## Blender VPS Research Findings

### VPS Status
- Blender 4.0.2 available via apt (not yet installed)
- VPS: 2 CPU cores, 3.7GB RAM, 4.9GB disk free (87% used — tight)
- No GPU — CPU rendering only
- Headless confirmed: `blender --background --python script.py` works on Ubuntu without display

### Key Architecture Decision
Blender = production layer. Meshy = concept/generation layer.
Both stay in pipeline. Blender handles the brand-critical work Meshy cannot.

### What Blender Unlocks That We Cannot Build Otherwise
1. Actual brain model for PureBrain visual identity (sculpt/displace)
2. Cycles-quality marketing renders (caustics, real glass refraction, volumetric fog)
3. Animated logo (3D text, glass material, Cycles render to MP4)
4. Baked texture workflow (high-poly to low-poly for web performance)
5. Parameterized batch render pipeline (nightly automated renders to R2)

### Claude + Blender Integration
- Claude writes bpy scripts — individual geometry/material/lighting quality is high
- Scene composition (object placement relative to each other) needs human review
- BlenderMCP (github.com/ahujasid/blender-mcp) = interactive Claude Desktop + GUI Blender
- For VPS automation: headless --background --python approach, no MCP needed

### Disk Management Rule (CRITICAL)
4.9GB free is tight. Blender renders go to temp dir immediately upload to R2 then delete local.
Never store renders long-term on VPS. Models (GLB, ~500KB-5MB each) are fine to keep.

### Material Mapping (Blender to Three.js)
Principled BSDF maps to MeshPhysicalMaterial as a direct 1:1 export.
IOR, transmission, roughness, metalness all carry through GLTF format correctly.
This is the core of the Blender-to-Three.js web pipeline.

### Render Time Expectations (CPU Only)
- Simple glass sphere, 1080p, 128 samples: 3-8 minutes
- Complex scene, 1080p, 256 samples: 20-45 minutes
- 4K marketing render: 2-4 hours
- Batch overnight = correct use of this VPS

### Eevee Headless Note
Eevee (fast render engine) requires virtual framebuffer for headless: Xvfb :1 & DISPLAY=:1 blender
Cycles works fully headless without any display server.
Default: use Cycles for VPS renders.

### First Build Priority Order
1. Install Blender (apt) + verify headless
2. Procedural glass brain model (Python script, export GLB)
3. Parameterized Cycles render script (model path to PNG output)
4. Animated logo render (3D text, glass, Cycles to MP4)
