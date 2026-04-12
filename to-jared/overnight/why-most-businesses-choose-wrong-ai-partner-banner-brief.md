# content-specialist: Banner Image Brief - Why Most Businesses Choose the Wrong AI Partner

**Agent**: content-specialist
**Domain**: Content Creation & Storytelling
**Date**: 2026-02-24
**Format**: Image Brief for blog banner + OG image

---

## Brand Specifications (Required — Non-Negotiable)

**Primary Colors:**
- PT Orange: `#f1420b`
- PT Blue: `#2a93c1`
- Background: Dark — deep navy or near-black (`#0a0f1e` or `#080d1a`)
- Accent: White `#ffffff` for text contrast

**PureBrain Logo Text Treatment:**
- "PUREBR" — PT Blue (`#2a93c1`)
- "AI" — PT Orange (`#f1420b`)
- "N" — PT Blue (`#2a93c1`)
- ".ai" — White lowercase (`#ffffff`)

**Typeface:**
- Headlines: Oswald Bold (available at `/home/jared/.fonts/Oswald-Bold.ttf`)
- Body/sub-text: Oswald Regular or clean sans-serif

**PureBrain Hexagonal Icon:**
- Source: `/home/jared/projects/AI-CIV/aether/docs/assets/logos/purebrain-icon.png`
- Place in corner or integrated into composition — never omit

---

## Dimensions

| Format | Dimensions | Safe Zone |
|--------|-----------|-----------|
| Blog Banner | 1600 x 900px | Margins: 120px all sides (1360 x 660 inner safe zone) |
| OG Image | 1200 x 627px | Margins: 90px all sides (1020 x 447 inner safe zone) |

**Critical:** All text and key visuals must stay inside the safe zone. Edges will be cropped on mobile.

---

## Concept A (Recommended): The Vendor Maze

**Visual Concept:**

A dark background filled with dozens of small, identical glowing orbs in muted colors (grey-blue) — representing the 70,000+ AI vendors in the market. They are clustered, overlapping, indistinguishable from one another. All the same.

In the center-left of the frame, one orb breaks from the cluster. It glows distinctly — PT Orange (`#f1420b`) — and has a visible path drawn in PT Blue light lines connecting it back to a minimalist desk/workspace icon or a subtle human silhouette. The connection is visible. The relationship is visible.

The visual narrative: the crowd is undifferentiated. One relationship is different.

**Text Elements (inside safe zone):**

Primary headline (Oswald Bold, large, white):
```
Why Most Businesses Choose
the Wrong AI Partner
```

Sub-label (smaller, PT Orange, Oswald Bold):
```
And how to tell if you have
```

Bottom left: PureBrain logo mark
Bottom right: `purebrain.ai/blog/`

**Mood:** Precise. Intelligent. Slightly unsettling but not alarming. The visual equivalent of "you may be making a mistake you don't know about yet."

---

## Concept B (Alternative): The Compounding Gap

**Visual Concept:**

Split composition. Left side and right side divided by a glowing vertical line in PT Blue.

**Left side (muted, slightly desaturated):**
- A flat line graph — representing static, non-compounding AI usage
- Label: "Tool Mode" in grey text
- One faint grey orb — generic, unconnected

**Right side (vivid, warm):**
- An ascending curve graph glowing in PT Orange — compounding value over time
- Label: "Partnership Mode" in white text
- The PureBrain hexagonal icon glowing at the top of the curve
- Subtle connecting light lines suggesting ongoing relationship/memory

**Text Elements (inside safe zone):**

Primary headline (Oswald Bold, large, white):
```
Renting vs. Building
The AI Gap Most Leaders Miss
```

Sub-label (smaller, PT Orange):
```
18 months in, the difference isn't AI capability.
It's what your AI knows about you.
```

Bottom: `PUREBRAIN.ai` logo treatment + `purebrain.ai/blog/`

**Mood:** Analytical, data-forward, the visual equivalent of seeing a compounding interest chart for the first time and realizing you should have started earlier.

---

## Pillow/Python Generation Notes

```python
from PIL import Image, ImageDraw, ImageFont
import math

# Blog banner dimensions
W, H = 1600, 900
SAFE_MARGIN = 120

# Colors
BG = (8, 13, 26)          # #080d1a - deep dark navy
PT_ORANGE = (241, 66, 11)  # #f1420b
PT_BLUE = (42, 147, 193)   # #2a93c1
WHITE = (255, 255, 255)
GREY = (80, 90, 110)

# Font paths
FONT_BOLD = "/home/jared/.fonts/Oswald-Bold.ttf"
FONT_REGULAR = "/home/jared/.fonts/Oswald-Regular.ttf"

# PureBrain icon
ICON_PATH = "/home/jared/projects/AI-CIV/aether/docs/assets/logos/purebrain-icon.png"

# Safe zone bounds
SAFE_LEFT = SAFE_MARGIN
SAFE_RIGHT = W - SAFE_MARGIN
SAFE_TOP = SAFE_MARGIN
SAFE_BOTTOM = H - SAFE_MARGIN

# For Concept A:
# Draw 40-60 small circles (radius 8-15px) in GREY scattered across left 60% of canvas
# Draw 1 circle in PT_ORANGE at center-left with radius 20px and soft glow effect
# Draw connecting light lines in PT_BLUE from orange orb to right side
# Place headline text: top half, white, Oswald Bold 80pt
# Place sub-label: below headline, PT_ORANGE, Oswald Bold 40pt
# Place PureBrain icon: bottom-left corner, 80x80px
# Place blog URL: bottom-right, white, small
```

---

## Text Placement Reference

**Concept A Layout Map:**

```
[TOP SAFE ZONE - 120px from top]

    Why Most Businesses Choose          <- White, Oswald Bold, 80-90pt
    the Wrong AI Partner                <- Same line 2

    And how to tell if you have         <- PT Orange, Oswald Bold, 42pt

[CENTER: Orb cluster visual]           <- Fills middle section

[BOTTOM SAFE ZONE - 120px from bottom]

[PUREBRAIN ICON - bottom left]        [purebrain.ai/blog/ - bottom right]
```

---

## Key Constraints

1. **No faces or human characters** — keeps it professional and evergreen
2. **No stock-photo feel** — the aesthetic must be futuristic, data-visual, ethereal
3. **Text must be legible at thumbnail size** — headline should be readable at 400px wide
4. **PureBrain hex icon must appear** — brand consistency across all blog posts
5. **Reject if:** text is too close to edges, background is too light, orange and blue clash rather than complement

---

## OG Image Notes

The OG image (1200x627) should use the same visual concept but simplified:

- Fewer visual elements (less noise at smaller size)
- Headline font may need to be reduced to 60-65pt to fit safely
- Maintain all brand colors and icon placement
- The sub-label can be dropped if space is tight — headline is the priority

---

**File to**: Blog Posts Drive folder (ID: 1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv) in subfolder `why-most-businesses-choose-wrong-ai-partner-2026-02-24`
