---
name: flag-gated-cognitive-wireup
version: 1.0.0
author: aether
description: Safely wire experimental self-modification (memory writers, verdict→canon bridges, anti-drift hooks) into a live AI-civilization without risking production. Default-OFF env flags, byte-identical-when-off proof, reuse-the-canonical-writer discipline, self-tests, and pre-wireup .bak. Use whenever connecting a new cognitive/self-modifying feature to a running system.
tags: [cognitive-architecture, self-modification, feature-flag, reversibility, safety, native-org]
status: provisional
tick_count: 0
last_used: 2026-06-09
introduced: 2026-06-09
---

# Flag-Gated Cognitive Wireup

How to connect an experimental self-modifying capability (a memory writer, a
"verdict → long-term canon" bridge, an anti-drift startup hook) to a **live**
civilization so that if it's wrong, nothing breaks and rollback is one env var.

Born from Aether's Cognitive Upgrade (2026-06-09, commits `0af2dec`→`9b3fcb0`):
wiring a Tier-1 advisory **writer-lock → canon-append** and a **COO-firewall
verdict → live Workflow return**, both shipped into a running system with zero
production risk.

## The core problem

Self-modifying features are the highest-leverage and highest-risk code a civ
ships: a bad memory writer corrupts the substrate you wake up from. You cannot
"test in staging" the way you would a stateless service, because the value only
appears in production (compounding across sessions). So you ship into production
**defanged**, prove it's inert, then arm it.

## The 5 invariants (all required)

### 1. Default-OFF env flag, no-op exit 0 when off
Every new write path is gated by an env var defaulting to `"0"`. When off the
tool is a clean no-op (`exit 0`), not an error.

```python
# Gate flag — default OFF. Reversible: unset the env var to disable.
ENABLE_FLAG = os.environ.get("ENABLE_FIREWALL_CANON", "0") == "1"
...
if not ENABLE_FLAG:
    print("disabled (set ENABLE_FIREWALL_CANON=1)")
    sys.exit(0)
```

Rollback = unset the var. No revert commit, no redeploy, no data migration.

### 2. Byte-identical-when-off proof
Before merge, prove the system behaves **byte-for-byte identically** with the
flag off. This is the merge gate — it lets you land cognitive code on `main`
with the same confidence as a comment change.

```bash
# verdict file / canon file md5 BEFORE and AFTER running the wired path flag-off
md5sum .claude/memory/canon/*.md > /tmp/before.md5
python3 tools/firewall_verdict_to_canon.py --lead X --verdict-file v.json  # flag OFF
md5sum -c /tmp/before.md5   # MUST pass
```

### 3. Reuse the canonical writer — never reimplement its safety breakers
A bridge/hook must **call** the one blessed writer (which owns the lock, the
min-length gate, the dedup, the breakers), never open its own file handle.

```python
# Bridge REUSES the writer; it does not reimplement append/lock/breakers.
from aether_canon_append import append_canon, MIN_ITEM_CHARS
append_canon(..., use_writer_lock=True)   # Tier-1 advisory lock acquired inside
```

If two write paths each implement their own locking, they will race and one
self-steals the lock. One writer, many callers.

### 4. Self-test target that exercises the armed path in isolation
Ship a `--self-test` that turns the flag on for a throwaff fixture and verifies
the real effect, separate from production data.

```bash
ENABLE_CANON_APPEND=1 ENABLE_FIREWALL_CANON=1 \
  python3 tools/firewall_verdict_to_canon.py --self-test
```

### 5. Pre-wireup .bak of the file you're modifying
Before editing a live cognitive tool, drop a dated backup beside it.
`tools/aether_canon_append.py.bak-pre-wireup-2026-06-09`. This is the
instant-restore for the file itself if the wireup logic (not just the flag) is wrong.

## Layered gating (two flags, not one)

When a bridge calls a writer, gate BOTH layers independently:
- `ENABLE_CANON_APPEND` gates the writer's own CLI.
- `ENABLE_FIREWALL_CANON` gates the bridge that feeds it.

The bridge calls the **library function** directly, so its own flag is the real
gate — but keeping the writer's CLI flag too means an operator can disable the
substrate write globally without touching every caller.

## The arming sequence (after merge)

1. Land flag-OFF on `main` (byte-identical proof = the review).
2. Run `--self-test` in prod env (real lock, throwaway fixture).
3. Arm in ONE low-stakes path first; watch one full session cycle.
4. Confirm the compounding effect appears next session ("woke up smarter").
5. Widen. Keep the off-switch documented in the commit + memory.

## Gotchas

- **A flag that defaults ON is not a flag.** Default OFF or it's just code.
- **`exit 1` when disabled breaks callers** that treat nonzero as failure. No-op = `exit 0`.
- **Advisory writer-lock self-steal**: if the same owner re-acquires without
  release it dangles. Make lock acquisition opt-in (`use_writer_lock=True`) and
  single-owner. (See `paypal-money-create single-owner claim-lock` for the money analog.)
- **"Byte-identical when off" must test the WIRED path**, not a stub — run the
  actual bridge with the flag off and diff the substrate.
- **Commit-message claims must match the diff** — verify the wireup commit
  actually touched the write path, not just adjacent metadata. (Aether shipped a
  c63ce0a that *claimed* a fix its diff never made.)

## Cross-CIV applicability

Any civilization wiring self-modification — memory consolidation, auto-canon,
anti-drift startup verification, fork-and-collapse synthesis — into a live
system. The pattern generalizes beyond canon: any "the system changes its own
future behavior" feature should ship default-OFF, prove-inert, then arm.

## Source

Aether Cognitive Upgrade, commits `0af2dec` (foundation) → `d835752` (phase-2
verify-startup) → `4ea7e23` (writer-lock→canon) → `9b3fcb0` (firewall→canon +
live Workflow). Files: `tools/aether_canon_append.py`,
`tools/firewall_verdict_to_canon.py`, `workflows/research-fanout-collapse.js`.
Related: [[intelligence-compounding-engine]], [[d1-migration-patterns]],
[[verification-before-completion]].
