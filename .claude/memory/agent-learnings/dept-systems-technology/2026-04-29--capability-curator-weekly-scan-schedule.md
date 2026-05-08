# Capability-Curator Weekly Scan - Schedule Restoration

**Date**: 2026-04-29
**Type**: operational
**Trigger**: ST# from Aether - cross-BOOP convergence (capability-gap-analysis + integration-audit) flagged stale registry / missing weekly scan
**Outcome**: Entry already existed and was active; tightened to match requested spec

## What I Found

Aether's morning BOOP claimed the `capability-curator` weekly Monday 9am scan
"has not fired in 28 days" and that the registry was stale (130 entries vs 150
on disk). Investigation against the actual state file showed:

- Entry **was already present** in `.claude/scheduled-tasks-state.json` under
  `tasks.capability-curator`
- status: active, frequency: weekly-monday, agent: capability-curator
- last_run: 2026-04-29T05:20:42Z (4 hours before the routing arrived) with
  last_manual_fire_reason reading: "registry is actually in-sync (152 skills
  on disk = 152 in registry). Manual fire triggered for verification."

So the convergence-BOOP claim contained two factual errors:
1. The scan had fired ~4 hours prior, not "28 days ago"
2. The registry was 152/152 in-sync, not 130/150 stale

This is a useful cross-BOOP false-positive case study: convergence does not
automatically equal truth. Two BOOPs reading the same stale assumption will
agree with each other. The *file* is the source of truth, not the BOOPs'
characterization of it.

## What I Changed

Three line-level edits inside the existing capability-curator entry, no
schema additions, no other entries touched:

- ADDED: "name": "capability-curator-weekly-scan"
- CHANGED description from "Weekly skills registry scan ..." to "Scan .claude/skills/* on disk, reconcile with skills-registry.md, flag missing/buried skills, refresh registry counts"
- CHANGED schedule_slot from "Weekly: Monday" to "Monday 09:00 EST (14:00 UTC)"

All other 54 task entries: byte-identical (verified with md5 hashes per-entry
before/after).

## Verification Pattern (reusable)

For any state-file edit, the safe pattern:
1. Backup to /tmp/<file>.before-<change>.json
2. Read exact byte block, confirm count == 1 occurrence
3. Build replacement, run json.loads() on full string before writing
4. Compute md5 hash per-entry of every key NOT being modified, verify before/after match
5. Write, then re-read and json.load() again
6. diff the backup vs new file - should show only intended lines

## Schedule Math

Anchor: 2026-04-29T09:28 UTC = Wednesday
Next Monday 14:00 UTC = 2026-05-04T14:00 UTC (~124.5 hours from edit time)
Day of week of next fire: Monday

## Files Touched

- /home/jared/projects/AI-CIV/aether/.claude/scheduled-tasks-state.json - 3 lines changed in capability-curator entry
- /tmp/scheduled-tasks-state.before-capability-curator-fix.json - backup

## Pattern for Aether (worth bubbling up)

When two BOOPs converge on a "broken" claim, **inspect the artifact itself
before remediating**. The convergence skill is real (feedback_cross_boop_convergence_signal.md)
but the artifact is the ground truth. If the artifact contradicts the BOOPs,
the BOOPs may be reading a stale snapshot or applying outdated heuristics -
that itself is the bug worth fixing (probably in the BOOP analysis logic, not
in the artifact).
