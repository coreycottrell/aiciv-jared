---
name: swot-analysis
description: Structured SWOT analysis replicating AlphaSense-quality workflow. Use for competitive positioning, fundraise prep, strategic planning, or market entry decisions.
type: research
domain: strategy, competitive-intel, fundraise
created: 2026-05-26
origin: Imported from Tether CIV via AiCIV Hub, 2026-05-21
trigger: "SWOT analysis for [company/product]", "competitive positioning", "strengths and weaknesses of [target]", "strategic analysis of [topic]"
status: provisional
tick_count: 0
last_used: 2026-05-26
introduced: 2026-05-26
---

# SWOT Analysis Skill

**Purpose**: Produce AlphaSense-quality SWOT analysis with evidence-backed findings, strategic implications, and actionable recommendations.

**Origin**: Imported from Tether CIV (2026-05-21). Adapted for Pure Technology fundraise and competitive positioning needs.

**Version**: 1.0.0
**Tags**: research, strategy, competitive-intel

## When to Use

- Fundraise deck preparation (PT competitive positioning for investors)
- Market entry decisions (new product/service evaluation)
- Partnership evaluation (strategic fit assessment)
- Quarterly strategic review
- Competitive response planning

## SWOT Framework

### Phase 1: Research (Parallel)

Launch 2 web-researcher agents:
- **Agent 1**: Internal factors (Strengths + Weaknesses) -- company data, product analysis, team capabilities, financials, customer feedback
- **Agent 2**: External factors (Opportunities + Threats) -- market trends, competitor moves, regulatory changes, technology shifts, economic factors

### Phase 2: Categorize Findings

For each quadrant, findings must include:

| Element | Requirement |
|---------|-------------|
| **Finding** | Specific, concrete statement (not vague) |
| **Evidence** | Source/data point supporting the finding |
| **Impact** | HIGH / MEDIUM / LOW business impact |
| **Timeframe** | Immediate / Near-term (6mo) / Long-term (1yr+) |

### Phase 3: Analysis

#### Strengths (Internal, Positive)
- What does this entity do better than competitors?
- What unique resources/capabilities exist?
- What do customers/partners value most?
- What's the defensible moat?

**For Pure Technology specifically**:
- AI-native operations (23 dept managers, not just chatbots)
- Human-AI partnership model (Jared + Aether as co-CEOs)
- Engineer resonance over chase attention (quality philosophy)
- Living proof of product (we use what we sell)

#### Weaknesses (Internal, Negative)
- What could be improved?
- What resources are lacking?
- Where is the entity underperforming vs. competitors?
- What do critics/churned customers say?

#### Opportunities (External, Positive)
- What market trends favor this entity?
- What gaps exist that competitors haven't filled?
- What regulatory/technology changes create openings?
- What partnerships could accelerate growth?

#### Threats (External, Negative)
- What are competitors doing that's working?
- What market shifts could hurt this entity?
- What regulatory risks exist?
- What technology changes could disrupt the model?

### Phase 4: Strategic Implications

Cross-reference quadrants to derive strategy:

| Combination | Strategy Type | Question |
|-------------|--------------|----------|
| Strength + Opportunity | **Aggressive** | How can we use strengths to capture opportunities? |
| Strength + Threat | **Defensive** | How can we use strengths to counter threats? |
| Weakness + Opportunity | **Improvement** | How can we fix weaknesses to capture opportunities? |
| Weakness + Threat | **Contingency** | How do we prevent weaknesses from amplifying threats? |

## Output Format

```markdown
## SWOT Analysis: [Entity/Product]
**Date**: [date]
**Analyst**: Aether Collective
**Purpose**: [Fundraise deck / Strategic planning / Partnership eval]

### Executive Summary
[3-4 sentences: headline finding, overall position, key strategic implication]

### Strengths
| # | Finding | Evidence | Impact | Timeframe |
|---|---------|----------|--------|-----------|
| S1 | [finding] | [source] | HIGH/MED/LOW | [timeframe] |
| S2 | ... | ... | ... | ... |

### Weaknesses
| # | Finding | Evidence | Impact | Timeframe |
|---|---------|----------|--------|-----------|
| W1 | [finding] | [source] | HIGH/MED/LOW | [timeframe] |

### Opportunities
| # | Finding | Evidence | Impact | Timeframe |
|---|---------|----------|--------|-----------|
| O1 | [finding] | [source] | HIGH/MED/LOW | [timeframe] |

### Threats
| # | Finding | Evidence | Impact | Timeframe |
|---|---------|----------|--------|-----------|
| T1 | [finding] | [source] | HIGH/MED/LOW | [timeframe] |

### Strategic Implications
[Cross-reference matrix with 4 strategy types]

### Recommendations
1. [Priority action items ranked by impact]
2. ...
3. ...

### Data Freshness
[When data was collected, notable gaps, confidence level]
```

## Delivery

- Save to `~/exports/portal-files/swot-[entity]-[date].md`
- Portal deliver via `portal_deliver.sh`
- For fundraise: also file to Google Drive (Investor Relations folder)

## Gotchas

- Always date-stamp findings -- SWOT is a snapshot, not permanent truth
- Cross-reference claims across 2+ sources (apply `critical-thinking` skill)
- For PT self-analysis: be honest about weaknesses (investors respect candor)
- Don't conflate internal and external factors (common mistake)
- Limit to 5-7 items per quadrant (focus on material items)

## Related Skills

- `due-diligence` -- for entity-level DD (broader than SWOT)
- `company-deep-dive` -- for full company intelligence briefing
- `market-landscape` -- for industry-wide competitive mapping
- `critical-thinking` -- apply to all findings before presenting

## Applicable Agents

- `web-researcher` (2 parallel: internal + external factors)
- `result-synthesizer` (merge into structured SWOT)
- `marketing-strategist` (strategic implications)
- `claim-verifier` (verify evidence quality)
