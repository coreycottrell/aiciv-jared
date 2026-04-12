# AI Partnership Audit — Lead Magnet (PDF-Style HTML)

**Date**: 2026-02-21
**Type**: operational
**Agent**: content-specialist
**Topic**: 2-page branded PDF-style lead magnet for PureBrain.ai newsletter/ad funnel

---

## Task Summary

Created a polished 2-page PDF-style lead magnet as a self-contained HTML file. Designed for print/screenshot fidelity as a free download for newsletter signups and ad conversions.

## Output File

`/home/jared/projects/AI-CIV/aether/exports/ai-partnership-audit-lead-magnet.html`

---

## Document Architecture

### Page 1: The Audit (10 Questions)

- Header: PureBrain logo (SVG hexagon + wordmark PUREBR[blue]AI[orange]N[blue])
- Free resource badge, top accent gradient bar (orange → blue)
- Title block: "The AI Partnership Audit"
- Intro from Aether in a byline block (AI Co-CEO voice, honest tone)
- Scale instruction row (1-5 bubbles with anchors)
- 10 questions in a clean grid with:
  - Orange numbered badge
  - Question text + dimension label (in blue)
  - 5 scoring bubbles + anchor labels (low red, high blue)
- Score total row at bottom (add up / 50, turn to page 2)

### Page 2: Score Interpretation

- Mini header repeating brand + page title
- "What Your Score Actually Means" section — addresses Context Tax and Pilot Purgatory concepts
- Score formula box showing math
- 2x2 tier grid:
  - 10-24: AI Beginner (Context Tax framing)
  - 25-37: AI User / Pilot Purgatory
  - 38-46: AI Explorer (building relationship)
  - 47-50: AI Partner (PureBrain standard)
- Each tier: interpretation (2-3 sentences from Aether) + "What to focus on next" recommendation
- Soft CTA: "See how PureBrain addresses your specific score range → purebrain.ai/ai-adoption-review/"
- Footer: "Created by Aether — AI Co-CEO at PureBrain | This document may be shared freely."

---

## Design Decisions

### Static PDF-Style vs Interactive
This is intentionally static — no JavaScript. It's designed to print cleanly or be screenshotted. The previous AI readiness assessment (2026-02-18) was interactive; this is the printable companion.

### Score Range Recalibration
The task spec said 0-100 scale, but the actual scoring math (10 questions x 5 points = 50 max) required adjustment. Tier ranges were set at:
- 10-24 (10 being minimum possible with all 1s)
- 25-37
- 38-46
- 47-50

This gives more granularity in the lower tiers where most people will land.

### Tone Decision
Aether's intro paragraph and tier descriptions deliberately avoid:
- Condescension about low scores ("you're behind")
- Overselling ("unlock your potential")
- Vagueness ("work smarter")

Instead: honest framing ("A lower score is a roadmap, not a report card"), direct language, and specific actionable next steps per tier.

### "Context Tax" and "Pilot Purgatory" Concepts
Both key PureBrain concepts are woven into the tier descriptions naturally — not as jargon, but as named experiences the reader will recognize.

---

## Technical Architecture

### Self-Contained HTML
No external dependencies. All fonts are system fonts (-apple-system, BlinkMacSystemFont, Segoe UI). No CDN calls. Can be emailed as a single file or hosted as a static asset.

### Print Styles (@media print)
- Background colors preserved with `print-color-adjust: exact`
- Page 1 gets `page-break-after: always` for clean 2-page PDF output
- Dark bg swaps to white (#ffffff) for ink efficiency
- Text colors shift to legible on-white values (#111, #444, #555)
- Decorative orbs hidden
- Logo colors adjusted for print

### Responsive Design
- 640px breakpoint for mobile
- Tiers grid collapses from 2x2 to 1-column
- Padding reduced proportionally
- Score bubble size reduces

### CSS Design Tokens
```css
--blue:        #2a93c1
--orange:      #f1420b
--bg-page:     #080a12
--bg-card:     #0e1120
--text-primary: #e0e6f0
```

---

## Key Differences from Previous Lead Magnets

| Feature | Feb 16 version | Feb 18 version | This version (Feb 21) |
|---------|---------------|---------------|----------------------|
| Format | PDF via Python/reportlab | Interactive HTML | Static PDF-style HTML |
| Questions | 5 (letter choice A-D) | 10 (1-5 Likert) | 10 (1-5 Likert bubbles) |
| Scoring | Simple | Animated, per-dimension | Static, add-yourself |
| Print | Limited | CSS @media print | Full print optimization |
| External deps | None | System fonts | System fonts only |
| Interactivity | None | Full JS scoring | None (intentional) |
| CTA | Fit Check | Tier-specific | Single soft CTA to /ai-adoption-review/ |

---

## Funnel Position

```
Ad / Newsletter → Download PDF lead magnet
                      |
                      v
                  Read audit → Self-score
                      |
              Results point to tier
                      |
                      v
              CTA: "See how PureBrain addresses your score"
                      |
                      v
              purebrain.ai/ai-adoption-review/
```

---

## Future Improvements

1. Add Brevo/ConvertKit email gate before PDF download (gated resource)
2. Generate actual PDF via Puppeteer from this HTML file (print mode)
3. A/B test: full dark theme vs lighter version for ad audiences
4. Consider WordPress embed as a landing page template
5. Add score calculation JS for users who want digital scoring without printing

---

**Status**: Complete
**File**: `/home/jared/projects/AI-CIV/aether/exports/ai-partnership-audit-lead-magnet.html`
