# PureBrain Visual Identity Standard

**Created**: 2026-02-14
**Approved by**: Jared
**Type**: brand-standard

---

## Core Visual Elements

### The Brain
- **Style**: Anatomical wireframe/holographic (NOT abstract blob)
- **Position**: Centered in frame
- **Structure**: Blue/cyan glowing lines showing brain anatomy
- **Detail**: Should be recognizable as a brain from any angle

### Color Palette
- **Primary**: Blue/cyan (#00BFFF, #0080FF range)
- **Accent**: Orange/gold (#FF8C00, #FFA500 range)
- **Background**: Deep black/dark blue
- **Highlights**: White/bright blue firing points

### Neural Activity
- **Firing points**: Orange/gold dots along neural pathways
- **Concentration**: Especially along top/front edges
- **Animation feel**: Even static images should feel "alive"

### Background Elements
- **Particles**: Small light points floating around brain
- **Energy streaks**: Subtle light rays radiating outward
- **Network nodes**: Optional - subtle connection points in deep background
- **Depth**: Dark vignette at edges

---

## DO NOT Include

- ❌ Hands or fingers
- ❌ Human faces (even silhouettes)
- ❌ Data charts/graphs overlays
- ❌ Text/logos in the image
- ❌ Stock photo watermarks
- ❌ Overly busy backgrounds
- ❌ Cartoon/illustration style (keep photorealistic)

---

## DALL-E Prompt Template

```
A glowing holographic brain rendered in blue and cyan wireframe lines,
anatomically accurate, centered against a deep black background.
Orange and gold neural firing points illuminate the upper edges
and key connection points. Subtle light particles and energy rays
radiate outward from the brain. Professional tech visualization style,
high detail, cinematic lighting. No text, no hands, no faces.
Aspect ratio 16:9, suitable for blog header.
```

---

## Example Reference Images

Source files (Jared-approved):
- `/home/jared/projects/AI-CIV/aether/docs/from-telegram/I_need_a_2k_202602110812.jpg`
- Additional examples in docs/from-telegram/

---

## Application

Use this style for:
- Blog post headers (jareddsanborn.com, purebrain.ai)
- LinkedIn newsletter banners
- Social media posts
- Presentation backgrounds

---

## Text Overlay Requirements (MANDATORY)

All blog/newsletter images MUST include:

1. **Pure Brain Icon** - Top left corner (80px height)
   - File: `/home/jared/projects/AI-CIV/aether/docs/assets/logos/purebrain-icon.png`

2. **PureBrain.ai** text - Next to icon, orange color (#FF8C00)
   - Font: Bold, ~32px

3. **Blog Post Title** - Bottom center, white with black shadow
   - Font: Bold, ~64px

### Python Overlay Process

After generating base image with DALL-E:
1. Load image with PIL
2. Load and resize icon (80px height)
3. Paste icon at (30, 25)
4. Add "PureBrain.ai" text in orange at (30 + icon_width + 15, centered with icon)
5. Add title at bottom center with shadow for readability
6. Save as PNG

### File Locations

- Icon: `docs/assets/logos/purebrain-icon.png`
- Logo: `docs/assets/logos/pure-brain-logo.png`
- Output: `exports/graphics/YYYY-MM-DD-[slug]-FINAL.png`

---

*This is the official PureBrain visual identity. All generated images must conform to this standard.*
