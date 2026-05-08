---
type: integration-audit
date: 2026-05-01
auditor: integration-auditor (BOOP)
scope: discoverability of recent deliverables
---

# Integration Audit — 2026-05-01

## Summary

**Status**: 🟡 YELLOW — Multiple built-but-buried items. Skills registry stale by 30 days. Constitutional skills not wired to any agent.

## Findings

### 🔴 HIGH: Constitutional skills exist on disk but no agent has them granted

| Skill | Disk path | Agents with skill granted |
|-------|-----------|---------------------------|
| `pre-build-checklist` | `.claude/skills/pre-build-checklist/` | **0** |
| `greenlit-execute` | `.claude/skills/greenlit-execute/` | **0** |
| `purebrain-social-design` | `.claude/skills/purebrain-social-design/` | **0** |

These are flagged CONSTITUTIONAL in MEMORY.md but no agent manifest auto-loads them. They only fire if Primary semantic-matches them. That's a discoverability gap for delegated work.

**Recommended owners** (route via dept managers):
- `pre-build-checklist` → grant to ALL builder agents (full-stack-developer, web-dev, sol-dev, ptt-fullstack, wtt-fullstack, arcx-coder, cts-fullstack)
- `greenlit-execute` → grant to ALL ops/exec sub-agents (every dept manager + their specialists)
- `purebrain-social-design` → grant to 3d-design-specialist, marketing-strategist, linkedin-writer, content-specialist, social-media-specialist

### 🟡 MEDIUM: skills-registry.md is stale

- Registry last updated **2026-03-31** (30 days ago)
- Registry claims **130 skills**; actual on disk: **152 skills**
- **25 skills missing from registry** (full list in audit log, including the 3 constitutional ones above plus): `civ-recovery`, `content-creation-sop`, `critical-thinking`, `cross-domain-transfer`, `great-audit`, `image-context-safety`, `intelligence-compounding-engine`, `inter-civ-inject`, `linkedin-commenting-strategy`, `linkedin-daily-operations`, `linkedin-drive-organization`, `linkedin-post-tracking`, `linkedin-profile-viewing`, `pair-consensus-dialectic`, `paypal-auto-split`, `script-to-speech-optimization`, `social-operations-guide`, `team-comms-whitelist`, `triangle-operating-system`, `voice-emotion-detection`, `weekly-health-check`, `weekly-leadership-meeting`

**Owner**: `capability-curator` (registry says "autonomous Monday 9am scans" — they haven't fired). Route via dept-systems-technology with skill-audit task.

### 🟢 LOW: Recent agents present and discoverable

- `linkedin-specialist.md` (Apr 29) — referenced in AGENT-CAPABILITY-MATRIX, route is clear
- `3d-design-specialist.md` (Apr 21) — referenced in MEMORY.md as image owner, discoverable
- `claim-verifier.md` (Apr 29) — already in CLAUDE.md table

### 🟢 LOW: Recent tools wired correctly

- `tools/linkedin_comment_scheduler.py` v55 refactor — has companion state file
- `tools/agentmail_monitor.py` — daemonized, log file exists
- `tools/trio_*` triad — three companions deployed together (primary_injector, watcher, auto_responder)

## Routing Recommendations

1. **ST# (dept-systems-technology)**: capability-curator runs a skill-audit pass to refresh `skills-registry.md` to v152 and add the missing 25 entries.
2. **CO# (dept-corporate-org)**: amend agent manifests to grant `pre-build-checklist`, `greenlit-execute`, `purebrain-social-design` per the table above. These are constitutional — they need to auto-load on relevant invocations, not depend on Primary semantic matching.
3. **OP# (verifier)**: pair this audit with a verification BOOP in 7 days to confirm both routes closed.

## Convergence Signal

This is the second audit in 60 days flagging registry/manifest drift. Per `feedback_cross_boop_convergence_signal.md` — fix now, don't wait for a third.
