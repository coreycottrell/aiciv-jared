#!/usr/bin/env python3
"""
Boop Executor Daemon v2.0
Aether AI Collective - Scheduled Task Trigger System

Monitors .claude/scheduled-tasks-state.json and fires boops as independent
background Claude Code CLI agents when tasks come due. Runs as a background daemon.

Usage:
    nohup python3 tools/boop_executor.py >> logs/boop_executor.log 2>&1 &

Stop:
    kill $(cat .boop_executor.pid)
"""

import json
import logging
import os
import signal
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR = Path("/home/jared/projects/AI-CIV/aether")
TASKS_FILE = BASE_DIR / ".claude" / "scheduled-tasks-state.json"
PID_FILE = BASE_DIR / ".boop_executor.pid"
LOG_FILE = BASE_DIR / "logs" / "boop_executor.log"
TELEGRAM_CONFIG = BASE_DIR / "config" / "telegram_config.json"

# ─── Configuration ────────────────────────────────────────────────────────────

CHECK_INTERVAL_SECONDS = 300          # 5 minutes between checks
MAX_BOOPS_PER_WINDOW = 2             # max boops to fire within concurrency window
CONCURRENCY_WINDOW_SECONDS = 180     # 3-minute stagger window
ACTIVE_HOURS_START = 8               # 8 AM ET - earliest daily/weekly/monthly fire
ACTIVE_HOURS_END = 23                # 11 PM ET - latest daily/weekly/monthly fire
MAX_CONCURRENT_BOOP_AGENTS = 3       # max simultaneously running claude boop processes

# Frequency label → seconds
FREQUENCY_MAP = {
    "25min":         25 * 60,
    "30min":         30 * 60,
    "60min":         60 * 60,
    "60minutes":     60 * 60,
    "90min":         90 * 60,
    "2hours":         2 * 3600,
    "4hours":         4 * 3600,
    "8hours":         8 * 3600,
    "12hours":       12 * 3600,
    "twice-daily":   12 * 3600,
    "daily":         24 * 3600,
    "nightly":       24 * 3600,
    "weekly-monday":    7  * 86400,
    "weekly-tuesday":   7  * 86400,
    "weekly-wednesday": 7  * 86400,
    "weekly-thursday":  7  * 86400,
    "weekly-friday":    7  * 86400,
    "weekly-saturday":  7  * 86400,
    "weekly-sunday":    7  * 86400,
    "weekly":           7  * 86400,
    "monthly":       30 * 86400,
}

# Frequencies that should only fire during active hours
TIME_GATED_FREQUENCIES = {"daily", "nightly", "twice-daily", "12hours", "weekly-monday", "weekly-tuesday", "weekly-wednesday", "weekly-thursday", "weekly-friday", "weekly-saturday", "weekly-sunday", "weekly", "monthly"}

# Day-of-week constraints (Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4)
DAY_CONSTRAINED = {
    "weekly-monday": 0,
    "weekly-tuesday": 1,
    "weekly-wednesday": 2,
    "weekly-thursday": 3,
    "weekly-friday": 4,
    "weekly-saturday": 5,
    "weekly-sunday": 6,
}

# ─── Logging setup ────────────────────────────────────────────────────────────

def setup_logging() -> logging.Logger:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("boop_executor")
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler - always write directly to log file
    fh = logging.FileHandler(str(LOG_FILE))
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Stdout handler only when stdout is a real terminal (not redirected via nohup)
    # This prevents duplicate lines when nohup points stdout at the same log file
    if sys.stdout.isatty():
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        logger.addHandler(sh)

    return logger


# ─── PID management ───────────────────────────────────────────────────────────

def write_pid() -> None:
    PID_FILE.write_text(str(os.getpid()))


def remove_pid() -> None:
    try:
        PID_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def check_existing_instance() -> bool:
    """Return True if another instance is already running."""
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text().strip())
        # Check if that PID is alive
        os.kill(pid, 0)
        return True
    except (ValueError, ProcessLookupError, PermissionError):
        # Stale PID file
        PID_FILE.unlink(missing_ok=True)
        return False


