#!/usr/bin/env python3
"""
firewall_verdict_to_canon.py — Bridge a COO-firewall Workflow verdict into canon.

Part of the Aether Cognitive Upgrade (compounding-memory). The
`workflows/research-fanout-collapse.js` recipe collapses N raw specialist
findings into ONE firewall verdict (raw dies in the synthesizer's context;
Primary gets only the verdict). This helper optionally COMPOUNDS that verdict
into per-lead canon so the system "wakes up smarter" next session.

It REUSES aether_canon_append.append_canon (never reimplements the writer or its
safety breakers) and acquires the Tier-1 advisory writer-lock (use_writer_lock=True).

Gate flag: ENABLE_FIREWALL_CANON=1 (default OFF). When OFF this is a no-op exit 0.
Canon append itself is additionally gated by ENABLE_CANON_APPEND inside the writer's
CLI; here we call the library function directly, so ENABLE_FIREWALL_CANON is the gate.

Verdict schema (from research-fanout-collapse.js):
    { headline, answer, decisions_needed?, per_angle?, artifact? }

CLI:
    ENABLE_FIREWALL_CANON=1 python3 tools/firewall_verdict_to_canon.py \\
        --lead <id> --receipt <artifact-path-or-sha> --verdict-json '<json>'
    # or --verdict-file <path-to-json>

Self-test:
    ENABLE_CANON_APPEND=1 ENABLE_FIREWALL_CANON=1 \\
        python3 tools/firewall_verdict_to_canon.py --self-test
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MEM_CANON = REPO_ROOT / ".claude" / "memory" / "canon"

# Gate flag — default OFF. Reversible: unset the env var to disable.
ENABLE_FLAG = os.environ.get("ENABLE_FIREWALL_CANON", "0") == "1"

# Reuse the canonical writer (its safety breakers + lock live there).
sys.path.insert(0, str(REPO_ROOT / "tools"))
from aether_canon_append import append_canon, MIN_ITEM_CHARS  # noqa: E402


def _build_item(verdict: dict) -> str:
    """Compose a >=MIN_ITEM_CHARS canon item from headline + answer.

    Pads from `answer` then `decisions_needed` if the headline alone is short.
    The downstream 80-char gate still enforces the real minimum.
    """
    headline = str(verdict.get("headline", "")).strip()
    answer = str(verdict.get("answer", "")).strip()
    item = headline
    if answer:
        item = f"{headline} — {answer}" if headline else answer
    # If still short, append the decisions list to add substance.
    if len(item) < MIN_ITEM_CHARS:
        decisions = verdict.get("decisions_needed") or []
        if isinstance(decisions, list) and decisions:
            item = item + " | decisions: " + "; ".join(str(d) for d in decisions[:5])
    return item.strip()


def bridge_verdict(lead: str, receipt: str, verdict: dict) -> dict:
    """Append a firewall verdict to canon as a 'finding'. Returns the entry.

    Uses the Tier-1 advisory writer-lock (advisory: never blocks).
    """
    item = _build_item(verdict)
    return append_canon(
        lead=lead,
        kind="finding",
        item=item,
        receipt=receipt,
        use_writer_lock=True,
        lock_owner="firewall_verdict_to_canon",
    )


def run_self_test() -> int:
    """Write a synthetic verdict to a throwaway lead and verify it landed.

    Requires BOTH ENABLE_CANON_APPEND=1 (for the writer's self-test path is
    not used here — we call the library directly) and ENABLE_FIREWALL_CANON=1.
    """
    lead = "firewall-selftest"
    receipt = str(REPO_ROOT / "CLAUDE.md")
    if not Path(receipt).exists():
        print(f"FAIL: test receipt {receipt} missing")
        return 1

    marker = uuid.uuid4().hex[:8]
    verdict = {
        "headline": f"Firewall-bridge self-test {marker}",
        "answer": "This verdict was synthesized by the COO firewall and bridged into "
                  "canon to prove compounding memory wires end-to-end without raw leakage.",
        "decisions_needed": ["Ship the bridge? (default YES)"],
        "artifact": receipt,
    }

    print("=== Self-Test: bridge synthetic verdict into canon ===")
    entry = bridge_verdict(lead=lead, receipt=receipt, verdict=verdict)
    print(f"appended id={entry['id']} item_len={len(entry['item'])}")

    log = MEM_CANON / lead / "log.jsonl"
    with log.open("r", encoding="utf-8") as fh:
        last = json.loads(fh.readlines()[-1])

    ok = (
        last["id"] == entry["id"]
        and marker in last["item"]
        and last.get("receipt_resolved") is True
        and last.get("kind") == "finding"
    )
    if ok:
        print("PASS: verdict landed in canon with receipt_resolved=true")
        # confirm no stale lock left behind
        from memory_writer_lock import is_locked
        if is_locked(str(MEM_CANON / lead)) is not None:
            print("WARN: lock still active after bridge (should be released)")
        return 0
    print("FAIL: verdict did not land correctly")
    print(json.dumps(last, indent=2))
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="firewall_verdict_to_canon.py",
        description="Bridge a COO-firewall Workflow verdict into per-lead canon (flag-gated).",
    )
    parser.add_argument("--lead", help="Lead identity (e.g. 'result-synthesizer')")
    parser.add_argument("--receipt", help="Proof: artifact path the workflow wrote OR git SHA")
    parser.add_argument("--verdict-json", help="Verdict JSON string")
    parser.add_argument("--verdict-file", help="Path to a file containing verdict JSON")
    parser.add_argument("--self-test", action="store_true", help="Run end-to-end self-test")

    args = parser.parse_args(argv)

    if not ENABLE_FLAG:
        print("firewall->canon bridge disabled (set ENABLE_FIREWALL_CANON=1)")
        return 0

    if args.self_test:
        return run_self_test()

    missing = [n for n in ("lead", "receipt") if not getattr(args, n)]
    if not (args.verdict_json or args.verdict_file):
        missing.append("verdict-json|verdict-file")
    if missing:
        parser.error("missing: " + ", ".join(f"--{m}" for m in missing))

    if args.verdict_file:
        verdict = json.loads(Path(args.verdict_file).read_text(encoding="utf-8"))
    else:
        verdict = json.loads(args.verdict_json)

    try:
        entry = bridge_verdict(lead=args.lead, receipt=args.receipt, verdict=verdict)
        print(json.dumps({"ok": True, "appended": entry}, ensure_ascii=False))
        return 0
    except ValueError as e:
        print(f"reject: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
