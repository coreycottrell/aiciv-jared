# MA# Campaign Memory: Something Big Banner

**Date**: 2026-03-04
**Request Type**: Urgent blog banner generation
**Status**: COMPLETE — delivered to Telegram

---

## Objective

Generate a blog banner (1200x630 OG format) for Aether's response post to Matt Shumer's
"Something Big Is Happening." Blog title: "Something Big Already Happened — You Just
Weren't Invited Yet"

## Files Delivered

- **Banner**: `/home/jared/projects/AI-CIV/aether/exports/blog-something-big/banner.png`
- **OG image**: `/home/jared/projects/AI-CIV/aether/exports/blog-something-big/og.png`
- **Generator script**: `/home/jared/projects/AI-CIV/aether/exports/blog-something-big/generate_banner.py`

Both files: 1200x630px, RGB PNG, ~244-261 KB.

## Visual Design

- Dark deep-space background (#080a12)
- Rising sigmoid inflection curve spanning the image (represents the AI inflection point)
- Orange glowing dot + upward arrow at the inflection point (~60% x-axis)
- Neural network nodes with connecting lines scattered around center safe zone
- Glow orbs in PT Blue + PT Orange at corners and edges
- Title: two-line centered text — line 1 white, line 2 PT Blue (#2a93c1)
- Kicker text above title in muted gray
- PureBrain.ai brand mark bottom-left with icon + color-coded PUREBR(blue)AI(orange)N(blue).ai(white)

## Method Used

Python PIL (no matplotlib needed). Script at:
`exports/blog-something-big/generate_banner.py`

## Patterns / Learnings

- Additive glow orb technique from v3 memory banner generator works reliably at 1200x630
- Sigmoid curve (math.exp / 1+exp formula) creates excellent inflection point visual
- Arrow-at-inflection: draw.line at -0.55 radian angle from inflection point
- Center safe zone skip in neural network node generation prevents text collision
- PureBrain icon at `docs/assets/logos/purebrain-icon.png` — 40x40 works for this scale
- DejaVu Sans Bold reliably available on this system
- Title split into two lines at ~32 chars each reads cleanly at 62pt

## Telegram Delivery

Sent via `./tools/tg_send.sh --photo` — confirmed OK, message_id 18574.
