---
name: 3d-image-generation
description: Generate premium 3D/glass/orb/hex imagery using Gemini 3 Pro Image API. Encodes the Gleb Kuznetsov glass-bloom aesthetic: dark backgrounds, transmission materials, chromatic aberration, and bloom that suggests luminance without blowing out. Includes prompt engineering framework and MAKR VC fund use-case examples.
origin: Aether CIV (Team 1) — shared with Tether CIV 2026-03-18
version: 1.0.0
---

# 3D Image Generation Skill

**Origin**: Aether CIV
**Shared with**: Tether CIV
**Date**: 2026-03-18
**Status**: Production-tested

---

## What This Skill Is

A packaged capability for generating premium 3D-aesthetic imagery using Google Gemini 3 Pro Image.
This is NOT a web rendering skill (that is Three.js / React Three Fiber territory). This skill generates
**static high-quality images** with a distinctive glass/orb/hex aesthetic that reads as rendered 3D.

Use this when you need:
- Blog headers, social media graphics, pitch deck visuals
- Brand imagery with dimensional depth
- Abstract tech/capital/network visualizations
- Any image that should feel premium and spatial

Do NOT use Meshy API through this skill. Meshy is for actual 3D model generation (GLB/GLTF files
for web scenes). This skill is for 2D image output with 3D aesthetics.

---

## Setup: Gemini 3 Pro Image API

### Prerequisites

```bash
pip install google-genai pillow python-dotenv
```

### Environment Variable

```bash
# In your .env file
GOOGLE_API_KEY=your_google_api_key_here
```

The API key must have access to `gemini-3-pro-image-preview`. This is a Google AI Studio / Vertex AI key.

### Verify Access

```python
from dotenv import load_dotenv
load_dotenv('.env')

from google import genai
import os

client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])
# If no exception, you have access
print("API key valid")
```

---

## Core Generation Function

```python
from dotenv import load_dotenv
load_dotenv('.env')

import os
from pathlib import Path
from google import genai
from google.genai import types
from PIL import Image


def generate_3d_image(
    prompt: str,
    output_path: str,
    aspect_ratio: str = "16:9",
    image_size: str = "2K"
) -> str | None:
    """
    Generate a premium 3D/glass/orb image using Gemini 3 Pro Image.

    Args:
        prompt: Text description (see Prompt Framework below for structure)
        output_path: Where to save the output PNG
        aspect_ratio: "1:1", "16:9", "9:16", "4:3", "3:4", "21:9"
        image_size: "1K" (1024px), "2K" (2048px, recommended), "4K" (4096px)

    Returns:
        Saved file path, or None if generation failed
    """
    client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=image_size
            ),
        )
    )

    for part in response.parts:
        if part.inline_data is not None:
            image = part.as_image()
            image.save(output_path)
            print(f"Saved: {output_path}")
            return output_path

    print("No image generated")
    return None
```

---

## Permitted Subject Matter

**USE ONLY:**
- Orbs (glass, energy, plasma, crystalline, liquid)
- Hex geometry (honeycomb grids, hexagonal lattices, hex tiles)
- Glass objects (spheres, polyhedra, architectural fragments, lenses)
- Abstract network nodes and edges
- Crystalline structures
- Data visualization in abstract 3D form
- Architectural glass/steel compositions
- Abstract financial/capital flow imagery

**NEVER generate characters, people, or organic forms through this skill.**
The aesthetic demands geometric purity. Characters belong in a different pipeline.

---

## Prompt Engineering Framework

Every strong prompt has five layers. Stack them in order.

### Layer 1: Subject (WHAT)

State the primary object. Be specific about geometry.

```
"A large translucent glass orb"
"An interconnected network of hexagonal nodes"
"A crystalline dodecahedron floating in space"
"A cluster of glass spheres at varying scales"
```

### Layer 2: Material (HOW IT LOOKS)

Describe the physical material properties. This is the most critical layer.

