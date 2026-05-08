# Analyzer BOOP Audit Gate Patch — 2026-04-29

**Issued by**: dept-systems-technology
**Routed to**: full-stack-developer (apply patches) + qa-engineer (dry-run verify)
**Constitutional**: false-positive convergence breaks routing-quality bar (`feedback_cross_boop_convergence_signal.md`)

---

## The Bug

Last night (2026-04-28→29), two BOOPs falsely converged on:

- "skills registry has 130 entries vs 150 on disk (drift, 28 days stale)"
- "capability-curator weekly scan broken/unregistered"
- "constitutional skills `greenlit-execute` and `pre-build-checklist` buried/missing"

**Ground truth verified by manual fire** (`exports/capability-curator/capability-scan-2026-04-29.json`):
- Registry: **152/152 in sync**, 0 drift
- capability-curator IS registered (`weekly-monday`, last_run 2026-04-29T17:32:18Z)
- All 5 constitutional skills present in registry AND on disk
- 0 missing, 0 stub, 0 broken

**Root cause**: The two analyzer BOOPs (`capability-gap-analysis` run by `agent-architect`, and `integration-audit` run by `integration-auditor`) reported count-deltas without naming specific items, and there was no sanity gate forcing them to re-grep before flagging. They share heuristics (count-based deltas) so their "convergence" was not independent corroboration — it was the same false-positive emitted twice.

The two affected skills/agents:

1. `.claude/skills/capability-gap-boop/SKILL.md` — drives `capability-gap-analysis` BOOP, agent: `agent-architect`
2. `.claude/agents/integration-auditor.md` + integration-audit BOOP entry in `.claude/scheduled-tasks-state.json`

---

## Patch 1: capability-gap-boop SKILL.md

**File**: `/home/jared/projects/AI-CIV/aether/.claude/skills/capability-gap-boop/SKILL.md`

**Insert this section IMMEDIATELY BEFORE the existing `## Output Format` heading** (current line ~140):

```markdown
## 🔴 MANDATORY AUDIT GATE (added 2026-04-29 — fixes false-convergence bug)

**Before flagging ANY of: "registry stale", "registry drift", "skills missing/buried", "scheduled task broken/unregistered" — you MUST satisfy this gate. No exceptions.**

### Step A — Read the actual artifacts fresh (no caching, no assumptions)

For every claim about registry state, scheduled-task state, or skill presence, run these in the SAME BOOP cycle (do not rely on a cached snapshot from a prior cron run):

\`\`\`bash
REGISTRY=/home/jared/projects/AI-CIV/aether/.claude/skills-registry.md
SKILLS_DIR=/home/jared/projects/AI-CIV/aether/.claude/skills
TASKS=/home/jared/projects/AI-CIV/aether/.claude/scheduled-tasks-state.json

ls -la "$REGISTRY" "$TASKS"   # capture mtimes — print these in the report
DISK_COUNT=$(ls -d "$SKILLS_DIR"/*/ 2>/dev/null | wc -l)
REGISTRY_COUNT=$(grep -c '^| \`[a-z]' "$REGISTRY")   # skill rows only
\`\`\`

### Step B — Print these audit fields in the report (MANDATORY — report is INVALID without them)

- `artifact_path` for every file read
- `artifact_mtime` for each
- `disk_count` (actual `ls`-derived)
- `registry_count` (actual `grep`-derived)
- `delta` = disk_count − registry_count (signed)
- For every claimed-missing skill: its **NAME**, not just a delta number
- For every claimed-broken scheduled task: its **JSON-key name**, `last_run`, `frequency`, `status`

### Step C — Sanity gate (BEFORE firing the alert)

For each item you intend to flag as missing/broken/stale, RE-VERIFY against the live artifact:

\`\`\`bash
# Skill claimed missing from registry
NAME="<skill-name>"
grep -q "\\\`${NAME}\\\`" "$REGISTRY" \\
    && echo "ABORT_FLAG: ${NAME} IS in registry — false-positive prevented" \\
    || echo "CONFIRMED_MISSING: ${NAME}"

# Scheduled task claimed unregistered/broken
TASK="<task-key>"
python3 -c "
import json
d = json.load(open('$TASKS'))
if '$TASK' in d.get('tasks', {}):
    t = d['tasks']['$TASK']
    print(f'ABORT_FLAG: $TASK IS registered. last_run={t.get(\\\"last_run\\\")} status={t.get(\\\"status\\\")}')
else:
    print(f'CONFIRMED_UNREGISTERED: $TASK')
"
\`\`\`

**Stale definition**: mtime > 7 days AND delta != 0. If delta == 0 the registry is IN SYNC regardless of mtime age. Do not flag a synced registry as stale.

If the gate aborts, log under "false-positive averted" in the report (so trend tracking still sees the near-miss) but DO NOT FIRE THE ALERT.

### Step D — Cross-BOOP convergence guard

Before treating "two BOOPs agree" as high signal:
- If the other BOOP's claim is also a count delta with NO named items, it is NOT independent corroboration — they may share the same heuristic. **Do not escalate count-only convergence.**
- Convergence is high-signal ONLY when both BOOPs name the SAME specific items (skill names, task keys, file paths).
```

