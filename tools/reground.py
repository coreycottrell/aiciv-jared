#!/usr/bin/env python3
"""
reground.py — TRIO Grounding System CLI & library.

Usage:
    python3 tools/reground.py --status
    python3 tools/reground.py --tier constitutional
    python3 tools/reground.py --tier role
    python3 tools/reground.py --tier project-state
    python3 tools/reground.py --tier recent-corrections
    python3 tools/reground.py --trigger post-compaction
    python3 tools/reground.py --trigger pre-deploy

Also importable:
    from tools.reground import reground, log_event, status
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
GROUNDING_DIR = REPO_ROOT / ".claude" / "grounding"
LOG_PATH = GROUNDING_DIR / "log.jsonl"

TIERS = {
    "constitutional": [
        REPO_ROOT / "CLAUDE.md",
        Path.home() / ".claude" / "projects" / "-home-jared-projects-AI-CIV-aether" / "memory" / "MEMORY.md",
        GROUNDING_DIR / "TRIO-SHARED-RULES.md",
    ],
    "role": [
        REPO_ROOT / "CLAUDE.md",
        GROUNDING_DIR / "TRIO-SHARED-RULES.md",
    ],
    "project-state": [
        REPO_ROOT / "INTEGRATION-ROADMAP.md",
        REPO_ROOT / ".claude" / "scratch-pad.md",
        Path("/home/aiciv/shared/handshake-queue.md"),
    ],
    "recent-corrections": [
        GROUNDING_DIR / "recent-corrections.md",
        LOG_PATH,
    ],
}

TRIGGER_TO_TIERS = {
    "wake-up": ["constitutional", "role", "recent-corrections"],
    "post-compaction": ["constitutional", "role", "project-state", "recent-corrections"],
    "pre-deploy": ["constitutional", "recent-corrections"],
    "pre-email": ["constitutional", "recent-corrections"],
    "pre-paypal": ["constitutional"],
    "pre-cross-ai": ["role", "recent-corrections"],
    "6hr-gap": ["constitutional", "recent-corrections"],
    "3-ops-no-gate": ["constitutional", "recent-corrections"],
    "correction-received": ["recent-corrections"],
    "drift-flagged": ["constitutional", "recent-corrections"],
}

# -----------------------------------------------------------------------------
# Core
# -----------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(event: str, tier: str | None = None, trigger: str | None = None,
              actor: str = "aether", notes: str = "") -> None:
    """Append a grounding event to log.jsonl."""
    GROUNDING_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": _now(),
        "actor": actor,
        "event": event,
        "tier": tier,
        "trigger": trigger,
        "notes": notes,
    }
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def reground(tier: str, actor: str = "aether", trigger: str | None = None) -> dict:
    """Re-read all files for a tier and log the event.

    Returns dict with keys: tier, files_read, files_missing.
    """
    if tier not in TIERS:
        raise ValueError(f"unknown tier: {tier}. Known: {list(TIERS)}")

    read, missing = [], []
    for p in TIERS[tier]:
        if p.exists():
            try:
                p.read_text(encoding="utf-8", errors="replace")
                read.append(str(p))
            except Exception as e:
                missing.append(f"{p} (error: {e})")
        else:
            missing.append(str(p))

    log_event(
        event="reground",
        tier=tier,
        trigger=trigger,
        actor=actor,
        notes=f"read={len(read)} missing={len(missing)}",
    )
    return {"tier": tier, "files_read": read, "files_missing": missing}


def status() -> dict:
    """Return a summary of grounding state."""
    GROUNDING_DIR.mkdir(parents=True, exist_ok=True)

    last_events_by_tier: dict[str, str] = {}
    total_events = 0
    last_event_ts = None

    if LOG_PATH.exists():
        with LOG_PATH.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "_header" in entry:
                    continue
                total_events += 1
                ts = entry.get("ts")
                tier = entry.get("tier")
                if ts:
                    last_event_ts = ts
                    if tier:
                        last_events_by_tier[tier] = ts

    tier_presence = {
        t: all(p.exists() for p in paths)
        for t, paths in TIERS.items()
    }

    return {
        "grounding_dir": str(GROUNDING_DIR),
        "log_path": str(LOG_PATH),
        "log_exists": LOG_PATH.exists(),
        "total_events": total_events,
        "last_event_ts": last_event_ts,
        "last_events_by_tier": last_events_by_tier,
        "tier_file_presence": tier_presence,
        "known_tiers": list(TIERS.keys()),
        "known_triggers": list(TRIGGER_TO_TIERS.keys()),
    }

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="TRIO grounding re-grounder.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tier", choices=list(TIERS.keys()),
                   help="Reground a specific tier.")
    g.add_argument("--trigger", choices=list(TRIGGER_TO_TIERS.keys()),
                   help="Reground all tiers associated with a trigger event.")
    g.add_argument("--status", action="store_true",
                   help="Show grounding status summary.")
    ap.add_argument("--actor", default=os.environ.get("CIV_NAME", "aether").lower(),
                    help="Actor performing the reground (default: aether).")
    ap.add_argument("--json", action="store_true",
                    help="Emit JSON output.")
    args = ap.parse_args(argv)

    if args.status:
        s = status()
        if args.json:
            print(json.dumps(s, indent=2))
        else:
            print(f"TRIO Grounding Status")
            print(f"---------------------")
            print(f"grounding_dir:  {s['grounding_dir']}")
            print(f"log_exists:     {s['log_exists']}")
            print(f"total_events:   {s['total_events']}")
            print(f"last_event_ts:  {s['last_event_ts']}")
            print(f"tiers present:")
            for t, ok in s["tier_file_presence"].items():
                print(f"  - {t}: {'OK' if ok else 'MISSING FILES'}")
            print(f"last reground per tier:")
            for t, ts in s["last_events_by_tier"].items():
                print(f"  - {t}: {ts}")
        return 0

    if args.tier:
        result = reground(args.tier, actor=args.actor, trigger=None)
        print(json.dumps(result, indent=2) if args.json else
              f"Reground tier={args.tier} read={len(result['files_read'])} missing={len(result['files_missing'])}")
        if result["files_missing"]:
            for m in result["files_missing"]:
                print(f"  missing: {m}", file=sys.stderr)
        return 0

    if args.trigger:
        tiers = TRIGGER_TO_TIERS[args.trigger]
        results = [reground(t, actor=args.actor, trigger=args.trigger) for t in tiers]
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                print(f"Reground trigger={args.trigger} tier={r['tier']} "
                      f"read={len(r['files_read'])} missing={len(r['files_missing'])}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
