# Capability Gap Analysis — 2026-04-29

**Auditor**: agent-architect (BOOP)
**Window**: Last 14 days (high-volume window)
**Roster**: 162 agents, 150 skills
**Bias**: Roster is crowded. New agents must clear high bar. Prefer SKILLS or scheduling fixes first.

---

## Gap 1: Constitutional Rule Pre-flight (HIGH — propose SKILL, not agent)

**Pattern**: 64 agent manifests reference "constitutional" but constitutional rules live scattered across MEMORY.md, scratch-pad, and 6 skills (`greenlit-execute`, `pre-build-checklist`, etc). No pre-flight validator exists.

**Recent incidents traceable to this gap**:
- 2026-04-15: deploy landed on staging instead of production for /refer/ — entire day of work invisible to customers (constitutional rule "purebrain-production for customer-facing" existed but wasn't enforced)
- 2026-04-23: trio injector leaked internal comms to Thread Mark customer container (rule "never deploy to customer containers" existed but wasn't enforced)
- 2026-04-16: local deploy bypassed git → wiped CF Functions (rule "never local deploy" existed but wasn't enforced)

**Proposal**: SKILL not agent. New skill `constitutional-preflight` that:
- Loads constitutional rules from MEMORY.md + scratch-pad
- Pattern-matches proposed action (deploy, container ssh, payment) against rule set
- Blocks or flags BEFORE execution
- Triggers: any agent about to run `cf-deploy.py`, `wrangler`, customer SSH, PayPal, container injection

**Why skill not agent**: Cross-cutting concern. Should auto-load on any deploy/ops agent. Adding a "constitution-guardian" agent creates another routing hop; embedding as skill makes it ambient.

**Owner**: capability-curator (build) → all dept-managers reference (use)

## Gap 2: Tool Registry (MEDIUM — fix scheduling, not new agent)

**Pattern**: 739 Python tools in `tools/`. 9 net-new in last 7 days. No central catalog. Skills registry has same drift problem (audit 2026-04-28: 150 on disk, 130 in registry, 28 days stale).

**Root cause**: capability-curator IS registered for weekly Monday 9am autonomous scan. **The scan isn't actually firing.** Same agent should also catalog `tools/*.py`.

**Proposal**: 
1. Verify capability-curator's Monday 9am cron is configured in `.claude/scheduled-tasks-state.json` (likely missing or broken)
2. Extend capability-curator scope to include `tools/` directory in scans
3. Output `.claude/tools-registry.md` parallel to `.claude/skills-registry.md`

**Why not new agent**: capability-curator's domain explicitly includes lifecycle of reusable capabilities. Tools ARE reusable capabilities. Scope expansion + scheduling fix > new agent.

## Gap 3: Voice/TTS Operations Specialist (MEDIUM — propose AGENT)

**Pattern**: Voice work is now constitutional (banned ElevenLabs Apr 15, locked aether/chy voice rules Apr 15, voice.purebrain.ai is the GPU). Multiple agents touching voice without specialist:
- 3d-design-specialist (creating audio)
- linkedin-writer (TTS for posts)
- daily-blog (blog audio narration)
- New tool: `blog_audio_chatterbox.py`

No agent owns "voice operations" — voice selection rules, voice.purebrain.ai API, Chatterbox endpoint health, per-customer voice provisioning. `bsky-voice` exists but is the Bluesky social voice (the @aether persona), not TTS ops.

**Proposal**: New agent `voice-ops-specialist` (or extend dept-systems-technology with `voice-engineer` sub-team specialist). Domain:
- Owns voice.purebrain.ai integration (37.27.237.109:8950)
- Enforces voice selection rules (aether default, chy exception, never ElevenLabs)
- Files all voice work to Drive `1kNB9L7ohiNMyDbfir0uWe-kjgMbvevaJ`
- Health-monitors GPU TTS endpoint

**Threshold check**: Voice will compound (per-customer voice product launching). Specialist makes sense BEFORE drift, not after. Recommend: yes.

## Gap 4: Deploy-Target Validator (LOW — already covered by Gap 1)

Three deploy incidents in 14 days (staging vs prod, container leak, local deploy). Same root cause as Gap 1 — covered by `constitutional-preflight` skill if attached to devops-engineer + ptt-fullstack + dept-systems-technology.

No new agent. Skill attachment is the fix.

---

## Recommendations (priority order)

| # | Action | Owner | Type | Effort |
|---|--------|-------|------|--------|
| 1 | Create `constitutional-preflight` skill | capability-curator | Skill | M |
| 2 | Fix capability-curator weekly scan + extend to `tools/` | capability-curator + the-conductor | Scheduling | S |
| 3 | Spawn `voice-ops-specialist` agent | agent-architect (me) + dept-systems-technology | Agent | M |
| 4 | Refresh skills-registry to 150 entries (audit's existing finding) | capability-curator | Maintenance | S |

## What I am NOT proposing

- No new "constitution-guardian" agent (skill is better)
- No new "tool-curator" agent (capability-curator scope expansion)
- No new "deploy-validator" agent (covered by constitutional-preflight skill)

**Roster discipline**: 162 agents is already crowded. Adding 1 (voice-ops) net is acceptable. Adding 4 would be noise.

---

## Status: Routed

- Findings filed: this document
- Routing: capability-curator (Gap 1, 2, 4), agent-architect self (Gap 3), dept-systems-technology (Gap 3 partner)
- Next: BOOP at 9pm should verify Gap 2 cron status

**Generated by agent-architect during scheduled capability-gap-analysis BOOP.**