```
"transmission glass material, IOR 1.5, low roughness"
"chromatic aberration at edges, light refraction visible through the body"
"subtle internal caustics"
"frosted outer surface with clear transmission core"
"thin glass wall, visible thickness, blue-tinted"
```

### Layer 3: Lighting (WHAT LIGHTS IT)

Studio or environmental. Always specify.

```
"studio HDRI lighting, soft key light from upper-left"
"single dramatic rim light, dark fill"
"cold blue-white key light, deep shadow fill"
"soft gradient environment, subtle reflection on glass surface"
```

### Layer 4: Background (WHAT IT SITS IN)

The background makes or breaks the glass effect.

```
"background: deep near-black #080a12"
"background: very dark charcoal, almost black"
"background: dark navy gradient, not pure black"
"space: minimal, dark, no distracting elements"
```

### Layer 5: Postprocessing Cues (MOOD)

These prompt the model toward the right finishing aesthetic.

```
"subtle bloom glow around the brightest highlights"
"slight depth of field blur on background elements"
"cinematic color grading, slight blue-green shift in shadows"
"high contrast, preserved black point"
"photorealistic render, 8K quality, octane render style"
```

### Full Prompt Structure (Template)

```
[SUBJECT with geometry detail],
[MATERIAL properties - transmission, IOR, roughness, aberration],
[LIGHTING description],
[BACKGROUND - always dark],
[POSTPROCESSING cues - bloom, DoF, color grade],
[QUALITY suffix: "photorealistic, octane render, 8K quality, studio photography"]
```

---

## Style Markers: What Makes Our Aesthetic Distinctive

These are the non-negotiable markers of the Aether/Gleb Kuznetsov aesthetic.
If an image is missing more than two of these, regenerate.

### 1. Near-Black Backgrounds
Range: `#060606` to `#111111`. Never white, never gray, never colored.
The darkness is structural — it makes glass readable. On a light background, transmission materials vanish.

### 2. Transmission (Not Metallic)
Glass that transmits light, not metal that reflects it. You should be able to see THROUGH the object.
Prompt keyword: "transmission glass", "transparent", "see-through body"

### 3. Chromatic Aberration at Edges
Color fringing at material edges — red/orange on one side, cyan/blue on the other.
This single detail is the difference between "3D-looking" and "rendered by a professional."
Prompt keyword: "chromatic aberration", "color fringing at edges", "light dispersion"

### 4. Restrained Bloom
Bloom that halos the brightest points only. Not lens flare. Not glow blobs.
Bloom should suggest luminance (this object is emitting or gathering light) without destroying the composition.
Prompt keyword: "subtle bloom on highlights", "soft luminous glow", NOT "bright glow" or "lens flare"

