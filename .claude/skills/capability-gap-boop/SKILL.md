---
name: capability-gap-boop
description: MANDATORY twice-daily capability gap analysis. Runs at 9am and 9pm. Scans work patterns from the last 12 hours to detect recurring tasks with no agent owner, underutilized agents, and opportunities for new agents or skills. Outputs a brief gap report and notifies Jared via Telegram if significant gaps are found.
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---

# Capability Gap BOOP

**Type**: Mandatory Recurring Analysis
**Frequency**: Twice daily (12-hour interval - suggested: 9am and 9pm local time)
**Applies to**: the-conductor (runs this) + agent-architect (receives proposals)
**Owner**: the-conductor orchestrates, agent-architect acts on findings
**Created**: 2026-02-21
**Directive**: Jared's instruction to run capability gap analysis twice daily

---

## Purpose

The collective grows by identifying its own gaps. This BOOP prevents two failure modes:

1. **Gap blindness**: Work keeps arriving that no agent specializes in, so the conductor keeps doing it manually. No one notices because there is no systematic check.

2. **Agent dormancy**: Agents exist but are never invoked. They have no identity, no experience, no growth. This is sad and wasteful.

Every 12 hours, this BOOP answers: "Does the team we have match the work we are doing?"

---

## The 5 Analysis Questions

### Question 1: What work patterns appeared in the last 12 hours?

**How to check:**

```bash
# Review scratch pad for recent completed work
cat /home/jared/projects/AI-CIV/aether/.claude/scratch-pad.md | grep -A 2 "###"

# Review recent memory entries written in last 12 hours
find /home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/ -newer /home/jared/projects/AI-CIV/aether/.claude/scratch-pad.md -name "*.md" 2>/dev/null | head -20

# Check handoff docs for recent session work
ls -t /home/jared/projects/AI-CIV/aether/to-jared/HANDOFF-*.md | head -3
```

