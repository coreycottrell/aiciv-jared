# Hunden Partners x PureBrain Sales Page Build
**Date**: 2026-03-02
**Type**: operational + pattern
**Topic**: Personalized AI sales page for destination real estate consulting firm

## What Was Built
- `/home/jared/projects/AI-CIV/aether/exports/hunden-partners-purebrain.html`
- 2,573 lines, ~73KB, fully self-contained single HTML file
- 10 sections matching the Graham Martin investor page design system

## Client Context
- Hunden Partners: destination real estate consulting firm, Chicago HQ
- CEO: Robin Scott Hunden (rob@hunden.com)
- 1,000+ studies, $25B+ projects, 8 service verticals, 4 offices
- Team: Rob Hunden (CEO), Jay Burress (EVP Tourism, ex-Visit Anaheim), Bethanie DeRose (EVP Consulting, ex-JLL)
- Notable projects: KC Power & Light, Navy Pier, Chicago Riverwalk, Fort Worth Stockyards

## Sections Built
1. Hero — PUREBRAIN for Hunden Partners, 4 hero stats
2. Opportunity — 4 opp cards (1,000+ studies, $25B+, 8 verticals, 4 offices) + problem box
3. What PureBrain Changes — 6 use case cards with domain-specific examples
4. Compounding Advantage — interactive canvas calculator (dual curve: Hunden vs competitor)
5. Competitive Moat — two-panel comparison (HVS/JLL/CBRE vs Hunden+PureBrain)
6. Implementation Roadmap — 4-phase timeline with phase dots and tags
7. ROI Projection — 4 metric cards (40% time reduction, 3x speed, $2M+, 50% capacity)
8. Why Now — 3 reason cards + urgency bar
9. Team — team cards for Rob, Jay, Bethanie
10. CTA — centered CTA with pulsing ring animation

## Interactive Calculator Details
- Two sliders: months (1-36) + historical studies (100-2000)
- Canvas draws: Hunden compound curve (blue solid) vs competitor curve (orange dashed, 12-month delay)
- Gap fill area between curves
- Cursor line + dots at selected month
- Advantage multiplier and data points processed shown in real time
- Competitor starts 12 months late at lower growth rate (generic tools)
- Force reveal at 100ms + IntersectionObserver (threshold: 0.01, rootMargin: 200px)

## Design System (Matches Graham Martin)
- CSS vars: --pb-dark #080a12, --pb-blue #2a93c1, --pb-orange #f1420b
- Glass-morphism cards with backdrop-filter blur(12px)
- Reveal animation: progressive enhancement — default visible, JS adds reveal-ready class
- Fixed nav with PUREBRAIN.ai branding + mailto CTA button
- Inter font from Google Fonts
- noindex, nofollow meta

## Key Differences from Graham Martin Page
- Single page (not multi-page mini-site)
- Roadmap uses vertical timeline with phase dots (not Graham's horizontal layout)
- Canvas calculator uses dual compound curves instead of bar charts
- Team section added as Section 9 (specific to Hunden's known team)

## Contact
- CTA mailto: jared@puretechnology.nyc
- Subject: "Hunden Partners — AI Discovery Call"
- Footer: rob@hunden.com listed as recipient context
