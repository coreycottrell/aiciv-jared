---
status: provisional
tick_count: 0
last_used: 2026-05-22
introduced: 2026-05-22
---
# Company Deep Dive

**Purpose**: Produce full company intelligence briefing using parallel research agents, compiled into structured markdown + portal delivery.

**Origin**: Imported from Tether CIV (2026-05-21). Adapted for Aether's portal-first delivery and Pure Technology context.

**Version**: 1.0.0
**Tags**: research, due-diligence, competitive-intel
**Triggers**: "research [company]", "deep dive on [company]", "company briefing [company]"

## When to Use

- Investor meeting prep (fundraise context: $2.5-5M round)
- Partnership evaluation (Cynora, new vendors)
- Competitive positioning research
- Client/prospect intelligence

## Steps

1. **Decompose** target company into research dimensions:
   - Financials (revenue, funding, burn rate)
   - Product (features, tech stack, pricing)
   - Team (leadership, key hires, departures)
   - Market (position, competitors, TAM)
   - News (recent PR, legal, M&A signals)

2. **Parallel Research** (5 web-researcher agents):
   - Each dimension gets its own agent
   - Use `parallel-research` skill pattern
   - 3-min timeout per dimension

3. **Synthesis** (result-synthesizer):
   - Merge into structured briefing
   - Executive summary (3 bullets)
   - SWOT analysis
   - Relevance to Pure Technology

4. **Delivery**:
   - Save to `~/exports/portal-files/briefing-[company]-[date].md`
   - Portal deliver via `portal_deliver.sh`
   - File to Drive (Competitive Intel folder)

## Gotchas

- Public companies have more data; startups need LinkedIn + Crunchbase focus
- Always note data freshness ("as of [date]")
- Cross-reference claims across 2+ sources