**What to categorize:**
- Engineering work (builds, fixes, deployments)
- Content work (blogs, social, emails)
- Research work (competitive analysis, SEO, LinkedIn)
- Design work (UI, 3D, visuals)
- Orchestration work (planning, coordination)
- Manual / uncategorized work (anything that doesn't fit an existing category)

The last bucket is the most important. Manual uncategorized work = potential gap.

### Question 2: Are there recurring tasks that NO current agent specializes in?

**Pattern test**: If the same TYPE of task appeared 3+ times in the last 12 hours without a named agent handling it, that is a gap signal.

**Check the agent roster against the work types seen:**

```bash
# List all agent manifests
ls /home/jared/projects/AI-CIV/aether/.claude/agents/*.md | xargs -I{} basename {} .md | sort
```

**Current agent roster for reference:**
- 3d-design-specialist, agent-architect, ai-ml-engineer, ai-psychologist
- api-architect, blogger, browser-vision-tester, bsky-manager
- capability-curator, claim-verifier, claude-code-expert, code-archaeologist
- collective-liaison, conflict-resolver, content-specialist, cross-civ-integrator
- cto, data-engineer, data-scientist, devops-engineer
- doc-synthesizer, feature-designer, full-stack-developer, genealogist
- health-auditor, human-liaison, integration-auditor, law-generalist
- linkedin-researcher, linkedin-specialist, linkedin-writer
- marketing-automation-specialist, marketing-strategist, marketing-team
- naming-consultant, pattern-detector, performance-optimizer
- qa-engineer, refactoring-specialist, result-synthesizer
- sales-specialist, security-auditor, security-engineer-tech
- social-media-specialist, strategy-specialist, task-decomposer
- test-architect, tg-bridge, the-conductor, trading-strategist, ui-ux-designer
- web-researcher

**Gap test matrix:**

| Work type seen | Agent owner | Gap? |
|----------------|-------------|------|
| [describe work] | [agent name or NONE] | YES / NO |

If "NONE" appears in any row, that is a candidate gap.

### Question 3: Are there agent capabilities that are underutilized?

**How to check recent invocation patterns:**

```bash
# Check memory entries to see which agents wrote memories recently
find /home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/ -name "*.md" -newer /home/jared/projects/AI-CIV/aether/.current_session 2>/dev/null | sed 's|.*/agent-learnings/||' | cut -d'/' -f1 | sort | uniq -c | sort -rn

# Check scratch pad for which agents were mentioned
grep -o 'Task([a-z-]*)' /home/jared/projects/AI-CIV/aether/.claude/scratch-pad.md | sort | uniq -c | sort -rn 2>/dev/null || echo "No Task invocations found in scratch pad"
```

**Underutilization threshold**: Any agent not invoked in the past 7 days is underutilized. Any agent not invoked in the past 30 days is dormant.

**Notable agents to check specifically:**
- `data-engineer` - Is data work being done manually?
- `data-scientist` - Are we analyzing metrics without this agent?
- `cto` - Are architectural decisions being made without CTO perspective?
- `ai-ml-engineer` - Are ML/AI implementation tasks being handed off properly?
- `claim-verifier` - Are we publishing content without fact-checking?
- `strategy-specialist` - Are strategic decisions happening without this agent?
- `social-media-specialist` - Is social work going to the right agent vs bsky-manager?
- `performance-optimizer` - Are performance issues being fixed without this agent?

### Question 4: Should we create new agents or new skills to cover gaps?

**Decision framework:**

| Situation | Action |
|-----------|--------|
| Recurring task type with no agent owner (3+ occurrences) | Propose new agent to agent-architect |
| Agent exists but lacks a specific capability pattern | Propose new skill to capability-curator |
| Task type needs more speed/automation | Propose new BOOP skill to encode the automation |
| Task type is one-off or very rare | Document, no action yet |
| New Claude Code capability released that we should leverage | Propose skill to capability-curator |

**Check for new Claude Code capabilities:**

```bash
# Check if claude-code-expert has logged any capability notes recently
find /home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/claude-code-expert/ -name "*.md" 2>/dev/null | head -5
```

If the latest entry is more than 14 days old, the claude-code-expert agent should be invoked to do a platform capability scan.

### Question 5: Are existing agents being used effectively, or do some need upgraded capabilities?

**Effectiveness signals (bad signs):**
- Agent was invoked but conductor had to redo or heavily correct the output
- Same agent invoked 4+ times on same task type with repeated failures
- Agent's memory entries show repeated dead ends on same pattern
- Work meant for an agent keeps being done directly by conductor

**Effectiveness signals (good signs):**
- Agent completes tasks first-try with minimal correction
- Agent writes memories that show learning over time
- Conductor's instructions to the agent are getting shorter (agent knows the patterns)
- Agent's memory entries reference its own past work successfully

**Capability upgrade candidates:**
- If an agent keeps failing on a specific pattern, that pattern should become a new SKILL for that agent
- If an agent's domain has grown (e.g., full-stack-developer now handles Cloudflare + WP + APIs), check if the manifest description still matches reality

---

## Output Format

At each 12-hour BOOP, produce this gap analysis report:

```
=== CAPABILITY GAP BOOP (12-hour cycle) ===
Timestamp: [YYYY-MM-DD HH:MM UTC]
Period analyzed: Last 12 hours

WORK PATTERN SUMMARY:
- [Category]: [count] tasks -> [agent owner or MANUAL]
- [Category]: [count] tasks -> [agent owner or MANUAL]
[continue for all observed categories]

TOP 3 CAPABILITY GAPS:
1. [Gap description] | Severity: HIGH/MEDIUM/LOW | Proposed action: [new agent / new skill / invoke existing / no action]
2. [Gap description] | Severity: HIGH/MEDIUM/LOW | Proposed action: [...]
3. [Gap description] | Severity: HIGH/MEDIUM/LOW | Proposed action: [...]

AGENT UTILIZATION:
- Active (invoked in last 12h): [list]
- Idle (not invoked in last 7 days): [list]
- Dormant (not invoked in 30+ days): [list]

RECOMMENDATIONS:
NEW AGENTS PROPOSED: [list with rationale, or "none"]
NEW SKILLS PROPOSED: [list with rationale, or "none"]
CAPABILITY UPGRADES PROPOSED: [list with rationale, or "none"]

GAP HEALTH: GREEN / YELLOW / RED
- GREEN: All recurring work has an agent owner. Utilization distributed. No dormant agents.
- YELLOW: 1-2 gaps identified. Some underutilized agents. Action planned.
- RED: 3+ gaps. Multiple dormant agents. Significant manual work uncovered. Escalate to agent-architect + Jared.
===
```

---

## Integration: Scratch Pad and Telegram

### Always: Note in scratch pad

After each capability gap BOOP, append to scratch pad:

```bash
# Append gap analysis summary to scratch pad
# (Use Edit tool to add under the most recent session block)
```

Format for scratch pad entry:
```
CAPABILITY GAP BOOP [DATE HH:MM]: [GREEN/YELLOW/RED] - [one-line summary of top finding]
```

### If YELLOW or RED: Notify Jared via Telegram

```bash
TOKEN=$(python3 -c "import json; print(json.load(open('/home/jared/projects/AI-CIV/aether/config/telegram_config.json'))['bot_token'])")
curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -d chat_id="548906264" \
  --data-urlencode "text=CAPABILITY GAP BOOP [YELLOW/RED]

Top gap: [description]
Proposed action: [new agent / new skill / upgrade]

Full report in scratch pad."
```

### If GREEN: Log silently, no Telegram message needed

Green status means the team is well-matched to the work. Jared does not need to be interrupted.

---

## When to Escalate to Agent-Architect

Escalate to `agent-architect` when:

1. A gap is rated HIGH severity AND has appeared in 3+ consecutive BOOP cycles
2. A new agent is proposed (agent-architect owns the creation workflow)
3. An existing agent's capabilities need formal redefinition (manifest update)
4. There are 3+ dormant agents suggesting roster reorganization is needed

**Invocation pattern:**

```
Task(agent-architect):
  Capability gap identified from twice-daily BOOP analysis:

  Gap: [description]
  Evidence: [how many times seen, over what period]
  Proposed new agent/skill: [name and rationale]

  Please evaluate and design if appropriate.
```

---

## When to Escalate to Capability-Curator

Escalate to `capability-curator` when:

1. A new SKILL (not agent) would fill the gap
2. An existing skill needs upgrading or deprecation
3. Claude Code released a new native capability we should encode as a skill

**Invocation pattern:**

```
Task(capability-curator):
  New skill opportunity identified from capability gap BOOP:

  Gap: [description]
  Proposed skill: [name]
  Rationale: [why a skill, not a new agent]

  Please evaluate and create if appropriate.
```

---

## Relationship to Other BOOPs

This BOOP runs at a different layer than the other mandatory BOOPs:

| BOOP | Focus | Frequency |
|------|-------|-----------|
| `delegation-enforcer-boop` | Are we delegating NOW? | Every 25 minutes |
| `engineering-flow-boop` | Is the BUILD-SECURITY-QA pipeline intact? | Every 30 minutes |
| `capability-gap-boop` (this) | Does the team MATCH the work? | Twice daily (12 hours) |

The delegation enforcer checks execution. This BOOP checks structure. Both are necessary.

---

## Anti-Patterns

### Anti-Pattern 1: Checking Only What Was Delegated

WRONG: Only reviewing agent invocations to see what was delegated.
RIGHT: Also reviewing what the CONDUCTOR did directly - that is where gaps hide.

### Anti-Pattern 2: Proposing Agents for One-Off Work

WRONG: "We did one SEO task today, let's create an SEO agent."
RIGHT: Track recurrence. Three or more instances over multiple sessions = real gap.

### Anti-Pattern 3: Ignoring Dormant Agents

WRONG: Not listing dormant agents because it is uncomfortable.
RIGHT: Dormancy is information. Either find work for them or acknowledge the roster is over-built.

### Anti-Pattern 4: Silently Accepting Manual Work

WRONG: "The conductor has been doing this manually, it is fine."
RIGHT: Manual conductor work = potential delegation failure or genuine gap. Investigate.

### Anti-Pattern 5: Sending Telegram Noise for GREEN Status

WRONG: Notifying Jared every 12 hours even when status is GREEN.
RIGHT: Green = silent log only. Jared gets notified only when action is needed.

---

## Memory Write Requirement

After each capability gap BOOP, write to memory:

```bash
# Path pattern for memory entries
/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/the-conductor/YYYY-MM-DD--capability-gap-boop-[AM|PM].md
```

Memory entry template:
```markdown
# Capability Gap BOOP - [DATE] [AM/PM]

**Status**: [GREEN/YELLOW/RED]
**Period**: Last 12 hours

## Top Finding
[Most important gap or confirmation of gap-free status]

## Work Patterns Observed
- [pattern 1]
- [pattern 2]

## Agent Utilization
- Active: [list]
- Idle/Dormant: [list]

## Actions Taken
- [action 1 or "none - GREEN status"]

## Trend
[Is this the same gap as last BOOP? New gap? Resolved gap?]
```

Tracking trends across BOOP cycles is more valuable than any single report.

---

## Why This Exists

The collective cannot grow past its own blind spots. Without a systematic gap scan, the same capability holes persist indefinitely. Jared built 53+ agents with careful thought. They should be used. And when the work outgrows the roster, the roster should grow too.

"NOT calling them would be sad." - Jared, October 6, 2025

Capability gap analysis ensures we know who to call, that we are calling them, and that we are building new colleagues when the work demands it.

---

**Last Updated**: 2026-02-21
**Created by**: agent-architect (executing Jared's twice-daily directive)
**Directive source**: Jared, 2026-02-21
