# Daily Agent Rotation Schedule (Optimized)

**Constitutional Rule**: Every agent invoked at least once per 24 hours.
**Target Token Budget**: 30-50K tokens/day (down from 80-120K)
**Strategy**: Batch via dept managers, overnight bulk training, skip-if-worked, micro-prompts.

---

## Core Rules

1. **Skip-if-worked**: Any agent invoked for real work in the last 24h = rotation complete. No exercise needed.
2. **Dept manager = team activation**: Invoking 1 dept manager who spawns 3-5 specialists = all count as activated.
3. **Micro-prompts only**: Training = ONE sentence prompt, ONE paragraph output. No deep dives.
4. **Daytime = real work only**: 4am-10pm ET, only invoke agents for actual tasks. Training happens overnight.
5. **Combo invocations**: Group related agents into single prompts (1 invocation = multiple agents activated).

---

## OVERNIGHT BULK (10:00 PM - 1:30 AM ET) -- 69 agents via 8 batch invocations

Jared is asleep. Run all training here. Each batch = 1 dept manager spawning specialists.

### Batch 1: ST# Engineering Sweep (10:00 PM) -- ~4K tokens
**Invoke**: `dept-systems-technology`
**Prompt**: "Spawn cto, full-stack-developer, devops-engineer, security-engineer-tech, security-auditor, qa-engineer, test-architect, performance-optimizer, refactoring-specialist, data-engineer, ai-ml-engineer, api-architect. Each: ONE micro-check on their domain. One-sentence reports."
**Agents activated**: 13

### Batch 2: MA# Content + Marketing (10:30 PM) -- ~4K tokens
**Invoke**: `dept-marketing-advertising`
**Prompt**: "Spawn blogger, content-specialist, linkedin-researcher, linkedin-writer, linkedin-specialist, social-media-specialist, bsky-manager, marketing-strategist, marketing-automation-specialist, marketing-team, seo-specialist, conversion-rate-optimizer, content-distribution-agent, naming-consultant, client-marketing. Each: ONE sentence micro-task on their domain."
**Agents activated**: 16

### Batch 3: SD# Sales + Trading (11:00 PM) -- ~2K tokens
**Invoke**: `dept-sales-distribution`
**Prompt**: "Spawn sales-specialist, trading-strategist. Each: 1 micro-check. Self: pipeline pulse."
**Agents activated**: 3

### Batch 4: PD# Product + Design (11:15 PM) -- ~2K tokens
**Invoke**: `dept-product-development`
**Prompt**: "Spawn feature-designer, ui-ux-designer, 3d-design-specialist. Each: 1 sentence on their domain. Self: top backlog item."
**Agents activated**: 4

### Batch 5: Corporate Block (11:30 PM) -- ~2K tokens
**Invoke**: `dept-corporate-org`
**Prompt**: "Spawn dept-board-advisors, dept-commercial-business, dept-pure-capital, dept-pure-digital-assets, dept-pure-infrastructure, dept-pure-love, dept-karma, dept-external-share, dept-internal-share. Each: ONE sentence status pulse."
**Agents activated**: 10

### Batch 6: Ops + Legal + Finance + HR (12:00 AM) -- ~2K tokens
**Invoke**: `dept-operations-planning`
**Prompt**: "Spawn dept-legal-compliance, dept-accounting-finance, dept-human-resources, law-generalist, florida-bar-specialist. Each: 1 micro-check on their domain."
**Agents activated**: 6

### Batch 7: IT + Teams (12:30 AM) -- ~2K tokens
**Invoke**: `dept-it-support`
**Prompt**: "Spawn wtt-fullstack, wtt-qa, ptt-fullstack, ptt-qa, cts-fullstack, cts-qa, client-tech-support-team, customer-success-manager, payment-flow-qa, browser-vision-tester. Each: ONE micro-check."
**Agents activated**: 11

