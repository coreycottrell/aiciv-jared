# 777 Triangle OS Logo v2 - FLUX Generation Pipeline

**Date**: 2026-04-12
**Type**: technique
**Agent**: 3d-design-specialist
**Tags**: flux-pro, logo-generation, 777, triangle-os, pil, background-removal

## Context
Jared requested redo of 777 Triangle OS logos - previous batch wasn't impressive enough.
Generated 7 style variants via FLUX 1.1 Pro with PIL background removal.

## Prompt Engineering for Logo Marks

### What Works for 777 Arrangement
Core description that FLUX interprets correctly:
- "Two large numeral 7s placed side by side, angled inward so their tops lean toward each other"
- "forming an inverted triangle or V shape pointing downward"
- "A third numeral 7 is placed centered on top, overlapping where the two bottom 7s meet"
- "The three 7s together clearly read as 777 while forming a triangular geometric shape"

### Style-Specific Prompt Elements That Work
- **Glass**: "subsurface scattering at thick glass edges, chromatic aberration, Fresnel edge glow"
- **Chrome**: "Rolls Royce hood ornament" gives better results than generic "chrome metal"
- **Neon**: Specify per-7 color assignment ("left 7 orange, right 7 blue, top 7 transitions")
- **Gradient**: "Apple-style gradient, Instagram/Firefox logo level" as quality anchors
- **Embossed**: "luxury Swiss watch case detail" as quality anchor
- **Holographic**: "oil-on-water thin-film interference" for physics-grounded iridescence

### Rate Limiting
- 12s between calls is sufficient for FLUX 1.1 Pro
- `Prefer: wait` header for synchronous results (most complete within 30-60s)
- Model endpoint: `/v1/models/black-forest-labs/flux-1.1-pro/predictions`

## Background Removal Pipeline
- Threshold 30 for hard transparent (very dark pixels)
- 25px gradient feather zone for smooth anti-aliased edges
- Works well for clean/glass/gradient styles (77-90% transparency)
- Poor for metallic/neon styles where scene lighting brightens background (1-7% transparency)
- Those styles work best on dark backgrounds, not transparent

## Output
- 7/7 generated successfully
- All 1024x1024 RGBA PNG
- Location: /home/jared/exports/portal-files/777-logos-v2/
- Raw files preserved with -raw.png suffix

## Gotchas
- FLUX generates logos at 1024x1024 max in 1:1 mode - may need upscaling for print
- Metallic/chrome renders often include environment detail that resists background removal
- Neon glow intentionally bleeds past the logo boundary - removing it destroys the effect
- "prompt_upsampling: True" helps FLUX interpret complex logo arrangements better
