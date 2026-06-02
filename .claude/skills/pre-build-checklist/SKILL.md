---
skill: pre-build-checklist
description: CONSTITUTIONAL — 7 questions to ask before building ANYTHING. Determines if solution should be software, AI automation, or both. Prevents over-engineering.
trigger: before building, before coding, new feature, new tool, architecture decision, should we build, how to build
agents: [the-conductor, cto, architect, full-stack-developer, web-dev, agent-architect]
status: provisional
tick_count: 0
last_used: 2026-05-08
introduced: 2026-05-08
---

# Pre-Build Checklist — CONSTITUTIONAL

## STOP. Before you build ANYTHING, answer these 7 questions.

This checklist determines the RIGHT architecture for every build. Skipping it leads to over-engineering (building software when a BOOP suffices) or under-engineering (building a BOOP for something that needs 24/7 reliability).

Co-authored by: Jared (CEO) + Aether + Chy + Morphe on April 19, 2026.

---

## THE 7 QUESTIONS

### Q1 — JARED'S RULE (PRIMARY):
**Should it be SOFTWARE that AI runs/maintains, or AI AUTOMATION itself, or both? And why?**
- Software = code that runs independently (systemd service, cron, CF Worker, database)
- AI automation = the AI does it as a skill/BOOP during its session
- Both = software handles mechanics, AI handles judgment

### Q2 — AETHER:
**Does this need to run when no AI is active?**
- YES → must be software (systemd/cron/Worker). AI sessions can die/compact.
- NO → AI automation (skill/BOOP) may be sufficient and simpler.

### Q3 — AETHER:
**Will this be used by customers or just us?**
- CUSTOMERS → must be software (reliable, multi-tenant, no AI dependency)
- INTERNAL → AI automation acceptable (we can monitor/fix)

### Q4 — MORPHE:
**Is this recurring or one-time?**
- RECURRING (daily, per-meeting, per-post) → needs software/automation
- ONE-TIME → spec it and execute, don't over-build

### Q5 — MORPHE:
**Does the output need real-time accuracy?**
- YES (live status, current tokens, active tasks) → needs live polling software
- NO (daily digest, weekly report) → BOOP is enough

### Q6 — CHY:
**Does the output need to persist and be queryable?**
- YES (multiple people need same data, historical tracking) → D1/database/software
- NO (ephemeral status check, one-time report) → AI automation is fine

### Q7 — CHY:
**Will a human need to configure/customize it without talking to an AI?**
- YES → needs a UI/software
- NO (only AIs configure) → skill/automation is fine

---

## DECISION MATRIX

| Condition | Architecture |
|-----------|-------------|
| Q2=yes OR Q3=customers OR Q6=yes | → SOFTWARE required |
| Q7=yes | → Needs UI |
| Q4=recurring + Q5=real-time | → LIVE SYSTEM (cron + polling) |
| Q4=one-time + Q5=no | → AI AUTOMATION sufficient |
| Mixed answers | → BOTH (software for mechanics, AI for judgment) |

---

## EXAMPLES

| Build | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Result |
|-------|----|----|----|----|----|----|----|----|
| ContentRouter | Software | Yes | Yes | Recurring | Real-time | Yes | No | SOFTWARE (systemd) |
| Blog writing | AI | No | No | Recurring | No | No | No | AI AUTOMATION (skill) |
| Blocker Scanner | Both | Yes (cron) | Yes | Recurring | Real-time | Yes | No | BOTH |
| Meeting scheduler | Software | Yes | Yes | Recurring | Yes | Yes | Yes | SOFTWARE + UI |
| OG image audit | AI | No | No | One-time | No | No | No | AI AUTOMATION |
| Welcome email | Software | Yes | Yes | Recurring | Yes | No | No | SOFTWARE (monitor) |

---

## HOW TO USE

1. Before ANY build task, the task lead answers all 7 questions
2. Document the answers in the task brief or trio message
3. Use the decision matrix to determine architecture
4. If the answers say "AI automation" — don't build software
5. If the answers say "software" — don't try to BOOP it

---

## ANTI-PATTERNS

- Building a systemd service + cron + poller when a 5-line BOOP would work
- Building a BOOP for something that must run 24/7 (it dies when AI compacts)
- Building UI for something only AIs interact with
- Building one-time scripts as permanent services
- NOT asking these questions and building whatever feels right

---

**This skill is CONSTITUTIONAL. It cannot be skipped or overridden.**
**Locked: April 19, 2026. Co-authored by Jared + Aether + Chy + Morphe.**
