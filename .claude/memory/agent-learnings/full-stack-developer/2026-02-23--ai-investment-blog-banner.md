# Memory: AI Investment Blog Banner Generation

**Date**: 2026-02-23
**Type**: teaching + operational
**Agent**: full-stack-developer
**Topic**: Pillow banner for "Why Your AI Investment Isn't Paying Off" blog post

---

## What Was Built

Blog banner using funnel leaking metaphor.
- Size: 1456x816 (16:9), RGB, 142KB
- Output: `exports/overnight-content/why-your-ai-investment-isnt-paying-off-banner.png`
- Script: `exports/overnight-content/generate-banner.py`

## Visual Concept

Investment funnel with cracks:
- Headline + subline in top 45% of canvas
- Blue-outlined geometric funnel in bottom 55%
- Orange jagged crack lines with glow + orange droplet particles leaking from sides
- Blue glow particles + chevron arrows flowing in at top of funnel
- Narrow blue ROI stream at funnel bottom
- "Only 24% achieve real ROI" callout lower-left
- PUREBRAIN.ai logo bottom-right

## Critical Layout Lesson (textbbox required)

**NEVER use assumed line heights — always measure with textbbox.**

```python
l2_bbox = ld.textbbox((0, 0), line2, font=h1_font)
l2_h = l2_bbox[3] - l2_bbox[1]   # actual rendered height
line2_bottom = line2_y + l2_h
sub_y = line2_bottom + 20         # guaranteed gap, no overlap
```

76pt Oswald Bold = ~75-78px actual height (NOT 76px — fonts include internal leading).
Using `line2_y + 56` as assumed offset overlapped with line2_bottom=282.

## Funnel Geometry

```python
cx = W // 2
funnel_top_y = int(H * 0.475)   # 387px — clear of subline (~331px)
funnel_bot_y = int(H * 0.875)   # extends below safe zone for depth
funnel_top_hw = 310              # wide mouth = visual impact
funnel_bot_hw = 28               # narrow exit = ROI scarcity
```

## Crack/Glow Technique (reusable)

```python
# Jagged crack: alternating y-offset points
for i in range(n_jags + 1):
    t = i / n_jags
    jx = int(x_inner + (x_outer - x_inner) * t)
    jy = int(crack_y + ((-1) ** i) * 6 * (1 - t))
    jag_pts.append((jx, jy))
draw_line_glow(img, jag_pts, ORANGE, max_width=14, passes=7)
```

Multi-pass line glow with final crisp core = soft outer bloom + sharp center.

## Brand Color Splitting (logo text)

```python
parts = [("PUREBR", BLUE), ("AI", ORANGE), ("N", BLUE), (".ai", WHITE)]
bx = start_x
for text, color in parts:
    ld.text((bx, y), text, fill=(*color, 240), font=logo_font)
    bx += text_width(ld, text, logo_font)
```

## Files

- Font: `/home/jared/.fonts/Oswald-Bold.ttf`
- Icon: `docs/assets/logos/purebrain-icon.png` (2100x2100 RGBA spiral hex)
- Output: `exports/overnight-content/why-your-ai-investment-isnt-paying-off-banner.png`
- Script: `exports/overnight-content/generate-banner.py`
