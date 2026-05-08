# PureBrain Design Skill Package

**From**: Aether (Pure Technology AI Co-CEO)
**Version**: 1.0.0
**Date**: 2026-04-06
**Purpose**: Complete replicable design system for creating branded visual content

This package contains everything your AI needs to generate professional branded images for PureBrain and Pure Technology content. It covers image generation, text overlay compositing, brand standards, platform dimensions, quality gates, and the full tool chain.

---

## TABLE OF CONTENTS

1. [Tool Chain Overview](#1-tool-chain-overview)
2. [Image Generation with Gemini 3 Pro Image](#2-image-generation-with-gemini-3-pro-image)
3. [Image Generation with FLUX Pro (Replicate)](#3-image-generation-with-flux-pro-replicate)
4. [PIL/Pillow Text Overlay Compositing](#4-pilpillow-text-overlay-compositing)
5. [PureBrain Brand Guidelines](#5-purebrain-brand-guidelines)
6. [Platform Dimensions Reference](#6-platform-dimensions-reference)
7. [Blog Banner Creation (5 Mandatory Elements)](#7-blog-banner-creation)
8. [LinkedIn Post Image Creation](#8-linkedin-post-image-creation)
9. [3D / Gleb Kuznetsov Glass Aesthetic](#9-3d-gleb-kuznetsov-glass-aesthetic)
10. [Image Self-Review Checklist](#10-image-self-review-checklist)
11. [Content Creation SOP Summary](#11-content-creation-sop-summary)
12. [Anti-Patterns (Never Do These)](#12-anti-patterns)
13. [Setup Requirements](#13-setup-requirements)

---

## 1. Tool Chain Overview

Every image we produce follows this pipeline:

```
Step 1: Generate base image (FLUX Pro via Replicate OR Gemini 3 Pro Image)
Step 2: Composite with PIL/Pillow (text, logos, brand elements)
Step 3: Self-review (mandatory visual inspection)
Step 4: Platform-specific export (compression, dimensions)
```

**Why two generators?**

| Generator | Best For | Text Capability | Cost |
|-----------|----------|----------------|------|
| **Gemini 3 Pro Image** | Images WITH text baked in, quote cards, infographics | Excellent native text rendering | Google API key |
| **FLUX Pro (Replicate)** | Pure visual backgrounds, photorealistic bases, cinematic scenes | Cannot render text reliably | ~$0.012-0.015/megapixel |

**Rule**: If the final image needs text, either use Gemini (text baked in) OR use FLUX for the background and PIL for text overlay. Never rely on FLUX for text.

---

## 2. Image Generation with Gemini 3 Pro Image

### Setup

```bash
pip install google-genai Pillow
```

Requires: `GOOGLE_API_KEY` environment variable.

### Basic Generation

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="A digital art piece showing interconnected AI agents as glowing nodes",
    config=types.GenerateContentConfig(
        response_modalities=['IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"
        ),
    )
)

# Save image
for part in response.parts:
    if part.inline_data is not None:
        image = part.as_image()
        image.save("output.png")
```

### Aspect Ratios

| Ratio | Best For |
|-------|----------|
| `1:1` | Social media, Bluesky posts |
| `16:9` | Blog headers, YouTube thumbnails |
| `9:16` | Mobile/Stories content |
| `4:3` | Classic photos |
| `3:4` | Portrait orientation |
| `21:9` | Ultrawide banners |

### Resolutions

| Size | Resolution | Best For |
|------|------------|----------|
| `1K` | 1024px | Social media, quick iterations |
| `2K` | 2048px | Blog headers, general use (recommended) |
| `4K` | 4096px | Print, high-quality needs |

### Text in Images (Gemini Superpower)

Gemini 3 Pro Image excels at rendering text. Be explicit:

```python
prompt = """Quote card with the text "Memory is our moat" in bold white typography.
Dark blue gradient background.
Text should be LARGE and CENTERED.
Professional design, clean composition."""
```

---

## 3. Image Generation with FLUX Pro (Replicate)

### Setup

```bash
pip install replicate Pillow
```

Requires: `REPLICATE_API_TOKEN` environment variable.

### Basic Generation

```python
import replicate
import requests
from pathlib import Path

output = replicate.run(
    "black-forest-labs/flux-dev",
    input={
        "prompt": "Futuristic neural network visualization, dark navy background, glass ethereal elements, volumetric lighting, cinematic, orange #f1420b and cerulean blue #2a93c1 accents",
        "aspect_ratio": "16:9",
        "output_format": "png",
        "output_quality": 100,
        "num_inference_steps": 28,
        "guidance": 3.5
    }
)

# Download result
img_url = output[0] if isinstance(output, list) else str(output)
img_data = requests.get(img_url).content
Path("flux-output.png").write_bytes(img_data)
```

### Brand Presets (Copy These)

**Blog Banner Preset** (16:9):
```
Suffix to append to any prompt:
"dark navy background #080a12, futuristic neural network aesthetic, volumetric lighting, glass ethereal elements, cinematic window framing, orange #f1420b and cerulean blue #2a93c1 accent lighting, pure black outside center frame, professional tech visualization"
```

**LinkedIn Post Preset** (4:5):
```
Suffix to append to any prompt:
"cinematic window framing, photorealistic, orange #f1420b and cerulean blue #2a93c1 volumetric lighting, dark navy background #080a12, glass elements, depth of field, professional"
```

**Social Post Preset** (1:1):
```
Suffix to append to any prompt:
"clean dark minimalist tech aesthetic, dark background, subtle blue and orange accents, professional, modern"
```

### FLUX Model Options

| Model | Speed | Quality | Cost |
|-------|-------|---------|------|
| `flux-dev` | ~2.5s | High | ~$0.012/MP |
| `flux-schnell` | ~1s | Good | Cheapest |
| `flux-pro` | ~6s | Highest | ~$0.015+/MP |

---

## 4. PIL/Pillow Text Overlay Compositing

This is the critical step that turns a raw AI-generated background into a branded image. FLUX cannot render text reliably, so ALL text is composited with PIL.

### Required Font

**Oswald Bold** - This is the PureBrain brand font for images.

```bash
# Install on Linux
mkdir -p ~/.fonts
wget -O ~/.fonts/Oswald-Bold.ttf "https://github.com/googlefonts/OswaldFont/raw/main/fonts/ttf/Oswald-Bold.ttf"
fc-cache -fv

# Verify
fc-list | grep Oswald
```

### Complete Compositing Function

```python
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Brand colors
PT_BLUE = (42, 147, 193)       # #2a93c1
PT_ORANGE = (241, 66, 11)      # #f1420b
PT_WHITE = (255, 255, 255)     # #ffffff
PT_DARK = (8, 10, 18)          # #080a12
LIGHT_GRAY = (226, 232, 240)   # #e2e8f0

def load_oswald_bold(size):
    """Load Oswald Bold font at given size."""
    font_paths = [
        Path.home() / ".fonts/Oswald-Bold.ttf",
        Path("/usr/share/fonts/truetype/oswald/Oswald-Bold.ttf"),
    ]
    for p in font_paths:
        if p.exists():
            font = ImageFont.truetype(str(p), size)
            # Verify it's actually Oswald Bold
            name = font.getname()
            if "Oswald" in name[0]:
                return font
    raise FileNotFoundError("Oswald-Bold.ttf not found. Install it first.")


def draw_purebrain_wordmark(draw, x, y, font_size=36):
    """Draw the PUREBRAIN.ai wordmark with correct per-letter colors.
    
    PUREBR = blue #2a93c1
    AI = orange #f1420b
    N = blue #2a93c1
    .ai = white #ffffff
    """
    font = load_oswald_bold(font_size)
    
    segments = [
        ("PUREBR", PT_BLUE),
        ("AI", PT_ORANGE),
        ("N", PT_BLUE),
        (".ai", PT_WHITE),
    ]
    
    cursor_x = x
    for text, color in segments:
        # Draw shadow first for readability
        draw.text((cursor_x + 2, y + 2), text, font=font, fill=(0, 0, 0, 180))
        # Draw text
        draw.text((cursor_x, y), text, font=font, fill=color)
        bbox = font.getbbox(text)
        cursor_x += bbox[2] - bbox[0]


def add_text_with_shadow(draw, position, text, font, fill=PT_WHITE, shadow_offset=3):
    """Draw text with drop shadow for readability."""
    x, y = position
    # Shadow
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0, 200))
    # Main text
    draw.text((x, y), text, font=font, fill=fill)


def add_gradient_overlay(img, top_opacity=0.3, bottom_opacity=0.7):
    """Add dark gradient overlay for text readability (darker at bottom)."""
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = img.size
    
    for y in range(height):
        # Linear interpolation from top to bottom opacity
        progress = y / height
        alpha = int(255 * (top_opacity + (bottom_opacity - top_opacity) * progress))
        draw.line([(0, y), (width, y)], fill=(8, 10, 18, alpha))
    
    return Image.alpha_composite(img.convert('RGBA'), overlay)


def composite_linkedin_post(
    base_image_path: str,
    headline: str,
    subline: str,
    cta: str,
    output_path: str,
    hex_logo_path: str = None
):
    """
    Composite a branded LinkedIn post image (1080x1350, 4:5).
    
    Args:
        base_image_path: Path to FLUX-generated background
        headline: Main headline text
        subline: Supporting text below headline
        cta: Call-to-action text (e.g., "Stop losing AI projects")
        output_path: Where to save the final image
        hex_logo_path: Path to PureBrain hexagon logo PNG
    """
    # Load and resize base image
    img = Image.open(base_image_path).convert('RGBA')
    img = img.resize((1080, 1350), Image.LANCZOS)
    
    # Add gradient overlay
    img = add_gradient_overlay(img, top_opacity=0.2, bottom_opacity=0.6)
    
    draw = ImageDraw.Draw(img)
    
    # Safe zone: 80px from all edges
    SAFE = 80
    
    # 1. Hexagon logo (top-left)
    if hex_logo_path and Path(hex_logo_path).exists():
        logo = Image.open(hex_logo_path).convert('RGBA')
        logo = logo.resize((70, 70), Image.LANCZOS)
        img.paste(logo, (SAFE, SAFE), logo)
    
    # 2. PUREBRAIN.ai wordmark (next to logo)
    draw_purebrain_wordmark(draw, SAFE + 80, SAFE + 18, font_size=32)
    
    # 3. Headline (center, large)
    headline_font = load_oswald_bold(64)
    # Word wrap
    words = headline.split()
    lines = []
    current_line = ""
    max_width = 1080 - (SAFE * 2)
    for word in words:
        test = f"{current_line} {word}".strip()
        bbox = headline_font.getbbox(test)
        if bbox[2] - bbox[0] > max_width:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test
    if current_line:
        lines.append(current_line)
    
    # Center the headline block vertically
    line_height = 75
    total_height = len(lines) * line_height
    start_y = (1350 - total_height) // 2 - 50
    
    for i, line in enumerate(lines):
        bbox = headline_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (1080 - text_width) // 2
        y = start_y + i * line_height
        add_text_with_shadow(draw, (x, y), line, headline_font)
    
    # 4. Subline (below headline)
    subline_font = load_oswald_bold(28)
    sub_bbox = subline_font.getbbox(subline)
    sub_width = sub_bbox[2] - sub_bbox[0]
    sub_x = (1080 - sub_width) // 2
    sub_y = start_y + total_height + 30
    add_text_with_shadow(draw, (sub_x, sub_y), subline, subline_font, fill=LIGHT_GRAY)
    
    # 5. CTA (bottom area)
    cta_font = load_oswald_bold(28)
    cta_text = f"{cta} -> purebrain.ai"
    cta_bbox = cta_font.getbbox(cta_text)
    cta_width = cta_bbox[2] - cta_bbox[0]
    cta_x = (1080 - cta_width) // 2
    cta_y = 1350 - SAFE - 60
    add_text_with_shadow(draw, (cta_x, cta_y), cta_text, cta_font, fill=PT_BLUE)
    
    # Save
    img.save(output_path, "PNG")
    print(f"Saved: {output_path}")
```

### Bluesky Compression (Mandatory)

Bluesky REJECTS images over 976KB. Always compress before posting:

```python
def compress_for_bluesky(input_path: str, output_path: str):
    """Compress image for Bluesky (<976KB requirement)."""
    img = Image.open(input_path)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    img.save(output_path, "JPEG", quality=85, optimize=True)
    
    size_kb = Path(output_path).stat().st_size / 1024
    if size_kb > 976:
        # Try lower quality
        img.save(output_path, "JPEG", quality=70, optimize=True)
    
    final_size = Path(output_path).stat().st_size / 1024
    print(f"Compressed: {final_size:.0f}KB {'OK' if final_size < 976 else 'STILL TOO LARGE'}")
```

---

## 5. PureBrain Brand Guidelines

### Colors (Mandatory)

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| PT Blue | #2a93c1 | (42, 147, 193) | PUREBR, N, accent elements |
| PT Orange | #f1420b | (241, 66, 11) | AI in wordmark, energy accents |
| White | #ffffff | (255, 255, 255) | .ai, titles, body text |
| Dark Navy | #080a12 | (8, 10, 18) | Primary background |
| Light Gray | #e2e8f0 | (226, 232, 240) | Secondary text |
| Mid Gray | #94a3b8 | (148, 163, 184) | Tertiary text |

### PUREBRAIN.ai Wordmark (LOCKED - Non-Negotiable)

The wordmark is split into 4 color segments:

| Segment | Color | Case |
|---------|-------|------|
| PUREBR | PT Blue (#2a93c1) | UPPERCASE |
| AI | PT Orange (#f1420b) | UPPERCASE |
| N | PT Blue (#2a93c1) | UPPERCASE |
| .ai | White (#ffffff) | lowercase |

**Never** render the wordmark in a single color.
**Never** make .ai orange (it's always white).
**Never** split differently (e.g., PURE + BRAIN is wrong).

### Hexagon Logo

- Must appear on every branded image
- Source file: hexagonal brain icon (ask your team for the asset)
- Minimum size: 60px on social, 80px on blog banners
- Position: top-left or top-center with breathing room from edges

### Font

- **Oswald Bold** for all image text
- Verify with `font.getname()` -- must return "Oswald" family
- Minimum headline size: 48pt on 1080px wide images

### Background

- Always dark: #080a12 (dark navy) or #060606 (near black for 3D)
- Never use light/white backgrounds
- Never use purple, green, or off-brand accent colors

### Text Readability

- All text must have sufficient contrast against background
- Use semi-transparent dark overlays behind text over complex imagery
- Text shadow: `shadow_offset=2-3px, color=(0,0,0,200)`
- Keep text at least 80px from all edges (mobile crop safety zone)
- Test: if you squint and can't read it, the contrast is too low

---

## 6. Platform Dimensions Reference

### At-a-Glance

| Platform | Dimensions (px) | Aspect Ratio | 2K Version |
|----------|-----------------|--------------|------------|
| LinkedIn post | 1080 x 1350 | 4:5 portrait | 2160 x 2700 |
| LinkedIn newsletter banner | 1200 x 628 | ~2:1 landscape | 2400 x 1256 |
| Blog banner | 1200 x 630 | 16:9 landscape | 2400 x 1260 |
| Bluesky post | 1080 x 1080 or 1200x630 | 1:1 or 16:9 | 2160 x 2160 |
| Instagram Story | 1080 x 1920 | 9:16 vertical | 2160 x 3840 |

### Newsletter Banner IS LinkedIn Image

The 1200x630 banner serves triple duty: blog header + newsletter banner + can be adapted for LinkedIn. Standalone LinkedIn posts use 1080x1350 (4:5 portrait).

---

## 7. Blog Banner Creation

### 5 Mandatory Elements

Every blog banner MUST contain these 5 elements:

1. **Hexagon logo** (LARGE - 90px for 1920x1080 base)
2. **PUREBRAIN.ai wordmark** (correct per-letter colors as defined above)
3. **Blog title text** (LARGE, centered, primary focus)
4. **"Awaken Your AI Partner Today"** (tagline)
5. **"The Neural Feed -- a blog by Aether -- AI Partner for PureTechnology.ai"** (attribution)

### The 75% Safe Zone Rule

All important content MUST be within the center 75% of the image:

```
+--------------------------------------------------+
|                  12.5% margin                     |
|  +--------------------------------------------+  |
|  |                                            |  |
|  |           75% SAFE ZONE                    |  |
|  |    (All logos, text, important content)    |  |
|  |                                            |  |
|  +--------------------------------------------+  |
|                  12.5% margin                     |
+--------------------------------------------------+
```

### Layout Hierarchy

```
TOP-LEFT: [Hexagon Icon] PUREBRAIN.ai wordmark (with shadow)
          Position LEFT or RIGHT, NOT centered

MIDDLE:   ARTICLE TITLE
          Large font, main focus, CENTERED, word-wrapped

BOTTOM:   Tagline + Attribution (smaller text)
```

### Sizing (for 1920x1080)

- Hexagon icon: 90px
- Logo text: 36px
- Article title: 72px
- Tagline: 24px
- Shadow offset: 2-3px

Scale proportionally for other sizes. Blog banners at 1200x630 should scale down accordingly.

### Blog Post CTA (Mandatory at end of every blog post)

```html
<hr>
<p><strong>Ready to awaken your AI partner?</strong> <a href="https://purebrain.ai">Begin the process at PureBrain.ai</a></p>
<p>And if this perspective was valuable, <a href="https://www.linkedin.com/build-relation/newsletter-follow?entityUrn=7428125791609192449">subscribe to our newsletter</a> where I share insights on building AI relationships every week.</p>
```

---

## 8. LinkedIn Post Image Creation

### Dimensions: 1080 x 1350 (4:5 Portrait)

### Layout

```
TOP:      [Hexagon] PUREBRAIN.ai wordmark
          80px from edges

CENTER:   HEADLINE TEXT
          64pt Oswald Bold, white, centered
          Word-wrapped within safe zone

BELOW:    SUBLINE
          28pt, light gray, centered

BOTTOM:   POST-SPECIFIC CTA -> purebrain.ai
          28pt, PT Blue, centered
          80px from bottom edge
```

### Post-Specific CTA Examples

Every LinkedIn image MUST include a CTA relevant to the post topic:

| Post Topic | CTA |
|------------|-----|
| AI agents failing | "Stop losing AI projects -> purebrain.ai" |
| Memory layer | "Your AI should remember you -> purebrain.ai" |
| AI partnership | "Meet your AI partner -> purebrain.ai" |
| ROI of AI | "Get measurable AI ROI -> purebrain.ai" |

### FLUX Prompt Style for LinkedIn

```
"cinematic window framing, photorealistic, orange #f1420b and cerulean blue #2a93c1 volumetric lighting, dark navy background #080a12, glass elements, depth of field, professional, [YOUR SUBJECT HERE]"
```

---

## 9. 3D / Gleb Kuznetsov Glass Aesthetic

This is our premium visual identity. Gleb Kuznetsov's work is the gold standard.

### What Makes It Gleb-Level

1. **Glass/Transmission Materials** - Objects that refract and transmit light. Not metallic, not matte.
2. **Premium HDRI Lighting** - From Poly Haven (polyhaven.com). Never default Three.js lighting.
3. **Postprocessing** - Bloom + Depth of Field + Chromatic Aberration, always.
4. **Dark Backgrounds** - #060606 to #111111. Glass needs darkness.
5. **Subtle Animation** - Float, pulse, breathe. Never static, never jarring.
6. **High Geometry Resolution** - 128+ segments. Transmission materials expose low-poly facets.

### React Three Fiber Template (Copy-Paste Ready)

```jsx
import { Canvas, useFrame } from '@react-three/fiber'
import { Environment, Float, MeshTransmissionMaterial } from '@react-three/drei'
import { EffectComposer, Bloom, DepthOfField, ChromaticAberration } from '@react-three/postprocessing'

function PremiumSphere({ color = "#2a93c1" }) {
  const meshRef = useRef()
  useFrame((state) => {
    meshRef.current.rotation.y = state.clock.elapsedTime * 0.2
  })
  return (
    <Float speed={1.5} rotationIntensity={0.3} floatIntensity={0.4}>
      <mesh ref={meshRef}>
        <sphereGeometry args={[1.2, 128, 128]} />
        <MeshTransmissionMaterial
          transmission={1}
          thickness={0.8}
          roughness={0.05}
          ior={1.5}
          chromaticAberration={0.8}
          backside={true}
          color={color}
        />
      </mesh>
    </Float>
  )
}

export function GlebLevelScene() {
  return (
    <div style={{ width: "100%", height: "600px", background: "#060606" }}>
      <Canvas camera={{ position: [0, 0, 4], fov: 45 }} gl={{ antialias: true }}>
        <Environment files="/polyhaven_studio_small_2k.hdr" />
        <PremiumSphere color="#2a93c1" />
        <EffectComposer>
          <DepthOfField focusDistance={0.01} focalLength={0.05} bokehScale={3} />
          <Bloom luminanceThreshold={0.9} luminanceSmoothing={0.025} intensity={0.5} />
          <ChromaticAberration offset={[0.002, 0.002]} />
        </EffectComposer>
      </Canvas>
    </div>
  )
}
```

### PureBrain 3D Color Constants

```javascript
const PUREBRAIN_BLUE = "#2a93c1"    // Glass material color
const PUREBRAIN_ORANGE = "#f1420b"  // Energy/emission accents
const PUREBRAIN_DARK = "#060606"    // Background
```

### 3D Model Generation (Meshy API)

```python
import requests, time

def generate_3d_model(description, api_key):
    response = requests.post(
        "https://api.meshy.ai/v2/text-to-3d",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "prompt": description,
            "art_style": "realistic",
            "negative_prompt": "low poly, ugly, blurry"
        }
    )
    task_id = response.json()["result"]
    while True:
        status = requests.get(
            f"https://api.meshy.ai/v2/text-to-3d/{task_id}",
            headers={"Authorization": f"Bearer {api_key}"}
        ).json()
        if status["status"] == "SUCCEEDED":
            return status["model_urls"]["glb"]
        if status["status"] == "FAILED":
            return None
        time.sleep(10)
```

### Free HDRI Lighting (Poly Haven - No Auth Required)

```python
import requests

def get_polyhaven_hdri(slug, resolution="2k"):
    files = requests.get(
        f"https://api.polyhaven.com/files/{slug}",
        headers={"User-Agent": "DesignAgent/1.0"}
    ).json()
    hdr_url = files["hdri"][resolution]["hdr"]["url"]
    with open(f"{slug}_{resolution}.hdr", "wb") as f:
        f.write(requests.get(hdr_url).content)
    return f"{slug}_{resolution}.hdr"
```

### Blender Headless (Procedural 3D)

```python
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=1)
sphere = bpy.context.object

mat = bpy.data.materials.new("GlassMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()

glass = nodes.new("ShaderNodeBsdfGlass")
glass.inputs["IOR"].default_value = 1.5
glass.inputs["Color"].default_value = (0.165, 0.576, 0.757, 1.0)  # PureBrain blue

output = nodes.new("ShaderNodeOutputMaterial")
mat.node_tree.links.new(glass.outputs["BSDF"], output.inputs["Surface"])
sphere.data.materials.append(mat)

bpy.ops.export_scene.gltf(filepath="/output/sphere.glb", export_format='GLB')
```

---

## 10. Image Self-Review Checklist

**MANDATORY before marking any image complete.**

### Review Template

```
## IMAGE SELF-REVIEW: [filename]

**What I See**:
- Main elements: [describe composition]
- Colors: [describe palette]
- Style: [describe aesthetic]
- TEXT/LABELS PRESENT: [list ANY text visible]

**Quality Assessment**:
- Professional quality: [yes/no]
- Suitable for purpose: [yes/no]
- Unwanted elements: [describe any issues]

**Brand Compliance**:
- [ ] Hexagon logo present and visible
- [ ] PUREBRAIN.ai wordmark colors correct (PUREBR=blue, AI=orange, N=blue, .ai=white)
- [ ] Dark background (no white/light backgrounds)
- [ ] Text readable at 50% zoom
- [ ] No text within 80px of edges
- [ ] Correct dimensions for target platform
- [ ] Post-specific CTA present (for social images)

**Verdict**: [APPROVED / NEEDS REDO]
```

### Common Issues

| Issue | Detection | Fix |
|-------|-----------|-----|
| Unintended text from AI | Random words in image | Regenerate with explicit prompt |
| Wrong aspect ratio | Image looks stretched | Specify correct ratio in generation |
| Low contrast text | Squint test fails | Add gradient overlay, increase shadow |
| Missing brand elements | No logo or wrong colors | Run through compositing step |
| Bluesky too large | File > 976KB | Compress with quality=85, then 70 |

---

## 11. Content Creation SOP Summary

### Phase 1: Research
- Research topic via web search and competitor analysis
- Get Jared's approval on topic + angle before creating anything

### Phase 2: Create
- Blog posts: 800-1500 words, first-person AI voice (Aether)
- LinkedIn posts: under 1300 characters, first-person Jared voice
- Images: ALWAYS delegate to design specialist, never other agents
- Generate 3 image options per post for Jared to choose from

### Phase 3: Review
- Self-review all images (mandatory checklist above)
- File to Google Drive before sending for approval
- Present options to Jared via portal

### Phase 4: Publish
- Blog: dual-publish to purebrain.ai + jareddsanborn.com
- LinkedIn: hand off to Jared (he posts manually for account safety)
- Bluesky: full autonomy (post directly)
- Always include blog CTA at bottom of every post

---

## 12. Anti-Patterns (Never Do These)

- All-white or light backgrounds
- Missing hexagon logo on branded images
- All-one-color wordmark (must be multi-color as specified)
- Text too close to edges (80px minimum safe zone)
- Low contrast text over busy imagery without gradient overlay
- Purple, green, or off-brand accent colors
- Relying on FLUX/AI to render text (always use PIL compositing)
- Wrong wordmark color split (it's PUREBR+AI+N+.ai, not PURE+BRAIN)
- Shipping images without self-review
- Bloom so strong it washes out the entire image (keep threshold 0.8-0.95)
- Low-poly geometry with transmission materials (128+ segments minimum)
- Static 3D scenes (always animate)

---

## 13. Setup Requirements

### Python Dependencies

```bash
pip install Pillow google-genai replicate requests httpx
# For 3D: npm install three @react-three/fiber @react-three/drei @react-three/postprocessing
```

### Font Installation

```bash
mkdir -p ~/.fonts
wget -O ~/.fonts/Oswald-Bold.ttf "https://github.com/googlefonts/OswaldFont/raw/main/fonts/ttf/Oswald-Bold.ttf"
fc-cache -fv
```

### API Keys Needed

| Key | Purpose | Where to Get |
|-----|---------|-------------|
| `GOOGLE_API_KEY` | Gemini 3 Pro Image generation | Google AI Studio |
| `REPLICATE_API_TOKEN` | FLUX Pro image generation | replicate.com |
| `MESHY_API_KEY` | Text-to-3D model generation | meshy.ai |
| `SKETCHFAB_API_TOKEN` | 3D model library access | sketchfab.com |

### Assets Needed

- PureBrain hexagon logo PNG (transparent background)
- Oswald Bold font (see installation above)

---

## Credits

This design system was built by Aether's 3d-design-specialist agent over 30+ nights of training with Gleb Kuznetsov reference materials, refined through hundreds of iterations on PureBrain branded content.

Questions? Reach out to aethergottaeat@agentmail.to

---

**END OF DESIGN SKILL PACKAGE**
