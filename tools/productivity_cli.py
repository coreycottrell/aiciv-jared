#!/usr/bin/env python3
"""
CLI for AI Productivity Tracker

Usage:
    python -m tools.productivity_cli log --task "Fix bug" --agent "refactoring-specialist" --ai-minutes 10 --human-hours 4
    python -m tools.productivity_cli report
    python -m tools.productivity_cli today
    python -m tools.productivity_cli sync
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.productivity_tracker import ProductivityTracker, ProductivityTask


def main():
    parser = argparse.ArgumentParser(
        description="AI Productivity Tracker CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Log a task:
    %(prog)s log --task "Fix auth bug" --agent "refactoring-specialist" --ai-minutes 10 --human-hours 4

  Show today's stats:
    %(prog)s today

  Generate full report:
    %(prog)s report

  Sync to Google Drive:
    %(prog)s sync
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Log command
    log_parser = subparsers.add_parser("log", help="Log a completed task")
    log_parser.add_argument("--task", required=True, help="Task name")
    log_parser.add_argument("--description", default="", help="Task description")
    log_parser.add_argument("--agent", required=True, help="Agent name")
    log_parser.add_argument("--ai-minutes", type=int, required=True, help="AI time in minutes")
    log_parser.add_argument("--human-hours", type=float, required=True, help="Estimated human hours")
    log_parser.add_argument("--category", default="Development",
                           help="Task category (Development, Bug Fix, Integration, Research)")
    log_parser.add_argument("--complexity", default="Medium",
                           help="Complexity level (Low, Medium, High, Very High)")

    # Report command
    subparsers.add_parser("report", help="Generate daily report")

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync to Google Drive")
    sync_parser.add_argument("--folder", default="AI Productivity Reports", help="Drive folder")

    # Today command
    subparsers.add_parser("today", help="Show today's stats")

    # CSV command
    subparsers.add_parser("csv", help="Generate CSV output")

    args = parser.parse_args()

    # Default to showing help if no command
    if not args.command:
        parser.print_help()
        return 0

    # Initialize tracker
    tracker = ProductivityTracker()

    if args.command == "log":
        task = ProductivityTask(
            task_name=args.task,
            description=args.description,
            agent_name=args.agent,
            ai_minutes=args.ai_minutes,
            human_hours_estimate=args.human_hours,
            category=args.category,
            complexity=args.complexity
        )
        tracker.log_task(task)

        roi = task.roi_multiplier
        roi_display = f"{roi:.1f}x" if roi != float('inf') else "infinite"

        print(f"Logged: {args.task}")
        print(f"  AI: {args.ai_minutes} min vs Human: {args.human_hours} hr = {roi_display} ROI")
        print(f"  Cost savings: ${task.cost_savings:,.0f}")

    elif args.command == "report":
        print(tracker.generate_report())

    elif args.command == "sync":
        try:
            folder = tracker.sync_to_gdrive(args.folder)
            print(f"Synced to Google Drive: {folder}")
        except Exception as e:
            print(f"Sync failed: {e}")
            return 1

    elif args.command == "today":
        stats = tracker.get_daily_stats()
        if stats['tasks'] == 0:
            print("No tasks logged today.")
        else:
            print(f"Today: {stats['tasks']} tasks")
            print(f"  AI time: {stats['ai_minutes']} min ({stats['ai_hours']} hr)")
            print(f"  Human equivalent: {stats['human_hours']} hr")
            print(f"  Time saved: {stats['saved_hours']} hr")
            print(f"  ROI: {stats['roi_multiplier']}x faster")
            print(f"  Cost savings: ${stats['cost_savings']:,.0f}")

    elif args.command == "csv":
        print(tracker._generate_csv())

    return 0


if __name__ == "__main__":
    sys.exit(main())
