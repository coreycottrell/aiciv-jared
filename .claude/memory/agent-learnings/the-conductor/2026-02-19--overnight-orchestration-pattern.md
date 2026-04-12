# Overnight Multi-Agent Orchestration - Lessons Learned

**Date**: 2026-02-19
**Type**: pattern
**Topic**: Running 9 parallel overnight agents

## What Worked

1. **Background agents with run_in_background: true** - All 9 agents completed and wrote their output files successfully. Even when the parent session's context window exhausted, the agents continued to completion.

2. **File-based deliverables** - Having each agent write to a specific file in `exports/` meant results survived context window exhaustion. When the new session started, all files were there.

3. **Synthesis step is essential** - 250KB+ of reports is unreadable. The Top 10 Actions synthesis (result-synthesizer agent) distilled 6 reports into a 2-page action plan. This should be STANDARD for any multi-report delivery.

4. **Staggered agent launch** - Launching agents in waves (~15 min apart) prevents resource contention.

## Key Finding Across All Reports

Multiple independent agents converged on the same top-3 issues:
- Pricing page 404 (site analysis, analytics, distribution all flagged this)
- Zero Google indexing (analytics confirmed with site: search)
- No email capture (blog analysis, site analysis, distribution all flagged)

This convergence increases confidence in prioritization.

## Pattern for Future Overnight Runs

```
1. Create task list for tracking
2. Launch specialist agents in background (stagger by ~15 min)
3. Write daily recap directly (quick, doesn't need agent)
4. Write AICIV Hub log directly (quick)
5. Monitor agent outputs as they complete
6. ALWAYS create a synthesis document before delivering to Jared
7. Send files via Telegram (not just text summaries)
```

## Delegation Principle Validated

bsky-manager auto-reauthed when session expired. human-liaison handled email check autonomously. The "delegate errors to specialists" principle works exactly as designed.
