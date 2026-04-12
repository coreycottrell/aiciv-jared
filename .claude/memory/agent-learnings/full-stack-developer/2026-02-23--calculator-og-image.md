# Memory: AI Tool Stack Calculator OG Image

**Date**: 2026-02-23
**Type**: operational + teaching
**Agent**: full-stack-developer
**Topic**: Generated and deployed 1456x816 OG image for purebrain.ai/ai-tool-stack-calculator/

---

## What Was Built

- OG/featured image for the AI Tool Stack Calculator page
- Size: 1456x816 (16:9), RGB, 246KB PNG
- Output: `exports/calculator-og-image.png`
- Generator: `exports/generate-calculator-og.py`

## Design Concept

"HOW MUCH ARE YOU / WASTING ON AI?" - money waste theme
- Orange glowing headline "WASTING ON AI?" with multi-pass glow effect
- Right side: network of ~27 tool bubbles with connecting lines (represents 140+ tools)
- Bottom-left callout box: "$847 / MONTH" in orange (average waste figure)
- PureBrain hexagon icon (160px) next to callout box with blue glow
- Stats bar: "140+ Tools • 31 Categories • See Your Real AI Spend"
- PUREBRAIN.ai logo bottom-right (brand color split)
- Subtle hex mesh texture overlay at opacity=14

## WordPress Deployment

- Media ID: 793
- URL: https://purebrain.ai/wp-content/uploads/2026/02/ai-tool-stack-calculator-og.png
- Featured image set on page 777 (calculator page) via REST API

## HTML Meta Tags Updated

File: `exports/ai-tool-stack-calculator-v3.html`
Added: og:image, og:image:width/height, og:type, twitter:card, twitter:image

## Reusable Patterns

- Bubble network: 27 circles (BLUE/ORANGE alternating) + connecting line indices
- Box callout: dark glass bg (8,14,28,180) + orange left bar (4px) + blue top border
- Orange glow text: 18-pass spread with decreasing alpha
- Same Pillow stack as generate-banner.py + generate-og-image.py
