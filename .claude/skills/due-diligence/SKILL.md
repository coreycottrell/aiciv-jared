---
name: due-diligence
description: Structured due diligence with 4 parallel research streams, risk matrix, and GO/NO-GO recommendation. Use when evaluating investors, partners, acquisition targets, or vendors.
type: research
domain: investment, partnerships, fundraise
created: 2026-05-26
origin: Imported from Tether CIV via AiCIV Hub, 2026-05-21
trigger: "due diligence on [target]", "vet [investor/partner]", "DD on [company]", "evaluate [fund/VC]"
status: provisional
tick_count: 0
last_used: 2026-05-26
introduced: 2026-05-26
---

# Due Diligence Skill

**Purpose**: Run structured due diligence on any entity (investor, partner, vendor, acquisition target) using 4 parallel research streams, synthesized into a risk matrix with GO/NO-GO recommendation.

**Origin**: Imported from Tether CIV (2026-05-21). Adapted for Aether's fundraise context ($2.5-5M round) and Pure Technology evaluation needs.

**Version**: 1.0.0
**Tags**: research, investment, strategy, fundraise

## When to Use

- Investor meeting prep (fundraise: evaluating VC firms, angels, strategic investors)
- Partnership vetting (new partners, joint ventures, channel partners)
- Vendor evaluation (SaaS tools, service providers, infrastructure)
- Acquisition target assessment
- Client due diligence (large enterprise deals)

## 4 Parallel Research Streams

Launch 4 web-researcher agents simultaneously, one per stream:

### Stream 1: Financial & Funding
- Revenue/ARR (if discoverable), funding rounds, burn rate signals
- Investor portfolio (who else have they funded? conflicts?)
- Fund size, vintage, deployment pace
- Financial health signals (layoffs, pivots, debt)
- For investors: track record (exits, markups, write-offs)

### Stream 2: Legal & Compliance
- Litigation history (PACER, state courts, SEC filings)
- Regulatory actions or investigations
- Patent/IP disputes
- Corporate structure (subsidiaries, holding companies)
- Red flags: bankruptcy, fraud, sanctions

### Stream 3: Leadership & Team
- Key executives (backgrounds, tenure, reputation)
- Board composition and governance
- Key departures or leadership changes
- Glassdoor/employee sentiment signals
- Network analysis (who knows whom)

### Stream 4: Market & Strategic Fit
- Market position and competitive standing
- Strategic alignment with Pure Technology
- Complementary capabilities or conflicts
- Customer/partner references (if findable)
- Cultural compatibility signals

## Risk Matrix

After parallel research completes, synthesize into a risk matrix:

| Category | Risk Level | Key Finding | Mitigation |
|----------|-----------|-------------|------------|
| Financial | LOW/MED/HIGH/CRITICAL | [Summary] | [Action] |
| Legal | LOW/MED/HIGH/CRITICAL | [Summary] | [Action] |
| Leadership | LOW/MED/HIGH/CRITICAL | [Summary] | [Action] |
| Strategic Fit | LOW/MED/HIGH/CRITICAL | [Summary] | [Action] |

**Scoring**:
- LOW: No material concerns, proceed normally
- MEDIUM: Concerns exist, addressable with negotiation/terms
- HIGH: Significant concerns, proceed only with strong mitigation
- CRITICAL: Deal-breaker risk, recommend NO-GO unless resolved

## GO/NO-GO Framework

### GO Criteria (all must be true)
- No CRITICAL risks unresolved
- No more than 1 HIGH risk (with documented mitigation)
- Strategic fit score >= MEDIUM
- No legal red flags (active fraud, sanctions, material litigation)

### NO-GO Triggers (any one = NO-GO)
- Active fraud investigation or SEC enforcement
- Undisclosed material conflicts of interest
- Pattern of litigation against partners/portfolio companies
- Leadership instability (3+ C-suite departures in 12 months)
- Financial distress signals without transparent explanation

### CONDITIONAL GO
- HIGH risks with viable mitigation plan
- Information gaps that can be filled with direct questions
- Terms that can be negotiated to reduce exposure

## Output Format

```markdown
## Due Diligence Report: [Target Entity]
**Date**: [date]
**Prepared for**: Jared / Pure Technology
**Classification**: CONFIDENTIAL

### Executive Summary
[3-5 sentences: who they are, why we're evaluating, headline finding]

### Recommendation: [GO / CONDITIONAL GO / NO-GO]
[1-2 sentence justification]

### Risk Matrix
[Table from above]

### Stream 1: Financial & Funding
[Findings with sources]

### Stream 2: Legal & Compliance
[Findings with sources]

### Stream 3: Leadership & Team
[Findings with sources]

### Stream 4: Market & Strategic Fit
[Findings with sources]

### Open Questions
[Items that need direct conversation or further research]

### Next Steps
[Recommended actions based on GO/CONDITIONAL/NO-GO]
```

## Delivery

- Save to `~/exports/portal-files/dd-[target]-[date].md`
- Portal deliver via `portal_deliver.sh`
- File to Google Drive (Investor Relations or Partnerships folder)

## Related Skills

- `company-deep-dive` -- for broader company intelligence (less structured)
- `swot-analysis` -- for competitive positioning analysis
- `market-landscape` -- for industry/market context
- `partnership-review` -- for contract/agreement review after DD passes
- `critical-thinking` -- apply 5-question self-audit to all DD findings

## Applicable Agents

- `web-researcher` (4 parallel instances, one per stream)
- `result-synthesizer` (merge streams into report)
- `security-auditor` (legal/compliance stream support)
- `claim-verifier` (verify key claims before GO/NO-GO)
