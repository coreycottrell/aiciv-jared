#!/usr/bin/env python3
"""drift-watch.py — detect grounding drift patterns from log.jsonl

Patterns flagged (from Chy's self-audit):
  1. No reground event in >100K tokens
  2. Post-compact trigger not followed by reground within 5 min
  3. Hour 6+ of session without any reground
  4. 3+ operations without a decision-gate reground

Usage: python3 drift-watch.py [--log PATH] [--ai NAME]
Output: JSON report to stdout
"""
import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_LOG = Path(__file__).parent / "log.jsonl"


def load_events(log_path, ai_filter=None):
    events = []
    if not log_path.exists():
        return events
    for line in log_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            evt = json.loads(line)
            if ai_filter and evt.get("ai_name") != ai_filter:
                continue
            events.append(evt)
        except json.JSONDecodeError:
            continue
    return events


def detect_patterns(events):
    flags = []
    if not events:
        return [{"pattern": "no_events", "severity": "info", "msg": "Log is empty."}]

    events.sort(key=lambda e: e.get("timestamp", ""))

    # Pattern 1: post-compact without reground within 5 min
    for i, e in enumerate(events):
        if e.get("trigger") == "post-compact":
            next_reground = False
            e_time = datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))
            for later in events[i + 1:]:
                l_time = datetime.fromisoformat(later["timestamp"].replace("Z", "+00:00"))
                delta = (l_time - e_time).total_seconds()
                if delta > 300:
                    break
                if later.get("trigger") in ("session-start", "token-threshold", "decision-gate"):
                    next_reground = True
                    break
            if not next_reground:
                flags.append({
                    "pattern": "post_compact_no_reground_5min",
                    "severity": "high",
                    "ai": e.get("ai_name"),
                    "at": e["timestamp"],
                })

    # Pattern 2: gap >100K tokens without reground (proxy: >6hr session without event)
    last_ts = None
    for e in events:
        t = datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))
        if last_ts is None:
            last_ts = t
            continue
        gap = (t - last_ts).total_seconds() / 3600
        if gap > 6:
            flags.append({
                "pattern": "hour6_plus_gap",
                "severity": "medium",
                "ai": e.get("ai_name"),
                "gap_hours": round(gap, 1),
                "from": last_ts.isoformat(),
                "to": e["timestamp"],
            })
        last_ts = t

    # Pattern 3: 3+ non-grounding operations streak (needs op-log cross-reference — placeholder)
    # Placeholder — emit hint for operator
    flags.append({
        "pattern": "pattern_3_requires_op_log",
        "severity": "info",
        "msg": "Cross-reference with ops log to detect 3-op streaks without decision-gate.",
    })

    return flags


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--log", default=str(DEFAULT_LOG))
    p.add_argument("--ai", default=None)
    args = p.parse_args()

    events = load_events(Path(args.log), ai_filter=args.ai)
    flags = detect_patterns(events)
    out = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "events_scanned": len(events),
        "ai_filter": args.ai,
        "flags": flags,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
