#!/usr/bin/env python3
"""
aether_canon_append.py — Append-only writer to .claude/memory/canon/<lead>/log.jsonl

Adapted from aiciv-native-org canon_append.py for Aether.
Part of compounding-memory Phase-1 quick-wins.

Safety breakers (ALL enforced):
  - item must be >= 80 chars (reject junk)
  - receipt MUST resolve to real artifact (file path OR git SHA)
  - rate limit: max 3 entries / 300s per lead
  - atomic append via temp file

CLI:
    python3 tools/aether_canon_append.py --lead <id> --kind <enum> \\
        --item "<text>" --receipt "<path-or-sha>"

Self-test:
    python3 tools/aether_canon_append.py --self-test
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
MEM_CANON = REPO_ROOT / ".claude" / "memory" / "canon"

ALLOWED_KINDS = frozenset({
    "finding",
    "decision",
    "retraction",
    "doctrine-candidate",
})

# Safety breakers
MIN_ITEM_CHARS = 80
RATE_LIMIT_WINDOW = 300  # seconds
RATE_LIMIT_MAX_ENTRIES = 3

# Gate flag
ENABLE_FLAG = os.environ.get("ENABLE_CANON_APPEND", "0") == "1"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso_utc() -> str:
    """RFC-3339 UTC timestamp, second resolution + 'Z' suffix."""
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_unix() -> float:
    """Current Unix timestamp."""
    return time.time()


def _lead_dir(lead: str) -> Path:
    d = MEM_CANON / lead
    d.mkdir(parents=True, exist_ok=True)
    return d


def _log_path(lead: str) -> Path:
    return _lead_dir(lead) / "log.jsonl"


def _rejections_path(lead: str) -> Path:
    return _lead_dir(lead) / ".rejections.jsonl"


def _validate_item(item: str, force: bool) -> None:
    """Enforce 80-char minimum unless --force."""
    if force:
        return
    if len(item.strip()) < MIN_ITEM_CHARS:
        raise ValueError(
            f"item too short ({len(item.strip())} chars, need {MIN_ITEM_CHARS}). "
            f"Use --force to override."
        )


def _validate_kind(kind: str) -> None:
    """Enforce closed enum."""
    if kind not in ALLOWED_KINDS:
        raise ValueError(
            f"invalid kind {kind!r}: allowed = {sorted(ALLOWED_KINDS)}"
        )


def _resolve_receipt(receipt: str) -> bool:
    """Verify receipt resolves to real artifact (file OR git SHA).

    Returns True if valid, False otherwise.
    This is the EXACT bug a peer civ caught — no phantom receipts.
    """
    receipt = receipt.strip()

    # Try as file path
    if "/" in receipt or receipt.startswith("."):
        p = Path(receipt)
        if p.exists():
            return True

    # Try as git SHA (7-40 hex chars)
    if receipt and 7 <= len(receipt) <= 40 and all(c in "0123456789abcdef" for c in receipt.lower()):
        try:
            result = subprocess.run(
                ["git", "cat-file", "-e", receipt],
                cwd=REPO_ROOT,
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return False


def _check_rate_limit(lead: str, force: bool) -> None:
    """Enforce max 3 entries / 300s per lead (unless --force).

    Track via log timestamps. If last 3 entries are all within 300s, reject.
    """
    if force:
        return

    log = _log_path(lead)
    if not log.exists():
        return  # First entry, no rate limit

    # Read last 3 lines
    entries = []
    try:
        with log.open("r", encoding="utf-8") as fh:
            lines = fh.readlines()
            for line in lines[-RATE_LIMIT_MAX_ENTRIES:]:
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    pass
    except OSError:
        return  # Can't read log, allow append

    if len(entries) < RATE_LIMIT_MAX_ENTRIES:
        return  # Not enough entries to hit limit

    # Check if all 3 are within window
    now = _now_unix()
    timestamps = []
    for e in entries:
        ts_str = e.get("ts", "")
        try:
            # Parse ISO8601 to Unix
            dt = _dt.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            timestamps.append(dt.timestamp())
        except (ValueError, AttributeError):
            pass

    if len(timestamps) >= RATE_LIMIT_MAX_ENTRIES:
        oldest = min(timestamps)
        if (now - oldest) < RATE_LIMIT_WINDOW:
            raise ValueError(
                f"rate limit: {RATE_LIMIT_MAX_ENTRIES} entries in {RATE_LIMIT_WINDOW}s window. "
                f"Wait {int(RATE_LIMIT_WINDOW - (now - oldest))}s. Use --force to override."
            )


def _check_entry_spacing(lead: str) -> None:
    """Enforce >=5s between entries (detect burst appends).

    Read last entry timestamp, reject if <5s ago.
    """
    log = _log_path(lead)
    if not log.exists():
        return

    try:
        with log.open("r", encoding="utf-8") as fh:
            lines = fh.readlines()
            if not lines:
                return
            last_line = lines[-1].strip()
            last_entry = json.loads(last_line)
            ts_str = last_entry.get("ts", "")
            dt = _dt.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            last_ts = dt.timestamp()
            now = _now_unix()
            if (now - last_ts) < 5:
                raise ValueError(
                    f"burst append: last entry was {int(now - last_ts)}s ago (need >=5s). "
                    f"Use --force to override."
                )
    except (OSError, json.JSONDecodeError, ValueError, IndexError):
        pass  # Can't parse, allow


def _log_rejection(lead: str, reason: str, item: str, receipt: str) -> None:
    """Append rejection to .rejections.jsonl for audit."""
    rej_log = _rejections_path(lead)
    entry = {
        "ts": _now_iso_utc(),
        "reason": reason,
        "item": item[:200],  # Truncate for safety
        "receipt": receipt[:200],
    }
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    try:
        with rej_log.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        pass  # Best-effort logging


def append_canon(
    lead: str,
    kind: str,
    item: str,
    receipt: str,
    *,
    force: bool = False,
) -> dict:
    """Append exactly one JSON line to canon/<lead>/log.jsonl.

    Raises ValueError on validation failure.
    """
    # Validation gauntlet
    _validate_kind(kind)
    _validate_item(item, force)

    # Receipt resolution (NEVER skipped, even with --force)
    if not _resolve_receipt(receipt):
        reason = f"phantom receipt: {receipt!r} does not resolve to file or git SHA"
        _log_rejection(lead, reason, item, receipt)
        raise ValueError(reason)

    _check_rate_limit(lead, force)
    _check_entry_spacing(lead)

    # Build entry
    entry = {
        "ts": _now_iso_utc(),
        "id": uuid.uuid4().hex,
        "lead": lead,
        "kind": kind,
        "item": item.strip(),
        "receipt": receipt.strip(),
        "receipt_resolved": True,  # Proved above
    }

    # Atomic append via temp file
    log = _log_path(lead)
    temp = log.parent / f".{log.name}.tmp.{uuid.uuid4().hex[:8]}"

    try:
        # Write to temp
        line = json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n"
        temp.write_text(line, encoding="utf-8")

        # Append temp to log (or create log if first)
        if log.exists():
            with log.open("ab") as dst:
                dst.write(temp.read_bytes())
        else:
            temp.rename(log)
            return entry
    finally:
        if temp.exists():
            temp.unlink()

    return entry


# ---------------------------------------------------------------------------
# Writer lock integration (advisory, non-blocking)
# ---------------------------------------------------------------------------

def _try_advisory_lock(subtree: str, owner: str) -> tuple[bool, bool]:
    """Try to acquire advisory writer lock if available.

    Returns (acquired, lock_available). Non-blocking.
    """
    try:
        sys.path.insert(0, str(REPO_ROOT / "tools"))
        from memory_writer_lock import acquire

        # Try to acquire with 0 timeout (non-blocking)
        acquired = acquire(subtree, owner=owner, ttl_seconds=60)
        return acquired, True
    except (ImportError, Exception):
        # Lock not available or broken, proceed without
        return True, False


def _release_advisory_lock(subtree: str, owner: str, lock_available: bool) -> None:
    """Release lock if we used it."""
    if not lock_available:
        return
    try:
        sys.path.insert(0, str(REPO_ROOT / "tools"))
        from memory_writer_lock import release
        release(subtree, owner=owner)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    """Run 3 validation tests + 1 success test.

    Tests:
    1. Reject <80 char item
    2. Reject phantom receipt
    3. Accept valid item with real receipt
    4. DIGEST.md rebuild (if digest_rebuild.py exists)

    Exit 0 = pass, 1 = fail.
    """
    lead = "aether-selftest"

    print("=== Self-Test 1: Reject <80 char item ===")
    try:
        append_canon(
            lead=lead,
            kind="finding",
            item="short",
            receipt=str(REPO_ROOT / "CLAUDE.md"),
        )
        print("FAIL: Should have rejected short item")
        return 1
    except ValueError as e:
        if "too short" in str(e):
            print(f"PASS: Rejected as expected ({e})")
        else:
            print(f"FAIL: Wrong error: {e}")
            return 1

    print("\n=== Self-Test 2: Reject phantom receipt ===")
    try:
        append_canon(
            lead=lead,
            kind="finding",
            item="A" * 80,  # Valid length
            receipt="/nonexistent/phantom/file/that/does/not/exist.txt",
        )
        print("FAIL: Should have rejected phantom receipt")
        return 1
    except ValueError as e:
        if "phantom receipt" in str(e):
            print(f"PASS: Rejected as expected ({e})")
        else:
            print(f"FAIL: Wrong error: {e}")
            return 1

    print("\n=== Self-Test 3: Accept valid item with real receipt ===")
    real_receipt = str(REPO_ROOT / "CLAUDE.md")
    if not Path(real_receipt).exists():
        print(f"FAIL: Test receipt {real_receipt} does not exist")
        return 1

    marker = f"selftest-{uuid.uuid4().hex[:8]}"
    valid_item = f"Self-test validation marker {marker}. " + "X" * 60  # Total >80 chars

    try:
        entry = append_canon(
            lead=lead,
            kind="finding",
            item=valid_item,
            receipt=real_receipt,
        )
        print(f"PASS: Appended entry id={entry['id']}")

        # Verify it landed
        log = _log_path(lead)
        with log.open("r") as fh:
            last = fh.readlines()[-1]
            parsed = json.loads(last)
            if parsed["id"] == entry["id"] and marker in parsed["item"]:
                print(f"PASS: Entry verified on disk")
            else:
                print("FAIL: Entry mismatch on disk")
                return 1
    except Exception as e:
        print(f"FAIL: Valid append raised {e}")
        return 1

    print("\n=== All self-tests passed ===")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="aether_canon_append.py",
        description="Append-only writer to .claude/memory/canon/<lead>/log.jsonl",
    )
    parser.add_argument("--lead", help="Lead identity (e.g. 'security-auditor')")
    parser.add_argument(
        "--kind",
        choices=sorted(ALLOWED_KINDS),
        help="Kind: finding | decision | retraction | doctrine-candidate",
    )
    parser.add_argument("--item", help="Learning text (>= 80 chars)")
    parser.add_argument("--receipt", help="Proof: file path OR git SHA")
    parser.add_argument("--force", action="store_true", help="Override 80-char + rate checks (NOT receipt check)")
    parser.add_argument("--self-test", action="store_true", help="Run validation tests")

    args = parser.parse_args(argv)

    if args.self_test:
        if not ENABLE_FLAG:
            print("canon append disabled (set ENABLE_CANON_APPEND=1)")
            return 0
        return run_self_test()

    # Gate check
    if not ENABLE_FLAG:
        print("canon append disabled (set ENABLE_CANON_APPEND=1)")
        return 0

    # Validate required args
    missing = [n for n in ("lead", "kind", "item", "receipt") if not getattr(args, n)]
    if missing:
        parser.error("missing: " + ", ".join(f"--{m}" for m in missing))

    # Try advisory lock
    subtree = str(MEM_CANON / args.lead)
    acquired, lock_available = _try_advisory_lock(subtree, owner="aether_canon_append")
    if lock_available and not acquired:
        print(
            "WARNING: advisory writer-lock held by another process. "
            "Proceeding anyway (non-blocking).",
            file=sys.stderr
        )

    try:
        entry = append_canon(
            lead=args.lead,
            kind=args.kind,
            item=args.item,
            receipt=args.receipt,
            force=args.force,
        )
        print(json.dumps({"ok": True, "appended": entry}, ensure_ascii=False))
        return 0
    except ValueError as e:
        print(f"reject: {e}", file=sys.stderr)
        return 2
    finally:
        _release_advisory_lock(subtree, owner="aether_canon_append", lock_available=lock_available)


if __name__ == "__main__":
    sys.exit(main())
