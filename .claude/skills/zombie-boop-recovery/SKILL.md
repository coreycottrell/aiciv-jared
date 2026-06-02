---
name: zombie-boop-recovery
description: Detect, diagnose, and recover from BOOP pipeline stalls caused by hung claude --print processes that block all new BOOP spawns
type: operations
domain: boop-infrastructure, process-management, incident-response
created: 2026-05-26
trigger: "when BOOPs stop firing, when boop_executor appears running but no new inbox/conductor-boop-*.md files appear, when BOOP gap exceeds 90 minutes"
status: provisional
tick_count: 0
last_used: 2026-05-26
introduced: 2026-05-26
---

# Zombie BOOP Recovery

**Purpose**: Diagnose and recover from BOOP pipeline stalls caused by `claude --print` processes that hang indefinitely. These zombie processes appear alive to `boop_executor.py` (valid PID, not defunct), blocking all new BOOP spawns because the executor believes a BOOP is already running.

**Origin**: 2026-05-22 through 2026-05-26 -- a 96-hour BOOP outage. The delegation-enforcer detected zombie PIDs 24 hours before anyone acted. Root cause: `boop_executor.py` had no max-runtime kill, so a stuck `claude --print` process counted as "running" indefinitely, preventing all subsequent BOOPs from spawning.

## Detection Steps

### Step 1: Check BOOP Output Freshness (First Signal)

```bash
# Age of newest BOOP output file -- >90min = BOOP-CRON-STALL
ls -t /home/jared/projects/AI-CIV/aether/inbox/conductor-boop-*.md 2>/dev/null | head -1
stat --format='%Y' "$(ls -t /home/jared/projects/AI-CIV/aether/inbox/conductor-boop-*.md 2>/dev/null | head -1)" 2>/dev/null | xargs -I{} bash -c 'echo "Age: $(( ($(date +%s) - {}) / 60 )) minutes"'
```

If age >90 minutes, proceed to Step 2.

### Step 2: Verify boop_executor Is Running

```bash
# Check PID file and process
cat /home/jared/projects/AI-CIV/aether/.boop_executor.pid 2>/dev/null
ps aux | grep boop_executor | grep -v grep
```

If executor is running but no outputs, the pipeline is stalled (not stopped).

### Step 3: Find Hung BOOP Processes

```bash
# List all claude --print processes with their age
ps aux | grep 'claude.*--print' | grep -v grep
# Show process tree to see parent-child relationships
pstree -p $(cat /home/jared/projects/AI-CIV/aether/.boop_executor.pid 2>/dev/null) 2>/dev/null
# Check process age (any claude --print older than 4 hours is suspect)
ps -eo pid,etimes,cmd | grep 'claude.*--print' | grep -v grep | awk '$2 > 14400 {print "ZOMBIE:", $0}'
```

### Step 4: Check Executor Logs for Confirmation

```bash
# Look for "already running" or concurrency-limit messages
tail -100 /home/jared/projects/AI-CIV/aether/logs/boop_executor.log | grep -i 'running\|skip\|concurrency\|already\|reap'
```

## Recovery Steps

### Step 5: Kill Zombie Processes

```bash
# Kill specific hung claude --print processes (by PID from Step 3)
kill <PID>
# If SIGTERM does not work after 10 seconds:
kill -9 <PID>
# Verify they are gone
ps aux | grep 'claude.*--print' | grep -v grep
```

### Step 6: Verify Pipeline Resumes

```bash
# Watch executor log for next BOOP fire
tail -f /home/jared/projects/AI-CIV/aether/logs/boop_executor.log &
# Wait 2-3 minutes for next cycle
# Verify new BOOP output appears
ls -t /home/jared/projects/AI-CIV/aether/inbox/conductor-boop-*.md | head -1
```

### Step 7: Verify Reaper Is Active (Prevention)

```bash
# Confirm MAX_BOOP_RUNTIME_SECONDS is set in boop_executor.py
grep MAX_BOOP_RUNTIME /home/jared/projects/AI-CIV/aether/tools/boop_executor.py
# Confirm reap_stuck_boop_processes is called in the main loop
grep reap_stuck_boop /home/jared/projects/AI-CIV/aether/tools/boop_executor.py
```

The reaper (added post-incident) kills any BOOP process older than `MAX_BOOP_RUNTIME_SECONDS` (default: 14400 = 4 hours). If this value is missing or the reaper function is not called in `run()`, the vulnerability is still present.

## Gotchas

1. **Process alive does not equal process working**: A `claude --print` process can sit idle with a valid PID, passing `os.kill(pid, 0)` checks, while producing zero output. The executor sees "running" and refuses to spawn new BOOPs.

2. **Delegation-enforcer detect does not equal fix**: The delegation-enforcer BOOP can detect zombie PIDs but cannot kill them or escalate to main thread automatically. If the enforcer reports zombie PIDs, a main-thread actor MUST intervene -- do not assume the finding will self-resolve.

3. **BOOP gap check must use output file timestamps, not PID existence**: Checking if `boop_executor.py` is running tells you the scheduler is alive, NOT that BOOPs are firing. Always check `inbox/conductor-boop-*.md` freshness as the primary signal.

4. **Killing the executor instead of the zombie makes it worse**: If you kill `boop_executor.py` instead of the hung `claude --print` child, you lose the scheduler AND the zombie persists. Always kill the child process first, then verify the executor recovers.

5. **Multiple zombies can accumulate**: If the executor retries and spawns additional `claude --print` processes that also hang (e.g., due to an upstream API issue), you may find 2-5 zombies. Kill all of them.

## Examples

### Real Incident: 96-Hour BOOP Outage (2026-05-22 to 2026-05-26)

**Timeline**:
- 2026-05-22: `claude --print` process hangs during a BOOP execution
- boop_executor sees PID as alive, skips all subsequent BOOP scheduling
- 2026-05-23: delegation-enforcer detects stale PIDs, logs warning
- No main-thread actor reads the warning or takes action
- 2026-05-26: Manual investigation discovers the zombie; process killed; BOOPs resume

**Root Cause**: `boop_executor.py` had no `MAX_BOOP_RUNTIME_SECONDS` or reaper function. A single hung process blocked the entire BOOP pipeline indefinitely.

**Fix Applied**: Added `reap_stuck_boop_processes()` function with 4-hour max runtime. Called every executor cycle in the `run()` loop.

**Lesson**: Critical infrastructure needs both detection AND automated remediation. Detection alone (delegation-enforcer) is insufficient if no actor is empowered to fix.