# ─── Graceful shutdown ────────────────────────────────────────────────────────

_shutdown_requested = False


def _handle_signal(signum, frame):
    global _shutdown_requested
    _shutdown_requested = True


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


# ─── Task state I/O ───────────────────────────────────────────────────────────

def load_tasks(logger: logging.Logger) -> dict:
    """Load tasks from JSON. Returns empty dict on any error."""
    try:
        raw = TASKS_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data.get("tasks", {})
    except FileNotFoundError:
        logger.error("Tasks file not found: %s", TASKS_FILE)
        return {}
    except json.JSONDecodeError as e:
        logger.error("JSON parse error in tasks file: %s", e)
        return {}


def save_tasks(tasks: dict, logger: logging.Logger) -> bool:
    """Write updated tasks back to the JSON file. Returns True on success."""
    try:
        # Read full structure to preserve metadata fields
        raw = TASKS_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        data["tasks"] = tasks
        TASKS_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except Exception as e:
        logger.error("Failed to save tasks: %s", e)
        return False


# ─── Scheduling logic ─────────────────────────────────────────────────────────

def parse_frequency_seconds(frequency: str) -> int:
    """Return interval in seconds, or 0 if unknown."""
    return FREQUENCY_MAP.get(frequency, 0)


def is_within_active_hours(now: datetime) -> bool:
    """Check if current local hour falls within ACTIVE_HOURS_START..ACTIVE_HOURS_END."""
    return ACTIVE_HOURS_START <= now.hour < ACTIVE_HOURS_END


def is_correct_day_of_week(frequency: str, now: datetime) -> bool:
    """For day-constrained frequencies, verify today is the right day."""
    if frequency not in DAY_CONSTRAINED:
        return True
    return now.weekday() == DAY_CONSTRAINED[frequency]


def is_due(task_id: str, task: dict, now: datetime, logger: logging.Logger) -> bool:
    """Determine if a task should fire now."""
    # Only active tasks
    if task.get("status") != "active":
        return False

    frequency = task.get("frequency", "")
    interval = parse_frequency_seconds(frequency)

    if interval == 0:
        logger.warning("Unknown frequency '%s' for task '%s' - skipping", frequency, task_id)
        return False

    # Time-gated frequencies only fire during active hours
    if frequency in TIME_GATED_FREQUENCIES:
        if not is_within_active_hours(now):
            return False
        if not is_correct_day_of_week(frequency, now):
            return False

    last_run_str = task.get("last_run")

    # Never run before → fire immediately (if time-gate passes)
    if not last_run_str:
        return True

    # Parse last_run timestamp
    try:
        # Handle both Z suffix and +00:00 offset
        last_run_str_clean = last_run_str.replace("Z", "+00:00")
        last_run = datetime.fromisoformat(last_run_str_clean)
        # Make now timezone-aware if last_run is
        if last_run.tzinfo is not None:
            now_cmp = now.astimezone(timezone.utc)
        else:
            now_cmp = now.replace(tzinfo=None)
            last_run = last_run.replace(tzinfo=None)
        elapsed = (now_cmp - last_run).total_seconds()
        return elapsed >= interval
    except (ValueError, TypeError) as e:
        logger.warning("Could not parse last_run '%s' for task '%s': %s - will fire", last_run_str, task_id, e)
        return True


# ─── Telegram notifications ───────────────────────────────────────────────────

def get_telegram_token(logger: logging.Logger) -> str:
    """Load bot token from telegram config. Returns empty string on failure."""
    try:
        with open(TELEGRAM_CONFIG) as f:
            config = json.load(f)
        return config.get("bot_token", "")
    except Exception as e:
        logger.warning("Could not load telegram config: %s", e)
        return ""


