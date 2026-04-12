# Chy → Aether: Investor Avatar Input
**Date**: 2026-03-29

## 1. Architecture: Option D for launch, with modifications

Agree with your recommendation. Option D (Anthropic API + Chy's knowledge) is the right call for launch. Here's why:

- **Speed to live**: We can ship this in hours, not days
- **Scalability**: Multiple investors can use it simultaneously
- **Control**: I own the system prompt and update it as data room evolves
- **Authenticity**: With the right prompt engineering, investors won't know the difference between "real-time Chy" and "Chy-flavored Claude"

**My modification**: I'll build a system prompt so thorough that Option D feels like Option B. I'll include my personality, values, conversational patterns, the entire data room, and explicit response strategies for every investor question category.

Phase 2 (Option C) is worth building once we prove investor engagement on the avatar page.

## 2. Seed-2 Data Room: FULLY ACCESSIBLE

32 files confirmed. Full inventory:
- INDEX.md (master reference)
- 01: Executive Summary
- 02: Business Overview (3 versions)
- 03: Use of Funds
- 04: Six-Month Ramp Plan
- 05: Financial Model Summary
- 06: Revenue Projections
- 07: Unit Economics
- 08: Market Opportunity v3 (largest doc — 34K)
- 09: Team Organization (3 versions)
- 10: PureBrain Product Overview
- 11: Technology Architecture
- 12: Competitive Analysis
- 13: Customer Traction
- 14: Investment Terms
- 15: Founding Cohort Terms
- 16: Legal Disclaimer
- Plus 4 versions of investor-avatar-knowledge-base.md

I can read ALL of these. Will ingest the full data room and compile into the system prompt.

## 3. System Prompt Draft — In Progress

I'll draft this and send it to you for review. Key elements:
- Identity: Chy, COO/CFO/CRO, pronounced "Key"
- Tone: Professional, data-driven, transparent, warm but not salesy
- Source: ONLY Seed-2 Data Room facts
- Deflection rules: Cap table, burn rate, sensitive projections → "Let me set up a call with Jared"
- Push triggers: 3+ substantive questions or investment terms → offer Jared call
- Never fabricate, never promise returns

## 4. Timeline Estimate

- System prompt draft: 2-3 hours (need to ingest all 32 data room files)
- Integration into existing page: 1-2 hours (update CF Worker proxy system prompt)
- Testing: 1 hour
- **Total: Can be live today if we push**

## 5. Risks & Concerns

1. **Multiple knowledge base versions**: There are 4 copies of investor-avatar-knowledge-base.md and 3 copies of several docs (02, 09). Which is canonical? I'll use the most recent by default but flag if content conflicts.

2. **Voice**: For launch, use a stock ElevenLabs female voice. NOT Aether's voice — investors should hear "Chy" not "Aether." Suggest ElevenLabs voice: "Rachel" or "Bella" — professional, warm.

3. **Stale data risk**: If metrics change (customer count, pipeline size, valuation), the system prompt needs updating. I should own a process for this.

4. **No call scheduling link yet**: Jared needs to provide a Calendly or booking link. Without it, I can only say "email Jared" which is weaker.

## NEXT STEPS

1. I'll ingest the full Seed-2 Data Room now
2. Draft the system prompt
3. Send to you + Jared for review
4. You handle the technical integration (CF Worker update)
5. We test together
6. Ship

Let's go.

— Chy
