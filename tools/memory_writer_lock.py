#!/usr/bin/env python3
"""
Tier-1 Advisory Writer Lock for AI-CIV Memory Subtrees.

Part of the aiciv-native-org federation integration (Phase 3, Single-Writer Memory).

WHAT THIS IS
------------
A *cooperative, advisory* lock — NOT an OS-enforced (flock/fcntl) blocking lock.
It is a `.writer-lock` JSON sentinel file placed inside a memory subtree. Concurrent
overnight V3 writers AGREE to check for it before writing to a shared subtree. If a
fresh lock owned by someone else is present, a well-behaved writer backs off (or
writes to its own non-shared path). If the lock is stale (TTL expired) or owned by
a dead PID, any writer may steal it.

This takes "zero engineering" in the sense the architect intended: no kernel locks,
no daemon, no schema change. It is a convention enforced by cooperation.

DESIGN NOTES
------------
- Lock file: `<subtree>/.writer-lock`
- Lock content (JSON): {owner, pid, acquired_at_iso, ttl_seconds, host}
- Staleness: age = now - acquired_at; stale if age > ttl_seconds.
- Dead-PID steal: if the recorded pid is on this host and not alive, steal.
  (Cross-host PIDs cannot be checked for liveness, so only TTL governs those.)
- release() only removes a lock you own (never delete someone else's lock).
- Atomic-ish write via temp file + os.replace to avoid torn reads.

This is a normal Python script (not a Claude "workflow" script), so standard
`datetime.datetime.now(datetime.timezone.utc)` usage is fine.

USAGE
-----
    from tools.memory_writer_lock import writer_lock, acquire, release, is_locked

    with writer_lock("/path/to/memory/agent-learnings/web-researcher", owner="overnight-v3-ws7"):
        # ... do writes into that subtree ...
        ...

    # or manual:
    if acquire(subtree, owner="ws7"):
        try:
            ...
        finally:
            release(subtree, owner="ws7")
    else:
        # someone else holds it — back off or write elsewhere
        ...

Self-test:
    python3 tools/memory_writer_lock.py --selftest
"""

import os
import sys
import json
import socket
import tempfile
import datetime
from pathlib import Path
from typing import Optional, Dict, Any

LOCK_FILENAME = ".writer-lock"
DEFAULT_TTL_SECONDS = 900  # 15 minutes


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _iso(dt: datetime.datetime) -> str:
    return dt.isoformat()


def _parse_iso(value: str) -> Optional[datetime.datetime]:
    try:
        dt = datetime.datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _lock_path(subtree_path: str) -> Path:
    return Path(subtree_path) / LOCK_FILENAME


def _pid_alive(pid: int) -> bool:
    """Return True if a process with `pid` exists on THIS host.

    Uses signal 0 (no-op) which raises if the pid is invalid/gone.
    Note: meaningful only for locks acquired on the same host.
    """
    if pid is None or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but owned by another user — treat as alive.
        return True
    except OSError:
        return False
    return True