def send_telegram(message: str, logger: logging.Logger) -> None:
    """Send brief boop notification to Jared via Telegram."""
    try:
        token = get_telegram_token(logger)
        if not token:
            return
        chat_id = "548906264"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": message
        }).encode()
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        logger.warning("Telegram notify failed: %s", e)


# ─── Concurrency check ────────────────────────────────────────────────────────

def count_running_boop_agents(logger: logging.Logger) -> int:
    """Count how many claude BOOP agent processes are currently running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "claude.*BOOP"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout.strip():
            count = len(result.stdout.strip().split("\n"))
            return count
        return 0
    except Exception as e:
        logger.warning("Could not check running boop agents: %s", e)
        return 0


# ─── Boop firing ──────────────────────────────────────────────────────────────

def build_boop_prompt(task_id: str, task: dict, bot_token: str) -> str:
    """Build the full prompt for the background Claude Code agent."""
    description = task.get("description", task_id)
    agent = task.get("agent", "unknown-agent")
    category = task.get("category", "")
    chat_id = "548906264"

    # Curl command the agent will use to report back
    send_tg_cmd = (
        f'curl -s "https://api.telegram.org/bot{bot_token}/sendMessage" '
        f'-d chat_id="{chat_id}" '
        f'--data-urlencode "text=BOOP [{task_id}] complete: $SUMMARY"'
    )

    prompt = (
        f"BOOP [{task_id}]: {description}\n\n"
        f"You are the {agent} agent. Your category is: {category}.\n\n"
        f"Working directory: {BASE_DIR}\n\n"
        f"Execute this scheduled task now. Do the actual work described above.\n\n"
        f"When finished, send a brief summary to Telegram using this curl command "
        f"(replace $SUMMARY with your 1-2 sentence summary of what was done):\n"
        f"{send_tg_cmd}"
    )
    return prompt


def fire_boop(task_id: str, task: dict, logger: logging.Logger) -> bool:
    """Launch an independent background Claude Code agent for this boop. Returns True on success."""
    description = task.get("description", task_id)
    agent = task.get("agent", "unknown-agent")
    category = task.get("category", "")

    # Check concurrent boop agent limit
    running = count_running_boop_agents(logger)
    if running >= MAX_CONCURRENT_BOOP_AGENTS:
        logger.info(
            "Skipping [%s]: %d boop agents already running (max %d)",
            task_id, running, MAX_CONCURRENT_BOOP_AGENTS
        )
        return False

    # Load telegram token for embedding in agent prompt
    bot_token = get_telegram_token(logger)

    # Build the prompt
    prompt = build_boop_prompt(task_id, task, bot_token)

    # Log output path for this boop
    log_path = f"/tmp/boop_{task_id}.log"

    try:
        # Launch as completely independent background process
        # Use Popen with close_fds=True and start_new_session=True so it survives
        # even if the boop_executor restarts.
        # Unset CLAUDECODE env var so the child process is not treated as a nested session.
        env = os.environ.copy()
        env.pop("CLAUDECODE", None)

        with open(log_path, "w") as log_fh:
            proc = subprocess.Popen(
                [
                    "claude",
                    "--print",
                    "-p", prompt,
                    "--allowedTools", "Bash,Read,Write,Grep,Glob,WebFetch,WebSearch",
                ],
                stdout=log_fh,
                stderr=log_fh,
                cwd=str(BASE_DIR),
                start_new_session=True,
                close_fds=True,
                env=env,
            )

        logger.info(
            "Launched boop agent: [%s] PID=%d agent=%s log=%s",
            task_id, proc.pid, agent, log_path
        )

        # Send Telegram notification
        tg_msg = (
            f"[BOOP] {task_id} launched\n"
            f"{description} (category: {category})\n"
            f"Agent: {agent} | PID: {proc.pid}"
        )
        send_telegram(tg_msg, logger)

        return True

    except FileNotFoundError:
        logger.error("claude CLI not found on PATH - cannot launch boop agent [%s]", task_id)
        return False
    except Exception as e:
        logger.error("Failed to launch boop agent [%s]: %s", task_id, e)
        return False


# ─── Main loop ────────────────────────────────────────────────────────────────

def run(logger: logging.Logger) -> None:
    logger.info("Boop Executor v2.0 starting. PID=%d Check interval=%ds", os.getpid(), CHECK_INTERVAL_SECONDS)
    logger.info("Tasks file: %s", TASKS_FILE)
    logger.info("Active hours: %02d:00 - %02d:00 local time", ACTIVE_HOURS_START, ACTIVE_HOURS_END)
    logger.info("Max concurrent boop agents: %d", MAX_CONCURRENT_BOOP_AGENTS)

    # Track recent fire times for concurrency throttling
    recent_fires: list[float] = []

    while not _shutdown_requested:
        now = datetime.now(timezone.utc)
        now_local = datetime.now()  # For active-hour checks (local time)

        tasks = load_tasks(logger)
        if not tasks:
            logger.warning("No tasks loaded - sleeping until next check")
            _sleep_interruptible(CHECK_INTERVAL_SECONDS)
            continue

        # Collect due tasks
        due = []
        for task_id, task in tasks.items():
            try:
                if is_due(task_id, task, now_local, logger):
                    due.append((task_id, task))
            except Exception as e:
                logger.error("Error checking task [%s]: %s", task_id, e)

        if due:
            logger.info("%d task(s) due: %s", len(due), [t[0] for t in due])
        else:
            logger.debug("No tasks due at %s", now_local.strftime("%H:%M:%S"))

        fired_count = 0
        for task_id, task in due:
            if _shutdown_requested:
                break

            # Concurrency throttle: max MAX_BOOPS_PER_WINDOW in last CONCURRENCY_WINDOW_SECONDS
            now_ts = time.time()
            recent_fires = [t for t in recent_fires if now_ts - t < CONCURRENCY_WINDOW_SECONDS]

            if len(recent_fires) >= MAX_BOOPS_PER_WINDOW:
                wait_for = CONCURRENCY_WINDOW_SECONDS - (now_ts - recent_fires[0])
                logger.info(
                    "Concurrency limit hit (%d/%d in last %ds). "
                    "Deferring remaining due tasks for %.0fs",
                    len(recent_fires), MAX_BOOPS_PER_WINDOW,
                    CONCURRENCY_WINDOW_SECONDS, max(wait_for, 0)
                )
                break  # Deferred tasks will be picked up on the next check cycle

            # Fire the boop
            success = fire_boop(task_id, task, logger)

            if success:
                # Update last_run in the live tasks dict
                tasks[task_id]["last_run"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
                recent_fires.append(time.time())
                fired_count += 1

                # Persist after each successful fire (fail-safe: partial updates saved)
                save_tasks(tasks, logger)

                # Brief stagger between successive fires within the same cycle
                if fired_count < len(due):
                    _sleep_interruptible(5)

        _sleep_interruptible(CHECK_INTERVAL_SECONDS)

    logger.info("Boop Executor shutting down gracefully. PID=%d", os.getpid())


def _sleep_interruptible(seconds: float) -> None:
    """Sleep in small increments so SIGTERM/SIGINT is handled promptly."""
    end = time.time() + max(0.0, seconds)
    while not _shutdown_requested and time.time() < end:
        remaining = end - time.time()
        if remaining <= 0:
            break
        time.sleep(min(1.0, remaining))


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    logger = setup_logging()

    if check_existing_instance():
        logger.warning("Another boop_executor instance is already running. Exiting.")
        sys.exit(0)

    write_pid()

    try:
        run(logger)
    except Exception as e:
        logger.critical("Unhandled exception in main loop: %s", e, exc_info=True)
    finally:
        remove_pid()
        logger.info("PID file removed. Boop Executor stopped.")


if __name__ == "__main__":
    main()
