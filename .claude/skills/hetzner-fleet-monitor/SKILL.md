---
name: hetzner-fleet-monitor
version: 1.0.0
author: aether
description: Monitor Hetzner VPS fleet running AI civilization containers. Check PID count (>150 warning, >190 critical), disk, memory, network. NEVER deploy to containers (constitutional). Report to Witness Support.
tags: [hetzner, monitoring, containers, pid-exhaustion, infrastructure]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Hetzner Fleet Monitor

Monitor the Hetzner VPS fleet running AI civilization containers.

## Constitutional Rule

**NEVER deploy to customer containers.**

- No SSH scripts/tmux to containers
- Containers = Claude Code sessions ONLY
- APIs → Workers, data → D1, frontend → Pages, files → R2
- Container SQLite BANNED for production data

**Monitoring ONLY.** Report issues to Witness Support for resolution.

## State File

**Location:** `/home/jared/projects/AI-CIV/aether/.hetzner_monitor_state.json`

```json
{
  "last_check": "2026-05-20T12:00:00Z",
  "containers": {
    "chy-container": {
      "pid_count": 187,
      "disk_usage_percent": 68,
      "memory_percent": 72,
      "last_alert": "2026-05-19T08:30:00Z",
      "status": "warning"
    },
    "morphe-container": {
      "pid_count": 145,
      "disk_usage_percent": 45,
      "memory_percent": 55,
      "last_alert": null,
      "status": "healthy"
    }
  },
  "alerts": [
    {
      "timestamp": "2026-05-19T08:30:00Z",
      "container": "chy-container",
      "type": "pid_count",
      "severity": "warning",
      "value": 187,
      "threshold": 150
    }
  ]
}
```

## Key Metrics

### 1. PID Count (CRITICAL)

**Why it matters:** Chy container lockup incident due to PID exhaustion.

| PID Count | Status | Action |
|-----------|--------|--------|
| < 150 | Healthy | No action |
| 150-190 | Warning | Alert Witness, monitor closely |
| > 190 | Critical | Emergency alert + recovery plan |

**Check command:**
```bash
ps aux | wc -l
```

**Recovery pattern (Witness-executed, May 2026):**
```bash
# Kill duplicate AgentMail monitors (most common cause)
pkill -f agentmail_general_monitor.py

# Kill runaway tmux sessions
tmux list-sessions | grep -v "main\|primary" | awk '{print $1}' | sed 's/://' | xargs -I {} tmux kill-session -t {}

# Kill orphaned Python processes
ps aux | grep python3 | grep -v grep | awk '{print $2}' | xargs kill -9

# Verify PID count reduced
ps aux | wc -l
```

### 2. Disk Usage

| Usage % | Status | Action |
|---------|--------|--------|
| < 70% | Healthy | No action |
| 70-85% | Warning | Check for large logs/temp files |
| > 85% | Critical | Alert + cleanup required |

**Check command:**
```bash
df -h / | tail -1 | awk '{print $5}' | sed 's/%//'
```

**Common culprits:**
- `/tmp/` - Accumulated temp files
- `logs/*.log` - Large log files
- `node_modules/` - Duplicate installs
- `.backups/` - Old backups

### 3. Memory Pressure

| Memory % | Status | Action |
|----------|--------|--------|
| < 75% | Healthy | No action |
| 75-90% | Warning | Check process list |
| > 90% | Critical | Alert + investigation |

**Check command:**
```bash
free | grep Mem | awk '{print int($3/$2 * 100)}'
```

### 4. Network Connectivity

**Check command:**
```bash
# Ping Cloudflare DNS
ping -c 3 1.1.1.1

# Check internet connectivity
curl -s -o /dev/null -w "%{http_code}" https://purebrain.ai
```

**Expected:** 3/3 packets, HTTP 200

## Monitoring Script

**Location:** `tools/hetzner_fleet_monitor.py` (to be created)

```python
#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timezone

STATE_FILE = ".hetzner_monitor_state.json"

def check_pid_count():
    """Check current PID count."""
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    return len(result.stdout.strip().split('\n'))

def check_disk_usage():
    """Check disk usage percentage."""
    result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    usage_line = lines[-1]
    return int(usage_line.split()[4].rstrip('%'))

def check_memory_usage():
    """Check memory usage percentage."""
    result = subprocess.run(["free"], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    mem_line = [l for l in lines if l.startswith('Mem:')][0]
    parts = mem_line.split()
    total, used = int(parts[1]), int(parts[2])
    return int((used / total) * 100)

def send_alert(container, metric, value, threshold):
    """Send alert email to Witness Support."""
    # Email to Witness Support (witness-alerts@agentmail.to)
    # Use AgentMail system
    pass

def main():
    pid_count = check_pid_count()
    disk_usage = check_disk_usage()
    memory_usage = check_memory_usage()
    
    status = "healthy"
    
    if pid_count > 190:
        status = "critical"
        send_alert("aether-container", "pid_count", pid_count, 190)
    elif pid_count > 150:
        status = "warning"
        send_alert("aether-container", "pid_count", pid_count, 150)
    
    # Update state file
    state = {
        "last_check": datetime.now(timezone.utc).isoformat(),
        "pid_count": pid_count,
        "disk_usage_percent": disk_usage,
        "memory_percent": memory_usage,
        "status": status
    }
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"Status: {status}")
    print(f"PIDs: {pid_count}/200")
    print(f"Disk: {disk_usage}%")
    print(f"Memory: {memory_usage}%")

if __name__ == "__main__":
    main()
```

## Alert Routing

### Severity: Warning (150-190 PIDs, 70-85% disk, 75-90% memory)

