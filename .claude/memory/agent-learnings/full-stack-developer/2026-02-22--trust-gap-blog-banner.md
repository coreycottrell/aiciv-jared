# Memory: Trust Gap Blog Banner Generation

**Date**: 2026-02-22
**Type**: teaching + operational
**Agent**: full-stack-developer
**Topic**: Pillow banner generation for "The AI Trust Gap" blog post

---

## What Was Built

Blog banner for "The AI Trust Gap Is the Real Problem (Not the Technology)"
- Size: 1456x816 (16:9)
- Output: `exports/trust-gap-blog-banner.png` (528KB)
- Script: `tools/generate_trust_gap_banner.py`

## Visual Concept

Split composition with center crack:
- LEFT: Blue-lit simple task icons (envelope, document, chat bubble) = trusted AI zone
- CENTER: Jagged vertical crack with orange energy/sparks = the trust gap
- RIGHT: Shadowed chess king with question marks = strategic decisions (distrusted)
- TOP: Title text "THE AI TRUST GAP" (large, bold) + subtitle
- BRAND: PureBrain icon + text in safe zone bottom-right

## Pillow Techniques That Worked Well

### Multi-pass crack glow
```python
for spread in [140, 110, 85, ...]:
    alpha = int(55 * (1 - spread / 140))
    cd.line(offset_pts, fill=(241, 66, 11, alpha), width=max(1, spread // 2))
```
Then blur + re-composite sharp version on top = soft outer glow with crisp core.

### Icon glow halos
Create separate RGBA layer, draw radial ellipses with tiny alpha, composite over main img.

### Jagged crack path
Define list of (x, y) points with alternating left/right offsets - creates natural lightning effect.

### Brand name color splitting (PUREBR in blue, AI in orange, N in blue)
```python
brand_parts = [("PUREBR", blue), ("AI", orange), ("N", blue), (".AI", gray)]
bx = start_x
for text, color in brand_parts:
    draw.text((bx, y), text, fill=color, font=font, anchor="lm")
    bx += font.getbbox(text)[2] - font.getbbox(text)[0]
```

### Text shadow depth
Draw text at (x+2, y+2) with low alpha, then draw main text at (x, y).

## Layout Lesson

**Icons should NOT be in the vertical center** - they compete with title text.
Push icons to LOWER THIRD (H * 2 // 3) and keep title at TOP THIRD.
This creates clear visual hierarchy: text first, icons second.

## Files Referenced

- Font: `/home/jared/.fonts/Oswald-Bold.ttf`
- Icon: `docs/assets/logos/purebrain-icon.png` (2100x2100 RGBA)
- Output: `exports/trust-gap-blog-banner.png`
- Script: `tools/generate_trust_gap_banner.py`

## Safe Zone

- x: 182-1274, y: 102-714
- All text and icons kept within this zone
- Vignette darkens corners beyond safe zone
