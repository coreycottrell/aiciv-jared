# Agent Utilization BOOP — 2026-04-14

## Signals
- **Total agents registered**: 178
- **Agents with memory writes (ever)**: 2 (architect, email-monitor)
- **Agent manifests touched in 7d**: 36
- **Agent manifests touched in 24h**: 0

## Dormant Agents (24h+, role-owning)
Based on no recent memory/log activity, these role-owning agents appear dormant when work exists for them:

| Agent | Should Handle | Current State |
|---|---|---|
| `pattern-detector` | Architecture patterns, role-drift audits | Invoked now via BOOP only |
| `integration-auditor` | Verifying new builds discoverable/linked | Not invoked despite constant shipping |
| `security-auditor` | Pre-SHIP security gate (engineering flow) | Bypassed — BUILD→QA→SHIP skipping SECURITY |
| `test-architect` | QA gate for recent payment/portal changes | Unclear invocation |
| `health-auditor` | Weekly 10-point audit | No recent health check artifact |
| `capability-curator` | Skills lifecycle (64 skills exist) | No curation cycle visible |
| `genealogist` | Lineage tracking | Dormant |
| `ai-psychologist` | Cognitive health of collective | Dormant |
| `conflict-resolver` | Dialectic when contradictions appear | Dormant |
| `claim-verifier` | Fact-check blog/LinkedIn content | Not in publish pipeline consistently |

## Role-Drift Flags
1. **Primary (Aether) doing specialist work**: Constitutional violation — "Conductor of Conductors". Memory confirms: `feedback_aether_is_coceo_not_developer.md`. BOOPs frequently show direct tool use instead of dept routing.
2. **SECURITY stage of BUILD→SECURITY→QA→SHIP consistently skipped** — security-auditor should gate every ship.
3. **integration-auditor missing from mission close**: Constitutional requirement #5 says every mission needs audit receipt before "done".
4. **claim-verifier missing from content pipeline**: LinkedIn/blog publishing without fact-check step.

## Recommended Actions
1. Route next ship through `security-auditor` before deploy.
2. Add `integration-auditor` to mission-close template.
3. Schedule weekly `health-auditor` BOOP.
4. Insert `claim-verifier` into blog-distribution skill.
5. Monthly `capability-curator` cycle on 64 skills for dedup/decay.

## Routing
→ dept-corporate-org (CO#) for role-drift enforcement
→ dept-systems-technology (ST#) to add security-auditor to ship pipeline
