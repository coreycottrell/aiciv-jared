# Fork-and-Collapse Flow

**Status**: Phase-4 capability built, dry-run validated, **NOT live-wired** (default-OFF)
**Pattern source**: coreycottrell/aiciv-native-org (Fork-and-Collapse + COO Firewall)
**Runner**: `tools/dynamic_workflow_runner.py`
**Date**: 2026-06-02

---

## What This Is

The Opus-4.8-native fork/join orchestrator that replaces the 3.x-era
`incarnation_runner.py` workaround (which no longer exists in this repo and was
NOT ported). It does two things:

1. **fork(task_id, subtasks, max_parallel)** — spawns N sub-agents as parallel
   `claude --print` subprocesses (same invocation contract as
   `boop_executor.fire_boop()`), each writing structured JSON to
   `/tmp/fork-results/{task_id}/{agent_id}.json`. Concurrency capped at
   `max_parallel` via a thread pool. Timeouts, missing/invalid JSON, and partial
   failures are recorded as failed results and NEVER crash the batch.

2. **collapse(task_id)** — invokes the `result-synthesizer` agent over all
   `/tmp/fork-results/{task_id}/*.json` using the Phase-2 COO firewall contract
   (`.claude/templates/coo-firewall-prompt.md`), producing ONE digest
   (3 bullets + YES/NO decisions + action queue) written to `inbox/`. Raw JSON
   stays on disk for audit.

A time-of-day guard `in_nightly_window(now_utc)` (0-6 UTC) is present for the
FUTURE pilot to gate on. It is NOT wired to anything live.

---

## Dry-Run Validation (already done)

```bash
python3 tools/dynamic_workflow_runner.py --selftest
```

Proves, with trivial subtasks and ZERO expensive agent calls:
- N subtasks fork in parallel (overlapping start timestamps; wall ~2.3s vs 8s serial)
- All JSON results collected
- An injected invalid-JSON subtask AND an injected missing-JSON subtask are
  handled gracefully (recorded `failed`, batch survives)
- Collapse produces a contract-shaped digest in `inbox/`
- Test artifacts cleaned up afterward

---

## CURRENT SAFETY POSTURE (what is NOT touched)

As shipped this phase:
- does NOT modify `tools/boop_executor.py`
- does NOT modify `.claude/scheduled-tasks-state.json`
- does NOT raise the running executor's `MAX_CONCURRENT_BOOP_AGENTS` (still 3)
- does NOT restart/kill the running `boop_executor` (PID ~3537329) or touch its `.pid`
- is never invoked by the live overnight V3 pipeline

The live overnight pipeline remains exactly as-is.

---

## FUTURE SUPERVISED PILOT — Enablement Steps (DO NOT run unattended)

This is the SEPARATE, supervised step to try fork-and-collapse on ONE overnight
task. A human (Jared) supervises; CTO pre-build review required (touches the
executor's concurrency assumptions).

### Pre-flight
1. `git status` clean; create a backup branch.
2. Confirm `result-synthesizer` manifest present: `.claude/agents/result-synthesizer.md`.
3. Confirm COO firewall template present: `.claude/templates/coo-firewall-prompt.md`.
4. Sync with Corey on the OPEN QUESTION below (manifest-vs-disk-folder).

### Enable for ONE task (supervised, in-window only)
5. Pick ONE low-risk overnight task (NOT the main overnight V3). Define its
   subtasks as a `list[dict]` with `agent_id` + `instruction` each.
6. Gate the invocation on the nightly window:
   ```python
   from tools.dynamic_workflow_runner import fork, collapse, in_nightly_window
   from datetime import datetime, timezone
   if in_nightly_window(datetime.now(timezone.utc)):
       summary = fork("pilot-task", subtasks, max_parallel=8)  # real agents
       result = collapse("pilot-task")                          # ONE synthesizer call
   ```
7. Run it MANUALLY first (not via boop_executor) during the 0-6 UTC window,
   watching the logs in `/tmp/fork-results/pilot-task/`.
8. Compare the collapse digest against what the existing serial path produces
   for the same task. Output-comparison gate before any cut-over.

### Concurrency raise (only if wiring into boop_executor later)
9. The pilot's parallel fork wants more than the live `MAX_CONCURRENT_BOOP_AGENTS=3`.
   The forked subprocesses are launched by THIS runner's thread pool, NOT by
   `boop_executor`, so they do NOT consume boop_executor slots directly. BUT if a
   future step launches `fork()` *from inside* a BOOP task, that BOOP occupies one
   executor slot while its children run. Plan: keep the fork's `max_parallel` (8)
   independent of the executor cap, and only ever run the fork inside the 0-6 UTC
   window when no other BOOPs compete. Do NOT raise `MAX_CONCURRENT_BOOP_AGENTS`
   globally — time-gate instead.

### Rollback
- The capability is default-OFF and standalone. To roll back the pilot: stop
  invoking `fork()/collapse()` — nothing in the live pipeline references them.
- If a pilot wired a flag into a scheduled task, remove that flag from
  `.claude/scheduled-tasks-state.json` and the task reverts to serial.
- `git checkout` the backup branch if any executor edits were made.
- Raw fork results in `/tmp/fork-results/` are ephemeral; safe to `rm -rf`.

---

## OPEN QUESTION — sync with Corey (manifest-vs-disk-folder compatibility)

ACG's canonical Fork-and-Collapse assumes **managers-as-disk-folders** (wake N
copies of a folder-based manager). Aether uses **agent manifests**
(`.claude/agents/*.md`), not disk folders, as the manager unit. This runner
implements the pattern by spawning manifest-based sub-agents via parallel
`claude --print` subprocesses.

**Confirm with Corey before the live pilot**: is the manifest-based spawn
compatible with the canonical disk-folder pattern, or should we bridge the two
representations (e.g. materialize a transient folder per forked manifest)? The
collapse step (result-synthesizer over `/tmp/fork-results/*.json`) is
representation-agnostic and should be portable either way.

---

## API Quick Reference

```python
from tools.dynamic_workflow_runner import fork, collapse, in_nightly_window

# fork: parallel spawn, capped at max_parallel
summary = fork(
    task_id="my-task",
    subtasks=[{"agent_id": "a1", "instruction": "..."}, ...],
    max_parallel=8,          # pool cap
    timeout_s=1800,          # per-subtask wall cap
    dry_run=False,           # True => trivial _dry_cmd subtasks, no token spend
)
# summary => {task_id,total,ok,failed,results_dir,wall_s,results:[...]}

# collapse: one synthesizer call -> inbox digest
result = collapse(task_id="my-task", dry_run=False)
# result => {task_id,inbox_path,status,exit_code,error,mode}

# nightly guard (for the pilot to gate on; not wired live)
in_nightly_window()  # True iff 0 <= UTC hour < 6
```