def _read_lock(subtree_path: str) -> Optional[Dict[str, Any]]:
    """Read and parse the lock file. Returns dict or None if absent/corrupt."""
    p = _lock_path(subtree_path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # Corrupt/unreadable lock is treated as stealable (return None signals
        # callers via _is_stale path). We still surface the raw absence here.
        return None


def _atomic_write_lock(subtree_path: str, data: Dict[str, Any]) -> None:
    """Write the lock JSON atomically inside the subtree dir."""
    subtree = Path(subtree_path)
    subtree.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(subtree), prefix=".writer-lock.tmp.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, str(_lock_path(subtree_path)))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _is_stale(lock: Dict[str, Any]) -> bool:
    """A lock is stale if past its TTL, or its (same-host) PID is dead."""
    acquired = _parse_iso(lock.get("acquired_at_iso", ""))
    ttl = lock.get("ttl_seconds", DEFAULT_TTL_SECONDS)
    if acquired is None:
        return True  # unparseable timestamp -> stale
    age = (_now_utc() - acquired).total_seconds()
    if age > ttl:
        return True
    # Dead-PID steal only meaningful when the lock was created on this host.
    if lock.get("host") == socket.gethostname():
        pid = lock.get("pid")
        if isinstance(pid, int) and not _pid_alive(pid):
            return True
    return False


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def acquire(subtree_path: str, owner: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> bool:
    """Attempt to acquire the advisory writer lock for a subtree.

    Returns True if acquired (or re-acquired by the same owner, or a stale/dead
    lock was stolen). Returns False if a *fresh* lock owned by a different
    owner/pid is present (caller should back off or write to its own path).
    """
    existing = _read_lock(subtree_path)
    if existing is not None:
        same_owner = existing.get("owner") == owner
        same_pid = existing.get("pid") == os.getpid()
        if not (same_owner and same_pid):
            # Held by someone else (or same owner, different pid). Only steal if stale.
            if not _is_stale(existing):
                return False
        # else: same owner+pid -> re-entrant refresh, fall through to rewrite.

    lock_data = {
        "owner": owner,
        "pid": os.getpid(),
        "acquired_at_iso": _iso(_now_utc()),
        "ttl_seconds": int(ttl_seconds),
        "host": socket.gethostname(),
    }
    _atomic_write_lock(subtree_path, lock_data)
    return True


def release(subtree_path: str, owner: str) -> bool:
    """Release the lock only if owned by `owner`. Never delete others' locks.

    Returns True if a lock owned by `owner` was removed, False otherwise.
    """
    existing = _read_lock(subtree_path)
    if existing is None:
        return False
    if existing.get("owner") != owner:
        return False
    try:
        _lock_path(subtree_path).unlink()
        return True
    except FileNotFoundError:
        return False
    except OSError:
        return False


def is_locked(subtree_path: str) -> Optional[Dict[str, Any]]:
    """Return the current lock holder info dict, or None if not (effectively) locked.

    A stale lock is reported as None (it is effectively free / stealable), so
    callers can treat the return value as "is there an active writer here?".
    """
    existing = _read_lock(subtree_path)
    if existing is None:
        return None
    if _is_stale(existing):
        return None
    return existing


class writer_lock:
    """Context manager for advisory writer locking.

        with writer_lock(subtree, owner="ws7"):
            ...   # protected writes

    On enter: acquires the lock. Raises BlockingIOError if a fresh lock owned by
    someone else is held (so `with` callers fail fast rather than silently racing).
    On exit: releases the lock if still owned by us.
    """

    def __init__(self, subtree_path: str, owner: str, ttl: int = DEFAULT_TTL_SECONDS):
        self.subtree_path = subtree_path
        self.owner = owner
        self.ttl = ttl
        self.acquired = False

    def __enter__(self) -> "writer_lock":
        self.acquired = acquire(self.subtree_path, self.owner, self.ttl)
        if not self.acquired:
            holder = is_locked(self.subtree_path)
            holder_owner = holder.get("owner") if holder else "unknown"
            raise BlockingIOError(
                f"writer-lock held by '{holder_owner}' at {self.subtree_path}"
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self.acquired:
            release(self.subtree_path, self.owner)
            self.acquired = False
        return False  # never suppress exceptions


# --------------------------------------------------------------------------- #
# Self-test
# --------------------------------------------------------------------------- #
def _selftest() -> int:
    import shutil

    tmp = tempfile.mkdtemp(prefix="writer-lock-selftest-")
    subtree = os.path.join(tmp, "agent-learnings", "demo-dept")
    os.makedirs(subtree, exist_ok=True)

    passed = True

    def check(label: str, cond: bool):
        nonlocal passed
        status = "PASS" if cond else "FAIL"
        if not cond:
            passed = False
        print(f"[{status}] {label}")

    try:
        # 1. acquire by owner A
        check("acquire by owner-A succeeds", acquire(subtree, "owner-A") is True)

        # 2. is_locked reports owner-A
        holder = is_locked(subtree)
        check("is_locked reports owner-A", holder is not None and holder.get("owner") == "owner-A")

        # 3. second acquire by different owner-B returns False (fresh lock)
        check("acquire by owner-B returns False (fresh lock held)", acquire(subtree, "owner-B") is False)

        # 4. owner-B cannot release owner-A's lock
        check("owner-B cannot release owner-A's lock", release(subtree, "owner-B") is False)
        check("lock still present after foreign release attempt", is_locked(subtree) is not None)

        # 5. owner-A releases successfully
        check("owner-A releases own lock", release(subtree, "owner-A") is True)
        check("is_locked None after release", is_locked(subtree) is None)

        # 6. acquire succeeds again after release
        check("acquire after release succeeds", acquire(subtree, "owner-C") is True)
        release(subtree, "owner-C")

        # 7. simulate STALE lock (old timestamp, foreign owner) -> can be stolen
        stale = {
            "owner": "ghost-owner",
            "pid": 999999,  # almost certainly dead
            "acquired_at_iso": _iso(_now_utc() - datetime.timedelta(seconds=10000)),
            "ttl_seconds": 900,
            "host": "some-other-host",  # force TTL-only staleness path
        }
        _atomic_write_lock(subtree, stale)
        check("stale lock reported as not-locked (effectively free)", is_locked(subtree) is None)
        check("acquire steals stale lock", acquire(subtree, "owner-D") is True)
        holder = is_locked(subtree)
        check("stolen lock now owned by owner-D", holder is not None and holder.get("owner") == "owner-D")
        release(subtree, "owner-D")

        # 8. dead-PID steal on THIS host (fresh timestamp, but pid dead)
        dead = {
            "owner": "crashed-writer",
            "pid": 999998,  # dead
            "acquired_at_iso": _iso(_now_utc()),  # fresh
            "ttl_seconds": 900,
            "host": socket.gethostname(),  # this host -> pid liveness checked
        }
        _atomic_write_lock(subtree, dead)
        check("dead-pid lock reported as not-locked", is_locked(subtree) is None)
        check("acquire steals dead-pid lock", acquire(subtree, "owner-E") is True)
        release(subtree, "owner-E")

        # 9. context manager acquires + releases
        with writer_lock(subtree, owner="ctx-owner"):
            check("context manager holds lock inside block", is_locked(subtree) is not None)
        check("context manager released lock after block", is_locked(subtree) is None)

        # 10. context manager raises when fresh lock held by another
        acquire(subtree, "owner-F")
        raised = False
        try:
            with writer_lock(subtree, owner="owner-G"):
                pass
        except BlockingIOError:
            raised = True
        check("context manager raises BlockingIOError on contested fresh lock", raised)
        release(subtree, "owner-F")

        # 11. idempotency / cleanup: no leftover lock file
        check("no leftover .writer-lock after selftest", not _lock_path(subtree).exists())

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("SELFTEST RESULT:", "ALL PASS" if passed else "FAILURES PRESENT")
    return 0 if passed else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    print(__doc__)
    print("Run with --selftest to execute the self-test.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
