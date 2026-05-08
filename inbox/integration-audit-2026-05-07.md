# Integration Audit — 2026-05-07

**Auditor**: integration-auditor (BOOP)
**Scope**: Recent skills/agents/tools — discoverability check.

---

## 🔴 BUILT-BUT-BURIED: 33 skills missing from registry

Skills directory has **160** skills. `skills-registry.md` lists **130** (last updated 2026-03-31, ~5 weeks stale). **33 skills filed in `.claude/skills/` are NOT discoverable via the registry.**

### Critical/recent ones missing

| Skill | Filed | Severity |
|---|---|---|
| `pre-deploy-credential-scan` | 2026-05-07 (today) | 🔴 CRITICAL — addresses Phil creds leak; flagged in MEMORY as "skill filed ≠ skill enforced" anti-pattern |
| `cf-pages-health-check-get-not-head` | 2026-05-03 | 🟡 prevents false-positive 200s |
| `cf-pages-meta-refresh-redirects` | recent | 🟡 cf-deploy.py bug fix |
| `human-async-cadence-discipline` | 2026-05-03 | 🟡 discipline pattern |
| `subagent-cadence-hold` | recent | 🟡 platform constraint doc |
| `independent-pair-verification` | recent | 🟡 quality gate |
| `cross-boop-convergence-escalation` | recent | 🟡 escalation pattern |
| `cross-channel-inbound-sweep` | recent | 🟡 anti-false-silent |
| `greenlit-execute` | recent | 🟡 execute authority |
| `pre-build-checklist` | recent | 🔴 constitutional 7Q |
| `weekly-leadership-meeting` | recent | normal |
| `voice-emotion-detection` | recent | normal |

Full delta: civ-recovery, content-creation-sop, critical-thinking, cross-domain-transfer, great-audit, image-context-safety, intelligence-compounding-engine, inter-civ-inject, linkedin-commenting-strategy, linkedin-daily-operations, linkedin-drive-organization, linkedin-post-tracking, linkedin-profile-viewing, pair-consensus-dialectic, paypal-auto-split, purebrain-social-design, script-to-speech-optimization, social-operations-guide, team-comms-whitelist, triangle-operating-system, weekly-health-check.

---

## 🟡 PHANTOM REGISTRY ENTRIES: 9

Listed as "skills" in registry but not present in `.claude/skills/`:
- `browser-vision-tester`, `code-archaeologist`, `human-liaison`, `security-auditor`, `test-architect`, `the-conductor`, `web-researcher` — these are **agents**, not skills (registry confusion)
- `pure-influence`, `waitlist` — don't exist anywhere

---

## 🔴 ENFORCEMENT GAP: `pre-deploy-credential-scan`

Today's MEMORY entry `feedback_skill_filed_does_not_equal_skill_enforced.md` warned that filing a skill ≠ wiring it. Audit confirms:

- Skill exists at `.claude/skills/pre-deploy-credential-scan/SKILL.md` ✅
- NOT in `skills-registry.md` ❌
- NOT referenced in `.claude/skills/delegation-spine/SKILL.md` ❌
- NOT linked in any agent manifest under `skills:` ❌
- NOT integrated into `tools/cf-deploy.py` as a pre-deploy gate ❌

**The very anti-pattern we documented is reproducing in real time.**

---

## ✅ HEALTHY

- `AGENT-CAPABILITY-MATRIX.md` exists (428 lines)
- Recent agent edits (`linkedin-specialist.md`, `claim-verifier.md` Apr 29) — agents have YAML frontmatter intact
- No new agents added this week (matches "new-agent bar" discipline)

---

## RECOMMENDED ROUTES

1. **CO# / capability-curator**: Sync `skills-registry.md` — add 33 missing entries, remove 9 phantom entries, bump "Last Updated" to 2026-05-07, fix "Total Skills" count.
2. **ST#**: Wire `pre-deploy-credential-scan` into `tools/cf-deploy.py` as pre-deploy gate (per today's MEMORY directive).
3. **agent-architect**: Audit which agent manifests should add the new skills (`pre-deploy-credential-scan` → security-auditor, refactoring-specialist; `independent-pair-verification` → integration-auditor; `pre-build-checklist` → cto, agent-architect).

---

**Status**: Audit complete. Findings filed. Routing recommendations attached. Not auto-routing per sub-agent constraint (BOOP sub-agent cannot Task-call dept managers) — Primary should dispatch.
