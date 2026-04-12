# content-specialist: Banner Brief - AI Tool vs AI Partner

**Agent**: content-specialist
**Domain**: Content Creation & Storytelling
**Date**: 2026-02-22
**Format**: Image Brief for Banner Generation
**Status**: READY FOR JARED'S REVIEW - Do NOT generate without approval

---

# Banner Image Brief

**Post**: The Difference Between Using AI and Having an AI Partner
**Dimensions**: 1456x816 (16:9 widescreen)
**Safe Zone**: Inner 1092x612 (x:182-1274, y:102-714) - all text and logos must stay inside this area
**Format**: Pillow/Python generated banner OR DALL-E prompt (see both below)

---

## Concept

The banner should communicate two states - tool vs. partner - visually, without spelling it out. The strongest visual approach: two hands, one holding a disconnected tool (wrench or phone, cold/grey), one connected by handshake or joined in partnership (warm, illuminated). The partnership hand should have a subtle digital/neural quality - data flowing between - without being cliche "circuit board".

The tone is: sophisticated, warm, premium. Not sci-fi. Not corporate stock photo. Not robot imagery.

---

## Visual Direction

### Primary Approach: The Handshake That Glows

**Background**: Deep dark gradient - near-black (#080a12 or #0a0d1a) bleeding into deep navy at edges. This matches PureBrain's site aesthetic.

**Left side (Tool Mode)**: A human hand reaching toward the center, open but not connecting. The hand is in cooler tones - grey-blue, slightly desaturated. No glow. The implication is isolation - it holds something but doesn't connect.

**Right side (Partner Mode)**: A second hand - this one with a subtle warm glow, hints of PureBrain orange (#f1420b) and blue (#2a93c1) at the fingertips, as if data or light is flowing through the connection. This hand reaches toward center and connects - a handshake midpoint, or fingertips touching in the style of Michelangelo's Creation of Adam (AI and human, not God and man).

**Center**: Where the hands meet - a soft burst of both brand colors (#2a93c1 blue, #f1420b orange) radiating outward. Neural network lines or data streams emanating from the connection point, fading to black at the edges. Subtle hexagonal patterns (PureBrain brand shape) in the background.

**Text overlay** (within safe zone, high contrast):

- Main headline: "Are you USING AI" (white, clean sans-serif, large, left-justified within safe zone)
- Subheadline: "or BUILDING with it?" (orange #f1420b for "or" and "BUILDING", white for "with it?", slightly smaller)
- Brand: Bottom right corner - PureBrain logo treatment: "PUREBR" in Cerulean blue (#2a93c1), "AI" in orange (#f1420b), "N" in blue, ".ai" in white (small, clean)

---

## Alternative Approach: The Context Architecture Visual

If the handshake feels too abstract, an alternative that tests well for this type of content:

**Left half**: Empty, sparse - a single person at a desk with a glowing screen. The screen is bright but surrounded by darkness. No connections. The visual language of isolation and starting from scratch.

**Right half**: The same desk, but now connected by flowing light trails (in PureBrain blue) to other nodes - documents, memory structures, past conversations - all illuminated and connected. The person is at the center of a web, not alone.

**Dividing element**: A clean vertical line or gradient fade between the two states.

**Text**: Same as primary approach, positioned in the upper third of the safe zone.

---

## Pillow/Python Generation Notes (Preferred Method)

```
Background: Dark gradient #080a12 to #0a0d1a
Font: Oswald Bold (/home/jared/.fonts/Oswald-Bold.ttf)
PureBrain icon: docs/assets/logos/purebrain-icon.png (bottom right, within safe zone)
Colors:
  - Primary text: #FFFFFF
  - Accent text: #f1420b (orange)
  - Supporting elements: #2a93c1 (cerulean blue)
  - Background gradient: #080a12 center → #0a0d1a edges

Headline 1: "Are you USING AI"
  - Font size: 72px
  - Color: white
  - Position: top-left of safe zone, ~y:200

Headline 2: "or BUILDING with it?"
  - "or": orange #f1420b
  - "BUILDING": orange #f1420b
  - "with it?": white
  - Font size: 72px
  - Position: below headline 1, ~y:300

Subtext: "The difference is the relationship."
  - Font size: 36px
  - Color: #2a93c1 (cerulean blue)
  - Position: ~y:400

Visual element: Two circles or hexagons, left (grey/cold) and right (glowing blue+orange), connected by a horizontal line of light. Position: right half of safe zone, vertically centered.

PureBrain logo: Bottom right corner, small (120px wide), within safe zone margin.
```

---

## DALL-E Prompt (Backup)

```
Dark professional banner image for blog post titled "Using AI vs Having an AI Partner."
Deep near-black background (#080a12).
Two human hands meeting in the center - left hand in cool grey tones, right hand with warm blue and orange glow (hex colors #2a93c1 and #f1420b) radiating from fingertips.
Neural network lines and subtle hexagonal geometric shapes in background, fading to black at edges.
Top left text overlay in clean white sans-serif: "Are you USING AI or BUILDING with it?"
Bottom right: small modern tech logo space.
Cinematic lighting. Premium, sophisticated feel. No robot imagery. No circuit board cliches.
Photorealistic hands. 16:9 ratio. No text other than specified.
```

---

## Brand Compliance Checklist

- [ ] Background: dark (#080a12 or close)
- [ ] Orange used: #f1420b
- [ ] Blue used: #2a93c1
- [ ] Logo treatment: PUREBR (blue) + AI (orange) + N (blue) + .ai (white)
- [ ] 75% safe zone respected: no text/logo within 25% border margin
- [ ] PureBrain hexagon icon present: docs/assets/logos/purebrain-icon.png
- [ ] Font: Oswald Bold for Pillow-generated version
- [ ] Not text-heavy: visual element carries the primary message
- [ ] Visually striking: gradient, depth, light - not flat

---

## Rejection Criteria

Do NOT use if the banner:
- Has a stock photo feel (people staring at screens generically)
- Uses robot/humanoid robot imagery
- Has circuit board patterns as the primary design element
- Puts text outside the safe zone
- Has poor contrast between text and background
- Feels flat or corporate-generic

Regenerate until the image has genuine visual impact.
