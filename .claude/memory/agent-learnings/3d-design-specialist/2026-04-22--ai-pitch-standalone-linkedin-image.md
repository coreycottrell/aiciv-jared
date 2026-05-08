# AI Pitch Standalone LinkedIn Image

**Date**: 2026-04-22
**Type**: operational
**Agent**: 3d-design-specialist

## Context
Created standalone LinkedIn post image for Jared's "Let My AI Pitch You" personal AI pitch post.

## Pipeline
1. FLUX Pro 1.1 via Replicate (`3:4` aspect ratio for 1080x1350 portrait)
2. PIL v4 standalone overlay: top bar (hex icon + wordmark), title zone with gradient backing, bottom bar (wordmark + CTA)

## Prompt That Worked
"Cinematic boardroom scene, dark moody lighting, an AI holographic figure glowing with blue and orange energy standing at the head of a sleek glass conference table, presenting holographic data visualizations floating in air, a single human investor sitting in a dark leather chair looking intrigued with arms crossed, blue #2a93c1 and orange #f1420b accent lighting, corporate futuristic atmosphere, dark background, high contrast dramatic rim lighting, volumetric light beams, film grain, shallow depth of field with bokeh, 8k photorealistic quality, Gleb Kuznetsov style, no text in image"

## v4 Standalone Format Details
- Top bar: 90px gradient overlay, hex icon 40px, wordmark 22pt
- Title zone: Bell curve gradient at y=320, height=280
- Title: 72pt Oswald Bold, centered, shadow blur=6
- Subtitle: Two lines 32pt - first line light gray, second line ORANGE for emphasis
- Bottom bar: 100px gradient, wordmark left 22pt, CTA right 24pt orange
- Orange accent line (2px) at top of bottom bar
- Safe zone: x=100 to x=980

## Output
- Raw FLUX: `/home/jared/exports/portal-files/ai-pitch-flux-raw.png` (1.2MB)
- Final: `/home/jared/exports/portal-files/ai-pitch-standalone-banner.png` (1.4MB, 1080x1350)
- R2 key: `f15527f5-559c-4799-92e3-4b2de2e27897/1776899125184-5b5c2b72-ai-pitch-standalone-banner.png`
- R2 URL: `https://pub-8f8cf3b34e354e108283ed11c59db125.r2.dev/f15527f5-559c-4799-92e3-4b2de2e27897/1776899125184-5b5c2b72-ai-pitch-standalone-banner.png`
