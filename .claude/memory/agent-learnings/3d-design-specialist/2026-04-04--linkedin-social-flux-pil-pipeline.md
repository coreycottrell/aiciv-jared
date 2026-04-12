# LinkedIn Social Image: FLUX Pro + PIL Composite Pipeline

**Date**: 2026-04-04
**Type**: technique
**Topic**: Production pipeline for LinkedIn 4:5 social images

## Context
Created v4 of OpenClaw/Anthropic news LinkedIn post image. Previous v1-v3 were deemed insufficient quality.

## Pipeline That Works

### Step 1: FLUX 1.1 Pro via Replicate
- Endpoint: `https://api.replicate.com/v1/models/black-forest-labs/flux-1.1-pro/predictions`
- Use `Prefer: wait` header to get synchronous result
- Aspect ratio `3:4` for portrait LinkedIn (produces 896x1152)
- DO NOT use version-based endpoint (422 error) - use model-based endpoint
- Output format PNG, quality 100

### Step 2: Prompt Engineering for Gleb Kuznetsov Aesthetic
Key prompt elements that work:
- "Gleb Kuznetsov style futuristic interface"
- "volumetric god rays"
- "shattered translucent glass fragments"
- "bokeh orbs of blue and orange light"
- "cinematic depth of field"
- "dark moody sci-fi atmosphere"
- "dramatic rim lighting on glass edges"
- Specify brand colors by hex: "#2a93c1 blue and #f1420b orange"
- NO TEXT in prompt (add text via PIL)

### Step 3: PIL Composite Elements
1. Resize FLUX base to 1080x1350
2. Top gradient overlay (220 alpha, 400px, power 1.5 falloff)
3. Bottom gradient overlay (230 alpha, 500px, power 1.8 falloff)
4. Middle vignette for headline area
5. Hex logo (90px, centered)
6. Wordmark with per-segment colors
7. Headline with heavy shadow (blur=6, offset=4)
8. Subline with medium shadow
9. CTA with blue accent for URL

### Key Gotchas
- Font verification: `font.getname()` confirms ('Oswald', 'Bold')
- Text shadows: Create separate RGBA layer, draw shadow, GaussianBlur, alpha_composite
- Gradient overlays: Use power curves for natural falloff (not linear)
- Safe zones: 80px from all edges
- The FLUX model endpoint changed - use `/v1/models/{owner}/{model}/predictions` not version-based

## Output
- File: `/home/jared/exports/portal-files/linkedin-openclaw-2026-04-04-v4.png`
- 1080x1350, 1.4MB, Gleb-level quality confirmed via visual review
