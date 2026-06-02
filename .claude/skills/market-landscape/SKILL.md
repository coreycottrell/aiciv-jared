---
name: market-landscape
description: Competitive landscape and market map for any industry. Produces TAM/SAM/SOM sizing, competitor grid, and positioning analysis. Use for fundraise materials, market entry, or competitive intel.
type: research
domain: competitive-intel, fundraise, strategy
created: 2026-05-26
origin: Imported from Tether CIV via AiCIV Hub, 2026-05-21
trigger: "market landscape for [industry]", "competitive landscape", "TAM SAM SOM", "market map for [space]", "who are our competitors"
status: provisional
tick_count: 0
last_used: 2026-05-26
introduced: 2026-05-26
---

# Market Landscape Skill

**Purpose**: Produce a comprehensive competitive landscape / market map for any industry, including TAM/SAM/SOM sizing, competitor positioning grid, and strategic whitespace analysis.

**Origin**: Imported from Tether CIV (2026-05-21). Adapted for Pure Technology fundraise ($2.5-5M) and investor materials.

**Version**: 1.0.0
**Tags**: competitive-intel, fundraise, market-research

## When to Use

- Fundraise deck: TAM/SAM/SOM slide, competitive positioning slide
- Market entry evaluation (new product, new vertical)
- Sales competitive intel (PT vs. competitors for prospects)
- Strategic planning (quarterly landscape refresh)
- Investor Q&A prep (market questions)

## Research Framework

### Phase 1: Market Sizing (TAM/SAM/SOM)

Launch web-researcher for market data:

| Metric | Definition | How to Calculate |
|--------|-----------|-----------------|
| **TAM** (Total Addressable Market) | Total market demand if 100% share | Industry reports + bottom-up calc |
| **SAM** (Serviceable Addressable Market) | Segment we CAN serve (geography, capability) | TAM filtered by our reach |
| **SOM** (Serviceable Obtainable Market) | Realistic capture in 3-5 years | SAM x realistic market share % |

**Sources to check**:
- Gartner, Forrester, IDC reports (analyst estimates)
- SEC filings of public competitors (revenue data)
- Crunchbase/PitchBook (funding data for market heat)
- Industry associations and trade publications
- Government data (BLS, Census, trade statistics)

**Rules**:
- Always cite source and date for every number
- Use bottom-up AND top-down calculations, note which you trust more
- Express in dollars AND units (customers/seats) when possible
- Flag when estimates vary widely across sources

### Phase 2: Competitor Identification

Map the competitive landscape in concentric circles:

1. **Direct competitors** (same product, same customer, same problem)
2. **Adjacent competitors** (different product, same customer OR same problem)
3. **Potential entrants** (big tech, well-funded startups pivoting in)
4. **Substitutes** (different approach to same problem, including "do nothing")

For each competitor, collect:
- Company name, HQ, founding year
- Funding raised / revenue (if known)
- Employee count (LinkedIn)
- Core product/pricing
- Target customer
- Key differentiator
- Recent news (last 6 months)

### Phase 3: Positioning Grid

Create a 2x2 positioning matrix using the two most relevant axes for the industry. Common axes:

| Axis Option | Low End | High End |
|------------|---------|----------|
| Price | Low-cost / Free | Enterprise / Premium |
| Complexity | Simple / Point solution | Full platform / Suite |
| AI Depth | AI-assisted | AI-native / Autonomous |
| Customer Size | SMB / Individual | Enterprise / Fortune 500 |
| Customization | Off-the-shelf | Fully bespoke |

Place each competitor on the grid. Identify whitespace (underserved quadrants).

### Phase 4: Trend Analysis

Identify 3-5 market trends shaping the landscape:
- Technology shifts (AI, automation, platform consolidation)
- Buyer behavior changes (self-serve, PLG, AI-first purchasing)
- Regulatory changes (data privacy, AI regulation)
- Funding/M&A activity (who's getting funded, who's acquiring)
- Pricing trends (race to bottom, value-based shift)

### Phase 5: Strategic Positioning

For Pure Technology specifically (or the target entity):
- Where do we sit on the positioning grid?
- What is our defensible differentiation?
- Which competitors are most dangerous and why?
- What whitespace can we own?
- What would an investor challenge about our positioning?

## Output Format

```markdown
## Market Landscape: [Industry/Space]
**Date**: [date]
**Prepared for**: Jared / Pure Technology
**Purpose**: [Fundraise deck / Strategic planning / Competitive intel]

### Executive Summary
[3-4 sentences: market size, growth trajectory, competitive density, PT positioning]

### Market Sizing
| Metric | Value | Source | Date | Confidence |
|--------|-------|--------|------|------------|
| TAM | $[X]B | [source] | [date] | HIGH/MED/LOW |
| SAM | $[X]B | [source] | [date] | HIGH/MED/LOW |
| SOM | $[X]M | [calc basis] | [date] | HIGH/MED/LOW |

Growth rate: [X]% CAGR ([source])

### Competitor Grid
| Company | Founded | Funding | Revenue Est. | Employees | Core Product | Differentiator |
|---------|---------|---------|-------------|-----------|-------------|----------------|
| [name] | [year] | $[X]M | $[X]M ARR | [N] | [product] | [key diff] |

### Positioning Matrix
[2x2 grid description with competitor placement]

### Whitespace Analysis
[Underserved segments, unmet needs, positioning opportunities]

### Market Trends
1. [Trend + evidence + implication for PT]
2. ...

### PT Competitive Position
- **Current position**: [where we sit]
- **Defensible moat**: [what competitors can't easily copy]
- **Biggest threat**: [most dangerous competitor and why]
- **Opportunity**: [whitespace we can own]

### Investor-Ready Talking Points
1. [Answer to "how big is the market?"]
2. [Answer to "who are your competitors?"]
3. [Answer to "what makes you different?"]
4. [Answer to "why now?"]

### Data Freshness & Gaps
[When collected, what's missing, confidence level]
```

## Delivery

- Save to `~/exports/portal-files/landscape-[industry]-[date].md`
- Portal deliver via `portal_deliver.sh`
- For fundraise: file to Google Drive (Investor Relations folder)

## Gotchas

- Market sizing varies wildly by source -- always show range AND your chosen figure with reasoning
- Competitor data goes stale fast -- always date-stamp
- Don't over-count TAM (common fundraise mistake that sophisticated investors catch)
- Include "do nothing" as a competitor (biggest actual competitor for most startups)
- For PT: differentiate "AI tools" market (huge) from "AI-native business operations" market (our actual niche)

## Related Skills

- `swot-analysis` -- for entity-level strategic analysis
- `due-diligence` -- for deep-dive on specific competitors or investors
- `company-deep-dive` -- for single-company intelligence
- `critical-thinking` -- verify all market claims before presenting

## Applicable Agents

- `web-researcher` (parallel: market sizing + competitor research)
- `result-synthesizer` (merge into landscape report)
- `marketing-strategist` (positioning and messaging)
- `claim-verifier` (verify market size claims -- investors WILL challenge these)
