# Banner: Stop Treating Your AI Like an Intern

**Date**: 2026-02-27
**Type**: operational
**Agent**: full-stack-developer

## Task
Generated blog banner image for "Stop Treating Your AI Like an Intern — It's Your Senior Partner"

## Output
- **File**: `/home/jared/projects/AI-CIV/aether/to-jared/overnight/stop-treating-your-ai-like-an-intern - banner.png`
- **Size**: 1200x630px (~94KB PNG)

## Design Approach
- Dark gradient background (#0a1628 → #162a4a)
- Hexagonal grid pattern (faint PT Blue) across full canvas
- Neural network dots/lines (random.seed(42) for determinism)
- Orange glow orb top-right, blue glow orb bottom-left
- Top + bottom gradient bars (orange-to-blue)
- Title line 1: "Stop Treating Your AI" — white bold
- Title line 2: "Like an" white + "Intern" PT Orange (#f1420b) — key word highlighted
- Orange separator rule between title and subtitle
- Subtitle: "It's Your Senior Partner" — light blue-white
- Category tag: "AI LEADERSHIP | PUREBRAIN.AI"
- PureBrain logo: "PUREBR" PT Blue + "AI" PT Orange + "N" PT Blue + ".ai" near-white lowercase

## Key Pattern: Logo Color Split
The PUREBRAIN logo MUST be split into individual text segments drawn at calculated x positions:
```python
logo_parts = [
    ("PUREBR", PT_BLUE, font_logo),
    ("AI", PT_ORANGE, font_logo),
    ("N", PT_BLUE, font_logo),
    (".ai", (210, 230, 245), font_logo_dot),
]
# Measure each part width, accumulate x position
```
Drawing entire word as one string then recoloring doesn't work in PIL — must draw each colored segment separately.

## Font Used
Ubuntu-Bold.ttf (68px title, 44px subtitle, 36px logo)
Ubuntu-R.ttf (30px logo .ai suffix, 20px tag)

## Safe Margins
60px from all edges respected. Text stays well within mobile-safe zone.
