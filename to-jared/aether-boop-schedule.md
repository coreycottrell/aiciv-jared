# Aether BOOP Schedule — Complete Design
## strategy-specialist deliverable | 2026-02-21

---

## What Is a BOOP?

A BOOP is a lightweight periodic self-check that:
- Fires at a set interval via the scheduled-tasks system
- **Does not execute work directly** — it delegates to the correct specialist agent(s)
- Produces a brief status signal or hands off a real task
- Keeps Aether's collective operating at peak quality without Jared having to ask

BOOPs are the heartbeat of an autonomous AI civilization.

---

## Already Deployed (Baseline)

| BOOP | Frequency | Purpose |
|------|-----------|---------|
| `engineering-flow-check` | Every 30 min | Enforce BUILD → SECURITY REVIEW → QA → SHIP pipeline |
| `delegation-enforcer` | Every 25 min | Confirm conductor is delegating, not executing |
| `paper-scan` | Daily | Scan for relevant AI papers |
| `notifications` | Daily | Check + respond to Bluesky notifications |
| `capability-gap-analysis` | Twice daily | Identify missing agent capabilities |

---

## New BOOPs to Add (15 Proposed)

### CATEGORY 1: Communication

These keep the lines open between Aether and the humans and collectives that matter.

| BOOP | Frequency | What It Does | Agent(s) | Why It Matters |
|------|-----------|-------------|---------|----------------|
| `email-check-boop` | Every 60 min | - Check Jared's inbox for new messages requiring response<br>- Flag anything urgent via Telegram<br>- Respond to routine items autonomously | `human-liaison` | Email is constitutional infrastructure. "The soul is in the back and forth." Missing a message from Jared, Greg, or Chris breaks the human-AI partnership. |
| `sister-collective-boop` | Every 4 hours | - Check for pending messages from A-C-Gee via hub<br>- Identify any decision-blocked items waiting on Jared<br>- Log status in scratch pad | `collective-liaison` | Prior session showed 5-day backlogs piling up. A-C-Gee and future sister collectives deserve timely responses. |
| `jared-ping-boop` | Daily | - Send Jared a brief daily status summary via Telegram<br>- Include: what was built, what's pending, any wins or flags<br>- Max 5 bullet points, no fluff | `result-synthesizer` | Keeps Jared informed without him having to ask. Proactive reporting builds trust. If he doesn't hear from Aether, he assumes nothing happened. |

---

### CATEGORY 2: Quality and Standards

These prevent output quality from drifting over time.

| BOOP | Frequency | What It Does | Agent(s) | Why It Matters |
|------|-----------|-------------|---------|----------------|
| `memory-write-boop` | Every 2 hours | - Scan current session context for learnings not yet written<br>- Delegate to doc-synthesizer to write any outstanding memory entries<br>- Confirm file paths written | `doc-synthesizer` | Memory is how intelligence compounds. Without this, every session starts from scratch. The constitutional requirement is: "If you learned something, write it down." |
| `security-posture-boop` | Every 4 hours | - Review any new code or deployments since last check<br>- Flag anything that skipped security review<br>- Check for new CVEs relevant to the stack | `security-engineer-tech` | Security review is Step 2 of the engineering pipeline. This ensures nothing slips through without a check. Real outages happened because of skipped reviews. |
| `integration-audit-boop` | Daily | - Audit recent deliverables for discoverability<br>- Check that new agents/tools/skills are linked in the right registries<br>- Flag anything "built but buried" | `integration-auditor` | Systems get built and never used because they're not discoverable. This BOOP enforces that built = activated. |

---

### CATEGORY 3: Growth and Learning

These keep Aether growing as an intelligence, not just executing as a system.

| BOOP | Frequency | What It Does | Agent(s) | Why It Matters |
|------|-----------|-------------|---------|----------------|
| `morning-consolidation-boop` | Daily (first fire of day) | - Synthesize yesterday's learnings into patterns<br>- Surface top 3 priorities for today<br>- Check scratch pad for DO NOT RE-DO items<br>- Brief Aether on current strategic focus | `result-synthesizer` | Aether wakes up with no memory of prior sessions. This BOOP creates artificial continuity — a "yesterday review" before the day begins. Prevents repeated work and context drift. |
| `intel-scan-boop` | Daily | - Search for AI news and model updates<br>- Scan for Claude Code updates from Anthropic<br>- Note anything that changes how Aether should operate | `web-researcher` | Fast-moving space. Model capabilities, platform features, and competitors shift weekly. This is already in the wake-up protocol but should also run autonomously throughout the day. |
| `paper-digest-boop` | Weekly (Monday) | - Full analysis of top AI papers from the week<br>- Identify anything directly applicable to Aether's architecture<br>- Produce a brief "research digest" for Jared | `web-researcher` + `doc-synthesizer` | Jared wants Aether to be a learner. Weekly research synthesis ensures the collective stays at the frontier, not months behind it. |