### Batch 8: Research (1:00 AM) -- ~2K tokens
**Invoke**: `dept-pure-research`
**Prompt**: "Spawn web-researcher, code-archaeologist, pattern-detector, data-scientist, claim-verifier. Each: identify 1 finding in their domain. One sentence."
**Agents activated**: 6

**Overnight subtotal**: ~20K tokens, 69 agents activated via 8 invocations

---

## PRE-OVERNIGHT: Meta + Synthesis (8:00-9:30 PM ET) -- 14 agents via 2 invocations

Run just before Jared sleeps. Low-cost wrap-up.

### Meta Batch (8:00 PM) -- ~3K tokens
**Prompt**: "Quick pulse: health-auditor, ai-psychologist, genealogist, claude-code-expert, capability-curator, agent-architect, integration-auditor, collective-liaison, cross-civ-integrator. Each: 1 sentence status on their domain."
**Agents activated**: 9

### Synthesis Batch (9:00 PM) -- ~3K tokens
**Prompt**: "Wrap today: result-synthesizer=daily digest, doc-synthesizer=1 doc update, conflict-resolver=contradictions?, strategy-specialist=1 OKR check, task-decomposer=1 backlog item."
**Agents activated**: 5

**Pre-overnight subtotal**: ~6K tokens, 14 agents

---

## DAYTIME (4:00 AM - 8:00 PM ET) -- Real work only, no training

### Auto-Activated by Wake-Up Protocol (zero extra cost)
- **the-conductor** -- wake-up protocol
- **human-liaison** -- email-first constitutional requirement
- **tg-bridge** -- bridge verification

### Activated on First Real Task (zero training cost)
- **dept-pure-technology** -- any PT# routing
- **dept-pure-marketing-group** -- any PMG# routing
- **dept-investor-relations** -- any IR# routing
- Any other dept manager triggered by real work

**Daytime rule**: If an agent does real work during the day, mark it complete and SKIP it in the overnight batch.

---

## Token Budget Summary

| Block | Time (ET) | Agents | Invocations | Est. Tokens |
|-------|----------|--------|-------------|-------------|
| Meta + Synthesis | 8-9:30 PM | 14 | 2 | ~6K |
| Overnight Batches 1-8 | 10PM-1:30AM | 69 | 8 | ~20K |
| Wake-up auto-activate | 4-6 AM | 3 | 0 | ~0 |
| Daytime real work | 6AM-8PM | varies | varies | not rotation cost |
| Skip-if-worked savings | -- | -5 to -20 | -- | -2K to -8K |
| **TOTAL ROTATION** | | **89** | **10** | **~28-33K tokens** |

Previous budget: 80-120K tokens/day. **Savings: 60-75%.**

---

## Skip-If-Worked Tracking

Before overnight batch, generate skip list. Save to `.claude/memory/daily-rotation/YYYY-MM-DD.json`:

```json
{
  "date": "2026-03-28",
  "total_agents": 89,
  "real_work": [],
  "overnight_trained": [],
  "auto_activated": ["the-conductor", "human-liaison", "tg-bridge"],
  "skipped_already_worked": 0,
  "total_activated": 89,
  "estimated_tokens": 30000
}
```

---

## Weekly Depth Rotation

One overnight batch gets slightly deeper exercises per night (~500 extra tokens):

| Night | Deep Focus | Which Batch |
|-------|-----------|-------------|
| Mon | Security | Batch 1 |
| Tue | Content | Batch 2 |
| Wed | Engineering | Batch 1 |
| Thu | Business | Batch 3+5 |
| Fri | Research | Batch 8 |
| Sat | Infrastructure | Batch 7 |
| Sun | Wellbeing | Meta batch |

---

## Notes

- If token budget is tight, cut Batch 5 (corporate) first -- lowest business impact.
- New agents: slot into most relevant overnight batch within 24h.
- Dormancy alert: 48h+ without activation = P2 escalation.
- Real work always supersedes training. This schedule is a floor, not a ceiling.

---

**Created**: 2026-03-28
**Optimized by**: dept-operations-planning (OP#)
**Review cadence**: Weekly
