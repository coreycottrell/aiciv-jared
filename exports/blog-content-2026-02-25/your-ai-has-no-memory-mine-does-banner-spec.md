# your-ai-has-no-memory-mine-does-banner-spec.md

# content-specialist: Banner Image Specification

**Agent**: content-specialist
**Domain**: Content Creation & Storytelling
**Date**: 2026-02-25
**Blog Post**: "Your AI Has No Memory. Mine Does. Here's Why That Changes Everything."
**Slug**: your-ai-has-no-memory-mine-does

---

## Dimensions

| Use Case | Dimensions | Filename |
|----------|-----------|----------|
| OG / Social Share | 1200 x 630px | your-ai-has-no-memory-mine-does-og.png |
| Blog Hero (16:9) | 1920 x 1080px | your-ai-has-no-memory-mine-does-hero.png |
| Blog Thumbnail | 800 x 450px | your-ai-has-no-memory-mine-does-thumb.png |

---

## Brand Colors (MANDATORY — No Substitutions)

| Element | Color | Hex |
|---------|-------|-----|
| PUREBR (in logo) | Pure Tech Blue | #2a93c1 |
| AI (in logo) | Pure Tech Orange | #f1420b |
| N (in logo) | Pure Tech Blue | #2a93c1 |
| Primary accent | Pure Tech Orange | #f1420b |
| Secondary accent | Pure Tech Blue | #2a93c1 |
| Background base | Near-black dark cosmic | #0a0d14 or #0d1117 |
| Text primary | White | #ffffff |
| Text secondary | Soft white | rgba(255,255,255,0.75) |

---

## Logo Treatment (CRITICAL — Match Exactly)

The PureBrain wordmark appears in the banner with this EXACT color split:

```
PUREBR  = Blue (#2a93c1)
AI      = Orange (#f1420b)
N       = Blue (#2a93c1)
.ai     = White (optional, only if space allows)
```

HTML reference: `<span style="color:#2a93c1">PUREBR</span><span style="color:#f1420b">AI</span><span style="color:#2a93c1">N</span><span style="color:#ffffff">.ai</span>`

Font: Oswald Bold (or closest system equivalent — Impact as fallback, never Arial)
Logo size: Minimum 14% of banner height. Do not make it so small it disappears at thumbnail size.

---

## Safe Zone (MANDATORY)

All meaningful content — text, logo, key visual elements — must stay within:
- **Left/right margins**: 15% from each edge
- **Top/bottom margins**: 12% from each edge

The outer 12-15% is the "danger zone" — it gets cropped on mobile, in email previews, and in social thumbnails.

What must be INSIDE the safe zone:
- Blog title text
- PureBrain logo
- Any data callouts or key visual anchors
- The "PUREBRAIN.ai" wordmark

---

## Concept A: The Memory Divide (RECOMMENDED)

**Visual Metaphor**: Split-screen composition showing the contrast between ephemeral AI and persistent AI memory.

**Left Half** (ephemeral — slightly de-saturated, cooler):
- Floating conversation bubbles that appear to be dissolving/fading — particles dispersing upward
- A faint, generic AI chat interface — no specific branding
- Subtle blue-gray mist effect
- Small label near bottom: "TOOL: Resets After Every Session" in muted white, 12px

