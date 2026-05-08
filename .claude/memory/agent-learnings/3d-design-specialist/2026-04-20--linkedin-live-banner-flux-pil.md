# LinkedIn Live Banner - FLUX Pro + PIL Pipeline

**Date**: 2026-04-20
**Type**: operational
**Agent**: 3d-design-specialist

## Context
Created 2400x1260 LinkedIn Live event banner for PureBrain AI awakening event.

## Pipeline
1. FLUX Pro via `tools/flux_image_gen.py` with `--model pro --aspect 16:9`
2. PIL overlay script for branding (gradient, wordmark, text, LIVE indicator)

## What Worked
- FLUX Pro generated in 11s, cost $0.03 - excellent for event banners
- Bottom 40% gradient (Option D) starting at 55% height with alpha easing (progress^0.7) creates clean text zone
- Oswald Bold at 80pt for main title, 48pt subtitle, 32pt date - good hierarchy at 2400px width
- Orange accent line (3px) under main title adds brand energy
- LIVE indicator: red dot + glow ellipse (alpha 80) + "LIVE" text in upper-right

## Key Parameters
- Gradient alpha: 220 max, power curve 0.7
- Text starts at HEIGHT - 340 for comfortable bottom positioning
- Hex icon: 50px, wordmark font: 36pt
- Host names in #aaaaaa (muted) to not compete with title

## Gotchas
- Must convert RGBA to RGB before final save for LinkedIn compatibility
- Hex icon paste requires alpha mask parameter: `img.paste(icon, pos, icon)`

## Output Files
- Raw: `/home/jared/exports/portal-files/linkedin-live-banner-raw.png` (1519 KB)
- Final: `/home/jared/exports/portal-files/linkedin-live-banner-final.png` (2514 KB, 2400x1260)
