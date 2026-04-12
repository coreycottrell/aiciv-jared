# Memory: Origin Story Blog Banner Generation

**Date**: 2026-02-23
**Type**: teaching + operational
**Agent**: full-stack-developer
**Topic**: Pillow banner for "We Both Wrote This Post. That's the Point." origin story post

---

## What Was Built

Blog banner using dual-stream convergence metaphor.
- Size: 1456x816 (16:9), RGB, 206KB
- Output: `exports/origin-story-banner.png`
- Script: `exports/generate-origin-story-banner.py`

## Visual Concept

Two voices converging at center hex:
- ORANGE fan (5 streams, left side) = HUMAN voice
- BLUE fan (5 streams, right side) = AI voice
- CENTER: nested hexagons with PureBrain icon = convergence point
- Title in top 45% of canvas (headline + subline)
- HUMAN/AI labels below the fan spread (not above, to avoid text overlap)
- `purebrain.ai/blog` URL bottom-left, PureBrain logo bottom-right

## Fan Stream Technique (New Pattern)

5 Bezier curves per side, spread wide at edges, converge to hex approach point:

```python
stream_defs = [
    (-110, -22, -60),   # (start_y_offset, end_y_offset, ctrl_bulge)
    (-55,  -12, -30),
    (  0,    0,  10),   # center stream = widest (max_width=14)
    ( 55,   12,  35),
    (110,   22,  70),
]
max_widths = [6, 9, 14, 9, 6]

for (sy_off, ey_off, ctrl_b), max_w in zip(stream_defs, max_widths):
    sy = start_y_center + sy_off
    ey = cy_center + ey_off
    ctrl_x = int(start_x + (end_x - start_x) * 0.45)
    ctrl_y = int((sy + ey) / 2 + ctrl_b)
    # Quadratic bezier: n=50 points
```

The ctrl_b bulge creates gentle S-curves vs straight lines — more organic.
Center stream at 45% ctrl_x position gives smooth convergence curvature.

## Layout Lessons

1. **Labels below fan spread** — placing them above (start_y - 130) caused overlap
   with subline text. Place below: `start_y_center + 125` (below lowest stream).

2. **Visual element Y position** — cy = H * 0.60 (not 0.54) gives clean separation
   from the subline text (~300px) and keeps everything in safe zone.

3. **Center hex needs double-outline pass** for crispness after glow composite:
   ```python
   for _ in range(2):
       ld2.polygon(pts_mid, outline=(*BLUE, 200), fill=None)
   ```

4. **Line glow alpha 140 (not 110)** gives better stream visibility on dark bg.

## Mixed-Color Headline Technique

```python
# "That's" in orange, "the Point." in white — same font, same line
thatw = text_width(ld, "That\u2019s ", h2_font)
ld.text((line2_x, line2_y), "That\u2019s ", fill=(*ORANGE, 255), font=h2_font)
ld.text((line2_x + thatw, line2_y), "the Point.", fill=(*WHITE, 255), font=h2_font)
```

## Files

- Font: `/home/jared/.fonts/Oswald-Bold.ttf`
- Icon: `docs/assets/logos/purebrain-icon.png` (2100x2100 RGBA spiral hex)
- Output: `exports/origin-story-banner.png`
- Script: `exports/generate-origin-story-banner.py`