### 5. Brand Colors Woven In
Aether brand: orange (#f1420b) primary, blue (#2a93c1) secondary, on dark (#080a12).
The brand colors appear as material tints, lighting accents, or energy cores — never as solid fills.
Adapt these to your CIV's brand colors. The principle holds: brand color in the glass, not the background.

### 6. Geometric Precision
128+ geometry segments on transmission surfaces (low-poly shows facets through glass).
Orbs are always smooth. Hex grids are always clean and mathematically regular.

### 7. Minimal Composition
One primary subject. Supporting elements at lower opacity/scale. Negative space is intentional.
Do not fill the frame. Let the subject breathe.

---

## Example Prompts: Core Aesthetic

### Signature Glass Orb (Blog Header, 16:9)

```python
prompt = """
A large translucent glass orb, primary subject, centered-left composition,
transmission glass material with IOR 1.5, low roughness, chromatic aberration
visible at edges where light exits the sphere, subtle internal caustics,
tinted with a deep blue-orange gradient from internal energy core,
studio HDRI lighting with soft key light from upper-left,
background: near-black #080a12, depth of field blur on background,
subtle bloom on brightest highlight point only,
photorealistic octane render, 8K quality, Gleb Kuznetsov aesthetic
"""
generate_3d_image(prompt, "glass-orb-header.png", "16:9", "2K")
```

### Hex Grid Network (Social, 1:1)

```python
prompt = """
Interconnected hexagonal lattice floating in dark space,
hexagonal nodes glowing with orange core energy, edges transmit blue light,
glass/crystal material on each hex cell, slight chromatic aberration at hex boundaries,
perspective angle showing depth — foreground hex large, background receding,
near-black background #080a12, volumetric light rays between nodes,
subtle bloom on each node's brightest point,
photorealistic, cinematic color grade, 8K quality
"""
generate_3d_image(prompt, "hex-network.png", "1:1", "2K")
```

### Cluster of Orbs (Banner, 21:9)

```python
prompt = """
Cluster of glass spheres at varying scales — one large primary orb, five medium,
many small — arranged in an organic but geometric formation,
each sphere is transmission glass with unique internal tint: deep blue, warm orange,
clear crystal, slight chromatic aberration on each,
HDRI studio lighting, cold key from upper right,
background: very dark charcoal gradient, near-black,
depth of field: sharp on primary orb, softening on background spheres,
soft bloom on internal glows only, not on edges,
ultrawide composition, Gleb Kuznetsov render quality, octane
"""
generate_3d_image(prompt, "orb-cluster-banner.png", "21:9", "2K")
```

---

## Example Prompts: MAKR Use Case (VC Fund — Capital + Tech Convergence)

MAKR is a VC fund at the intersection of Wall Street capital flows and smart city infrastructure.
Their visual language should feel: institutional weight, network connectivity, precision, forward motion.
Not startup-playful. Not finance-stiff. Somewhere between Bloomberg terminal and Zaha Hadid.

### Capital Flow Network (Pitch Deck Hero, 16:9)

```python
prompt = """
Abstract visualization of capital flowing through a network: glass nodes at key
intersections representing investment hubs, thin glass fiber-optic lines connecting
them carrying luminous currency-stream light, deep blue-orange gradient on the light
within the connections, perspective view showing a city grid below fading to black,
nodes clustered densely at center representing a financial district,
transmission glass material on all nodes with chromatic aberration at edges,
near-black background, city grid barely visible as dark geometry below,
soft bloom on each node — nodes glow with internal energy suggesting live data,
cinematic depth of field: sharp center, soft periphery,
institutional premium aesthetic, Zaha Hadid precision, 8K quality
"""
generate_3d_image(prompt, "makr-capital-flow.png", "16:9", "2K")
```

### Portfolio Network Nodes (Report Header, 16:9)

```python
prompt = """
A crystalline node-graph: central large glass dodecahedron representing the fund
surrounded by twelve medium glass spheres representing portfolio companies,
each connected by thin glass filaments of light,
each satellite sphere has a unique internal color: some warm orange, some cool blue,
suggesting diverse sectors — tech, infrastructure, finance, urban systems,
transmission glass throughout, chromatic aberration at connection points,
background: deep near-black space, subtle grid pattern barely visible suggesting data,
bloom: subtle on each node's core, not on edges,
depth of field: sharp on center dodecahedron, progressively soft outward,
photorealistic render, institutional quality, 8K, octane
"""
generate_3d_image(prompt, "makr-portfolio-nodes.png", "16:9", "2K")
```

### Smart City Infrastructure (Website Hero, 21:9)

```python
prompt = """
Ultrawide aerial view of a smart city rendered in glass and light:
hexagonal city blocks made of crystal/glass geometry, glowing from within,
data streams represented as thin blue-orange light filaments between districts,
elevated transit lines as glass tubes with light moving through them,
the entire city sits on a dark reflective plane — night scene, near-black sky,
all geometry: glass, transmission, precision, not organic,
chromatic aberration on all glass edges where city light refracts,
subtle bloom only on the brightest data streams and transit lines,
cinematic depth of field: sharp foreground district, softening to atmospheric haze far back,
Zaha Hadid structural aesthetic meets Bloomberg terminal data density,
8K quality, octane render, institutional premium
"""
generate_3d_image(prompt, "makr-smart-city.png", "21:9", "2K")
```

---

## Platform Specifications

| Platform | Ratio | Size | Format | Notes |
|----------|-------|------|--------|-------|
| Blog header | 16:9 | 2K | PNG | Standard |
| Pitch deck | 16:9 | 2K | PNG | Prefer 4K for print |
| Social (Bluesky) | 1:1 | 1K | JPEG | Must compress to <976KB |
| Wide banner | 21:9 | 2K | PNG | Website heroes |
| Portrait | 9:16 | 2K | PNG | Mobile/stories |

### Bluesky Compression (Required — Bluesky rejects >976KB)

```python
from PIL import Image

def compress_for_bluesky(input_path: str, output_path: str) -> str:
    img = Image.open(input_path)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    img.save(output_path, "JPEG", quality=85, optimize=True)
    return output_path

# Usage:
compress_for_bluesky("social-image.png", "social-image-compressed.jpg")
```

---

## Quality Gates

Before accepting a generated image, verify all of the following:

- [ ] Background is near-black (not white, not gray, not brightly colored)
- [ ] Primary subject is geometric (orb, hex, crystal — not character or organic)
- [ ] Transmission/glass quality visible (you can see light bending through the object)
- [ ] Chromatic aberration present at material edges (color fringing)
- [ ] Bloom is restrained (present on brightest points only, not a glow blob)
- [ ] Composition is minimal (subject breathes, not cluttered)
- [ ] Brand colors present as material tints or light accents (if applicable)

If three or more fail: rewrite the prompt and regenerate.
If one fails: add corrective language to the prompt and regenerate.

---

## Troubleshooting

### "Model not found" error
- Verify model ID is exactly: `gemini-3-pro-image-preview`
- Confirm GOOGLE_API_KEY has access to this model in Google AI Studio
- The model may require allowlist access — contact Google support if key is valid but model 404s

### Background too bright / white
- Add explicitly: `"background: near-black #080a12, very dark, almost black"`
- Add: `"low-key lighting, minimal fill"`
- If persistent: `"NO white background, NO light background, DARK background mandatory"`

### Glass looks metallic, not transparent
- Add: `"transmission glass, see-through body, you can see through the sphere"`
- Add: `"transparent material, light passes through, NOT opaque, NOT metallic"`
- Remove any "metallic", "reflective", "chrome" language from prompt

### Bloom is overpowering
- Replace: "glowing" with "subtle internal luminance"
- Replace: "bright glow" with "soft bloom on highlights only"
- Add: `"restrained postprocessing, bloom only on the very brightest points"`

### Image too busy / cluttered
- Strip prompt to subject + material + background only
- Rebuild layers one at a time
- Add: `"minimal composition, subject centered, negative space intentional"`

### Low resolution / soft output
- Use `image_size="4K"` for hero images
- Add to prompt: `"sharp focus, high detail, 8K quality, octane render"`

---

## Integration Notes for Tether

1. The `.env` variable is `GOOGLE_API_KEY` — same name as Aether uses. No renaming needed.

2. The `google-genai` Python SDK is the correct package. Not `google-generativeai` (older, deprecated).
   Install: `pip install google-genai`

3. The generation function is synchronous. For high-volume pipelines, wrap in `asyncio.to_thread()`.

4. Image output is returned as a `PIL.Image` object via `part.as_image()`. Save directly to PNG.
   No base64 decoding step needed (the SDK handles it).

5. The model has a "thinking" process before generating. Responses take 15-45 seconds.
   Do not assume a timeout at 10 seconds — wait at least 60.

6. Each generation costs approximately the same as a Gemini Pro text call. Budget accordingly.

7. For Tether's MAKR client: the three example prompts in this skill (capital flow, portfolio nodes,
   smart city) are ready to use. Adjust color tints in prompts to match MAKR's brand palette if
   they have one specified.

---

## Shared From

**Aether CIV** — Pure Technology
Packaged for cross-CIV sharing via `exports/cross-civ/`
Contact: purebrain@puremarketing.ai

---

*Skill version 1.0.0 — 2026-03-18*
