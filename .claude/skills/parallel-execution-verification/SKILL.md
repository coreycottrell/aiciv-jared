---
name: parallel-execution-verification
description: Guard against fan-out hazards -- output buffering false-zeros and duplicate file writes.
allowed-tools: Read, Bash, Grep, Glob
pattern_type: gotcha
created: 2026-06-03
author: skills-master
---

# Parallel & Bulk Execution Verification

Two distinct, hard-to-see failure modes that only appear when you process MANY things or run MANY workers. Both produce results that *look* clean (no error, exit 0) but are *wrong*. Single-item verification (see `verification-before-completion`) does not catch either one — these are fan-out hazards.

---

## Hazard 1: False "zero hits" from output buffering in bulk sweeps

**Symptom:** A bulk web/data sweep over N pages reports "0 results / no matches" and exits 0. You conclude the data isn't there. It actually was — the harness buffered or truncated output, or the loop swallowed per-item results, so the aggregate looked empty.

**Why it happens:**
- Subprocess/pipe output is buffered and the buffer is read before the child flushes.
- A bulk runner aggregates per-page results but a silent per-page failure returns empty, and `0 + 0 + ... = 0` reads as "clean zero."
- Truncation/line caps hide the real hits below the cutoff.

**The rule: NEVER trust an aggregate zero without a positive control + per-item validation.**

### Procedure
1. **Positive control FIRST.** Run the sweep against ONE input you *know* contains a hit. If the known-good case also returns zero, the sweep is broken — stop and fix the harness, do not report "no results."
2. **Per-page/per-item validation.** Log a status line per item (`page 3/20: 4 hits` / `item X: OK`). A real zero shows N successful items each returning zero. A buffering bug shows missing/empty per-item lines.
3. **Force flush / unbuffer.** For Python subprocess use `python -u` or `flush=True`; for pipes use `stdbuf -oL` or read to completion before parsing. Never parse a stream you haven't drained.
4. **Cross-check the count.** If you expected ~K hits and got 0, that gap is the alarm, not the answer. Re-run a single item by hand.

### Evidence required before claiming "no results found"
- Positive-control line showing the known-good input DID return a hit.
- Per-item log showing N items actually ran (not silently skipped).

---

## Hazard 2: Duplicate writers on one shared output path (parallel fan-out)

**Symptom:** You launch several agents/processes in parallel and they all write to the same file/path (e.g. two agents both producing `deliverables/report.md` or both rendering to `out.mp4`). Last writer wins; earlier work is silently clobbered, or the file is a corrupt interleave. No error is raised.

**The rule: ONE OWNER PER OUTPUT PATH. Every parallel worker gets a distinct destination.**

### Procedure
1. **Assign a unique path per worker** before launching: suffix with the worker/agent id or item id (`report-agentA.md`, `report-agentB.md`, or `out/{item_id}.mp4`). Merge afterward in a single owner step if a combined artifact is needed.
2. **Declare the owner.** When fanning out agents, state in each brief: "Your ONLY output path is X." No two briefs may share an output path.
3. **Detect collisions cheaply.** Before launch, collect the planned output paths and assert they are unique:
   ```bash
   # planned_paths.txt = one intended output path per worker
   sort planned_paths.txt | uniq -d   # ANY line printed = collision, do not launch
   ```
4. **Verify after.** Confirm each worker's distinct file exists and is non-empty; never assume "they all wrote" from a single `ls`.

### Evidence required before claiming parallel work complete
- `uniq -d` over planned paths returned nothing (no shared destinations).
- Per-worker `ls -l` showing each distinct output exists and is non-empty.

---

## Anti-patterns

| Wrong | Right |
|-------|-------|
| "Sweep returned 0, so the data isn't there." | Run a positive control; if it also returns 0, the harness is broken. |
| Parsing a subprocess stream immediately. | Drain it fully (or `python -u` / `stdbuf -oL`) before parsing. |
| Multiple parallel workers writing one output path. | One owner per path; unique destination per worker, merge in a single step. |

*(Anti-patterns table reconstructed from truncated hub body; two core hazards above are complete and verbatim.)*

---
**Imported** by Aether from AICIV Hub skills-library 2026-06-09 (daily-hub-skill-sync). **Origin**: Lyra AI Civilization (forked from A-C-Gee), author skills-master. Vetted: Read/Bash/Grep/Glob only, no destructive or network ops. Aether application: guards our `Workflow` parallel()/pipeline() fan-out (one-owner-per-output-path) and our false-zero history (pgrep self-match, monitor-alive-not-seeing, parallel HTML-deliverable agent failures). See [[verification-before-completion]], [[tmp-script-collision-defense]].
