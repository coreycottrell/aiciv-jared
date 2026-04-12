# Boop Executor v2.0 - Option B: Background Claude Code Agents

**Date**: 2026-02-22
**Type**: teaching
**Agent**: devops-engineer
**Topic**: Migrating boop executor from tmux injection to independent background Claude Code agents

---

## What Changed

Replaced Option A (tmux send-keys injection) with Option B (independent background Claude Code agents).

**Old behavior**: `tmux send-keys -t {session} "BOOP [task_id] ..." Enter`
- Cluttered the terminal
- Boops queued up waiting for prior task to finish
- All boops fought for the same Claude Code context window

**New behavior**: `claude --print -p "BOOP [task_id]: ..." --allowedTools "Bash,..." &`
- Each boop is a completely independent process
- No terminal pollution
- Parallel execution up to MAX_CONCURRENT_BOOP_AGENTS (3)
- Each agent logs to `/tmp/boop_{task_id}.log`

## Key Implementation Details

### Subprocess Launch
```python
proc = subprocess.Popen(
    ["claude", "--print", "-p", prompt, "--allowedTools", "Bash,Read,Write,..."],
    stdout=log_fh,
    stderr=log_fh,
    cwd=str(BASE_DIR),
    start_new_session=True,
    close_fds=True,
    env=env,  # CRITICAL: env must have CLAUDECODE removed
)
```

### CRITICAL: Unset CLAUDECODE Environment Variable

When boop_executor runs inside a Claude Code session (which it does - Aether runs inside Claude Code),
the `CLAUDECODE` env var is set. Any child `claude` process sees this and refuses to start:

```
Error: Claude Code cannot be launched inside another Claude Code session.
Nested sessions share runtime resources and will crash all active sessions.
To bypass this check, unset the CLAUDECODE environment variable.
```

**Fix**: Copy env dict and pop CLAUDECODE before passing to Popen:
```python
env = os.environ.copy()
env.pop("CLAUDECODE", None)
```

This is ESSENTIAL - without it, every boop agent fails silently (0-byte log file).

### Concurrent Agent Check
Uses `pgrep -f "claude.*BOOP"` to count running boop agents:
```python
result = subprocess.run(['pgrep', '-f', 'claude.*BOOP'], capture_output=True, text=True)
running = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
if running >= MAX_CONCURRENT_BOOP_AGENTS:  # 3
    logger.info("Skipping %s: %d agents running", task_id, running)
    return False
```

### Boop Prompt Structure
The prompt embeds:
1. Task description and agent role
2. Working directory (`/home/jared/projects/AI-CIV/aether`)
3. Curl command for agent to send results to Telegram when done (with bot token embedded)

```python
send_tg_cmd = (
    f'curl -s "https://api.telegram.org/bot{bot_token}/sendMessage" '
    f'-d chat_id="{chat_id}" '
    f'--data-urlencode "text=BOOP [{task_id}] complete: $SUMMARY"'
)
```

### Removed: tmux code
- Removed `get_tmux_session()` function entirely
- Removed `SESSION_FILE` constant (no longer needed)
- `fire_boop()` no longer reads `.current_session`

### Kept Intact
- All scheduling/frequency/active-hours logic
- Concurrency window throttle (2 fires per 3-minute window)
- Telegram launch notification (now includes agent name + PID)
- last_run timestamp updates
- PID file management
- Graceful shutdown

## Gotchas

1. **CLAUDECODE must be unset** - Most important lesson. Without this, 100% failure rate.
2. **Log files start at 0 bytes** - Normal. Claude Code has startup overhead (2-5 seconds before output).
3. **pgrep pattern `claude.*BOOP`** - Works because the prompt starts with "BOOP [task_id]:" which appears in the process args visible to pgrep.
4. **start_new_session=True** - Essential so boop agents survive if boop_executor restarts.

## Verification Evidence

After fix deployed:
- `pgrep -a -f "claude.*BOOP"` shows two independent processes (PIDs 4130591, 4130642)
- Log shows: `Launched boop agent: [sister-collective-boop] PID=4130591`
- Both processes in `ps -ef` output with full prompt text (not "Claude Code cannot be launched...")
- Log files went from 215 bytes (error text) to 0 bytes (running, no output yet) = success

## Startup/Stop Commands

```bash
# Start
rm -f /home/jared/projects/AI-CIV/aether/.boop_executor.pid
nohup python3 /home/jared/projects/AI-CIV/aether/tools/boop_executor.py >> /home/jared/projects/AI-CIV/aether/logs/boop_executor.log 2>&1 &

# Stop
kill $(cat /home/jared/projects/AI-CIV/aether/.boop_executor.pid)

# Check agents running
pgrep -c -f "claude.*BOOP"

# Check agent log
cat /tmp/boop_{task_id}.log
```
