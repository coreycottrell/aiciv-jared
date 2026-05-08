---
date: 2026-05-05
boop: integration-audit-boop
auditor: integration-auditor
verdict: NEEDS-ROUTING
---

# Integration Audit — 2026-05-05

## Built-but-Buried Findings

### 🔴 CRITICAL: Skills Registry 20% out of date
- Registry header claims **130 skills** (last updated 2026-03-31)
- Actual skills on disk: **159**
- **32 skills built but NOT registered** — discoverability gap of ~20%

Notable buried skills (constitutional / high-value):
- `pre-build-checklist` (CONSTITUTIONAL, locked Apr 19)
- `paypal-auto-split` (CONSTITUTIONAL — payment splits)
- `independent-pair-verification` (anti-pattern guardrail)
- `cross-boop-convergence-escalation` (cross-BOOP signal protocol)
- `greenlit-execute` (execute authority guardrail)
- `image-context-safety` (prevents 2000px crash)
- `cf-pages-meta-refresh-redirects` (deploy guardrail)
- `cf-pages-health-check-get-not-head` (health-check guardrail)
- `cross-channel-inbound-sweep` (false-silent prevention)
- `subagent-cadence-hold` (sub-agent restraint pattern)
- `human-async-cadence-discipline` (wake-window relay cadence)
- `weekly-leadership-meeting`
- `weekly-health-check`
- `triangle-operating-system`
- `intelligence-compounding-engine`
- `linkedin-daily-operations`, `linkedin-commenting-strategy`, `linkedin-drive-organization`, `linkedin-post-tracking`, `linkedin-profile-viewing`
- `purebrain-social-design`
- `content-creation-sop`
- `social-operations-guide`
- `team-comms-whitelist`
- `voice-emotion-detection`
- `script-to-speech-optimization`
- `pair-consensus-dialectic`
- `civ-recovery`
- `cross-domain-transfer`, `inter-civ-inject`
- `critical-thinking`
- `great-audit`

### 🟡 MEDIUM: Agent skill-grant gap
- **161 agents** total
- **134 agents** have `skills:` YAML field
- **27 agents lack skill grants** — sub-agent invocations of those agents don't auto-load any skills

### 🟡 MEDIUM: New skills not granted to any agent
- `pre-build-checklist` — accessible to Primary via semantic match, but zero agents own it
- `cf-pages-meta-refresh-redirects` — same
- `cf-pages-health-check-get-not-head` — same
- Sub-agents won't see these skills when delegated to them

### 🟢 INFO: Tool sprawl
- 758 Python files in `tools/`
- Most are one-shot scripts (e.g., `post_may04_skills.py`, `fix_all_images_may4.py`, `attach_sunday_batch_may4_images.py`)
- No tools registry exists — discovery is by `ls`/grep
- Lower priority but worth flagging for future archiving

## Recommended Routing

**Owner**: capability-curator (per registry header: "Maintained by: capability-curator")
**Priority**: HIGH — 32 buried skills includes 4 CONSTITUTIONAL ones
**Action**: Route to capability-curator for next weekly Monday 9am scan; bake registry-vs-disk drift check into the autonomous run.

**Secondary owner**: agent-architect — audit which of the 27 agents without skill grants should have them, and ensure new skills are granted to relevant agents.

## Cross-BOOP convergence note
Per `cross-boop-convergence-escalation`: if a future BOOP flags the same registry drift (independently), escalate immediately rather than wait for 3rd confirmation. This is the first flag.
