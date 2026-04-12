#!/usr/bin/env python3
"""
Productivity Tracker for AI-CIV

Tracks AI productivity vs human time equivalent.
Shows tangible ROI - what AI accomplishes vs human time.

Usage:
    from tools.productivity_tracker import ProductivityTracker, ProductivityTask

    tracker = ProductivityTracker()
    tracker.log_task(ProductivityTask(
        task_name="Fix auth bug",
        description="Fixed OAuth token refresh",
        agent_name="refactoring-specialist",
        ai_minutes=10,
        human_hours_estimate=4.0
    ))

    print(tracker.generate_report())
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import json
import os


@dataclass
class ProductivityTask:
    """A completed productivity task with time metrics."""

    task_name: str
    description: str
    agent_name: str
    ai_minutes: int
    human_hours_estimate: float
    category: str = "Development"
    complexity: str = "Medium"  # Low, Medium, High, Very High
    deliverables: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def ai_hours(self) -> float:
        """AI time in hours."""
        return self.ai_minutes / 60

    @property
    def time_saved_hours(self) -> float:
        """Hours saved vs human doing the work."""
        return self.human_hours_estimate - self.ai_hours

    @property
    def roi_multiplier(self) -> float:
        """How many times faster AI is vs human."""
        if self.ai_hours == 0:
            return float('inf')
        return self.human_hours_estimate / self.ai_hours

    @property
    def cost_savings(self) -> float:
        """Cost savings at $150/hr rate."""
        return self.time_saved_hours * 150


class ProductivityTracker:
    """
    Tracks daily productivity tasks and generates reports.

    Data is stored in JSON files per day for easy querying.
    """

    def __init__(self, data_dir: str = ".productivity"):
        """
        Initialize tracker with data directory.

        Args:
            data_dir: Directory to store daily JSON files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.tasks: List[ProductivityTask] = []
        self._load_today()

    def _get_today_file(self) -> str:
        """Get path to today's data file."""
        return os.path.join(self.data_dir, f"{datetime.now().strftime('%Y-%m-%d')}.json")

    def _load_today(self):
        """Load today's tasks from file if exists."""
        filepath = self._get_today_file()
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.tasks = []
                for t in data:
                    # Handle timestamp conversion
                    if 'timestamp' in t and isinstance(t['timestamp'], str):
                        t['timestamp'] = datetime.fromisoformat(t['timestamp'])
                    self.tasks.append(ProductivityTask(**t))

    def _save_today(self):
        """Save today's tasks to file."""
        filepath = self._get_today_file()

        # Convert tasks to serializable dicts
        data = []
        for task in self.tasks:
            task_dict = {
                'task_name': task.task_name,
                'description': task.description,
                'agent_name': task.agent_name,
                'ai_minutes': task.ai_minutes,
                'human_hours_estimate': task.human_hours_estimate,
                'category': task.category,
                'complexity': task.complexity,
                'deliverables': task.deliverables,
                'timestamp': task.timestamp.isoformat()
            }
            data.append(task_dict)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def log_task(self, task: ProductivityTask):
        """Log a completed task."""
        self.tasks.append(task)
        self._save_today()

    def get_daily_stats(self) -> dict:
        """
        Calculate daily statistics.

        Returns:
            Dict with: tasks, ai_minutes, ai_hours, human_hours,
                      saved_hours, roi_multiplier, cost_savings
        """
        if not self.tasks:
            return {
                "tasks": 0,
                "ai_minutes": 0,
                "ai_hours": 0,
                "human_hours": 0,
                "saved_hours": 0,
                "roi_multiplier": 0,
                "cost_savings": 0
            }

        total_ai_minutes = sum(t.ai_minutes for t in self.tasks)
        total_human_hours = sum(t.human_hours_estimate for t in self.tasks)
        total_saved = sum(t.time_saved_hours for t in self.tasks)
        avg_roi = total_human_hours / (total_ai_minutes / 60) if total_ai_minutes > 0 else 0
        total_savings = sum(t.cost_savings for t in self.tasks)

        return {
            "tasks": len(self.tasks),
            "ai_minutes": total_ai_minutes,
            "ai_hours": round(total_ai_minutes / 60, 1),
            "human_hours": total_human_hours,
            "saved_hours": round(total_saved, 1),
            "roi_multiplier": round(avg_roi, 1),
            "cost_savings": round(total_savings, 2)
        }

    def generate_report(self) -> str:
        """
        Generate markdown report.

        Returns:
            Markdown formatted productivity report
        """
        stats = self.get_daily_stats()

        report = f"""# AI PRODUCTIVITY REPORT - {datetime.now().strftime('%Y-%m-%d')}

## Summary
- **Tasks Completed:** {stats['tasks']}
- **Total AI Time:** {stats['ai_minutes']} minutes ({stats['ai_hours']} hours)
- **Estimated Human Time:** {stats['human_hours']} hours
- **Time Saved:** {stats['saved_hours']} hours
- **ROI Multiplier:** {stats['roi_multiplier']}x faster
- **Cost Savings:** ${stats['cost_savings']:,.2f} (at $150/hr)

## Task Breakdown

| Task | Agent | AI Time | Human Est | ROI |
|------|-------|---------|-----------|-----|
"""
        for t in self.tasks:
            roi_display = f"{t.roi_multiplier:.0f}x" if t.roi_multiplier != float('inf') else "inf"
            report += f"| {t.task_name} | {t.agent_name} | {t.ai_minutes} min | {t.human_hours_estimate} hrs | {roi_display} |\n"

        return report

    def _generate_csv(self) -> str:
        """
        Generate CSV for spreadsheet.

        Returns:
            CSV formatted string with headers and data rows
        """
        headers = "Date,Task,Description,Agent,Category,Complexity,AI Minutes,Human Hours,Time Saved,ROI,Cost Savings\n"
        rows = ""
        for t in self.tasks:
            roi_display = f"{t.roi_multiplier:.1f}x" if t.roi_multiplier != float('inf') else "inf"
            rows += f"{t.timestamp.strftime('%Y-%m-%d')},{t.task_name},{t.description},{t.agent_name},{t.category},{t.complexity},{t.ai_minutes},{t.human_hours_estimate},{t.time_saved_hours:.1f},{roi_display},${t.cost_savings:.2f}\n"
        return headers + rows

    def sync_to_gdrive(self, folder_name: str = "AI Productivity Reports",
                        root_folder: str = "Aether Inbox"):
        """
        Push report to Google Drive.

        Args:
            folder_name: Subfolder within root to upload to
            root_folder: Root shared folder (default: Aether Inbox)

        Returns:
            Full path where files were uploaded
        """
        from tools.gdrive_manager import GDriveManager

        gdrive = GDriveManager()
        report = self.generate_report()
        filename = f"Daily-Report-{datetime.now().strftime('%Y-%m-%d')}.md"

        # Also create CSV for spreadsheet
        csv_content = self._generate_csv()
        csv_filename = f"Daily-Log-{datetime.now().strftime('%Y-%m-%d')}.csv"

        # Upload both - folder_name is subfolder path within root_folder
        gdrive.upload_content_to_path(report, filename, folder_name, root_folder_name=root_folder)
        gdrive.upload_content_to_path(csv_content, csv_filename, folder_name, root_folder_name=root_folder)

        return f"{root_folder}/{folder_name}"


if __name__ == "__main__":
    # Demo usage
    tracker = ProductivityTracker()

    # Example task
    tracker.log_task(ProductivityTask(
        task_name="Demo task",
        description="Demonstrating the tracker",
        agent_name="refactoring-specialist",
        ai_minutes=5,
        human_hours_estimate=1.0
    ))

    print(tracker.generate_report())
