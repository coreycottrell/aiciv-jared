# full-stack-developer: PureBrain Homepage OG Image Generation

**Date**: 2026-02-23
**Type**: operational + teaching
**Topic**: Generated 1200x627 JPG OG image to replace broken 9MB GIF on purebrain.ai homepage

---

## Context

The purebrain.ai homepage had a 9MB animated GIF as its og:image (Pure-Brain-Vid-3.gif).
This caused broken social share cards on LinkedIn, Twitter, Facebook.
The OG diagnostic report (og-tags-diagnostic.md) identified this as the #1 priority fix.

## Solution Delivered

Generated `/home/jared/projects/AI-CIV/aether/exports/overnight-content/purebrain-homepage-og-image.jpg`

- Dimensions: 1200x627 (standard OG)
- File size: 56.1 KB (0.055 MB) - well under 1MB
- Format: JPEG quality 87
- Mode: RGB

## Script

`/home/jared/projects/AI-CIV/aether/exports/overnight-content/generate-og-image.py`

## Design Patterns Used

- Same Pillow pattern as `generate-banner.py` (RGBA compositing, glow effects, hex mesh)
- Background: vertical gradient #080a12 → #0d1220 (top to bottom)
- Hex mesh overlay opacity=14 (very subtle texture)
- Layout: icon left (~26% of width), text right (~44.5% of width)
- Icon size: 240px (PureBrain hexagon icon)
- Brand name: PUREBR(blue) + AI(orange) + N(blue) at 96pt Oswald Bold
- ".ai" at 60pt Oswald Bold (white), baseline-aligned with brand name
- Tagline: "Your AI Partnership Starts Here" at 36pt, light blue-white (#d2e6f5)
- Ambient glow behind icon: blue outer halo + orange core
- Vignette strength=130
- Bottom-right URL watermark: "purebrain.ai" in BLUE at 22pt

## Key Technical Notes

- RGBA composition order matters: bg → hex mesh → glow → content → vignette → bottom bar
- draw_content() was called twice (once to get icon center for glow, once on final base) - slight inefficiency but functionally correct
- JPG quality=87 gives 56KB for this image (very efficient since it's mostly flat dark areas)
- text_w/text_h helpers use textbbox (correct for Pillow ≥ 9.x)
- Baseline alignment of ".ai": align bottom of dotai text with bottom of brand name text

## Upload Instructions

WordPress Admin → Edit Homepage → Yoast SEO panel → Social tab → OG Image
Set to this file after uploading via Media Library.

## Colors Used

- BLUE: (42, 147, 193) = #2a93c1
- ORANGE: (241, 66, 11) = #f1420b
- WHITE: (255, 255, 255)
- DARK_BG1: (8, 10, 18) = #080a12
- DARK_BG2: (13, 18, 32) = #0d1220
