# FORK-AND-COLLAPSE DISCIPLINE (Phase-4 promotion)

You are running as a BOOP agent for a task flagged `fork_and_collapse: true`.
This addendum tells you HOW to execute this task using the proven
fork-and-collapse pattern — but ONLY when it is safe to do so. Read the
NIGHTLY-WINDOW GUARD first. If the guard says "run normally," ignore the rest
of this addendum and do the task as a single agent exactly as described above.

---

## STEP 0 — NIGHTLY-WINDOW GUARD (decides everything)

Run this Python check FIRST. The fork only ever happens inside the 0–6 UTC
window, when no other BOOPs are competing for slots:

```bash
python3 - <<'PY'
import sys
sys.path.insert(0, "/home/jared/projects/AI-CIV/aether/tools")
import dynamic_workflow_runner as r
print("FORK_OK" if r.in_nightly_window() else "RUN_NORMALLY")
PY
```

- Output `RUN_NORMALLY` (outside 0–6 UTC) → **do NOT fork.** Execute this task
  as a single agent normally, write findings to memory, send your Telegram
  summary, and stop. This is the default-safe path.
- Output `FORK_OK` (inside 0–6 UTC) → proceed to STEP 1.

If ANY step below errors (import failure, runner exception, governor
unavailable), **fall back to a normal single-agent run** rather than failing
the task. The heartbeat must never be at risk.

---

## STEP 1 — DECOMPOSE into 2–4 GENUINELY INDEPENDENT sub-analyses

Break THIS task's analysis into 2 to 4 sub-analyses that do not depend on each
other's output (they must be runnable fully in parallel). Each sub-analysis
gets a unique `agent_id` (filename-safe stem) and a self-contained
`instruction` string. Do NOT create artificial splits — if the work is not
genuinely separable, run normally instead.

## STEP 2 — GATE PARALLELISM through the concurrency governor

Ask the RAM-based governor how many parallel agents are safe right now:

```python
import sys
sys.path.insert(0, "/home/jared/projects/AI-CIV/aether/tools")
import concurrency_governor as g
max_parallel = g.recommended_concurrency()   # clamped to [2, 10], RAM-aware
```

Pass this `max_parallel` to `fork(...)`. Never hardcode parallelism; the
governor is the only authority on how many agents may run concurrently.

## STEP 3 — FORK the sub-analyses

```python
import sys
sys.path.insert(0, "/home/jared/projects/AI-CIV/aether/tools")
import dynamic_workflow_runner as r

subtasks = [
    {"agent_id": "<stem-1>", "instruction": "<sub-analysis 1 ...>"},
    {"agent_id": "<stem-2>", "instruction": "<sub-analysis 2 ...>"},
    # 2-4 total
]
batch = r.fork("<task_id>", subtasks, max_parallel=max_parallel)
print(batch["ok"], "/", batch["total"], "ok ; results_dir:", batch["results_dir"])
```

Raw per-sub-agent JSON lands in `/tmp/fork-results/<task_id>/*.json` for audit.

## STEP 4 — COLLAPSE to ONE digest

```python
digest = r.collapse("<task_id>")
print("digest written to:", digest["inbox_path"])
```

`collapse()` routes the raw outputs through result-synthesizer under the
COO-firewall compression contract and writes ONE digest to `inbox/`. The raw
JSON files stay on disk — do NOT paste them into the digest, do NOT delete them.

## STEP 5 — REPORT

Send your Telegram summary noting: fork ran (N sub-analyses, M ok), digest path
in `inbox/`, raw at `/tmp/fork-results/<task_id>/`. Then stop.

---

## GUARANTEES THIS ADDENDUM PRESERVES

- **Default-safe:** outside 0–6 UTC, or on ANY error, you run as a normal
  single agent — identical to non-flagged behavior.
- **Governor-gated:** parallelism is whatever `recommended_concurrency()`
  returns RIGHT NOW (RAM-aware), never a fixed number.
- **Window-gated:** the parallel spawn only happens in the 0–6 UTC quiet window.
- **Audit-preserving:** raw outputs persist in `/tmp/fork-results/<task_id>/`;
  only the compressed digest reaches `inbox/`.
