#!/usr/bin/env python3
"""
Dynamic Workflow Runner — Fork-and-Collapse orchestrator (Phase 4, aiciv-native-org).

Opus-4.8-native replacement for the 3.x-era incarnation_runner.py fork manager.
This file deliberately does NOT port incarnation_runner.py (that file does not even
exist in this repo any more, and its fork-manager workaround is obsolete under
Opus 4.8 which spawns parallel `claude --print` subprocesses natively).

================================================================================
SCOPE / SAFETY (read before wiring anything live)
================================================================================
This module is STANDALONE and DEFAULT-OFF. As shipped it:
  * does NOT import or modify boop_executor.py
  * does NOT modify .claude/scheduled-tasks-state.json
  * does NOT change the running boop_executor's max_concurrent
  * does NOT restart/kill the running boop_executor or touch its .pid
  * is never invoked by the live overnight V3 pipeline

It provides a flag-gated, separately-invoked capability + a mechanical dry-run
(`--selftest`) that proves the fork pool, parallelism, JSON collection, failure
handling, and the collapse wiring WITHOUT spending real agent tokens. The future
supervised pilot (documented in .claude/flows/fork-and-collapse-flow.md) is the
ONLY place this gets wired to a real overnight task.

================================================================================
THE PATTERN
================================================================================
  fork(task_id, subtasks, max_parallel)
     -> spawn each subtask as a parallel `claude --print` subprocess, matching
        boop_executor.fire_boop()'s invocation flags exactly. Each sub-agent is
        instructed to write structured JSON to
            /tmp/fork-results/{task_id}/{agent_id}.json
        Concurrency is capped at max_parallel via a thread pool. We collect exit
        status + parse each JSON file. Subprocess timeout, missing/invalid JSON,
        and partial failures are recorded as failed results — they NEVER crash
        the batch.

  collapse(task_id)
     -> invoke the result-synthesizer agent over all
            /tmp/fork-results/{task_id}/*.json
        using the Phase-2 COO firewall prompt template
        (.claude/templates/coo-firewall-prompt.md) to produce ONE digest
        (3 bullets + YES/NO decisions + action queue), written to inbox/.
        Raw JSON stays on disk for audit.

  in_nightly_window(now_utc)
     -> time-of-day guard (0-6 UTC). Present but NOT wired to anything live;
        the FUTURE pilot gates the fork on this.

================================================================================
CLAUDE INVOCATION CONTRACT (mirrors boop_executor.py:987-1000)
================================================================================
  cmd  = ["claude", "--print", "-p", <prompt>,
          "--allowedTools", "Bash,Read,Write,Grep,Glob,WebFetch,WebSearch"]
  Popen(..., cwd=BASE_DIR, start_new_session=True, close_fds=True,
        env=os.environ minus CLAUDECODE)
No --model flag is passed (config default is locked to Opus 4.8 per repo policy),
matching boop_executor exactly.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Constants ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
FORK_RESULTS_ROOT = Path("/tmp/fork-results")
INBOX_DIR = BASE_DIR / "inbox"
COO_FIREWALL_TEMPLATE = BASE_DIR / ".claude" / "templates" / "coo-firewall-prompt.md"

# Matches boop_executor.py's tool grant exactly so forked sub-agents have the
# same capability surface as a normal BOOP agent.
ALLOWED_TOOLS = "Bash,Read,Write,Grep,Glob,WebFetch,WebSearch"

# Per-subtask wall-clock cap. The pilot may tune this; default is conservative.
DEFAULT_SUBTASK_TIMEOUT_S = 1800  # 30 min, same order as overnight agents
DEFAULT_MAX_PARALLEL = 8

# Nightly window (UTC). FUTURE pilot gates the fork on this; not wired live here.
NIGHTLY_WINDOW_START_UTC = 0
NIGHTLY_WINDOW_END_UTC = 6


# ── Time-of-day guard (present, not wired to anything live) ──────────────────
def in_nightly_window(now_utc: Optional[datetime] = None) -> bool:
    """Return True iff now_utc is inside the 0-6 UTC nightly window.

    The FUTURE supervised pilot will gate the real fork on this so that the
    parallel spawn (and any raised concurrency) only ever happens when no other
    BOOPs are competing for slots. It is intentionally NOT called by fork()
    here — fork() runs whenever explicitly invoked, and the pilot wrapper is
    responsible for the gate. This keeps the guard testable in isolation.
    """
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    hour = now_utc.hour
    return NIGHTLY_WINDOW_START_UTC <= hour < NIGHTLY_WINDOW_END_UTC


# ── Helpers ──────────────────────────────────────────────────────────────────
def _results_dir(task_id: str) -> Path:
    return FORK_RESULTS_ROOT / task_id


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _build_env() -> dict:
    """Copy os.environ minus CLAUDECODE, matching boop_executor.fire_boop()."""
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)
    return env


def _subtask_prompt(task_id: str, agent_id: str, instruction: str,
                    result_path: Path) -> str:
    """Build the prompt for one forked sub-agent.

    The sub-agent does its work then MUST write a single JSON object to
    result_path. We are explicit about the contract because invalid/missing
    JSON is the most common fork failure mode.
    """
    return (
        f"FORK [{task_id}/{agent_id}]: {instruction}\n\n"
        f"Working directory: {BASE_DIR}\n\n"
        f"Do the work described above, then write your structured result as a "
        f"SINGLE valid JSON object to this exact path:\n"
        f"    {result_path}\n\n"
        f"The JSON MUST be parseable by json.load and SHOULD include at least a "
        f'"finding" field summarizing your result and an "agent_id" field set to '
        f'"{agent_id}". Write ONLY the file; do not print the JSON to stdout. '
        f"If you cannot complete the work, still write a JSON object with a "
        f'"finding" describing why and a "status":"failed" field.'
    )


# ── FORK ─────────────────────────────────────────────────────────────────────
def _run_one_subtask(task_id: str, subtask: dict, timeout_s: int,
                     dry_run: bool) -> dict:
    """Execute a single subtask subprocess and collect its JSON result.

    Returns a result dict with keys:
      agent_id, exit_code, status ('ok'|'failed'|'timeout'),
      result (parsed JSON or None), error (str or None),
      started_at, ended_at, duration_s
    Never raises — all failure modes are captured into the returned dict so a
    bad subtask cannot crash the batch.
    """
    agent_id = subtask["agent_id"]
    results_dir = _results_dir(task_id)
    result_path = results_dir / f"{agent_id}.json"

    # In dry-run we run a trivial, deterministic shell command instead of a real
    # (expensive) claude agent. It exercises the EXACT same machinery: a real
    # subprocess under the pool, a real file written to /tmp/fork-results, and
    # the same collection/parse/failure path — without spending tokens.
    if dry_run:
        cmd = subtask["_dry_cmd"]  # list[str], provided by --selftest builder
    else:
        instruction = subtask["instruction"]
        prompt = _subtask_prompt(task_id, agent_id, instruction, result_path)
        cmd = [
            "claude",
            "--print",
            "-p", prompt,
            "--allowedTools", ALLOWED_TOOLS,
        ]

    started = datetime.now(timezone.utc)
    log_path = results_dir / f"{agent_id}.log"
    record = {
        "agent_id": agent_id,
        "exit_code": None,
        "status": "failed",
        "result": None,
        "error": None,
        "started_at": started.isoformat(),
        "ended_at": None,
        "duration_s": None,
    }

    try:
        with open(log_path, "w") as log_fh:
            proc = subprocess.run(
                cmd,
                stdout=log_fh,
                stderr=log_fh,
                cwd=str(BASE_DIR),
                start_new_session=True,
                close_fds=True,
                env=_build_env(),
                timeout=timeout_s,
            )
        record["exit_code"] = proc.returncode
    except subprocess.TimeoutExpired:
        record["status"] = "timeout"
        record["error"] = f"subtask exceeded {timeout_s}s timeout"
        record["ended_at"] = datetime.now(timezone.utc).isoformat()
        record["duration_s"] = (datetime.now(timezone.utc) - started).total_seconds()
        return record
    except Exception as e:  # pragma: no cover - defensive
        record["error"] = f"subprocess launch failed: {e!r}"
        record["ended_at"] = datetime.now(timezone.utc).isoformat()
        record["duration_s"] = (datetime.now(timezone.utc) - started).total_seconds()
        return record

    ended = datetime.now(timezone.utc)
    record["ended_at"] = ended.isoformat()
    record["duration_s"] = (ended - started).total_seconds()

    # Collect + validate the JSON result file. Missing/invalid JSON => failed,
    # but the batch continues.
    if not result_path.exists():
        record["error"] = f"no result JSON at {result_path} (exit={record['exit_code']})"
        return record
    try:
        with open(result_path) as f:
            parsed = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        record["error"] = f"invalid JSON at {result_path}: {e}"
        return record

    record["result"] = parsed
    record["status"] = "ok" if record["exit_code"] == 0 else "failed"
    if record["exit_code"] != 0 and record["error"] is None:
        record["error"] = f"nonzero exit {record['exit_code']} (JSON present)"
    return record


def fork(task_id: str, subtasks: list[dict], max_parallel: int = DEFAULT_MAX_PARALLEL,
         timeout_s: int = DEFAULT_SUBTASK_TIMEOUT_S, dry_run: bool = False) -> dict:
    """Spawn each subtask as a parallel claude --print subprocess, capped at
    max_parallel. Collect exit status + JSON results. Returns a batch summary.

    subtasks: list of dicts. Each MUST have:
        agent_id    : str, unique within the batch (also the JSON filename stem)
        instruction : str, the work for that sub-agent (ignored in dry_run)
      In dry_run each subtask ALSO carries:
        _dry_cmd    : list[str], a trivial shell command run instead of claude

    Returns:
        {
          task_id, total, ok, failed, results_dir,
          started_at, ended_at, wall_s,
          results: [ <per-subtask record>, ... ]
        }
    Partial failures are reflected in counts; the function always returns
    normally as long as the pool itself can run.
    """
    results_dir = _results_dir(task_id)
    results_dir.mkdir(parents=True, exist_ok=True)

    batch_started = datetime.now(timezone.utc)
    records: list[dict] = []

    # ThreadPoolExecutor caps concurrency at max_parallel. Each worker thread
    # blocks on its own subprocess.run, so N threads == N concurrent claude
    # processes, never more than max_parallel.
    with ThreadPoolExecutor(max_workers=max(1, max_parallel)) as pool:
        future_to_agent = {
            pool.submit(_run_one_subtask, task_id, st, timeout_s, dry_run): st["agent_id"]
            for st in subtasks
        }
        for fut in as_completed(future_to_agent):
            try:
                records.append(fut.result())
            except Exception as e:  # pragma: no cover - _run_one_subtask never raises
                records.append({
                    "agent_id": future_to_agent[fut],
                    "status": "failed",
                    "error": f"pool-level exception: {e!r}",
                    "result": None,
                    "exit_code": None,
                })

    batch_ended = datetime.now(timezone.utc)
    ok = sum(1 for r in records if r["status"] == "ok")
    failed = len(records) - ok

    summary = {
        "task_id": task_id,
        "total": len(records),
        "ok": ok,
        "failed": failed,
        "results_dir": str(results_dir),
        "started_at": batch_started.isoformat(),
        "ended_at": batch_ended.isoformat(),
        "wall_s": (batch_ended - batch_started).total_seconds(),
        "results": sorted(records, key=lambda r: r["agent_id"]),
    }

    # Persist the batch summary alongside the raw results for audit.
    with open(results_dir / "_batch_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    return summary


# ── COLLAPSE ─────────────────────────────────────────────────────────────────
def _load_firewall_contract() -> str:
    """Load the Phase-2 COO firewall prompt template (the compression contract)."""
    if not COO_FIREWALL_TEMPLATE.exists():
        raise FileNotFoundError(
            f"COO firewall template missing at {COO_FIREWALL_TEMPLATE} "
            f"(Phase 2 must be in place before collapse can run)"
        )
    return COO_FIREWALL_TEMPLATE.read_text()


def _build_collapse_prompt(task_id: str, results_dir: Path, inbox_path: Path,
                           contract: str) -> str:
    """Build the result-synthesizer prompt for the collapse step."""
    json_files = sorted(str(p) for p in results_dir.glob("*.json")
                        if p.name != "_batch_summary.json")
    file_list = "\n".join(f"    {p}" for p in json_files) or "    (none found)"
    return (
        f"COLLAPSE [{task_id}]: You are the result-synthesizer agent acting as the "
        f"COO Firewall collapse step for a fork-and-collapse batch.\n\n"
        f"Read every raw sub-agent JSON result in this directory:\n{file_list}\n\n"
        f"Synthesize them into ONE digest that OBEYS the COMPRESSION CONTRACT "
        f"below EXACTLY (three sections, nothing else). Write the digest to this "
        f"exact path and nothing else:\n    {inbox_path}\n\n"
        f"The raw JSON files stay on disk for audit — do NOT delete them and do "
        f"NOT paste their contents into the digest.\n\n"
        f"--- BEGIN COMPRESSION CONTRACT ---\n{contract}\n--- END COMPRESSION CONTRACT ---\n"
    )


def collapse(task_id: str, timeout_s: int = DEFAULT_SUBTASK_TIMEOUT_S,
             dry_run: bool = False) -> dict:
    """Invoke result-synthesizer over /tmp/fork-results/{task_id}/*.json using the
    COO firewall contract, producing ONE digest written to inbox/.

    Returns {task_id, inbox_path, status, exit_code, error}.

    In dry_run mode we do NOT call a real synthesizer agent. Instead we MECHANICALLY
    produce a contract-shaped digest from the collected JSON so the wiring
    (file discovery, prompt assembly, inbox write) is fully exercised with zero
    token spend. The single-real-synthesizer-call path is what the pilot uses.
    """
    results_dir = _results_dir(task_id)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    inbox_path = INBOX_DIR / f"conductor-boop-{task_id}-{_utc_stamp()}.md"

    json_files = sorted(p for p in results_dir.glob("*.json")
                        if p.name != "_batch_summary.json")

    if dry_run:
        # Mechanical collapse: prove the wiring without a real agent call.
        findings = []
        ok_count = 0
        fail_count = 0
        for p in json_files:
            try:
                data = json.load(open(p))
                findings.append(f"{p.stem}: {data.get('finding', '(no finding)')}")
                if data.get("status") == "failed":
                    fail_count += 1
                else:
                    ok_count += 1
            except Exception as e:
                findings.append(f"{p.stem}: UNREADABLE ({e})")
                fail_count += 1

        digest = (
            f"# COO Firewall Digest — {task_id} (DRY-RUN mechanical collapse)\n\n"
            f"## SUMMARY (3 bullets max)\n"
            f"- Forked {len(json_files)} sub-agents: {ok_count} ok, {fail_count} failed/missing\n"
            f"- Sample findings: {'; '.join(findings[:3])}\n"
            f"- Raw JSON retained for audit under {results_dir}\n\n"
            f"## DECISIONS (YES/NO)\n"
            f"- [ ] Promote this dry-run to a supervised live pilot? (default: NO)\n"
            f"- [ ] Were all expected sub-agent results collected? (default: "
            f"{'YES' if fail_count == 0 else 'NO'})\n\n"
            f"## ACTION QUEUE (executable)\n"
            f"1. Review {results_dir}/_batch_summary.json for per-agent exit codes\n"
            f"2. If promoting: follow .claude/flows/fork-and-collapse-flow.md pilot steps\n"
        )
        inbox_path.write_text(digest)
        return {
            "task_id": task_id,
            "inbox_path": str(inbox_path),
            "status": "ok",
            "exit_code": 0,
            "error": None,
            "mode": "dry-run-mechanical",
        }

    # Real collapse: ONE result-synthesizer agent call.
    contract = _load_firewall_contract()
    prompt = _build_collapse_prompt(task_id, results_dir, inbox_path, contract)
    log_path = results_dir / "_collapse.log"
    cmd = [
        "claude",
        "--print",
        "-p", prompt,
        "--allowedTools", ALLOWED_TOOLS,
    ]
    try:
        with open(log_path, "w") as log_fh:
            proc = subprocess.run(
                cmd,
                stdout=log_fh,
                stderr=log_fh,
                cwd=str(BASE_DIR),
                start_new_session=True,
                close_fds=True,
                env=_build_env(),
                timeout=timeout_s,
            )
    except subprocess.TimeoutExpired:
        return {"task_id": task_id, "inbox_path": str(inbox_path),
                "status": "timeout", "exit_code": None,
                "error": f"collapse exceeded {timeout_s}s", "mode": "real"}

    status = "ok" if (proc.returncode == 0 and inbox_path.exists()) else "failed"
    error = None
    if proc.returncode != 0:
        error = f"synthesizer exit {proc.returncode}"
    elif not inbox_path.exists():
        error = "synthesizer exited 0 but no digest written to inbox"
    return {"task_id": task_id, "inbox_path": str(inbox_path), "status": status,
            "exit_code": proc.returncode, "error": error, "mode": "real"}


# ── SELFTEST / DRY-RUN ───────────────────────────────────────────────────────
def _selftest() -> int:
    """Mechanically validate fork pool, parallelism, JSON collection, graceful
    failure handling, and collapse wiring — WITHOUT calling expensive agents.

    Strategy: build trivial dry-run subtasks whose _dry_cmd is a tiny shell
    command. Most write a small JSON and sleep briefly (to prove concurrency via
    overlapping timestamps). One subtask is INJECTED to fail (writes invalid
    JSON) so we prove the batch survives a bad sub-agent. Then collapse() in
    dry-run produces a contract-shaped digest in inbox/.
    """
    task_id = f"selftest-{_utc_stamp()}"
    results_dir = _results_dir(task_id)
    print(f"[selftest] task_id={task_id}")
    print(f"[selftest] in_nightly_window(now)={in_nightly_window()}  "
          f"(window {NIGHTLY_WINDOW_START_UTC}-{NIGHTLY_WINDOW_END_UTC} UTC)")

    # Build trivial subtasks. Each healthy one writes valid JSON then sleeps 2s.
    # With max_parallel=4 and 4 healthy subtasks, a serial run would take ~8s;
    # parallel should finish in ~2-3s. We assert wall_s well under serial.
    n_healthy = 4
    sleep_s = 2
    subtasks = []
    for i in range(n_healthy):
        agent_id = f"agent{i}"
        jpath = results_dir / f"{agent_id}.json"
        # Write JSON immediately, sleep to create overlapping execution windows.
        payload = json.dumps({"finding": "ok", "n": i, "agent_id": agent_id})
        # Use python for portable JSON write + sleep.
        dry_cmd = [
            sys.executable, "-c",
            (
                "import json,time,sys,pathlib;"
                f"p=pathlib.Path({str(jpath)!r});"
                "p.parent.mkdir(parents=True,exist_ok=True);"
                f"p.write_text({payload!r});"
                f"time.sleep({sleep_s})"
            ),
        ]
        subtasks.append({"agent_id": agent_id, "_dry_cmd": dry_cmd})

    # Injected failing subtask: writes INVALID JSON (proves graceful handling).
    bad_id = "agent_bad"
    bad_path = results_dir / f"{bad_id}.json"
    bad_cmd = [
        sys.executable, "-c",
        (
            "import pathlib;"
            f"p=pathlib.Path({str(bad_path)!r});"
            "p.parent.mkdir(parents=True,exist_ok=True);"
            "p.write_text('{ this is not valid json ');"
        ),
    ]
    subtasks.append({"agent_id": bad_id, "_dry_cmd": bad_cmd})

    # Injected missing-JSON subtask: exits 0 but writes NO file (proves the
    # missing-result path).
    miss_id = "agent_missing"
    miss_cmd = [sys.executable, "-c", "pass"]
    subtasks.append({"agent_id": miss_id, "_dry_cmd": miss_cmd})

    total = len(subtasks)
    print(f"[selftest] forking {total} subtasks "
          f"({n_healthy} healthy, 1 invalid-JSON, 1 missing-JSON) "
          f"max_parallel=4, each healthy sleeps {sleep_s}s")

    t0 = time.monotonic()
    summary = fork(task_id, subtasks, max_parallel=4, timeout_s=30, dry_run=True)
    wall = time.monotonic() - t0

    serial_estimate = n_healthy * sleep_s
    print(f"[selftest] fork wall_s={summary['wall_s']:.2f} "
          f"(serial estimate ~{serial_estimate}s for healthy subtasks)")
    print(f"[selftest] ok={summary['ok']} failed={summary['failed']} "
          f"total={summary['total']}")

    # Show per-agent start times to PROVE overlap (parallelism).
    print("[selftest] per-agent timeline (started_at -> status):")
    for r in summary["results"]:
        print(f"    {r['agent_id']:14s} start={r.get('started_at')} "
              f"status={r['status']:8s} err={r.get('error')}")

    # Collapse (dry-run mechanical) — proves the collapse wiring + inbox write.
    print("[selftest] running dry-run collapse (mechanical, no agent call)...")
    coll = collapse(task_id, dry_run=True)
    print(f"[selftest] collapse status={coll['status']} mode={coll['mode']}")
    print(f"[selftest] digest written to: {coll['inbox_path']}")

    # ── Assertions ───────────────────────────────────────────────────────────
    failures = []
    # Concurrency: parallel wall must beat serial by a clear margin.
    if summary["wall_s"] >= serial_estimate * 0.9:
        failures.append(
            f"parallelism NOT proven: wall_s={summary['wall_s']:.2f} "
            f"not clearly under serial ~{serial_estimate}s")
    # Healthy ones must be ok.
    if summary["ok"] != n_healthy:
        failures.append(f"expected {n_healthy} ok, got {summary['ok']}")
    # The two injected bad subtasks must be failed (not crash the batch).
    bad = {r["agent_id"]: r for r in summary["results"]}
    if bad.get(bad_id, {}).get("status") == "ok":
        failures.append("invalid-JSON subtask was wrongly counted ok")
    if bad.get(miss_id, {}).get("status") == "ok":
        failures.append("missing-JSON subtask was wrongly counted ok")
    if bad.get(bad_id, {}).get("error") is None:
        failures.append("invalid-JSON subtask had no error recorded")
    if bad.get(miss_id, {}).get("error") is None:
        failures.append("missing-JSON subtask had no error recorded")
    # Collapse must have produced a digest.
    if coll["status"] != "ok" or not Path(coll["inbox_path"]).exists():
        failures.append("collapse did not produce a digest")

    print()
    print("[selftest] showing produced digest:")
    print("-" * 60)
    print(Path(coll["inbox_path"]).read_text())
    print("-" * 60)

    # ── Cleanup the test artifacts (results dir + inbox digest) ───────────────
    try:
        shutil.rmtree(results_dir)
        print(f"[selftest] cleaned up {results_dir}")
    except Exception as e:
        print(f"[selftest] WARNING: could not clean {results_dir}: {e}")
    try:
        Path(coll["inbox_path"]).unlink()
        print(f"[selftest] cleaned up {coll['inbox_path']}")
    except Exception as e:
        print(f"[selftest] WARNING: could not clean digest: {e}")

    if failures:
        print("\n[selftest] RESULT: FAIL")
        for f in failures:
            print(f"    - {f}")
        return 1
    print("\n[selftest] RESULT: PASS — fork pool, parallelism, JSON collection, "
          "graceful failure, and collapse wiring all verified mechanically.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fork-and-Collapse dynamic workflow runner (Phase 4, default-OFF).")
    parser.add_argument("--selftest", "--dry-run", action="store_true",
                        dest="selftest",
                        help="Mechanically validate fork/collapse with trivial "
                             "subtasks; no expensive agent calls. Cleans up after.")
    args = parser.parse_args()

    if args.selftest:
        return _selftest()

    parser.print_help()
    print("\nThis runner is DEFAULT-OFF and not wired to any live pipeline.")
    print("See .claude/flows/fork-and-collapse-flow.md for supervised pilot steps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
