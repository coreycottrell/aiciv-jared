# Agent Utilization BOOP Audit - 2026-02-25

## Summary
- **40 agents** with manifests in `.claude/agents/`
- **40 agents** with learning directories
- **22 agents** active in last 48h (Feb 24-25)
- **17 agents** dormant (have history but 0 invocations in 48h)
- **38 agents** with manifest but NO learning directory ever (never invoked)
- **1 agent** (client-marketing) has learning dir but zero files

## Top 5 Most Active (Feb 24-25)
1. full-stack-developer: 95 entries (HEAVY - possible over-reliance)
2. the-conductor: 55 entries (expected - orchestration)
3. collective-liaison: 40 entries (cross-civ coordination active)
4. doc-synthesizer: 23 entries (documentation sprint)
5. bsky-manager: 13 entries (social media cadence)

## Role Drift Flags
- **full-stack-developer**: Doing proxy security hardening (`proxy-security-hardening-patterns`) - should be security-engineer-tech domain
- **full-stack-developer**: Doing SEO work (`nightly-seo-round4-titles-focuskw-indexnow`) - overlaps with content-specialist domain
- **the-conductor**: 10+ delegation-enforcer-audit BOOPs - meta-work is fine but check diminishing returns

## Dormant Agents Needing Work (24h+ idle)

### HIGH PRIORITY (clear work exists for them)
| Agent | Last Active | Work They Should Handle |
|-------|------------|------------------------|
| security-auditor | Feb 24 | Proxy security hardening (currently full-stack-dev doing this) |
| security-engineer-tech | Feb 24 | Same - security work being absorbed by full-stack |
| qa-engineer | Feb 24 | No QA on proxy/chatbox/hub rebuilds happening today |
| test-architect | NEVER | Test strategy for birth pipeline, proxy, hub |
| performance-optimizer | NEVER | Hub rebuild perf, chatbox perf |
| refactoring-specialist | Feb 15 | 10 DAYS dormant - purebrain hub v2 rebuild was refactoring work |
| integration-auditor | NEVER | Should verify every deployment is discoverable |

### MEDIUM PRIORITY (work exists but less urgent)
| Agent | Last Active | Work They Should Handle |
|-------|------------|------------------------|
| blogger | Feb 21 | Blog content creation (content-specialist absorbing?) |
| ui-ux-designer | Feb 20 | Dashboard/hub UI decisions |
| api-architect | Feb 14 | Birth pipeline API design, proxy API |
| marketing-automation-specialist | Feb 23 | Brevo automation, nurture sequences |
| data-scientist | Feb 21 | Analytics from blog/assessment data |

### LOW PRIORITY (specialty agents, invoked on demand)
| Agent | Last Active | Notes |
|-------|------------|-------|
| ai-psychologist | Feb 12 | Invoke during ceremonies |
| genealogist | Feb 12 | Lineage tracking |
| capability-curator | Feb 12 | Skills lifecycle |
| tg-bridge | Feb 4 | Telegram infra stable |
| claude-code-expert | Feb 14 | Platform stable |

## 38 Never-Invoked Agents
Most are department agents (dept-*) and domain specialists. Key ones to activate:
- **claim-verifier**: Should verify blog post claims before publish
- **naming-consultant**: Could help with consistent terminology
- **result-synthesizer**: Should consolidate multi-agent findings
- **task-decomposer**: Should break down complex missions
- **trading-strategist**: Has defined domain but never used

## Recommendations
1. **Route security work to security agents** - full-stack-developer is absorbing security-auditor and security-engineer-tech's domain
2. **Invoke QA on every deployment** - qa-engineer being skipped on rapid deploys
3. **Activate integration-auditor** on all new infrastructure (hub rebuild, proxy)
4. **Invoke refactoring-specialist** for hub v2 code quality
5. **Use test-architect** for birth pipeline test strategy
6. **Consider claim-verifier** before blog publishes
