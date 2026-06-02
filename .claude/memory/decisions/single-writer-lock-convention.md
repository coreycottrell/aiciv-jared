# Single-Writer Memory — Tier-1 Advisory Writer Lock Convention

**Status**: Active (Phase 3, aiciv-native-org federation integration)
**Date**: 2026-06-02
**Authority**: ST# build under explicit Jared GO ("do it all")
**Architect spec**: `.claude/memory/agent-learnings/architect/20260601-aiciv-native-org-federation-integration.md`
**Implementation**: `tools/memory_writer_lock.py`

---

## Problem

Overnight V3 runs many workstreams in parallel. Two or more of them can write into
the *same* memory subtree concurrently (e.g. two BOOPs both appending to
`agent-learnings/web-researcher/`). Uncoordinated concurrent writes risk scribble
/ corruption (interleaved or last-writer-wins clobbering).

## Decision

Adopt **Tier 1**: a *cooperative, advisory* `.writer-lock` file convention.

It is **NOT** an OS-enforced (flock/fcntl) blocking lock. It is a sentinel JSON
file that well-behaved writers AGREE to check before writing a shared subtree.
Architect guidance: "The `.writer-lock` file convention (Tier 1) is sufficient for
overnight V3 safety and takes zero engineering." Tiers 2-3 (canon_append.py
governance) are deferred.

This is **opt-in and additive**. `memory_core.py` default behavior is unchanged.

---

## Mechanics

- **Lock file**: `<subtree>/.writer-lock`
- **Contents (JSON)**: `{owner, pid, acquired_at_iso, ttl_seconds, host}`
- **TTL**: default 900s (15 min). A lock older than its TTL is *stale*.
- **Stale-steal**: any writer may overwrite (steal) a lock that is either past TTL,
  has an unparseable timestamp, or (same-host only) names a dead PID.
- **Cross-host PIDs**: liveness cannot be checked, so only TTL governs them.
- **release()**: removes the lock *only if you own it*. Never delete another
  owner's lock.
- **Atomic write**: temp file + `os.replace` to avoid torn reads.

## Subtree Granularity

Lock at the **department / agent-learnings subdirectory** level, e.g.:

```
.claude/memory/agent-learnings/<agent-or-dept>/
```

This is coarse enough to be cheap and meaningful (one active writer per agent's
learning dir at a time) without serializing the entire memory tree. Do NOT lock
the whole `.claude/memory` root — that would needlessly block unrelated writers.

## When To Acquire

Concurrent / overnight writers SHOULD acquire the lock when they will write
multiple files into a shared subtree, or append over time:

```python
from tools.memory_writer_lock import writer_lock

with writer_lock(".claude/memory/agent-learnings/web-researcher",
                 owner="overnight-v3-ws7", ttl=900):
    # ... all writes to this subtree ...
```

If `acquire()` returns False (a *fresh* lock is held by someone else), the
well-behaved writer either:
1. **backs off** and retries later, or
2. **writes to its own non-shared path** (e.g. a per-workstream subdir), or
3. for `with writer_lock(...)`, catches `BlockingIOError` and chooses one of the above.

Single-writer / interactive sessions do NOT need to acquire — this is purely a
concurrency-safety convention for parallel writers.

## Cooperative, Not Enforced

Because it is advisory, a misbehaving writer *can* ignore the lock and write anyway.
That is by design (Tier 1 = zero engineering, no kernel locks). The optional
`memory_core` hook (below) only *warns*; it never blocks.

## Optional memory_core Awareness Hook

`MemoryStore.write_entry()` gained two OPTIONAL, default-off parameters:

```python
store.write_entry(agent_id, entry,
                  warn_on_writer_lock=True,   # default False
                  lock_owner="my-workstream") # used only for the warning
```

When `warn_on_writer_lock=True` and the target subtree holds a lock owned by a
*different* owner, a `logging` WARNING is emitted and **the write proceeds
unchanged**. With the defaults (`warn_on_writer_lock=False`), `write_entry` is
byte-for-byte identical to its prior behavior — no lock is read, nothing changes.

---

## Verification

`python3 tools/memory_writer_lock.py --selftest` — 17 checks, ALL PASS:
acquire / is_locked / contested-acquire-returns-False / foreign-release-rejected /
release / re-acquire / stale-steal / dead-pid-steal / context-manager
acquire+release / context-manager raises on contested fresh lock / no leftover
lock file (idempotent cleanup).

`python3 tools/memory_core.py` — all built-in MemoryEntry + MemoryStore tests pass
with default behavior unchanged.

## Rollback

- Remove `tools/memory_writer_lock.py`.
- Restore `tools/memory_core.py` from `tools/memory_core.py.bak-pre-phase3-2026-06-02`.
- Delete this doc.

No data migration, no schema change, nothing to undo in stored memories.