---

## Patch 2: integration-auditor manifest

**File**: `/home/jared/projects/AI-CIV/aether/.claude/agents/integration-auditor.md`

**Insert this section IMMEDIATELY AFTER the existing `## Audit Methodology` block** (around line 175, after Phase 4):

```markdown
## 🔴 MANDATORY AUDIT GATE (added 2026-04-29 — fixes false-convergence bug)

**Before flagging "registry drift", "skills missing/buried", "constitutional skills not registered", or "scheduled task broken" — you MUST follow the same audit gate as capability-gap-boop. See `.claude/skills/capability-gap-boop/SKILL.md` § "MANDATORY AUDIT GATE".**

Specific to integration-auditor:

1. **Read freshly** — never trust a cached snapshot from a prior cron run. Re-read `skills-registry.md` and `scheduled-tasks-state.json` IN this BOOP cycle (capture mtimes in the report).

2. **Name every flag** — when you say "20 skills are buried", you MUST list all 20 names. If you can't list them, the flag is invalid.

3. **Re-grep before firing** — for each constitutional skill you suspect is missing, run:
   \`\`\`bash
   grep -n '`greenlit-execute`\\|`pre-build-checklist`\\|`memory-first-protocol`\\|`verification-before-completion`\\|`delegation-spine`' /home/jared/projects/AI-CIV/aether/.claude/skills-registry.md
   \`\`\`
   If the grep returns matches, the constitutional skill IS registered. ABORT the flag.

4. **Stale ≠ drift** — registry mtime age alone is not a problem; only mtime > 7 days WITH a non-zero count delta is "drift". Never flag a synced registry as stale just because the file is old.

5. **Convergence sanity** — if a count delta is the only evidence and another BOOP reports the same delta, that is NOT independent corroboration. Both may be using the same flawed heuristic. Require named items to call it convergence.
```

---

## Patch 3: tighten scheduled-tasks-state.json descriptions (optional but recommended)

**File**: `/home/jared/projects/AI-CIV/aether/.claude/scheduled-tasks-state.json`

For both `capability-gap-analysis` and `integration-audit-boop`, append to the `description` field:

> "MUST follow audit gate in capability-gap-boop SKILL § MANDATORY AUDIT GATE. Report INVALID without artifact_path/mtime fields and named (not count-only) flags."

---

## Verification (qa-engineer dry-run plan)

After patches applied, run both BOOPs in dry-run mode and confirm:

1. Each BOOP report includes `artifact_path` + `artifact_mtime` for `skills-registry.md` and `scheduled-tasks-state.json`
2. Each report shows `disk_count=152, registry_count=152, delta=0`
3. Each report explicitly states `IN_SYNC` (not "drift")
4. Each report names `capability-curator` as registered with `last_run=2026-04-29T17:32:18Z` (not "broken/unregistered")
5. Each report names all 5 constitutional skills as present (not "missing/buried")
6. If either report still fires a `count-only` alert, the patch is incomplete — re-route to full-stack-developer.

Dry-run command pattern (qa-engineer):

```
Task(agent-architect): Run capability-gap-boop in REPORT-ONLY mode against current state. Apply the new MANDATORY AUDIT GATE. Print all required audit fields. Do not send Telegram alerts.

Task(integration-auditor): Run integration audit on .claude/skills/ and .claude/scheduled-tasks-state.json. Apply the new MANDATORY AUDIT GATE. Print all required audit fields. Do not send Telegram alerts.
```

Both reports MUST conclude `IN_SYNC` (152/152, 5/5 constitutional, capability-curator registered + fired today). If either still claims drift, the patch failed.

---

## Why this patch (not a redesign)

- Doesn't touch the BOOPs' analytical logic — only adds an audit/sanity-gate layer
- Forces named flags (count-only flags = false-positive risk)
- Forces fresh reads (no cached snapshots)
- Defines "stale" precisely (mtime alone is not drift)
- Neutralizes the cross-BOOP false-convergence pattern by requiring named-item agreement, not count-delta agreement
- Constitutional alignment: routing-quality is constitutional; false-positive analyzers manufacture work and break the conductor-of-conductors loop

---

## Memory Path

Capture as: `.claude/memory/agent-learnings/dept-systems-technology/2026-04-29--analyzer-boop-audit-gate-patch.md`
Type: teaching
Topic: false-positive convergence between count-based analyzers, fixed by mandatory audit gate
