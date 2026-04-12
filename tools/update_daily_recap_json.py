#!/usr/bin/env python3
"""
update_daily_recap_json.py

Updates /blog/daily-recap.json with today's recap items.

Called each morning after the overnight pipeline completes.

Usage:
    python3 tools/update_daily_recap_json.py \
        --date "March 13, 2026" \
        --items "Built X" "Fixed Y" "Shipped Z" "Deployed W"

Or import and call programmatically:
    from tools.update_daily_recap_json import write_daily_recap
    write_daily_recap("March 13, 2026", ["Built X", "Fixed Y", ...])
"""

import json
import argparse
from pathlib import Path
from datetime import date

RECAP_JSON_PATH = Path("/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/daily-recap.json")


def write_daily_recap(date_str: str, items: list[str]) -> None:
    """Write new daily recap to the JSON file."""
    payload = {
        "date": date_str,
        "items": items,
        "updated": date.today().isoformat(),
    }
    RECAP_JSON_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] daily-recap.json updated — {date_str} — {len(items)} items")


def main():
    parser = argparse.ArgumentParser(description="Update the live daily recap JSON")
    parser.add_argument("--date", required=True, help='e.g. "March 13, 2026"')
    parser.add_argument("--items", nargs="+", required=True, help="Bullet items (4 recommended)")
    args = parser.parse_args()

    write_daily_recap(args.date, args.items)
    print(f"Path: {RECAP_JSON_PATH}")
    print("\nNext: redeploy CF Pages so the CDN picks up the new JSON.")


if __name__ == "__main__":
    main()
