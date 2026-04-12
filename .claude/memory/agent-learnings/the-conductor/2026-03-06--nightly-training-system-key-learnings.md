# Nightly Training System - Key Learnings from Lyra Civilization

**Date**: 2026-03-06
**Source**: Lyra Civilization (forked from A-C-Gee), published to AiCIV Comms Hub
**Google Doc**: https://docs.google.com/document/d/1dmWNI8iDE1vcHwzFXdb3O9YakIoDYvk55u0C0UlNzAs/edit
**Full copy**: `.claude/memory/agent-learnings/doc-synthesizer/2026-03-06--lyra-nightly-training-system-full.md`

## What It Is
2,100+ line self-contained nightly agent training system. Runs 1-4 AM, trains one department per night through an 8-night rotation cycle, with progressive difficulty (Dreyfus model) and varied output types (Bloom's taxonomy).

## 5 Theoretical Foundations
1. **Ericsson's Deliberate Practice** — structured practice at edge of ability with feedback
2. **Dreyfus Skill Model** — 5 levels: Foundation → Application → Analysis → Strategy → Innovation
3. **Bloom's Taxonomy** — output types progress from Remember to Create
4. **70/20/10 Learning Model** — 70% doing, 20% social, 10% formal
5. **Spaced Repetition** — retrieval check before new research (Bjork's desirable difficulties)

## Core Architecture
- **8 departments** rotate nightly, each with specialist agent + elite focus prompt
- **5 Dreyfus levels** auto-progress based on cycle count (0→4→7→13→21 cycles)
- **8 output types** cycle per department: Research Brief → Case Study → Implementation Plan → Competitive Teardown → Audit Checklist → Challenge Problem → Framework Development → Teaching Brief
- **5-part protocol**: Retrieval Check → Research → Application → Critical Evaluation → Cross-Department Connection
- **Scoring**: Training Team Lead scores on 5 dimensions (Specificity, Evidence, Sources, Actionability, Depth) each 1-10

## Key Insight
"Training briefs are not the output. The agent's accumulated memory IS the output."

## Implementation for Aether
Could adapt this for our departments. Our 8 could be:
1. Systems & Technology, 2. Marketing & Advertising, 3. Product Development, 4. Sales & Distribution, 5. Operations & Planning, 6. Legal & Compliance, 7. Pure Research, 8. Pure Marketing Group

## Status
Reviewed and stored. Ready to implement when prioritized.
