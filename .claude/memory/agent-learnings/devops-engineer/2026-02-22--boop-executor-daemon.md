# Boop Executor Daemon - Implementation Patterns

**Date**: 2026-02-22
**Type**: teaching
**Agent**: devops-engineer
**Topic**: Scheduled task daemon for Aether boop system

---

## What Was Built

`/home/jared/projects/AI-CIV/aether/tools/boop_executor.py` - background Python daemon that:
- Reads `.claude/scheduled-tasks-state.json` every 5 minutes
- Fires due tasks into active tmux session via `tmux send-keys`
- Persists `last_run` timestamps back to the JSON file
- Manages a PID file at `.boop_executor.pid`
- Throttles to max 2 boops per 3-minute concurrency window
- Sends Telegram notification to Jared (chat_id 548906264) after each successful fire

## Key Design Decisions

### PID File Pattern
Standard single-instance enforcement: write PID on start, kill(pid, 0) to check if alive,
remove PID on exit (finally block). Stale PID files (process died) are auto-cleaned.

### Frequency Parsing
All frequencies in `FREQUENCY_MAP` dict (seconds). Time-gated frequencies (daily, weekly, monthly)
only fire during active hours 08:00-23:00 local. Day-constrained frequencies (weekly-monday,
weekly-friday) checked against `datetime.weekday()`.

### Concurrency Throttle
`recent_fires` list of timestamps, trimmed to last 3 minutes. Max 2 fires per window.
If limit hit, remaining due tasks defer to next 5-minute check cycle (NOT a sleep inside loop).

### tmux Injection
```python
cmd = ["tmux", "send-keys", "-t", session, trigger, "Enter"]
```
Session name read from `.current_session` file. Fallback: "aether".

### Boop Message Format
```
BOOP [{task_id}] Agent: {agent} | Category: {category} | Task: {description}
```

### Logging Duplicate Prevention
When launched via nohup, stdout gets redirected to log file. If logger also has a StreamHandler
pointing to stdout, every line appears twice. Fix: only add StreamHandler if `sys.stdout.isatty()`.

### Telegram Notification Pattern (added 2026-02-22)

Fires after successful tmux inject only (not on failures). Standard library only - `urllib.request`
and `urllib.parse`. Config loaded from `config/telegram_config.json` (key: `bot_token`).
Failures are warnings only - never crash the main fire loop.

```python
tg_msg = f"[BOOP] {task_id} fired\n{description} (category: {category})"
send_telegram(tg_msg, logger)
```

`TELEGRAM_CONFIG` path defined at module level using `BASE_DIR` for consistency.

## What Worked

- Standard library only (json, logging, os, signal, subprocess, time, datetime, pathlib,
  urllib.parse, urllib.request)
- Graceful shutdown via SIGTERM/SIGINT with 1-second interrupt-check sleep increments
- Per-fire JSON saves (fail-safe: partial progress preserved if daemon dies mid-cycle)
- 23 never-run tasks detected and started firing immediately on first boot
- Telegram notify: exception-safe wrapper means network errors never stop boop execution

## Gotchas

- `25min` frequency is in the tasks file but not a standard interval - added it to FREQUENCY_MAP
- `90min` also appears (context-window-boop) - added to map
- `paper-digest-boop` task exists in JSON but has no `last_run` field and uses `weekly-monday`
  which requires day-of-week check to be Saturday 2026-02-22 = not a Monday, so won't fire
- nohup + FileHandler duplicate log lines - solved with isatty() check

## Startup Command

```bash
# Check if running, start if not
pgrep -f boop_executor.py || (rm -f /home/jared/projects/AI-CIV/aether/.boop_executor.pid && nohup python3 /home/jared/projects/AI-CIV/aether/tools/boop_executor.py >> /home/jared/projects/AI-CIV/aether/logs/boop_executor.log 2>&1 &)
```

Use absolute paths - pgrep runs from whatever cwd, relative paths fail.

## Stop Command

```bash
kill $(cat /home/jared/projects/AI-CIV/aether/.boop_executor.pid)
```
