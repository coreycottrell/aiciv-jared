# ADR-001: Boop Executor Constitutional Fairness Lane

**Status:** Approved-with-amendments (CTO 2026-05-16 02:15 UTC) — Implemented (ST# 2026-05-16)  
**Date:** 2026-05-16  
**Deciders:** architect-agent, conductor-of-conductors (Aether), CTO (pending review)  
**Branch:** feat/magic-link-auto-login-2026-05-15  
**Day-3 default deadline:** 2026-05-19 02:00 UTC — if no verdict, bridge fix becomes permanent debt

---

## 1. Problem Statement

### 1.1 Evidence: 3h 31m Starvation

At 2026-05-16 02:00 UTC, `engineering-flow-check` — the constitutional skill enforcing the SPEC→CTO→BUILD→SECURITY→QA→SHIP pipeline — had not fired since 2026-05-15 22:30 UTC. That is **3 hours 31 minutes of silence on a 30-minute constitutional guardrail.**

Three independent probe dimensions confirmed starvation (not crash):

- **Probe 1 (file mtime):** `inbox/engineering-flow-check-2026-05-15-2230utc.md` was the newest output, 3h31m stale.
- **Probe 2 (executor log):** `logs/boop_executor.log` shows: `"Concurrency limit hit (2/2 in last 180s). Deferring remaining due tasks for 170s"` at 01:00:47 UTC. This recurred across multiple 5-minute check intervals, each time deferring engineering-flow-check.
- **Probe 3 (process trace):** No `engineering-flow-check` PID launched since 22:30. Confirmed deferral, not crash.

Additionally, the log from 2026-05-07 shows a more severe failure class: **`MAX_CONCURRENT_BOOP_AGENTS=3` was exceeded** by nightly batch agents, causing `engineering-flow-check` (along with 20+ other tasks) to be skipped on every check cycle for the duration of the nightly run. That is a different blocking vector than the 2/180s window throttle but shares the same root cause: **no constitutional task gets a guaranteed execution slot.**

### 1.2 The Constitutional Dimension

**ST# BUILD CORRECTIONS (2026-05-16, post-CTO verdict):**

1. Constitutional task name: the initial draft used `delegation-enforcer-boop`. **Actual config name is `delegation-enforcer`** (no `-boop` suffix). BUILD uses the actual config name. Per CTO Amendment 1.
2. CTO Amendment 1 also dropped `capability-gap-analysis` from the initial constitutional set (different starvation profile — it's daily, not 30min). Initial set is exactly `[engineering-flow-check, delegation-enforcer]`.
3. **`priority_order` location confirmed**: ADR Section 1.2 / Section 9 references to `scheduled-tasks-state.json` were CORRECT (ground-truth probe by ST# verified `priority_order` lives at `.claude/scheduled-tasks-state.json:8`, NOT in `boop_config.json`). The CTO verdict's claim of `boop_config.json:8-35` was a mis-citation. Net effect: `priority_order` is read from `scheduled-tasks-state.json` by `load_priority_order()`; the **new** `boop_rules` configuration block (constitutional_tasks, reserved_slots, etc.) goes in `boop_config.json` as a separate namespace per CTO Amendment 6 (static policy lives with static policy).
4. Per CTO Amendment 2: hung-agent watchdog (45min max age, SIGTERM-then-SIGKILL after 30s grace) shipped in the SAME PR as the reserved slot.
5. Per CTO Amendment 3: scheduler-level dedup replaces the rejected "skill is idempotent" claim. `fire_boop` refuses when `elapsed_since_last < interval * constitutional_dedup_window_ratio (default 0.5)`.
6. Per CTO Amendment 4: portal alarm channel only (`tools/portal_deliver.sh`), 30min rate-limit per alarm key, NO Telegram.
7. Per CTO Amendment 5: `fcntl.flock(LOCK_EX)` wraps `save_tasks` read-modify-write; sidecar lock file at `<TASKS_FILE>.lock`. Bonus: atomic write via tmp + `os.replace`.


Per `feedback_skill_filed_does_not_equal_skill_enforced.md`: "Filing a skill is not enforcing it. Every skill filing MUST end with an integration plan (which file/hook/gate). Filing=docs; wiring=enforcement."

`engineering-flow-check` is filed. It runs as a 30-minute BOOP. But it can be silently starved for hours with no alarm, no override, no reservation. The skill is filed. It is not enforced.

Additionally, `.claude/scheduled-tasks-state.json` at lines 8-35 (inside `boop_rules`) contains a `priority_order` array that lists `engineering-flow-check` at position 7. `boop_executor.py` **never reads this field.** The priority model is declared in the data model and dead in the executor. This is the scheduler-level instance of the same anti-pattern — data structure filed, code enforcement absent.

### 1.3 Scope Correction (from ST# diagnosis)

The initial conductor brief assumed `boop_config.json` had a tier/priority field. ST# confirmed via ground-truth probe: `boop_config.json` has only frequency groups (the `groups` structure at lines 4-66), no priority. The executor has two hard constants (`MAX_BOOPS_PER_WINDOW=2`, `CONCURRENCY_WINDOW_SECONDS=180`) with FIFO semantics and zero priority awareness. Any "promote to tier-1 in config" patch would be a no-op — a theater-of-action anti-pattern.

The real fix requires code changes in `boop_executor.py`.

---

## 2. Constraints

The design must satisfy all of the following:

| Constraint | Source |
|---|---|
| **CEO Rule / Delegate always** | CLAUDE.md. Aether designs, ST# builds. No self-implementation. |
| **Sub-agents cannot spawn sub-agents** | `feedback_subagents_cannot_spawn_subagents.md`. ST# dispatches specialists directly, not chained. |
| **Backup before destructive edit** | `verification-before-completion` + execute-authority rules. Any modification to `boop_executor.py` must have the current file committed to git before the change lands. |
| **Git is the only source of truth** | `feedback_wrangler_deploy_must_be_preceded_by_git_commit.md`. Modified executor must be committed before restart. No live-edit-then-restart pattern. |
| **Never deploy to customer containers** | `feedback_never_deploy_to_customer_containers.md`. Not applicable here (this is the aether home server), but the principle of clean separation applies: systemd units and Python files are not co-mingled with customer-facing code. |
| **Nothing in containers** | `feedback_nothing_in_containers_ever.md`. The executor already runs as a native process (not a container) — maintain that. |
| **Multi-tenant always applicable** | `feedback_every_feature_multi_tenant_for_customers.md`. The constitutional task set (`constitutional_tasks`) must be configurable per-deployment, not hardcoded in the source. It must live in `scheduled-tasks-state.json` or `boop_config.json` so that a fork of this collective can define its own constitutional set without patching Python. |
| **CTO pre-build review mandatory** | `feedback_cto_pre_build_architectural_review.md`. No BUILD step until CTO has reviewed and greenlighted this spec. |
| **Pre-build 7 questions answered** | `.claude/skills/pre-build-checklist/SKILL.md`. See Section 6. |
| **Bridge (systemd timer) is intentional tech debt** | ST# is shipping it tonight. This design's migration section must define the clean removal path. Do NOT touch the bridge in this spec — it is a parallel track. |
| **Starvation alarm required** | `feedback_boop_gap_requires_last_output_timestamp_check.md`. The design must include a starvation alarm: if any constitutional task exceeds 2x its scheduled interval without firing, an alert is emitted (portal or log). |
| **`verification-before-completion`** | Any implementation that claims to fix starvation must be verified by a QA probe showing the task actually fired, not just that the code path was reached. |

---

## 3. Design Options

Three options are analyzed. They are not mutually exclusive on the implementation axis, but they represent distinct architectural stances.

---

### Option A: Reserved Concurrency Slot (Fairness Lane)

**Core idea:** Expand the total concurrency cap by a reserved amount dedicated exclusively to constitutional tasks. The global cap continues to protect system resources. Constitutional tasks bypass both the window throttle (`MAX_BOOPS_PER_WINDOW / CONCURRENCY_WINDOW_SECONDS`) and the process cap (`MAX_CONCURRENT_BOOP_AGENTS`), up to the size of their reserved slot.

**Data model change (in `tools/boop_config.json`):**

```json
"constitutional_tasks": [
  "engineering-flow-check",
  "delegation-enforcer",
  "capability-gap-analysis"
],
"constitutional_reserved_slots": 1
```

**Executor logic change (in `boop_executor.py`):**

```
At fire time:
  constitutional_set = load from boop_config.json["constitutional_tasks"]
  
  if task_id in constitutional_set:
    running_constitutional = count_running_boop_agents_matching(constitutional_set)
    if running_constitutional < constitutional_reserved_slots:
      fire()   # bypass window throttle AND process cap
    else:
      apply normal throttle (do not double-fire the same constitutional task)
  else:
    apply existing window throttle + process cap as-is
```

**Additional change:** The `priority_order` array in `.claude/scheduled-tasks-state.json` (lines 8-35, inside `boop_rules`) should be read by the executor. When multiple tasks are due in the same check cycle, constitutional tasks sort to the front before any window throttle evaluation. This closes the existing data-declared-but-not-enforced gap.

**Starvation alarm:** At the end of each check cycle, for each constitutional task, compute `now - last_run`. If `elapsed > 2 * interval`, log `CONSTITUTIONAL STARVATION ALERT [task_id]: Xm overdue` at WARNING level and emit to portal via the existing notification path.

**Diagram:**

```
Check cycle fires
      |
      v
  For each due task (sorted: constitutional first, then FIFO):
      |
      +--- Is this task in constitutional_set?
      |         |
      |        YES --> Is running_constitutional < reserved_slots?
      |                    |
      |                   YES --> FIRE (bypass window + process cap)
      |                    |
      |                    NO --> Apply normal throttle (already have a constitutional agent running)
      |
      +--- NO --> Apply existing window throttle + MAX_CONCURRENT check
```

**Trade-offs:**

| Pro | Con |
|---|---|
| Minimal blast radius — existing throttle logic unchanged for non-constitutional tasks | Requires defining constitutional_set explicitly (config maintenance burden) |
| Constitutional tasks get guaranteed forward progress | If reserved_slots=1 and constitutional task hangs, the slot is occupied; no second constitutional task can fire until it drains |
| Starvation alarm added as a direct consequence of the design | Slightly more complex fire_boop dispatch path |
| Configuration lives in JSON (multi-tenant compliant) | Need to handle the edge case where two constitutional tasks are both due in the same cycle |
| Closes the priority_order-declared-but-not-read gap | Does not address the case where `constitutional_reserved_slots > 1` and system resources are tight |
| Bridge systemd timer is a clean removal after this lands (see Section 5) | |

**Estimated implementation complexity:** Medium. ~50 lines net change to `boop_executor.py`. New config keys in `boop_config.json`.

---

### Option B: Priority Queue with Aging

**Core idea:** Replace the FIFO deferred-task loop with a priority queue. Every task has a numeric priority (read from `.claude/scheduled-tasks-state.json["boop_rules"]["priority_order"]` ordinal position, or from a new `"priority": N` field). Tasks that are overdue accrue an age bonus, preventing indefinite starvation of any task regardless of constitutional status.

**Data model change:**

Extend each task entry:
```json
"engineering-flow-check": {
  ...
  "priority": 10
}
```
Or derive priority from ordinal position in `priority_order` (lower index = higher priority).

**Executor logic change:**

When multiple tasks are due, sort by: `effective_priority = base_priority + aging_bonus(overdue_seconds)`. Fire the highest effective_priority task first within the existing cap.

**Aging formula (example):**

```
aging_bonus = min(overdue_seconds / interval_seconds, 5.0) * priority_weight
```

This means a task that is 2x overdue has ~2x its base priority for scheduling purposes.

**Trade-offs:**

| Pro | Con |
|---|---|
| No hardcoded constitutional set — any task can be prioritized | Aging arithmetic makes behavior harder to reason about; engineering-flow-check at 3h overdue may still lose to a task with 4x higher base priority |
| More general mechanism; handles graceful degradation under all task types | Does NOT provide a hard guarantee of forward progress for constitutional tasks — only probabilistic preference |
| `priority_order` array already exists; this makes it live | Priority values must be maintained as the task set grows; operational burden |
| Works for future constitutional tasks without schema changes | Requires careful tuning to prevent priority inversion |
| | Does not naturally produce a starvation alarm — alarm must be a separate monitor |

**Estimated implementation complexity:** High. Requires refactoring the entire due-task dispatch loop, introducing a heap or sorted list, and defining/maintaining priority values for all tasks.

**Fatal flaw for this use case:** Aging does not guarantee constitutional task execution. Under the observed failure mode (nightly batch occupying all 3 process slots for hours), a priority queue still evaluates against the process cap. Engineering-flow-check with the highest effective priority in the world still returns False from `count_running_boop_agents()`. The problem is resource reservation, not sort order.

---

### Option C: Raised Global Cap with Constitutional Pre-Emption

**Core idea:** Raise `MAX_CONCURRENT_BOOP_AGENTS` from 3 to 4 or 5, and raise `MAX_BOOPS_PER_WINDOW` from 2 to 3. No reserved slot logic — just more headroom. Optionally add a lightweight pre-emption rule: if a constitutional task has been starved for more than 1.5x its interval, one running non-constitutional agent's completion is awaited (or a new slot is force-opened up to a higher cap of 5) before firing.

**Trade-offs:**

| Pro | Con |
|---|---|
| Minimal code change — just bump constants | Raises resource consumption on the host machine (each claude agent is a full LLM session) |
| No config schema changes | Does not solve the root cause: no priority awareness. Nightly batch filling 4 slots is just as blocking as filling 3 slots |
| Reduces congestion under normal load | Pre-emption logic is operationally risky: killing a running agent mid-task can corrupt its output files, leave partial writes, or violate `verification-before-completion` |
| | Does not close the `priority_order` declared-but-not-read gap |
| | Not a structural solution — scaling task count will hit the cap again |

**Estimated implementation complexity:** Low (cap raise alone) to High (pre-emption logic). Cap raise alone does not solve the constitutional starvation problem; it delays its recurrence.

---

## 4. Recommendation

**Chosen Option: Option A — Reserved Concurrency Slot (Fairness Lane)**

**Rationale:**

1. **Hard guarantee vs. probabilistic preference.** Option B (priority queue) improves the odds of constitutional tasks firing but cannot guarantee it when all process slots are occupied. Option A's reserved slot is a hard guarantee: constitutional tasks always have at least one slot available that no non-constitutional task can occupy.

2. **Minimal blast radius.** Option A changes only the dispatch decision point for constitutional tasks. The existing throttle logic for all non-constitutional tasks is untouched. This reduces regression risk.

3. **Closes the existing declared-but-dead data gap.** The `priority_order` array is read and used to sort tasks before throttle evaluation. This is a low-effort closure of a constitutional anti-pattern (data model declared, code enforcement absent) that ST# identified in the scope correction.

4. **Multi-tenant compliant.** Constitutional set lives in `boop_config.json`, not hardcoded. Any deployment can define its own set.

5. **Bridge removal is clean.** The systemd timer bridge fires engineering-flow-check independently of boop_executor. When Option A lands, the reserved slot means boop_executor itself fires the task reliably. The bridge becomes redundant and can be removed via `systemctl disable --now engineering-flow-check-bridge.timer` plus a git commit deleting the unit file. No residual entanglement.

6. **Starvation alarm is a first-class output.** The alert at 2x interval overdue closes the silent-failure risk that let this starvation go undetected for 3h31m.

**Recommended constants:**

- `constitutional_reserved_slots = 1` initially. This allows one constitutional agent to always be running regardless of the global cap. Review after 30 days of operational data.
- `CONSTITUTIONAL_STARVATION_ALERT_MULTIPLIER = 2.0` — alert fires when `elapsed > 2 * interval`.

**What is NOT in scope for this ADR:**

- Changing `MAX_CONCURRENT_BOOP_AGENTS` or `CONCURRENCY_WINDOW_SECONDS` for non-constitutional tasks.
- Implementing Option B priority queue as a parallel mechanism (can be considered in a follow-on ADR if operational data shows non-constitutional starvation patterns).
- Modifying any systemd unit files (ST# bridge track is independent).

---

## 5. Migration Path: Removing the Systemd Bridge

ST# is shipping a dedicated systemd timer for engineering-flow-check tonight as intentional tech debt. The bridge fires the task independent of boop_executor. After Option A lands, the bridge must be removed cleanly.

**Removal preconditions (all must be true before bridge removal):**

1. Option A code is committed to git and boop_executor is restarted with the new code.
2. At least 3 consecutive successful fires of `engineering-flow-check` via boop_executor are observed in `logs/boop_executor.log` (not via the bridge's separate log).
3. The starvation alarm has not fired since restart (confirms the reserved slot is working).
4. CTO has signed off on the Option A implementation.

**Removal steps:**

```bash
# 1. Stop and disable the bridge timer
systemctl disable --now engineering-flow-check-bridge.timer

# 2. Remove the unit file
rm /etc/systemd/system/engineering-flow-check-bridge.timer
rm /etc/systemd/system/engineering-flow-check-bridge.service  # if exists
systemctl daemon-reload

# 3. Commit the deletion
git add -A
git commit -m "infra: remove engineering-flow-check bridge timer (superseded by fairness lane ADR-001)"

# 4. Verify: boop_executor still fires the task within its next 2 check intervals
# Watch: grep "engineering-flow-check" logs/boop_executor.log | tail -5
```

**Rollback path:** If after bridge removal engineering-flow-check shows >2x interval gap, re-enable the bridge immediately: `systemctl enable --now engineering-flow-check-bridge.timer`. Then debug via the starvation alarm path rather than deploying blind.

---

## 6. CTO Review Gate Questions

The following must be greenlighted by CTO before ST# proceeds to BUILD:

1. **Resource budget:** `constitutional_reserved_slots = 1` means the host may run `MAX_CONCURRENT_BOOP_AGENTS + 1` Claude processes simultaneously (3 + 1 = 4) during constitutional-task firing. Is 4 concurrent Claude sessions within the host's token budget and memory envelope?

2. **Constitutional set scope:** The initial constitutional set is `[engineering-flow-check, delegation-enforcer, capability-gap-analysis]`. Should `conductor-of-conductors` (60min, position 1 in priority_order) also be in the constitutional set? It is the orchestration heartbeat. Recommend CTO decision on whether the conductor qualifies as "constitutional" for slot reservation purposes.

3. **Hung agent handling:** If a constitutional task launches but hangs (e.g., Claude session does not exit), its PID remains in `count_running_boop_agents_matching(constitutional_set)`. The reserved slot is consumed indefinitely. Should we add a max-age watchdog (e.g., kill constitutional agent PIDs older than 45 minutes) as part of this implementation, or defer to a follow-on watchdog ADR?

4. **`scheduled-tasks-state.json` write contention:** Option A reads `constitutional_tasks` from `boop_config.json` on every check cycle. The runtime state file (`scheduled-tasks-state.json`) is written by `save_tasks()` on every successful fire. This is single-threaded today (one executor process), so there is no race. Confirm CTO agrees single-process assumption remains valid and there is no plan to run multiple executor instances.

5. **Bridge coexistence during transition:** After Option A ships but before the bridge is removed, both mechanisms fire engineering-flow-check. This means it may fire twice within a 30-minute window (once via bridge, once via executor). The task's `last_run` is updated by the executor. Does double-firing create any idempotency concern for the engineering-flow-check skill itself? CTO and QA should confirm the skill is safe to run twice in a window.

6. **Alert channel:** The starvation alarm at 2x interval overdue currently logs at WARNING level. Should it also emit to the portal via `/api/chat/send` or the portal WebSocket? That decision affects whether ST# needs to wire a portal notification in the same PR or defer it.

7. **Config location:** Should `constitutional_tasks` live in `scheduled-tasks-state.json` (dynamic, updated at runtime) or `boop_config.json` (static config, updated manually)? Recommendation: `boop_config.json` for the set definition (static, versioned), with `scheduled-tasks-state.json` only tracking last_run and status. This keeps the constitutional definition as a git-tracked config artifact.

---

## 7. Test Plan

QA must verify the following before the bridge is removed and the implementation is declared DONE.

### 7.1 Unit Tests (ST# devops-engineer)

**Test: Constitutional task bypasses window throttle**
- Setup: Set `MAX_BOOPS_PER_WINDOW=2`, fire 2 non-constitutional boops within the 180s window, then trigger a constitutional task.
- Expected: Constitutional task fires despite window being at cap.
- Verified by: `logs/boop_executor.log` shows "Launched boop agent: [engineering-flow-check]" after the window is saturated.

**Test: Constitutional task bypasses process cap**
- Setup: Manually start `MAX_CONCURRENT_BOOP_AGENTS=3` dummy claude processes matching the `claude.*BOOP` pattern. Trigger a constitutional task.
- Expected: Constitutional task fires as the 4th process, up to `constitutional_reserved_slots`.
- Verified by: Process list shows 4 concurrent agents. Log shows no "Skipping [engineering-flow-check]" message.

**Test: Constitutional slot is not monopolized by non-constitutional task**
- Setup: Fire `MAX_CONCURRENT_BOOP_AGENTS + constitutional_reserved_slots` non-constitutional tasks.
- Expected: Executor caps at `MAX_CONCURRENT_BOOP_AGENTS` for non-constitutional tasks; constitutional slot remains open.
- Verified by: `count_running_boop_agents_matching(constitutional_set)` returns 0; slot is available.

**Test: Starvation alarm fires at 2x interval**
- Setup: Set `last_run` for engineering-flow-check to `now - (2.1 * interval_seconds)`. Run check cycle.
- Expected: WARNING log contains "CONSTITUTIONAL STARVATION ALERT [engineering-flow-check]".
- Verified by: grep on log file.

**Test: `priority_order` sort moves constitutional tasks to front**
- Setup: 3 non-constitutional tasks and 1 constitutional task all due simultaneously.
- Expected: Constitutional task fires first (slot 1 of the cycle).
- Verified by: Order of "Launched boop agent" lines in log.

### 7.2 Integration Test (ST# qa-engineer)

**Test: Sustained nightly batch does not starve constitutional task beyond 1x interval**
- Setup: Simulate nightly batch by holding 3 long-running non-constitutional boop agents alive for 2 full check intervals (10 minutes). Ensure engineering-flow-check is due.
- Expected: engineering-flow-check fires within its normal 30-minute interval, using the reserved slot.
- Verified by: `inbox/engineering-flow-check-*.md` mtime shows file created during the simulated batch period.

**Test: Bridge coexistence does not cause double-write corruption**
- Setup: Run both the systemd bridge timer and boop_executor simultaneously. Let both fire engineering-flow-check within a 5-minute window.
- Expected: `scheduled-tasks-state.json` has a valid `last_run` for engineering-flow-check after both fires. No JSON corruption.
- Verified by: `python3 -c "import json; json.load(open('.claude/scheduled-tasks-state.json'))"` exits 0.

**Test: Full removal of bridge does not cause starvation regression**
- Setup: Disable bridge. Run boop_executor for 3 full 30-minute cycles under normal load.
- Expected: engineering-flow-check fires in each of the 3 cycles. No starvation alarm emitted.
- Verified by: 3 distinct `inbox/engineering-flow-check-*.md` files with timestamps 30min apart. No WARNING in log.

### 7.3 Acceptance Criterion (Aether conductor, post-ship)

The implementation is accepted when:
- `engineering-flow-check` has not been starved beyond 1.5x its interval for 72 consecutive hours.
- The starvation alarm has not fired after the 72-hour observation window.
- The bridge systemd timer has been removed and the removal is committed to git.

---

## 8. Pre-Build Checklist (`.claude/skills/pre-build-checklist/SKILL.md`)

| Question | Answer |
|---|---|
| SOFTWARE / AI / BOTH? | SOFTWARE — pure Python scheduler logic, no LLM inference in the executor itself |
| Runs without AI? | YES — boop_executor.py is a pure Python daemon; the constitutional slot logic requires no AI |
| Customer-facing? | NO — internal scheduling infrastructure only |
| Recurring? | YES — daemon runs indefinitely, check every 5 minutes |
| Real-time? | NO — 5-minute polling; near-real-time acceptable |
| Persistence (D1)? | NO — state in `scheduled-tasks-state.json` (filesystem JSON); no D1 |
| Human configurable? | YES — constitutional task set must be editable in `boop_config.json` without code change |

---

## 9. Implementation Guidance for ST#

This section is for the coder-agent (ST# devops-engineer). Design only — no code is implemented here.

**Files to modify:**

- `tools/boop_executor.py` — primary change site
- `tools/boop_config.json` — add `constitutional_tasks` array and `constitutional_reserved_slots` integer (static config, git-tracked)
- `.claude/scheduled-tasks-state.json` — no structural change needed; this file remains runtime state only (last_run, status)

**New constants to introduce in `boop_executor.py`:**

- `CONSTITUTIONAL_TASKS: set[str]` — loaded from `boop_config.json` at startup, not hardcoded
- `CONSTITUTIONAL_RESERVED_SLOTS: int` — loaded from `boop_config.json` (default 1)
- `CONSTITUTIONAL_STARVATION_ALERT_MULTIPLIER: float = 2.0`

**New function:** `count_running_constitutional_agents(constitutional_set, logger) -> int` — filter `pgrep -f "claude.*BOOP"` output against known constitutional task_ids. Requires that task_id appears in the boop prompt (already true — `fire_boop` embeds `[{task_id}]` in the prompt string).

**Modified function:** `fire_boop` — add pre-check: if task is constitutional AND `count_running_constitutional_agents < CONSTITUTIONAL_RESERVED_SLOTS`, bypass the window throttle and process cap checks.

**Modified main loop:** Sort `due` list with constitutional tasks first before the throttle evaluation loop. Read `priority_order` from `.claude/scheduled-tasks-state.json["boop_rules"]["priority_order"]` to determine sort position for non-constitutional tasks.

**New starvation check:** After the fire loop, for each constitutional task in `tasks`, compute elapsed since `last_run`. If `elapsed > CONSTITUTIONAL_STARVATION_ALERT_MULTIPLIER * interval`, emit WARNING.

**Git discipline (mandatory):**
```bash
# Before modifying boop_executor.py:
git add tools/boop_executor.py tools/boop_config.json
git commit -m "chore: pre-ADR-001 backup — unmodified boop_executor before fairness lane"

# After implementation:
git add tools/boop_executor.py tools/boop_config.json .claude/scheduled-tasks-state.json
git commit -m "feat(scheduler): constitutional fairness lane — ADR-001 implementation"

# Restart executor:
kill $(cat .boop_executor.pid)
nohup python3 tools/boop_executor.py >> logs/boop_executor.log 2>&1 &
```

---

## 10. Memory Search Results

- Searched: `.claude/memory/agent-learnings/architect/` for "boop", "scheduler", "starvation", "concurrency"
- Found: No prior architect entries (this is the first architect task in this directory)
- Searched: `.claude/memory/departments/systems-technology/` — found the ST# scope correction memo (2026-05-16--engineering-flow-check-starvation-scope-correction.md) which confirmed: (a) `boop_config.json` has no priority field, (b) executor is FIFO with hard constants, (c) JSON-only "promote to tier-1" is a no-op
- Applying: ST# scope correction informs Options A/B/C design, specifically the fatal flaw analysis of Option B and the finding that `priority_order` is declared but dead

---

## 11. Errata

**Date:** 2026-05-16  
**Source:** CTO ground-truth probe (post-design cleanup pass)

### Correction 1: `delegation-enforcer-boop` → `delegation-enforcer`

**Original text (Sections 3 and 6):** constitutional_tasks array included `"delegation-enforcer-boop"` and CTO Question 2 referenced `[engineering-flow-check, delegation-enforcer-boop, capability-gap-analysis]`.

**Corrected text:** `"delegation-enforcer"` (no `-boop` suffix).

**Ground truth:** `tools/boop_config.json` line 10 shows `"delegation-enforcer"` as the canonical task name. `.claude/scheduled-tasks-state.json` line 17 confirms the same. The `-boop` suffix was a naming error introduced during initial design — the pattern exists for some tasks (e.g., `email-check-boop`) but not for `delegation-enforcer`.

**Impact:** Affects the data model example in Section 3 Option A and the constitutional set enumeration in Section 6 Question 2. Both corrected above. The ST# BUILD brief was issued with the corrected name, so this ADR now matches the brief.

### Correction 2: File reference audit for `priority_order`

**CTO probe claim:** The BOOP cleanup brief stated `priority_order` is in `tools/boop_config.json:8-35`, not in `scheduled-tasks-state.json`.

**Post-correction ground truth (architect direct probe):** Direct read of both files confirms:
- `tools/boop_config.json` lines 8-35 contain the `groups` structure (frequency-to-boop mappings: `30min`, `60min`, `2hr`, `4hr`, `daily`, `weekly`). No `priority_order` field exists in this file.
- `.claude/scheduled-tasks-state.json` lines 8-35 contain the `priority_order` array (inside `boop_rules`), listing all 26 tasks by priority position.

**Conclusion:** The original ADR's file reference (`scheduled-tasks-state.json`) was correct. The CTO cleanup brief's stated correction appears to have had the two files transposed. No change to the file references in Sections 1.2 and 9 was warranted; those references are accurate as written.

**What was clarified:** Section 1.2 and Section 9 now use the precise path `.claude/scheduled-tasks-state.json["boop_rules"]["priority_order"]` (lines 8-35) rather than the bare `scheduled-tasks-state.json at line 8` phrasing, to eliminate ambiguity about the nesting level. This is a clarification, not a correction.

---

*Architect: architect-agent | Date: 2026-05-16 | ADR-001 | Last errata: 2026-05-16 02:18 UTC*

---

## 11. ST# BUILD verdict (2026-05-16)

- **Constitutional set in production**: `[engineering-flow-check, delegation-enforcer]` (exact, Amendment 1)
- **Files changed**:
  - `tools/boop_executor.py` — new helpers + reserved-slot bypass + watchdog + dedup + flock + starvation alarm
  - `tools/boop_config.json` — new `boop_rules` block (constitutional_tasks, reserved_slots, watchdog/starvation/dedup/alarm tunables)
  - `tests/test_boop_executor_adr001.py` — 25 QA tests (all green)
- **Security audit**: PASS (no realistic spoofing surface, watchdog timing bounded, no Telegram path, atomic write, advisory lock with owner-only sidecar)
- **QA**: 25/25 tests pass covering all 7 amendments + starvation alarm + /proc probes
- **Bridge removal preconditions** (still required, per Section 5 + CTO verdict):
  1. 3 consecutive successful fires via boop_executor (not bridge) — observation pending
  2. 72-hour starvation-alarm-free observation window — observation pending
  3. CTO sign-off on observation data

