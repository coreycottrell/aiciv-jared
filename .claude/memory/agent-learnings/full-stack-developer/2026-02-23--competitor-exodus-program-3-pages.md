# Competitor Exodus Program — 3 Landing Pages Built

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

Three self-contained HTML landing pages for competitor refugees. Part of Surprise & Delight V5 Item #2.

## Files

- `/home/jared/projects/AI-CIV/aether/exports/competitor-exodus-chatgpt.html` (36K)
- `/home/jared/projects/AI-CIV/aether/exports/competitor-exodus-copilot.html` (37K)
- `/home/jared/projects/AI-CIV/aether/exports/competitor-exodus-jasper.html` (38K)

## WordPress Deployment Slugs

- `switching-from-chatgpt`
- `switching-from-copilot`
- `switching-from-jasper`

## Architecture Pattern

Each page follows identical structural pattern:
1. Colored strip: competitor brand color → PureBrain blue (gradient at top)
2. Sticky nav with PureBrain logo + CTA button
3. Hero with competitor-specific headline + stats
4. Pain section with 3 quote cards (competitor brand color tint)
5. Optional unique section (pain-cards / lock-in breakdown / content ceiling)
6. 3-question quiz with vanilla JS state management
7. Email gate (POST to `https://purebrain.ai/wp-json/purebrain/v1/guide-unlock`)
8. Personalized results (4 personas per page, Q1 answer drives result)
9. CTA block (shown after quiz completion via #results-container .visible)
10. Comparison table
11. Footer

## Brand Color Differentiation Per Page

| Page | Competitor Color | Usage |
|------|-----------------|-------|
| ChatGPT | `#10a37f` (green) | Badge, section labels, pain cards, gradient strip |
| Copilot | `#7c4dff` (purple) | Badge, section labels, pain cards, gradient strip |
| Jasper | `#f5a623` (yellow/amber) | Badge, section labels, pain cards, gradient strip |

## Quiz Architecture

- 3 questions per page, each with 4 options (A/B/C/D)
- State stored in `answers` object: `{ q1: 'value', q2: 'value', q3: 'value' }`
- Q1 answer drives the personalized result persona (Q2/Q3 collected but used for future segmentation)
- 4 personas per page, each with title + desc + 3 capability items
- Completion: gate step → email form → `showResults()` → persona render

## Email Gate Pattern

- Endpoint: `POST https://purebrain.ai/wp-json/purebrain/v1/guide-unlock`
- Payload: `{ email: "...", first_name: "..." }` (first_name optional)
- Adds to Brevo List 3 (The Neural Feed)
- **Generous gate**: If fetch fails (CORS, network), `showResults()` is still called — user never blocked
- Uses same endpoint as AI Partnership Guide gate (v4.1.0 plugin)

## WordPress Deployment Method

Self-contained HTML (inline CSS + JS). Can be deployed as:
- Elementor HTML widget on blank-canvas page
- Custom page via WP REST API (purebrain.ai = elementor_canvas, jareddsanborn.com = page-template-blank.php)

## Key Design Decisions

1. **Persona driven by Q1** (primary frustration) — most predictive of what they need to hear
2. **Generous gate** — never block users even if Brevo call fails. Email capture is secondary to conversion.
3. **Results + CTA visible together** — `#results-container` reveals CTA section below quiz when results shown
4. **Scroll behavior** — each transition scrolls the next step into view smoothly
5. **Progress dots** — 3 dots: active=orange, done=blue, upcoming=muted white

## Patterns Learned

1. **Competitor color as "before" signal** — using the competitor's brand color for the "old" state creates visual narrative of transition without needing explicit comparison copy
2. **Generous gate pattern** — `try/catch` with `showResults()` in catch ensures 0% gate failure rate for users; email capture becomes best-effort, not user-blocking
3. **Quiz persona architecture** — driving result from Q1 (frustration) rather than all 3 answers together produces more coherent, resonant results. Q2/Q3 can be sent to CRM for deeper segmentation later.
4. **4 persona per competitor** — covers the full frustration space without over-engineering. Each persona addresses a different root cause.
