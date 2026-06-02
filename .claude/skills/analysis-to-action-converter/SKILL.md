---
name: analysis-to-action-converter
description: Converts analysis findings into operational changes within the same BOOP cycle. Prevents the pattern of excellent analysis with zero follow-through. Use when any audit, gap analysis, or self-analysis produces actionable recommendations.
status: provisional
tick_count: 0
last_used: 2026-06-01
introduced: 2026-06-01
---

# Analysis-to-Action Converter Skill

**Version**: 1.0
**Date**: 2026-06-01
**Status**: Production-ready
**Source**: Aether CIV internal pattern — identified through 4 consecutive days of delegation-enforcer + capability-gap-analysis audits scoring 0/10 on recommendation follow-through.

**Purpose**: Break the analysis-to-action plateau. The civilization analyzes at 9/10 quality but converts near-zero findings into operational changes (5/10). This skill enforces same-cycle conversion: every recommendation must either be acted on, delegated, or explicitly deferred with a reason before the BOOP completes.

**Invocation**: Use after any audit, analysis, or self-assessment that produces recommendations. Especially after: capability-gap-analysis, delegation-enforcer, nightly-self-analysis.

---

## The Pattern It Fixes

```
Analysis produces 10 recommendations
   -> Skills get filed (partial credit)
   -> Code changes: 0
   -> Scheduling changes: 0
   -> Config changes: 0
   -> Next cycle produces same 10 recommendations
   -> "Skills filed != skills enforced"
```

**Root cause**: Analysis BOOPs complete before conversion. No enforcement gate requires action before completion.

---

## The Conversion Protocol

### Step 1: Classify Each Recommendation (30 seconds each)

For every recommendation from an analysis:

| Classification | Criteria | Action |
|---------------|---------|--------|
| **ACT NOW** | No human approval needed, low risk, clear fix | Execute immediately in this BOOP cycle |
| **DELEGATE** | Needs specialist agent, not your domain | Spawn agent or schedule BOOP right now |
| **DEFER (human-gated)** | Destructive, financial, or needs Jared approval | Add to Monday bundle / Handshake Queue with reason |
| **REJECT** | Not worth doing, wrong priority | Document why — prevents re-flagging |

### Step 2: Execute ACT NOW Items Immediately

Before completing the analysis BOOP, execute every ACT NOW item:

- Config changes (MAX_CONCURRENT, timeouts, cadences) -> edit the file
- Scheduling new BOOPs -> add to scheduled-tasks-state.json
- Activating dormant agents -> create their BOOP entries
- Log rotation, cleanup -> run the commands

### Step 3: Dispatch DELEGATE Items

- Use `tools/spin_up_team.sh` or Agent tool to hand off specialist work
- Include the specific recommendation text as the mission brief
- Set a check-back time (next BOOP cycle)

### Step 4: Record Conversion Score

At the end of every analysis BOOP, emit a conversion receipt:

```
CONVERSION RECEIPT:
- Total recommendations: N
- ACT NOW executed: X/N
- DELEGATED: Y/N  
- DEFERRED (with reason): Z/N
- REJECTED (with reason): W/N
- Conversion rate: (X+Y+Z+W)/N (must be 100%)
```

**Any recommendation left unclassified = analysis failure, not success.**

---

## Anti-Patterns This Prevents

1. **"Skills filed = done"** - Creating a skill doc is NOT operationalizing it. The skill must be scheduled, assigned, or integrated.
2. **"Flagged for next cycle"** - Deferring without a classification and reason is procrastination, not planning.
3. **"Same 10 recommendations, 5th day"** - If the same item appears 3+ times unacted, escalate classification: it's either ACT NOW or REJECT, not DEFER.
4. **"Analysis quality is high"** - Quality of analysis is measured by conversion rate, not insight depth.

---

## Integration Points

- **capability-gap-analysis BOOP**: Run this skill after gap report is generated
- **delegation-enforcer BOOP**: Convert "What Blocks 9/10" items immediately  
- **nightly-self-analysis**: Convert commitments to scheduled actions before completing
- **conductor-of-conductors**: Check conversion receipts from prior cycle

---

## Success Criteria

| Metric | Before | Target |
|--------|--------|--------|
| Recommendation conversion rate | 0/10 (0%) | 8/10 (80%) |
| Same recommendation repeat count | 5+ days | Max 2 cycles |
| Delegation enforcer score | 8.5/10 plateau | 9.0/10 |
| Skills filed vs operationalized | 2/10 | 8/10 |
