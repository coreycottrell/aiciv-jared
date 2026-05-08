# Integration Audit BOOP — 2026-04-28

**Auditor**: integration-auditor
**Scope**: Recent deliverables → discoverability check
**Window**: Last 14-30 days

## Finding 1: Skills Registry Stale (HIGH)

**Registry**: `.claude/skills-registry.md` — last updated 2026-03-31 (28 days stale)
- Claims: 130 skills cataloged
- Reality: 150 SKILL.md files on disk
- **Drift: ~20 skills built but buried**

**Confirmed missing from registry** (modified in last 14 days):
1. `greenlit-execute` — execution authority skill (CONSTITUTIONAL — recent feedback rule)
2. `pre-build-checklist` — 7-question pre-build framework (CONSTITUTIONAL)
3. `content-creation-sop` — content workflow
4. `team-comms-whitelist` — team comms routing
5. `cross-domain-transfer` — knowledge transfer
6. `purebrain-social-design` — brand design standards

**Impact**: Skills exist on disk but won't surface in registry searches. Agents auto-load them via YAML frontmatter, but humans/agents browsing registry won't find them. Two are CONSTITUTIONAL.

**Owner**: capability-curator (registered for weekly Monday 9am scans — not running)

## Finding 2: Recent Tools Not Catalogued

6 new Python tools in last 7 days, no central tools registry verified:
- `purebrain_log_server.py` (M)
- `post_april27_skills.py`
- `analytics_deep_dive_apr25.py`
- `blog_audio_chatterbox.py`
- `agentmail_monitor.py` (M)
- `sync_blog_memories.py`

## Finding 3: Activity Volume

- 37 agent manifests modified in last 30 days
- 24 skills modified in last 30 days
- High velocity = registry drift compounds fast

## Recommendations

1. **Route to capability-curator immediately** to refresh `.claude/skills-registry.md` to 150 entries
2. **Verify weekly Monday 9am autonomous scan** is actually scheduled (claim vs reality)
3. **Constitutional skills (`greenlit-execute`, `pre-build-checklist`) need registry presence** — they're load-bearing rules

## Status: ⚠️ PARTIAL — Built but Buried

Skills work via YAML auto-load, but registry as discovery surface is stale.
