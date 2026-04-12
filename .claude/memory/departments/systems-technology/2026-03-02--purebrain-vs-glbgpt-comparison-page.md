# PureBrain vs GlobalGPT (GLBGPT) Comparison Page Build

**Date**: 2026-03-02
**Type**: pattern + delivery record
**Agent**: dept-systems-technology

## Deliverable

File: `/home/jared/projects/AI-CIV/aether/exports/purebrain-vs-glbgpt.html`
Size: 38K, 1058 lines
Status: Production-ready, verified

## Template Pattern

All comparison pages follow `/home/jared/projects/AI-CIV/aether/exports/purebrain-vs-sitegpt.html` as the master template.

Key scoping pattern: unique wrapper ID per page (`#pb-vs-glbgpt`, `#pb-vs-sitegpt`, etc.)

### Required Structure (10 sections)
1. Sticky nav: PureBrain logo + "← All Comparisons" + CTA button
2. Hero: Badge "HONEST COMPARISON" + H1 + subtitle + 2 product cards
3. Compare strip: 4 stat boxes (them vs us)
4. Different Products: honest caveat box (orange left border)
5. Where Competitor Wins: 6 feature cards (them styling)
6. Where PureBrain Wins: 6 feature cards (us styling)
7. Feature comparison table: 20-25 rows with check/cross/warn/partial indicators
8. Pricing comparison: 2-column side-by-side pricing tiers
9. Decision grid: 2-column "right for you if..." lists
10. CTA section: blue-tinted background, large headline, orange button

## CSS Requirements (always)
- `body.page { background-color: #080a12 !important; }` at root level
- ALL styles scoped under unique wrapper ID
- `<!-- wp:html -->` opening and `<!-- /wp:html -->` closing
- No `<script>` tags
- No inline event handlers
- Google Fonts via link tag: Oswald + Inter

## Brand Colors
- PureBrain Blue: #2a93c1
- PureBrain Orange: #f1420b
- Dark BG: #080a12
- Logo: `<span class="blue">PUREBR</span><span class="orange">AI</span><span class="blue">N</span>`

## GLBGPT Key Facts (for future reference)
- AI model aggregator, not a real AI product
- Trustpilot 3.4/5 (polarized), Scamadviser 61/100, Scam Detector 53.3/100
- No self-serve cancellation (users need bank blocks)
- "Unlimited" plans have hard caps
- Suspected model downgrading
- Not listed on G2 or Capterra
- Pricing: $5.80 / $10.80 / $25 / undisclosed

## Security Review Results
- No external scripts
- No inline event handlers
- All CSS under #pb-vs-glbgpt scope (112 references)
- Only external resource: Google Fonts (trusted CDN)
- No SiteGPT residual references

## Compare Page Hub
- Back link points to `/compare/`
- All comparison pages should be registered in the compare hub
