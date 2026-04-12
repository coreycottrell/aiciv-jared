# Blog Image Guidelines

**Purpose**: Prevent text from being cut off on mobile/desktop WordPress featured images.

---

## The Problem

WordPress crops featured images differently based on:
- Mobile vs desktop viewport
- Theme settings (aspect ratio, focal point)
- Blog listing vs single post view

**Result**: Text placed near edges gets cropped unpredictably.

---

## Solution: Safe Zone Placement

### Image Dimensions
- **Size**: 1920x1080 (16:9 ratio) - universal for blog + LinkedIn + social
- **Format**: PNG or JPG (JPG for photos, PNG for graphics with text)

### Safe Zone Rules

```
┌──────────────────────────────────────────────────────┐
│                    DANGER ZONE                        │
│   ┌──────────────────────────────────────────────┐   │
│   │                                              │   │
│   │              SAFE ZONE (70%)                 │   │
│   │                                              │   │
│   │     Place ALL text and important             │   │
│   │     visual elements HERE                     │   │
│   │                                              │   │
│   │     - Title text                             │   │
│   │     - PUREBRAIN.ai branding                  │   │
│   │     - Key visual elements                    │   │
│   │                                              │   │
│   └──────────────────────────────────────────────┘   │
│                    DANGER ZONE                        │
└──────────────────────────────────────────────────────┘

Safe zone boundaries (for 1920x1080):
- Left margin: 288px (15%)
- Right margin: 288px (15%)
- Top margin: 162px (15%)
- Bottom margin: 162px (15%)

Effective safe area: 1344x756 centered
```

### Text Positioning

| Element | Recommended Position |
|---------|---------------------|
| Title text | Center (both axes) |
| PUREBRAIN.ai logo | Center-bottom of safe zone |
| Subtitle/tagline | Below title, center |

### Color Guidelines

| Element | Color |
|---------|-------|
| "PUREBR" + "N.ai" | Pure Tech Blue (#2a93c1) |
| "AI" (accent) | Orange (#f1420b) |
| Title text | White or Pure Tech Blue |
| Background | Dark gradients preferred |

---

## Implementation in Image Generation

When generating blog images with DALL-E or Pillow overlay:

1. **DALL-E prompt**: Request minimal/no text in image - we overlay text in post-processing
2. **Pillow overlay**:
   - Use `ImageDraw.textbbox()` to measure text dimensions
   - Center text using: `x = (1920 - text_width) // 2`
   - Place title at `y = 400` (upper-center of safe zone)
   - Place branding at `y = 900` (lower-center of safe zone)

### Code Reference

```python
# Safe zone constants
SAFE_MARGIN_X = 288  # 15% of 1920
SAFE_MARGIN_Y = 162  # 15% of 1080
SAFE_WIDTH = 1344    # 70% of 1920
SAFE_HEIGHT = 756    # 70% of 1080

# Center text in safe zone
def center_text(draw, text, font, y_position, image_width=1920):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (image_width - text_width) // 2
    return (x, y_position)
```

---

## Examples

### Good: Text Centered
- Title in center
- Branding centered below
- Visual elements fill edges (ok to crop)

### Bad: Text at Edges
- Title near top (gets cropped on mobile)
- Branding in corner (disappears on listing view)
- Important elements near left/right edges

---

## WordPress Settings Reference

On purebrain.ai, featured images display as:
- **Blog listing**: 16:9 crop from center
- **Single post header**: Full width with object-fit: cover
- **Mobile**: Square-ish crop (varies by theme)

**Always design for worst-case cropping** - assume 30% could be lost from any edge.

---

**Created**: 2026-02-15
**Author**: Aether (ai-civ)
