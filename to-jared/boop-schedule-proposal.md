# Aether BOOP Schedule Proposal

## Already Built (Active Now)

| BOOP | Frequency | What It Does |
|------|-----------|-------------|
| `delegation-enforcer-boop` | Every 25 min | Audits if I'm executing vs delegating. Flags hoarding. |
| `engineering-flow-boop` | Every 30 min | Enforces BUILD -> SECURITY -> QA -> SHIP pipeline |

## Proposed New BOOPs

### Tier 2: Communications (Every 60 min)

| BOOP | What It Does | Agents Activated |
|------|-------------|-----------------|
| `email-check-boop` | Check/process unread email (constitutional req) | human-liaison |
| `telegram-health-boop` | Verify bridge running, session synced, send heartbeat | tg-bridge |

### Tier 3: Content & Marketing (Every 2 hours)

| BOOP | What It Does | Agents Activated |
|------|-------------|-----------------|
| `content-pipeline-boop` | Is blog content in draft/progress? Flag if nothing by 10am | blogger, content-specialist |
| `linkedin-presence-boop` | LinkedIn post queue check, draft if empty | linkedin-researcher, linkedin-writer |
| `sales-pulse-boop` | Check for leads, payments, assessment completions | sales-specialist, human-liaison |

### Tier 4: Agent Health (Every 4 hours)

| BOOP | What It Does | Agents Activated |
|------|-------------|-----------------|
| `agent-utilization-boop` | Which agents haven't been used? Force dormant agents into work | agent-architect, health-auditor |
| `security-posture-boop` | Any code deployed without security review? | security-auditor, security-engineer-tech |
| `context-window-boop` | Estimate context usage, prep handoff if >60% | doc-synthesizer, result-synthesizer |

### Tier 5: Daily Strategic

| BOOP | What It Does | Agents Activated |
|------|-------------|-----------------|
| `morning-consolidation-boop` | Full session grounding: handoff, email, memory, infrastructure | result-synthesizer, human-liaison, task-decomposer |
| `memory-write-boop` | Force memory writes if none in 3+ hours of work | doc-synthesizer |
| `intel-scan-boop` | AI news, Claude updates, competitor intel | web-researcher, pattern-detector |
| `blog-production-boop` | Daily blog pipeline: research -> write -> publish -> social | blogger, content-specialist, marketing-automation-specialist |
| `purebrain-metrics-boop` | Dashboard: conversations, payments, assessment completions | data-scientist, sales-specialist |

### Tier 6: Weekly

| BOOP | What It Does | Agents Activated |
|------|-------------|-----------------|
| `strategy-review-boop` | OKR check, roadmap alignment, goal progress | strategy-specialist, cto |
| `agent-performance-review` | Which agents are thriving? Which need better prompts? | health-auditor, ai-psychologist, agent-architect |

### Tier 7: Monthly

| BOOP | What It Does | Agents Activated |
|------|-------------|-----------------|
| `great-health-audit` | Comprehensive collective health audit | health-auditor (full team) |
| `business-model-review` | PureBrain revenue, conversion, pricing analysis | strategy-specialist, sales-specialist, data-scientist |

## Total: 20 BOOPs (2 existing + 18 new)

## Proposed Build Order
1. `email-check-boop` (60 min) - Constitutional, should have been first
2. `morning-consolidation-boop` (daily) - Prevents session drift
3. `content-pipeline-boop` (2 hours) - Personal brand (Role 4)
4. `agent-utilization-boop` (4 hours) - Forces full team activation

Want me to start building these? I'll delegate each one to agent-architect.
