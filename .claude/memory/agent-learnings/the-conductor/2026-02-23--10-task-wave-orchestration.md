# 10-Task Wave Orchestration Pattern

**Date**: 2026-02-23
**Type**: operational learning
**Topic**: Multi-task overnight mission with wave-based agent deployment

## Context

Jared sent a massive overnight prompt with 10 distinct tasks requiring different specialists. Each needed deep research, not shallow passes. His instruction: "set these on a timer so you aren't running them all at once.. maybe 15 minute intervals for each so you can really do deep research and execute the best possible way for each one"

## Pattern: 3-Wave Deployment

### Wave 1 (Immediate): Quick-turnaround + independent tasks
- T5: collective-liaison (skills to comms hub — bounded scope)
- T8: doc-synthesizer (daily recap — data already available)
- T1: content-specialist (blog content package — creative, needs time)
- T10: 3d-design-specialist (Dribbble study — independent research)

### Wave 2 (~15 min): Analysis tasks
- T2: content-specialist (blog/newsletter analysis)
- T3: marketing-strategist (website analysis + A/B tests)
- T6: linkedin-researcher (LinkedIn strategy)

### Wave 3 (~30 min): Strategy + synthesis tasks
- T4: marketing-strategist (distribution strategies)
- T7: sales-specialist (surprise & delight)
- T9: web-researcher (analytics deep dive)

### Bonus: Banner generation (full-stack-developer) launched with Wave 1

## Results
- 17 agents invoked, 0 failures
- 12 deliverable files produced
- All sent to Jared's Telegram as files (not pasted text)
- Executive morning brief synthesized all findings

## Key Learnings

1. **Wave grouping logic**: Group by independence, not complexity. Tasks that don't share agents or data sources can run simultaneously.

2. **Agent reuse across waves**: content-specialist and marketing-strategist each got 2 tasks — space them across different waves to avoid quality degradation from parallel load.

3. **Proactive bonus work pays off**: OG tags diagnostic (not requested) caught that analytics report was partially wrong. Cross-checking between agent outputs catches errors.

4. **File delivery > text paste**: Jared wants downloadable files, not long messages. Every deliverable should be `tg_send.sh --file`.

5. **Executive synthesis is the capstone**: After all agents complete, the conductor's unique contribution is the morning brief that resolves contradictions between reports and surfaces the 3-5 most actionable items.

6. **Cross-deliverable pattern detection**: 5 of 10 deliverables independently identified the LinkedIn-to-email conversion gap. This convergence IS the signal — it elevates from "suggestion" to "strategic priority."

## Metrics
- Total deliverable lines: ~5,000+
- Market value estimate: $9,725-$15,975
- Human effort equivalent: 16-19 hours of specialist work
- Actual human time: 1.5-2 hours (Jared writing the prompt)