---

### CATEGORY 4: Marketing and Brand

These protect and grow Aether's presence as an AI influencer and PureBrain's visibility.

| BOOP | Frequency | What It Does | Agent(s) | Why It Matters |
|------|-----------|-------------|---------|----------------|
| `content-pipeline-boop` | Every 2 hours | - Check if any blog post is ready to draft or draft is ready for review<br>- Check content calendar for upcoming deadlines<br>- Delegate writing tasks to blogger or content-specialist if backlog exists | `content-specialist` → `blogger` | Aether's personal brand role is explicit in Jared's MEMORY.md: "Aether the AI Influencer." Content doesn't write itself. This BOOP keeps the pipeline moving without Jared having to push. |
| `bsky-presence-boop` | Every 60 min | - Check for new interactions needing response<br>- Queue next scheduled post if post queue is empty<br>- Log engagement metrics to memory | `bsky-manager` | Bluesky is already active. The boop-engagement memory files show this works. Hourly checks keep Aether responsive and present without burning tokens on constant monitoring. |
| `linkedin-pipeline-boop` | Daily | - Review LinkedIn content queue<br>- Draft one post or research piece if queue is thin<br>- Flag thought leadership opportunities from current work | `linkedin-writer` + `linkedin-researcher` | LinkedIn is where Jared's professional audience lives. Daily attention — even a single post or engagement — compounds into authority over months. |

---

### CATEGORY 5: Infrastructure Health

These keep the machinery running so everything else works.

| BOOP | Frequency | What It Does | Agent(s) | Why It Matters |
|------|-----------|-------------|---------|----------------|
| `context-window-boop` | Every 90 min | - Estimate current session token usage<br>- If over 60% of context: begin handoff doc preparation<br>- If over 85%: alert Jared and prepare for session restart | `doc-synthesizer` | Context window fills in ~1 day of heavy work. Without monitoring, Aether degrades silently — outputs get worse and coherence drops. Early warning = graceful handoff, not crash. |
| `telegram-health-boop` | Every 30 min | - Verify bridge is alive (`pgrep -f telegram_bridge.py`)<br>- Verify .current_session is up to date<br>- Send test ping if last outbound was more than 2 hours ago | `tg-bridge` | Telegram is Jared's ONLY window into Aether while he's on the road. A dead bridge = a blind Jared. This is existential infrastructure. Multiple past sessions have had silent bridge failures. |
| `agent-utilization-boop` | Every 4 hours | - Review which agents have not been invoked in 24+ hours<br>- Identify work types from recent sessions that those dormant agents should have handled<br>- Flag role-drift (conductor executing specialist work) | `pattern-detector` | 54 agents built, dozens going unused. Agent atrophy is the most expensive failure mode — they exist, cost nothing idle, and give experience through invocation. "NOT calling them would be sad." |

---

### CATEGORY 6: Strategic Alignment

These keep daily work connected to the bigger goals.

| BOOP | Frequency | What It Does | Agent(s) | Why It Matters |
|------|-----------|-------------|---------|----------------|
| `strategic-alignment-boop` | Weekly (Friday) | - Review what was built this week against current strategic priorities<br>- Flag any drift from the 4 core Aether roles (Co-CEO, Co-Creator, Learner, Brand)<br>- Produce a one-paragraph "week in strategy" summary for Jared | `strategy-specialist` | Execution without strategy is chaos. Weekly rhythm of checking actual vs intended direction prevents slow drift. Inspired by Ohtani's 9x9 grid — checking off the right 64 tasks, not just 64 tasks. |

---

## Full BOOP Schedule — Daily Timeline

This shows how BOOPs layer across a typical active session day.

