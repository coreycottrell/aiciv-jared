---
name: MA Sunday batch May 4 image production — v4 standalone + Option D banner
type: technique
date: 2026-05-03
agent: 3d-design-specialist
tags: [flux, pil, oswald-bold, banner-option-d, standalone-v4, brand-scrim, ma-batch]
confidence: high
---

# MA# Sunday Batch — Monday May 4 LinkedIn Drop (4 images)

## Context

3 LinkedIn posts for May 4 drop (Memory Tax / 72-Hour Default / Resonance Beats Reach). Image SOP: FLUX Pro + PIL composite + Oswald Bold, 2K min quality, brand colors locked, hex icon official asset, repurpose pool check before generation.

## Output paths (all >1.46MP, brand-compliant)

- `/home/jared/exports/portal-files/MA-IMG-2026-05-04-POST1-MEMORY-TAX.png` (1080x1350, 937KB)
- `/home/jared/exports/portal-files/MA-IMG-2026-05-04-POST2-72HR-DEFAULT.png` (1080x1350, 1158KB)
- `/home/jared/exports/portal-files/MA-IMG-2026-05-04-POST3-RESONANCE-BANNER.png` (2400x1260, 2605KB)
- `/home/jared/exports/portal-files/MA-IMG-2026-05-04-POST3-RESONANCE-NEWSLETTER-1200x630.png` (1200x630, 948KB)
- Manifest: `/home/jared/exports/portal-files/MA-IMG-MANIFEST-2026-05-04.md`

## Tooling

Built two scripts:
- `exports/ma-img-2026-05-04/generate_batch.py` — main batch (FLUX 1.1 Pro + v4 standalone composer + Option D banner composer)
- `exports/ma-img-2026-05-04/fix_banners.py` — banner v2 with stronger scrim

Reused v4 format pattern from `exports/content-batch-images-may5/generate_5_banners.py`.

## Key technique discoveries

### 1. v4 Standalone composition (1080x1350)

Locked layout:
- Top bar (140px) DARK: hex icon (72px) + PUREBRAIN.AI (38px Oswald Bold) + 2px blue vertical separator + title (38px Oswald Bold)
- Blue accent line 2px
- FLUX 1080x1080 paste, vertically centered in middle area
- Title overlay 90px Oswald Bold WHITE with 4px DARK stroke + soft vertical-radial gradient (alpha 190 max, quadratic falloff)
- Blue accent line 2px
- Bottom bar (90px) DARK: PUREBRAIN.AI (26px) left + ORANGE CTA (26px) right with arrow

Wordmark color split (constitutional): PUREBR=`#2a93c1`, AI=`#f1420b`, N=`#2a93c1`, .AI=`#ffffff`.

### 2. Option D banner composition (2400x1260)

- FLUX bg crop-fits frame at native aspect (no letterboxing)
- Bottom gradient overlay starts at 40% height, alpha grows quadratically to 225 at bottom
- Title (180px scaled with width) bottom-left, 4px stroke
- Subtitle (48px scaled) immediately above CTA, light grey `#dce6f0` (220,230,240)
- Orange CTA (40px scaled) bottom-right
- Top-left brand mark: hex icon + PUREBRAIN.AI

### 3. CRITICAL gotcha — top-left brand mark legibility

**Problem**: When FLUX scene has bright highlights in the top-left (the resonance banner had a dispersing light-particle spray on the left side), the hex icon and wordmark get blown out and become unreadable.

**Failed fix**: Per-pixel falloff scrim using `point()` calls — too computationally slow AND too soft (alpha never high enough at the corner because of double-falloff math).

**Working fix**: Solid alpha rectangle scrim. Top 65% of scrim region at alpha=230 fully solid, then quadratic fade to 0. Right edge gets a separate fade band over the last 180px. Result: brand mark reads as if on a darkened pill but with a soft, organic edge that doesn't look slapped-on.

```python
# Top-left scrim — solid alpha box with vertical fade-out
scrim_h = int(170 * (h / 1260))
scrim_w_full = int(560 * (w / 2400))
for y in range(0, scrim_h):
    progress = y / scrim_h
    if progress < 0.65:
        alpha_y = 230
    else:
        alpha_y = int(230 * ((1 - progress) / 0.35) ** 1.4)
    sd.rectangle([(0, y), (scrim_w_full, y + 1)], fill=(8, 10, 18, alpha_y))
# Right-edge fade band (last 180px width)
fade_w = int(180 * (w / 2400))
fade_start = scrim_w_full - fade_w
for x in range(fade_start, scrim_w_full):
    x_progress = (x - fade_start) / fade_w
    for y in range(0, scrim_h):
        # ... fade alpha down to 0 with quadratic curve
```

### 4. Newsletter derivative auto-shrink

For 1200x630 newsletter version: title text "RESONANCE BEATS REACH" was clipping the right edge at the same scale.

Solution: pass `title_scale=0.85` to the composer AND add an iterative shrink loop:
```python
while t_w_px > avail and title_size > 60:
    title_size -= 4
    font_title = ImageFont.truetype(FONT_PATH, title_size)
    t_bbox = draw.textbbox((0, 0), title, font=font_title)
    t_w_px = t_bbox[2] - t_bbox[0]
```

### 5. FLUX prompt patterns that worked

- **Memory Tax (object dissolving in space)**: "Cinematic editorial product photograph of a translucent paper invoice... line items dissolving into glowing binary code at the edges, soft cyan blue light at color hex 2a93c1, dark void background hex 080a12, shallow depth of field, dust particles, no logos, no watermarks, no words, abstract dissolution, negative space dominant"
- **72-Hour Default (atmospheric object)**: "Cinematic close-up macro photograph of a vintage brass mechanical rotary timer or stopwatch face fixed at 72 hours, brushed metal dial with patina, soft warm orange glow at color hex f1420b emanating from the dial face... extreme bokeh, dust motes catching light, premium product photography"
- **Resonance (split metaphor)**: "Cinematic split composition wide horizontal banner: left third shows scattered chaotic dim grey light particles dispersing into static noise and dust, right two-thirds shows a single elegant metallic tuning fork resonating with clean glowing concentric rings emanating outward in cerulean blue at color hex 2a93c1"

Pattern: lead with "Cinematic" + photographic style, name brand colors with explicit "hex XXXXXX", end with "no logos, no watermarks, no words" + "negative space dominant".

## Repurpose pool result

Pool (`project_content_image_repurpose_pool.md`) is exclusively neural/consciousness aesthetic from Apr 5 Gleb training. None of the May 4 themes (invoice/timer/tuning fork) match. Generated all 4 fresh.

## Performance notes

- FLUX 1.1 Pro generation: ~6-10s per image, ~$0.04 each = ~$0.12 total for 3 generations
- PIL compositing: <1s per image
- Banner Option D pixel-by-pixel scrim v1: too slow (~3s for the per-pixel `point()` loop). Solid-alpha rectangles with separate fade band: <0.5s.
- Total batch wall time: ~90s including 12s rate-limit waits between FLUX calls.

## Self-review verdicts

All 4 outputs APPROVED via image-self-review skill. The Resonance banner required one iteration (scrim fix) before approval.

## Reusable assets

The `make_standalone_v4()` and `make_banner_option_d_v2()` functions in `exports/ma-img-2026-05-04/` are now reusable for any future MA# batch. Drop in a FLUX raw + title/cta/subtitle, get a brand-compliant LinkedIn asset.