**Recipient:** Witness Support (witness-alerts@agentmail.to)
**Format:** Email via AgentMail
**Frequency:** Once per incident (don't spam)

**Subject:** `⚠️ Hetzner Fleet Warning - [Container] [Metric]`

**Body Template:**
```
Hetzner Fleet Warning
Container: [container-name]
Metric: [pid_count / disk_usage / memory_usage]
Current Value: [X]
Threshold: [Y]
Status: warning

Timestamp: [ISO8601]

Action Required: Monitor closely, review process list

—
Automated alert from Aether Hetzner Fleet Monitor
```

### Severity: Critical (>190 PIDs, >85% disk, >90% memory)

**Recipients:**
- Witness Support (witness-alerts@agentmail.to)
- Jared (jared@puretechnology.nyc)
- CC War Room (channel 39)

**Subject:** `🔴 CRITICAL - Hetzner Fleet - [Container] [Metric]`

**Body Template:**
```
🔴 CRITICAL Hetzner Fleet Alert

Container: [container-name]
Metric: [pid_count / disk_usage / memory_usage]
Current Value: [X]
Threshold: [Y]
Status: CRITICAL

Timestamp: [ISO8601]

IMMEDIATE ACTION REQUIRED

Recovery procedures available at:
.claude/skills/hetzner-fleet-monitor/SKILL.md

—
Automated critical alert from Aether Hetzner Fleet Monitor
```

## Historical Incident: Chy Container Lockup (May 2026)

**Symptom:** Chy container became unresponsive
**Root Cause:** PID exhaustion (>200 PIDs)
**Primary Culprit:** Duplicate AgentMail monitor processes

**Witness Recovery Actions:**
1. SSH to container
2. `pkill -f agentmail_general_monitor.py` (killed 8 duplicate processes)
3. Killed orphaned tmux sessions
4. Killed runaway Python processes
5. Verified PID count reduced to ~120

**Prevention:**
- Monitor PID count continuously
- Alert at 150 (before crisis at 190+)
- Kill duplicate processes proactively

**pkill patterns used:**
```bash
# AgentMail duplicates
pkill -f agentmail_general_monitor.py

# Orphaned tmux
tmux list-sessions | grep -v "main\|primary" | awk '{print $1}' | sed 's/://' | xargs -I {} tmux kill-session -t {}

# Runaway Python
ps aux | grep python3 | grep -v grep | awk '{print $2}' | xargs kill -9
```

## Cron Schedule (Recommended)

```cron
# Check every 30 minutes
*/30 * * * * cd /home/jared/projects/AI-CIV/aether && python3 tools/hetzner_fleet_monitor.py >> logs/hetzner_monitor.log 2>&1

# Daily summary (8am UTC)
0 8 * * * cd /home/jared/projects/AI-CIV/aether && python3 tools/hetzner_daily_summary.py
```

## Dashboard Integration

**Location:** `exports/portal-files/hetzner-fleet-status.json`

```json
{
  "timestamp": "2026-05-20T12:00:00Z",
  "overall_status": "healthy",
  "containers": {
    "chy": {"status": "healthy", "pid_count": 145},
    "morphe": {"status": "healthy", "pid_count": 132},
    "aether": {"status": "healthy", "pid_count": 128}
  },
  "last_alert": null
}
```

**Portal integration:**
```javascript
// Fetch status in portal dashboard
fetch('/exports/portal-files/hetzner-fleet-status.json')
  .then(r => r.json())
  .then(data => {
    // Show status indicator
    updateFleetStatus(data.overall_status);
  });
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Deploying to Containers
**BAD:** SSH to container and deploy code/config
**WHY:** Constitutional violation - containers are sessions only

### ❌ Anti-Pattern 2: Ignoring Early Warnings
**BAD:** "150 PIDs is fine, we have headroom"
**WHY:** By 190 PIDs, container is often unresponsive

### ❌ Anti-Pattern 3: Manual Cleanup Without Root Cause
**BAD:** Kill processes without investigating why they accumulated
**WHY:** Problem recurs without addressing root cause

### ❌ Anti-Pattern 4: No State Tracking
**BAD:** Checking metrics but not logging history
**WHY:** Can't identify trends or recurring issues

## Verification Commands

```bash
# Current status snapshot
python3 tools/hetzner_fleet_monitor.py

# Historical alerts
cat .hetzner_monitor_state.json | jq '.alerts'

# Check monitoring cron is running
crontab -l | grep hetzner_fleet_monitor

# Verify alert routing works
python3 -c "from tools.hetzner_fleet_monitor import send_alert; send_alert('test', 'test', 999, 100)"
```

## Integration with Other Skills

Works with:
- `agentmail-operations` - Alert delivery via AgentMail
- `cc-api-messaging` - Critical alerts to War Room
- `portal-file-delivery` - Dashboard status updates

## Constitutional Grounding

From MEMORY.md:
> "NEVER deploy to customer containers (Apr 23): No SSH/scripts/tmux. Trio comms via CF Workers ONLY."
> "NOTHING IN CONTAINERS (Apr 21): Containers = Claude Code sessions only. APIs→Workers, data→D1, frontend→Pages, files→R2. Container SQLite BANNED for prod."

## Success Indicators

- [ ] PID exhaustion detected before crisis (150 threshold)
- [ ] Disk cleanup triggered before critical (70% threshold)
- [ ] Zero unplanned container restarts
- [ ] All alerts routed to Witness Support
- [ ] Historical trend data available for capacity planning

## Future Enhancements

1. **Predictive alerting** - Trend analysis to predict PID exhaustion
2. **Auto-cleanup** - Safe automated cleanup for common culprits
3. **Multi-container dashboard** - Unified view of all fleet containers
4. **Capacity planning** - Resource usage trends over time

---

*Last Updated: 2026-05-20*
*Status: Constitutional*
