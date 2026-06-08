#!/usr/bin/env python3
"""
aether_digest_rebuild.py — Mechanical digest builder for canon memory.

Reads .claude/memory/canon/<lead>/log.jsonl, writes DIGEST.md with:
  - Frontmatter (lead, rebuilt_ts, ledger_lines_at_rebuild)
  - Last 200 canon items grouped by kind (decisions first, findings, retractions applied)

Phase 1: Extractive/mechanical (no LLM calls)
Phase 2: Agentic synthesis (importance over recency)

CLI:
    python3 tools/aether_digest_rebuild.py --lead <id>
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
MEM_CANON = REPO_ROOT / ".claude" / "memory" / "canon"

DIGEST_TAIL_LINES = 200

# Gate flag
ENABLE_FLAG = os.environ.get("ENABLE_DIGEST_REBUILD", "0") == "1"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _lead_dir(lead: str) -> Path:
    return MEM_CANON / lead


def _log_path(lead: str) -> Path:
    return _lead_dir(lead) / "log.jsonl"


def _digest_path(lead: str) -> Path:
    return _lead_dir(lead) / "DIGEST.md"


def rebuild_digest(lead: str) -> None:
    """Rebuild DIGEST.md for given lead.

    Mechanism:
      1. Read last 200 lines from log.jsonl
      2. Parse JSON, group by kind
      3. Apply retractions (omit referenced items)
      4. Render as markdown bullets: decisions first, then findings
      5. Write with frontmatter
    """
    log = _log_path(lead)
    digest = _digest_path(lead)

    if not log.exists():
        print(f"No log for lead {lead!r} at {log}", file=sys.stderr)
        sys.exit(1)

    # Read last N lines
    entries = []
    with log.open("r", encoding="utf-8") as fh:
        lines = fh.readlines()
        for line in lines[-DIGEST_TAIL_LINES:]:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                # Skip malformed lines
                pass

    # Count total lines for frontmatter
    total_lines = len(lines)

    # Group by kind
    decisions = []
    findings = []
    retractions = []
    doctrine_candidates = []

    for e in entries:
        kind = e.get("kind", "")
        if kind == "decision":
            decisions.append(e)
        elif kind == "finding":
            findings.append(e)
        elif kind == "retraction":
            retractions.append(e)
        elif kind == "doctrine-candidate":
            doctrine_candidates.append(e)

    # Apply retractions (simple: if retraction mentions an item ID, omit it)
    # For Phase 1, we just flag retractions; Phase 2 can do smart matching
    retracted_ids = set()
    for r in retractions:
        # Look for id references in item text (naive: search for hex strings)
        item_text = r.get("item", "")
        # Extract 32-char hex strings (UUIDs)
        import re
        for match in re.finditer(r'\b[0-9a-f]{32}\b', item_text.lower()):
            retracted_ids.add(match.group(0))

    # Filter out retracted
    decisions = [d for d in decisions if d.get("id") not in retracted_ids]
    findings = [f for f in findings if f.get("id") not in retracted_ids]

    # Build markdown
    lines_out = []

    # Frontmatter
    lines_out.append("---")
    lines_out.append(f"lead: {lead}")
    lines_out.append(f"rebuilt_ts: {_now_iso_utc()}")
    lines_out.append(f"ledger_lines_at_rebuild: {total_lines}")
    lines_out.append(f"source_log: .claude/memory/canon/{lead}/log.jsonl")
    lines_out.append("mechanism: extractive-mechanical")
    lines_out.append("---")
    lines_out.append("")
    lines_out.append(f"# Canon Memory Digest: {lead}")
    lines_out.append("")
    lines_out.append(f"**Last {len(entries)} entries** (from {total_lines} total)")
    lines_out.append("")

    # Decisions section
    if decisions:
        lines_out.append("## Decisions")
        lines_out.append("")
        for d in decisions:
            ts = d.get("ts", "?")
            item = d.get("item", "")
            receipt = d.get("receipt", "")
            lines_out.append(f"- `{ts}` **decision** — {item}")
            if receipt:
                lines_out.append(f"  - Receipt: `{receipt}`")
        lines_out.append("")

    # Findings section
    if findings:
        lines_out.append("## Findings")
        lines_out.append("")
        for f in findings:
            ts = f.get("ts", "?")
            item = f.get("item", "")
            receipt = f.get("receipt", "")
            lines_out.append(f"- `{ts}` **finding** — {item}")
            if receipt:
                lines_out.append(f"  - Receipt: `{receipt}`")
        lines_out.append("")

    # Doctrine candidates section
    if doctrine_candidates:
        lines_out.append("## Doctrine Candidates")
        lines_out.append("")
        for dc in doctrine_candidates:
            ts = dc.get("ts", "?")
            item = dc.get("item", "")
            receipt = dc.get("receipt", "")
            lines_out.append(f"- `{ts}` **doctrine-candidate** — {item}")
            if receipt:
                lines_out.append(f"  - Receipt: `{receipt}`")
        lines_out.append("")

    # Retractions section (show them for transparency)
    if retractions:
        lines_out.append("## Retractions (applied above)")
        lines_out.append("")
        for r in retractions:
            ts = r.get("ts", "?")
            item = r.get("item", "")
            lines_out.append(f"- `{ts}` **retraction** — {item}")
        lines_out.append("")

    # Write digest
    digest.write_text("\n".join(lines_out), encoding="utf-8")
    print(f"Rebuilt DIGEST.md for {lead!r}: {len(entries)} entries, {total_lines} total lines")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="aether_digest_rebuild.py",
        description="Rebuild DIGEST.md from canon log.jsonl",
    )
    parser.add_argument("--lead", required=True, help="Lead identity (e.g. 'security-auditor')")

    args = parser.parse_args(argv)

    # Gate check
    if not ENABLE_FLAG:
        print("digest rebuild disabled (set ENABLE_DIGEST_REBUILD=1)")
        return 0

    try:
        rebuild_digest(args.lead)
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