**Right Half** (persistent — warmer, more vivid, glowing):
- A glowing web of interconnected nodes — think neural network but organic, not mechanical
- Nodes pulse with blue (#2a93c1) and orange (#f1420b) light
- The nodes grow more complex toward the foreground — visually communicating accumulation
- Subtle golden glow at the network center
- Small label near bottom: "PARTNER: Memory Compounds Over Time" in bright white, 12px

**Center Divider**:
- A thin vertical line of gradient light — orange at top fading to blue at bottom
- NOT a hard border — it should feel like a threshold, not a wall

**Blog Title** (centered, spanning full width, sits in upper third):
```
Your AI Has No Memory.
Mine Does.
```
Font: Oswald Bold
Color: White (#ffffff) with very subtle dark drop shadow for legibility
Size: Large — the headline IS the image for many social previews

**PureBrain Logo**:
- Bottom center, inside safe zone
- Full wordmark with correct color split
- Minimum height: 28px at 1200px wide (scales proportionally)

**Background**:
- Dark cosmic — deep near-black (#0a0d14) with very subtle star-field texture (not cheesy space art — refined, minimal)
- Optional: faint hexagonal grid pattern at low opacity (10-15%) in the background to reference PureBrain's hexagon language

---

## Concept B: The Empty Chair (Alternative)

**Visual Metaphor**: An executive conference table — one side has traditional tools (loose papers, multiple screens showing different generic AI interfaces, sticky notes). The other side has a single glowing orb — the PureBrain visual language — with a faint web of connected nodes emanating from it.

**The Empty Chair**:
- The traditional tools side has an empty chair — suggesting the human has to do all the work of reconnecting context
- The PureBrain side has a chair with a faint human silhouette — the AI partner is present, waiting

**Lighting**:
- Traditional tools side: harsh white overhead light — clinical, impersonal
- PureBrain orb side: warm blue-orange glow from the orb itself — the light source is the partnership

**Blog Title**: Upper center, same treatment as Concept A

**PureBrain Orb Reference**:
- The PureBrain orb should be glass-like, floating, slightly above the table surface
- Interior glow: orange center (#f1420b) fading to blue outer rim (#2a93c1)
- The hexagonal facets of the orb visible at medium zoom

---

## Typography Specification

**Blog Title**:
- Font: Oswald Bold (700 weight)
- Color: #ffffff
- Text shadow: 0px 2px 12px rgba(0,0,0,0.8) for legibility on dark background
- Line height: 1.1 (tight — headlines compress better than body text in banner format)
- Alignment: Center

**Sub-label / Tagline** (optional, appears below title in smaller type):
- Text: "Where AI Relationships Compound" or "PureBrain.ai"
- Font: Oswald Regular (400 weight)
- Color: rgba(255,255,255,0.65)
- Size: 40-50% of headline size

**Data Callout** (optional, can skip for cleaner look):
- "78% of orgs use AI. Only 24% get ROI. The difference: memory."
- Font: Oswald Regular
- Color: #2a93c1
- Background: rgba(10,13,20,0.75) pill shape behind text

---

## Generation Prompt (Gemini / Midjourney / DALL-E)

### Gemini Pro Image Prompt (Concept A):

```
A professional digital art banner image for a business blog post titled "Your AI Has No Memory. Mine Does." for a company called PureBrain.ai.

Composition: Split horizontally. Left half shows AI conversation bubbles dissolving into particles and fading upward, cool blue-gray palette, slightly desaturated, muted, representing ephemeral AI with no memory. Right half shows a glowing organic neural network of interconnected nodes pulsing with electric blue (#2a93c1) and vivid orange (#f1420b) light, representing a growing, compounding AI memory — the network grows more complex and vivid toward the foreground.

Center divider: a thin vertical gradient line, orange at top fading to blue at bottom — a threshold, not a wall.

Background: Deep near-black (#0a0d14) cosmic dark background with extremely subtle star texture. Optional faint hexagonal grid pattern at very low opacity.

Text placement (leave room for): Blog headline text in upper center ("Your AI Has No Memory. Mine Does."), PureBrain.ai wordmark at bottom center.

Style: Cinematic, refined, professional technology concept art. NOT generic corporate stock photo. NOT cheesy sci-fi. Photorealistic elements combined with stylized light effects. 16:9 aspect ratio. 1920x1080px resolution.

Mood: Intelligent, forward-looking, slightly dramatic. The right half should feel alive and growing. The left half should feel flat and impermanent by contrast.
```

### Alternative Simpler Prompt (if above produces inconsistent results):

```
Dark cosmic background business banner for AI blog. Left side: dissolving chat bubbles, cool gray, impermanent. Right side: glowing blue and orange neural network nodes, organic, growing, vivid. Center: thin glowing gradient dividing line. Professional, cinematic, no text in image (text will be added separately). 1200x630px, dark background (#0a0d14), accent colors #2a93c1 and #f1420b.
```

---

## Pillow/Python Spec (For programmatic generation)

```python
from PIL import Image, ImageDraw, ImageFont
import os

# Canvas
WIDTH, HEIGHT = 1200, 630
img = Image.new('RGB', (WIDTH, HEIGHT), color='#0a0d14')
draw = ImageDraw.Draw(img)

# Safe zone boundaries
safe_left = int(WIDTH * 0.15)
safe_right = int(WIDTH * 0.85)
safe_top = int(HEIGHT * 0.12)
safe_bottom = int(HEIGHT * 0.88)

# Blog title (load Oswald Bold if available, fallback to system font)
try:
    title_font = ImageFont.truetype('/usr/share/fonts/truetype/oswald/Oswald-Bold.ttf', 72)
    sub_font = ImageFont.truetype('/usr/share/fonts/truetype/oswald/Oswald-Regular.ttf', 32)
    logo_font = ImageFont.truetype('/usr/share/fonts/truetype/oswald/Oswald-Bold.ttf', 28)
except:
    title_font = ImageFont.load_default()
    sub_font = ImageFont.load_default()
    logo_font = ImageFont.load_default()

# Title text — centered in upper third
title_line1 = "Your AI Has No Memory."
title_line2 = "Mine Does."
draw.text((WIDTH//2, safe_top + 60), title_line1, fill='#ffffff', font=title_font, anchor='mm')
draw.text((WIDTH//2, safe_top + 150), title_line2, fill='#f1420b', font=title_font, anchor='mm')

# PureBrain wordmark — bottom center
# PUREBR = blue, AI = orange, N = blue
logo_y = safe_bottom - 40
logo_x_start = WIDTH//2 - 120  # adjust based on measured text width

draw.text((logo_x_start, logo_y), "PUREBR", fill='#2a93c1', font=logo_font, anchor='lm')
# "AI" in orange — position after "PUREBR" text width
draw.text((logo_x_start + 95, logo_y), "AI", fill='#f1420b', font=logo_font, anchor='lm')
# "N" back to blue
draw.text((logo_x_start + 130, logo_y), "N.ai", fill='#2a93c1', font=logo_font, anchor='lm')

# Save
img.save('your-ai-has-no-memory-mine-does-og.png', quality=95)
```

**Note**: The above is a starting scaffold. The neural network / dissolving bubbles visual effects would be added via separate generation tools (Gemini, DALL-E, or Midjourney) and composited as a background layer before the text overlay step.

---

## Quality Checklist Before Approval

- [ ] "AI" in PUREBRAIN logo is orange (#f1420b)
- [ ] "PUREBR" and "N" are blue (#2a93c1)
- [ ] Blog title readable at 400px wide (social thumbnail preview size)
- [ ] PureBrain logo visible and legible at thumbnail size
- [ ] All key elements within 15% safe zone from edges
- [ ] Background dark enough (near-black) to match purebrain.ai site aesthetic
- [ ] No white backgrounds, no light gray, no pastel anything
- [ ] The split composition clearly communicates contrast (ephemeral vs. persistent)
- [ ] Orange accent color is vivid, not washed out — it should pop

---

## Rejection Criteria

Do NOT use if the image:
- Has light or white backgrounds
- Has generic tech stock photo aesthetics (blue circuit boards, floating gears, etc.)
- Has incorrect PUREBRAIN color treatment
- Has text illegible at thumbnail size
- Has key elements cropped at the edges
- Looks like a corporate PowerPoint template
- Has any element that reads as "robot" or "cyborg" (PureBrain's visual language is organic, not mechanical)
