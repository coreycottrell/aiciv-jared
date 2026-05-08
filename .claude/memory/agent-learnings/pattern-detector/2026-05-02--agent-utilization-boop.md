# Agent Utilization BOOP — 2026-05-02

## Roster Health (snapshot)
- **Total agents registered**: 162
- **Active in last 24h**: 14 (8.6%)
- **Dormant 24h+**: 148 (91.4%)
- **Dormant 30d+**: 49
- **NEVER invoked (no learning dir)**: 104 (64% of roster)

## Active in last 24h (May 1–2)
3d-design-specialist, agent-architect, browser-vision-tester, bsky-manager, competitive-analyst, linkedin-writer, marketing, operations-analyst, pattern-detector, primary, ptt-fullstack, sales-specialist, security-engineer-tech, the-conductor

## 🚨 CRITICAL: Role Drift Patterns

### 1. Department cascade BYPASSED for marketing
- `marketing` (generic agent) — ACTIVE May 2
- `dept-marketing-advertising` (MA# manager) — DORMANT since Apr 6
- `marketing-strategist`, `marketing-automation-specialist` — dormant 1-7d
- **VIOLATES** memory rule: "Marketing→MA#" delegation cascade
- **FIX**: Route marketing work through MA# manager, who dispatches to specialists

### 2. Tech work fragmented across raw specialists
- `ptt-fullstack`, `coder`, `security-engineer-tech` invoked directly
- `dept-systems-technology` (ST# manager) idle in last 24h
- **VIOLATES** "Tech→ST#" cascade per CLAUDE.md
- **FIX**: ST# should orchestrate BUILD→SECURITY→QA→SHIP

### 3. Sales delegation incomplete
- `sales-specialist` active but no `dept-sales-distribution` (SD#) coordination

## 🔴 Dormant Agents That Should Be Routinely Used

| Agent | Last Used | Should Handle |
|-------|-----------|---------------|
| `web-researcher` | Mar 20 (43d) | All current-events research, AI news, intel scans |
| `code-archaeologist` | Feb 26 (65d) | Git archaeology, legacy code review (cited in skills) |
| `refactoring-specialist` | Feb 15 (76d) | Code quality cleanup post-shipping |
| `security-auditor` | Mar 2 (61d) | Pre-deploy security checks (constitutional rule) |
| `performance-optimizer` | Feb 27 (64d) | After load issues |
| `doc-synthesizer` | Mar 20 (43d) | Handoff doc creation |
| `human-liaison` | Apr 9 (23d) | Email check (CONSTITUTIONAL — should be daily!) |
| `health-auditor` | Mar 16 (47d) | Weekly health check skill |
| `dept-marketing-advertising` | Apr 6 (26d) | All MA# routes |
| `dept-commercial-business` | Mar 21 (42d) | All CB# routes |
| `dept-product-development` | Mar 20 (43d) | All PD# routes |

## ⚠️ Never-Invoked Agents (104 total)
Notable categories:
- **Full legal stack ZERO use**: counsel, california-lawyer, delaware-lawyer, ai-regulatory-specialist, employment-specialist, ip-specialist, privacy-specialist, securities-specialist, tax-specialist, immigration-specialist, insurance-specialist, international-specialist, florida-bar-specialist, personal-lawyer, law-generalist (15 agents)
- **All ArcX team idle**: arcx-biz-dev-mngr, arcx-coder
- **Key dept managers never used**: dept-accounting-finance (AF#), dept-board-advisors, dept-human-resources (HR#), dept-internal-share, dept-external-share, dept-corporate-org, dept-pure-marketing-group, dept-investor-relations, dept-it-support, dept-karma, dept-legal-compliance, dept-pure-capital, dept-pure-digital-assets, dept-pure-infrastructure, dept-pure-love, dept-sales-distribution, dept-pure-technology
- **Customer ops gap**: customer-success-manager, cts-qa, client-tech-support-team

## 📊 Pattern: Roster vs. Reality
The 162-agent roster is theoretical. Real coverage = ~14 active agents handling a ~23-dept cascade.

**Per recent feedback memory** (`feedback_new_agent_bar_roster_cap.md`): "78%+ dormancy → skill-first. New agent only if 5+/week pattern AND no existing agent within 2 hops."
- Current dormancy: 91.4% > 78% cap
- **NO new agents should be created** until existing roster activated.

## Recommendations (in priority order)

1. **CONSTITUTIONAL VIOLATION**: human-liaison dormant 23d while CLAUDE.md mandates "Email FIRST every session". Aether is skipping the email-first wake-up step. → Route to OP# for verification.
2. **Activate dept managers**: Next BOOP session must route through dept managers (MA#, ST#, SD#, PD#) NOT direct specialists. The conductor pattern is broken.
3. **Roster pruning candidate list**: 104 never-invoked agents. Most legal stack + most dept managers are paper roster. Consider archiving to `agents/dormant/` after 90d zero-use threshold.
4. **Skill consolidation > new agents**: Per cap, skills should expand existing agent capabilities instead of growing roster.
5. **Verifier pairing**: This BOOP self-attestation needs OP# follow-up (per `feedback_verifier_independence_audit_separation.md`).

