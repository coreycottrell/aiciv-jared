# BOOP System Restoration - March 9, 2026

**Date**: 2026-03-09
**Issue**: All 31 BOOPs dormant for 12 days (since 2026-02-26, with state file reset on 2026-03-05 but executor never restarted)
**Root Cause**: `boop_executor.py` crashed on 2026-02-22 with `ValueError: sleep length must be non-negative` and was never restarted

---

## What Was Found

1. **Crash log**: `logs/boop_executor.log.gz` showed executor crashed at 2026-02-22 15:50:49 UTC
2. **Bug**: `_sleep_interruptible()` passed `end - time.time()` to `time.sleep()` which could be negative if the loop body ran over `end`
3. **Missing frequency mappings**: 4 frequencies in `scheduled-tasks-state.json` had no entry in `FREQUENCY_MAP`:
   - `60minutes` (conductor-of-conductors)
   - `8hours` (dept-manager-delegation)
   - `12hours` (all twice-daily BOOPs)
   - `nightly` (nightly-site-improvement)
4. **State file**: All 31 tasks had `last_run: 2026-03-05T10:19:16Z` — someone reset timestamps manually on March 5 but never started the executor
5. **No watchdog**: Crontab only had intent_engine + autonomy_nudge, no auto-restart for boop_executor

---

## Fixes Applied

### 1. Bug Fix in `tools/boop_executor.py`
```python
# BEFORE (buggy)
def _sleep_interruptible(seconds: float) -> None:
    end = time.time() + seconds
    while not _shutdown_requested and time.time() < end:
        time.sleep(min(1.0, end - time.time()))  # Can be negative!

# AFTER (fixed)
def _sleep_interruptible(seconds: float) -> None:
    end = time.time() + max(0.0, seconds)
    while not _shutdown_requested and time.time() < end:
        remaining = end - time.time()
        if remaining <= 0:
            break
        time.sleep(min(1.0, remaining))
```

### 2. Added Missing Frequency Mappings
```python
"60minutes": 60 * 60,
"8hours":     8 * 3600,
"12hours":   12 * 3600,
"nightly":   24 * 3600,
```

### 3. Added `nightly` and `12hours` to `TIME_GATED_FREQUENCIES`
These now only fire during active hours (8am-11pm UTC = 3am-6pm EST).

### 4. Reset All 31 Task Timestamps
All tasks backdated to 2 days ago so they immediately appear overdue and fire.

### 5. Started Daemon
```bash
nohup python3 tools/boop_executor.py >> logs/boop_executor.log 2>&1 &
```
PID: 518352

### 6. Added Cron Watchdog
```cron
*/10 * * * * pgrep -f boop_executor.py > /dev/null 2>&1 || (cd /home/jared/projects/AI-CIV/aether && nohup python3 tools/boop_executor.py >> logs/boop_executor.log 2>&1 &)
```

---

## How boop_executor.py Works

- **Daemon process** running continuously (PID file: `.boop_executor.pid`)
- **Check interval**: Every 5 minutes
- **Per cycle**: Max 2 BOOPs per 3-minute window (concurrency throttle)
- **Each BOOP**: Launches independent `claude --print` background process
- **State updates**: Writes `last_run` to `scheduled-tasks-state.json` after each fire
- **Telegram**: Sends fire notification for each BOOP launched
- **Active hours**: Daily/weekly/monthly BOOPs only fire 8am-11pm UTC (= 3am-6pm EST)
- **Sub-daily**: 60min/8hr/12hr BOOPs fire at any time (not time-gated)

---

## Verification

At 20:38 UTC, executor started and immediately:
- Found 24 overdue tasks
- Fired `conductor-of-conductors` (PID 518354)
- Fired `email-check-boop` (PID 518492)
- Deferred remaining 22 (concurrency limit hit, deferred 170s)

Weekly/monthly BOOPs (paper-digest, strategic-alignment, etc.) will fire within active hours once their frequency intervals elapse.

---

## Future: If BOOPs Go Silent Again

1. `pgrep -f boop_executor.py` - check if running
2. `tail -50 logs/boop_executor.log` - check for crash/errors
3. `cat .boop_executor.pid` - check PID file
4. If crashed: `nohup python3 tools/boop_executor.py >> logs/boop_executor.log 2>&1 &`
5. If state stuck: Reset last_run to past date via Python script (see this file)

The cron watchdog at `*/10 * * * *` should auto-restart within 10 minutes of a crash.
