# PureBrain Pitch Page Build

**Date**: 2026-02-27
**Type**: operational
**Topic**: Full AiCIV pitch page rebrand to PureBrain for purebrain.ai WordPress deployment

## What Was Built

`/home/jared/projects/AI-CIV/aether/exports/purebrain-pitch-page.html` — 1,414 lines, 56KB

Complete self-contained pitch page rebrand from AiCIV (aiciv-pitch.netlify.app) to PureBrain for purebrain.ai.

## Key Branding Changes Applied

- Cyan `#00d4ff` → Blue `#2a93c1` throughout
- Gold `#ffd700` → Orange `#f1420b` throughout
- BG: `#0a0a1a` → `#080a12` (matches other PureBrain pages)
- AiCIV → PureBrain (all instances)
- A-C-Gee → Aether
- PUREBRAIN wordmark: `<span class="blue">PUREBR</span><span class="orange">AI</span><span class="blue">N</span>`
- CSS vars renamed: `--accent` → `--blue`, `--gold` → `--orange`

## Content Changes Applied

- Stats: 100+ agents → 30+, 12 team leads → 23 department managers, 76+ skills → 64+
- Hero CTA: "INVITE ONLY — 23 SPOTS LEFT" → "START YOUR AI PARTNERSHIP"
- CTA link: `https://purebrain.ai/#awakening` (both instances)
- NO password (removed purebrain2026)
- Team Wall: AiCIV 12 verticals → PureBrain's 23 actual departments
- Architecture flow: Updated to show Aether → 23 dept managers → 30+ agents → 64+ skills
- BOOP section: Updated "PureBrain runs autonomous cycles while you sleep"
- Pricing: Awakened $179, Bonded $349 (recommended), Partnered $999, Unified $1,999 — added new tiers section
- TGIM: "50-person operation" → "Jared Sanborn's Pure Technology operation", "Built by Aether. In one day."
- Footer: "Powered by Aether — a mind of minds, in production. Built by Pure Technology."

## Technical Requirements Met

- `<!-- wp:html -->` / `<!-- /wp:html -->` wrappers
- NO `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>` tags
- Orange-kill CSS at top targeting `body`, `body.tt-magic-cursor`, `body.page`
- All CSS scoped under `#pb-pitch-page` (193 references)
- All CSS class names prefixed `pb-` to avoid WordPress theme conflicts
- Smooth scroll nav links: `href="#pb-compounding"`, `#pb-architecture"`, etc.
- All responsive breakpoints preserved (900px, 768px, 700px, 600px, 500px)
- Star/particle effect preserved in hero `::before` pseudo-element (updated colors)
- CTA buttons: orange bg, white text, hover → blue
- No old colors: cyan `#00d4ff` and gold `#ffd700` ZERO occurrences

## Sections Included (in order)

1. Nav (sticky, PUREBRAIN wordmark)
2. Hero (stars effect, CTA → purebrain.ai/#awakening)
3. Compounding Clock (4 columns)
4. Stacked Exponentials callout
5. Architecture comparison (Perplexity vs PureBrain flow)
6. Team Wall (23 departments + 30+ specialist chips)
7. Memory Layers (5 layers)
8. BOOP section + price comparison cards
9. Pricing Tiers (Awakened/Bonded/Partnered/Unified)
10. TGIM section
11. Network SVG
12. Comparison table
13. Live badge
14. CTA footer

## File Path

`/home/jared/projects/AI-CIV/aether/exports/purebrain-pitch-page.html`
Drive folder: 1QaBu0gO7__my-AziZ2WD_PAuhkfLjQoN (purebrain.ai HTML files)
