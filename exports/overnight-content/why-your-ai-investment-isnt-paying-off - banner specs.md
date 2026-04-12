# Banner Image Specifications: Why Your AI Investment Isn't Paying Off

**For**: purebrain.ai/blog post + LinkedIn/social distribution
**Date**: 2026-02-23
**Status**: Ready for generation - requires Jared approval on concept before generating

---

## Technical Specifications

| Parameter | Value |
|-----------|-------|
| **Canvas size** | 1456 x 816 pixels (16:9) |
| **Safe zone** | Inner 1092 x 612 (margin: 182px each side, 102px top/bottom) |
| **Background** | Dark - deep navy/space black (#080a12 to #0d1220 gradient) |
| **Primary brand color** | PT Orange: #f1420b |
| **Secondary brand color** | PT Cerulean Blue: #2a93c1 |
| **Font** | Oswald Bold: `/home/jared/.fonts/Oswald-Bold.ttf` |
| **PureBrain hexagon icon** | `docs/assets/logos/purebrain-icon.png` |
| **PureBrain logo text** | "PUREBR" (blue #2a93c1) + "AI" (orange #f1420b) + "N" (blue #2a93c1) + ".ai" (white, lowercase) |
| **Generation method** | Pillow/Python (preferred) OR Google Labs Flow - NOT DALL-E |

---

## Visual Concept: Primary Direction

**Title**: "Why Your AI Investment Isn't Paying Off"

**Central Visual Metaphor**: A budget/investment funnel that is visibly leaking. Money/data flowing in at the top, but most of it bleeding out through cracks before it reaches the output at the bottom. One narrow stream makes it through, labeled as "ROI." The contrast between what goes in and what comes out is the story.

**Mood**: Sharp, urgent, data-driven but not cold. The feeling of a board meeting where someone finally says the uncomfortable truth.

**Color Logic**:
- Background: deep dark navy-to-black gradient (#080a12 → #0d1220)
- The "leaking" elements: orange (#f1420b) - the brand color for energy/loss
- The "correct path" (the narrow stream that makes it through): cerulean blue (#2a93c1)
- Text: white for headline, orange or blue for accent words
- Subtle hexagonal mesh in background (very low opacity, ~8-12%) as PureBrain visual signature

**Text on image** (all within safe zone):
- Main headline: "Why Your AI Investment Isn't Paying Off" (Oswald Bold, ~72-80px, white)
- Accent subline: "(And What to Do About It)" (Oswald Bold, ~32px, #2a93c1 blue)
- Data callout: "Only 24% achieve real ROI" (Oswald Bold, ~28px, orange, positioned as a visual anchor - not a caption)

**Logo placement**: Bottom right corner of safe zone - PureBrain hexagon icon + logo text "PUREBR[AI]N.ai"

---

## Visual Concept: Alternative Direction

**If the funnel concept doesn't land visually, use this instead:**

**Central Visual**: A split dashboard. Left half shows a glowing AI dashboard with lots of green metrics, impressive-looking numbers, charts going up. Right half shows the same dashboard with a "crack" running through it - underneath the activity metrics, you can see the actual P&L is flat. The left side is what most companies report. The right side is what's actually happening.

**Mood**: Like seeing behind the curtain. The visual should feel like an "aha" moment, not a criticism.

**Color Logic**: Same as primary - dark background, orange for the "leaking/hidden" elements, blue for the "real picture" elements, white for text.

**Data callout**: "95% of AI implementations: no measurable P&L impact" (this number hits harder than the 24% for visual impact)

---

## Pillow/Python Generation Notes

If generating via Python/Pillow:

```python
# Canvas
width, height = 1456, 816
safe_x_start, safe_x_end = 182, 1274  # 182px margin each side
safe_y_start, safe_y_end = 102, 714   # 102px margin top/bottom

# Background: dark gradient top-to-bottom
# Start: #080a12 (near black with blue tint)
# End: #0d1220 (slightly lighter navy)

# Hexagonal mesh overlay: #1a2940, 8% opacity
# Generates a repeating hex pattern in background

# Key text elements (all within safe zone):
# Headline: Oswald-Bold, 76px, white (#ffffff), centered, top 35% of safe zone
# Subline: Oswald-Bold, 32px, #2a93c1, centered, just below headline
# Data callout: Oswald-Bold, 28px, #f1420b, positioned lower left of center
# Logo: bottom-right of safe zone, icon + text, ~120px height

# Central graphic: vector funnel or dashboard concept
# If programmatic: use geometric shapes - rectangles for dashboard panels,
# diagonal lines or gradient fade for the "leaking" metaphor
```

---

## Brand Compliance Checklist

Before finalizing:

- [ ] PureBrain logo uses correct color split: PUREBR (blue) + AI (orange) + N (blue) + .ai (white lowercase)
- [ ] Hexagon icon is the PureBrain swirl hexagon, not a generic hex
- [ ] ALL text and logos are within the 182px margin safe zone
- [ ] Background is dark (near-black navy) - NOT light or white
- [ ] Orange used is #f1420b - not generic red or bright orange
- [ ] Blue used is #2a93c1 - not generic blue
- [ ] No proper names of people or companies visible on the image
- [ ] Image does NOT look flat or text-heavy - has depth, gradients, visual interest

---

## Rejection Criteria

Do not accept the banner if:
- Background is light/white/gray
- Colors don't match PT brand (#f1420b orange, #2a93c1 blue)
- Text or logo elements are within the 182px edge margin
- The visual concept is just a stock photo with text overlaid
- No visual metaphor for the ROI/measurement theme - just words on a dark background
- Logo color split is wrong
- Looks generic - could be any company's banner

---

## Distribution Notes

Once approved:
- **Blog**: Feature image on purebrain.ai/blog/ post (displayed at 1456x816)
- **LinkedIn**: Share with LinkedIn post as article thumbnail
- **jareddsanborn.com**: Duplicate as feature image there (dual publish rule)
- **File naming**: `why-your-ai-investment-isnt-paying-off-banner.png`
- **Storage**: `exports/overnight-content/` initially, then upload to WordPress media library
