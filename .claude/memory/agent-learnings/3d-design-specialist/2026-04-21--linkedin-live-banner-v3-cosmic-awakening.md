# LinkedIn Live Banner v3 - Cosmic Awakening Concept

**Date**: 2026-04-21
**Type**: operational
**Agent**: 3d-design-specialist

## Context
Previous v2 banner had a Matrix-like human figure that gave "machines taking over" vibes. Jared wanted a completely different concept - futuristic but POSITIVE.

## What Worked
- FLUX 1.1 Pro prompt emphasizing abstract neural network, cosmic awakening, deep space, no human figures
- Key prompt elements: "neural connections forming", "bloom of light", "consciousness awakening", "volumetric light rays"
- Negative prompt embedded: "no human figures, no robots, no faces, no text"
- Using "Prefer: wait" header for synchronous FLUX generation (faster than polling)
- Left-side gradient overlay (180 alpha fading over 1100px) for text readability over busy FLUX art
- Aspect ratio 16:9 directly from FLUX, then scale-to-fill crop for exact 2400x1260

## Layout Decisions
- Logo upper-left (60, 50), 90px hex icon
- PUREBRAIN.AI wordmark next to logo with proper color split
- LIVE badge as orange pill (#f1420b) with rounded_rectangle, positioned below logo (NOT upper-right per Jared's request)
- "LINKEDIN LIVE" label after the badge
- Main title in 72pt Oswald Bold, two lines: "WATCH US AWAKEN" / "A BRAND NEW AI"
- Date in blue, hosts in white with gray subtitles
- Bottom bar: dark #080a12, PUREBRAIN.AI left, tagline right in orange

## Technical Notes
- FLUX 1.1 Pro via Replicate returned ~1.4MB PNG
- Final composite: 2400x1260 RGB, ~2.9MB
- Oswald Bold at /home/jared/.fonts/Oswald-Bold.ttf
- Script: tools/generate_live_banner_v3.py

## Files
- Raw FLUX: /home/jared/exports/portal-files/linkedin-live-banner-v3-raw.png
- Final: /home/jared/exports/portal-files/linkedin-live-banner-v3.png