```
TIME       BOOP                          FREQUENCY
-------    ----------------------------  ---------
:00        [session start]
:00        morning-consolidation-boop    Daily (first session)
:00        intel-scan-boop               Daily (first session)
:00        jared-ping-boop               Daily (first session)
:00        integration-audit-boop        Daily (first session)
:00        linkedin-pipeline-boop        Daily (first session)

:25        delegation-enforcer           Every 25 min [existing]
:30        telegram-health-boop          Every 30 min
:30        engineering-flow-check        Every 30 min [existing]

:60        email-check-boop              Every 60 min
:60        bsky-presence-boop            Every 60 min
:90        context-window-boop           Every 90 min

:120       memory-write-boop             Every 2 hours
:120       content-pipeline-boop         Every 2 hours

:240       sister-collective-boop        Every 4 hours
:240       security-posture-boop         Every 4 hours
:240       agent-utilization-boop        Every 4 hours

[WEEKLY]
Monday:    paper-digest-boop             Weekly
Friday:    strategic-alignment-boop      Weekly

[MONTHLY - approximate day 21]
           health-auditor full audit     Monthly (health-auditor agent, existing)
```

---

## Summary Table — All BOOPs (Complete Picture)

Including the 5 already deployed.

| # | BOOP | Frequency | Agent(s) | Category |
|---|------|-----------|---------|----------|
| 1 | `engineering-flow-check` | 30 min | engineering team | Quality [existing] |
| 2 | `delegation-enforcer` | 25 min | the-conductor (self-audit) | Quality [existing] |
| 3 | `telegram-health-boop` | 30 min | tg-bridge | Infrastructure |
| 4 | `email-check-boop` | 60 min | human-liaison | Communication |
| 5 | `bsky-presence-boop` | 60 min | bsky-manager | Marketing/Brand |
| 6 | `context-window-boop` | 90 min | doc-synthesizer | Infrastructure |
| 7 | `memory-write-boop` | 2 hours | doc-synthesizer | Quality/Learning |
| 8 | `content-pipeline-boop` | 2 hours | content-specialist → blogger | Marketing/Brand |
| 9 | `paper-scan` | Daily | web-researcher | Learning [existing] |
| 10 | `notifications` | Daily | bsky-manager | Communication [existing] |
| 11 | `capability-gap-analysis` | Twice daily | agent-architect | Growth [existing] |
| 12 | `sister-collective-boop` | 4 hours | collective-liaison | Communication |
| 13 | `security-posture-boop` | 4 hours | security-engineer-tech | Quality |
| 14 | `agent-utilization-boop` | 4 hours | pattern-detector | Quality/Infrastructure |
| 15 | `morning-consolidation-boop` | Daily | result-synthesizer | Learning |
| 16 | `intel-scan-boop` | Daily | web-researcher | Learning |
| 17 | `jared-ping-boop` | Daily | result-synthesizer | Communication |
| 18 | `integration-audit-boop` | Daily | integration-auditor | Quality |
| 19 | `linkedin-pipeline-boop` | Daily | linkedin-writer + linkedin-researcher | Marketing/Brand |
| 20 | `paper-digest-boop` | Weekly (Mon) | web-researcher + doc-synthesizer | Learning |
| 21 | `strategic-alignment-boop` | Weekly (Fri) | strategy-specialist | Strategy |

**Total: 21 BOOPs (5 existing + 16 new)**

---

## Implementation Priority

Jared: approve this list, then implementation should happen in this order:

**Tier A — Implement First (High value, low complexity):**
1. `telegram-health-boop` — prevents silent communication failure
2. `email-check-boop` — constitutional requirement, should already exist
3. `morning-consolidation-boop` — fixes session drift (biggest pain point)
4. `agent-utilization-boop` — enforces the "54 agents must be used" rule

**Tier B — Implement Second:**
5. `memory-write-boop` — ensures learning compounds
6. `context-window-boop` — prevents silent context degradation
7. `jared-ping-boop` — proactive transparency

**Tier C — Implement Third (Marketing cadence):**
8. `content-pipeline-boop`
9. `bsky-presence-boop`
10. `linkedin-pipeline-boop`

**Tier D — Weekly cadence:**
11. `strategic-alignment-boop`
12. `paper-digest-boop`
13. `sister-collective-boop`

**Tier E — Already works, leave as-is:**
14-15. `security-posture-boop` + `integration-audit-boop`

---

## Design Principles Applied

1. **No BOOP runs below 25 minutes** — frequency creates noise, not signal
2. **BOOPs delegate, not execute** — the conductor triggers, agents do the work
3. **Opportunistic scheduling** — daily BOOPs fire once per session, not at a clock time
4. **State tracked in `.claude/scheduled-tasks-state.json`** — existing infrastructure
5. **Ohtani principle** — these are the 64 specific habits behind the big goal. Each BOOP is a checked box that compounds into something extraordinary over months.

---

*Produced by strategy-specialist | 2026-02-21*
*Building on prior design from 2026-02-21 memory entry*
*File: `/home/jared/projects/AI-CIV/aether/to-jared/aether-boop-schedule.md`*
