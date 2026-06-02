---
name: weekly-health-check
description: 10-point system health audit with auto-fix for safe issues and week-over-week trend tracking
version: 1.0.0
source: AI-CIV/dept-systems-technology
allowed-tools: [Bash, Read, Write, Grep, Glob]
agents-required: [devops-engineer]
cadence: weekly (Saturday)
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---

# Weekly System Health Check

A comprehensive 10-point server health audit that checks processes, memory, disk, services, logs, and infrastructure. Outputs a color-coded health card, auto-fixes safe issues, flags items requiring human attention, and tracks trends week-over-week.

## When to Use

**Invoke when**:
- Saturday BOOP fires (scheduled weekly)
- Manually via `/weekly-health-check` when system feels sluggish
- After major deployments or infrastructure changes
- Before important demos or client-facing events

**Do not use when**:
- Active incident in progress (focus on the incident, audit after)

## Prerequisites

- SSH/local access to the server
- Read access to systemd, journalctl, /proc, /tmp
- Write access to `.claude/memory/health-audits/`

## Output Format

Each of the 10 categories gets a status:

```
[GREEN]  - Healthy, no action needed
[YELLOW] - Warning, monitor or minor action needed
[RED]    - Critical, requires immediate attention
```

## Procedure

Run ALL of the following checks. Collect results, then output the unified health card.

---

### CHECK 1: Zombie/Orphan Processes

```bash
# Count zombies
ZOMBIES=$(ps aux | awk '$8 ~ /Z/ {print}' | wc -l)
# List defunct processes
ps aux | grep -i defunct | grep -v grep
# Check orphan processes (PPID=1 that shouldn't be)
ps -eo pid,ppid,stat,comm | awk '$2==1 && $3 ~ /Z/'
```

**Rating**:
- GREEN: 0 zombies
- YELLOW: 1-3 zombies
- RED: 4+ zombies or growing trend

**Auto-fix**: None (zombies require parent process investigation)

---

### CHECK 2: Memory & Disk

```bash
# RAM usage
free -h
# Swap usage
swapon --show
# Disk usage (all mounts)
df -h
# Top 10 memory consumers
ps aux --sort=-%mem | head -11
# Claude process memory specifically
ps aux | grep -E 'claude|node.*claude' | grep -v grep
```

**Rating**:
- GREEN: RAM <70%, Swap <20%, Disk <75%
- YELLOW: RAM 70-85%, Swap 20-50%, Disk 75-90%
- RED: RAM >85%, Swap >50%, Disk >90%

**Auto-fix**: None (requires human decision on what to clear)

---

### CHECK 3: Running Services

```bash
# Check all critical services
for svc in aether-portal aether-session aether-telegram cloudflared nginx; do
  systemctl is-active "$svc" 2>/dev/null || echo "MISSING: $svc"
done

# Full service status
systemctl list-units --type=service --state=running | grep -E 'aether|cloud|nginx|postgres|redis'

# Check for failed services
systemctl --failed
```

**Rating**:
- GREEN: All critical services running, 0 failed
- YELLOW: Non-critical service down or 1 failed unit
- RED: Critical service down (aether-session, cloudflared, nginx)

**Auto-fix**: Attempt restart of non-critical failed services:
```bash
# Only restart non-critical services automatically
systemctl restart <failed-non-critical-service>
```

---

### CHECK 4: Stale PID Files

```bash
# Find all PID files in project root
cd /home/jared/projects/AI-CIV/aether
for pidfile in .*.pid; do
  [ -f "$pidfile" ] || continue
  PID=$(cat "$pidfile" 2>/dev/null)
  if [ -n "$PID" ] && ! kill -0 "$PID" 2>/dev/null; then
    echo "STALE: $pidfile (PID $PID not running)"
  fi
done
```

**Rating**:
- GREEN: 0 stale PID files
- YELLOW: 1-2 stale PID files (auto-cleaned)
- RED: 3+ stale PID files (suggests recurring crash pattern)

**Auto-fix**: Remove stale PID files:
```bash
# Safe auto-fix: remove PID files whose processes don't exist
rm -f "$pidfile"
echo "CLEANED: $pidfile"
```

---

### CHECK 5: tmux Sessions

```bash
# List all tmux sessions
tmux list-sessions 2>/dev/null || echo "No tmux server running"
# Check for sessions older than 7 days with no activity
tmux list-sessions -F '#{session_name} #{session_created}' 2>/dev/null
```

**Rating**:
- GREEN: 1-3 active sessions, all recent
- YELLOW: 4-6 sessions or some stale (>7 days inactive)
- RED: 7+ sessions or tmux server not running when expected

**Auto-fix**: None (sessions may contain important work - flag for human review)

---

### CHECK 6: Port Conflicts

```bash
# Check key ports for duplicate listeners
for port in 80 443 3000 3001 5000 8080 8950; do
  LISTENERS=$(ss -tlnp | grep ":${port} " | wc -l)
  if [ "$LISTENERS" -gt 1 ]; then
    echo "CONFLICT: Port $port has $LISTENERS listeners"
    ss -tlnp | grep ":${port} "
  fi
done
```

**Rating**:
- GREEN: No duplicate listeners on any port
- YELLOW: Duplicate listener on non-critical port
- RED: Duplicate listener on port 80, 443, or 3000

**Auto-fix**: None (requires human decision on which process to kill)

---

### CHECK 7: Log File Sizes

```bash
# Check log sizes in project
find /home/jared/projects/AI-CIV/aether/logs/ -type f -name "*.log" -exec ls -lh {} \; | sort -k5 -h -r | head -20

# Check system journal size
journalctl --disk-usage

# Check for logs > 100MB
find /home/jared/projects/AI-CIV/aether/logs/ -type f -size +100M -exec ls -lh {} \;

# Check /tmp for large files
find /tmp -maxdepth 2 -type f -size +50M -exec ls -lh {} \; 2>/dev/null
```

**Rating**:
- GREEN: No log > 100MB, journal < 2GB
- YELLOW: Log 100-500MB or journal 2-4GB
- RED: Log > 500MB or journal > 4GB

**Auto-fix**: Rotate oversized logs:
```bash
# Truncate logs > 200MB (keep last 10K lines)
for logfile in $(find /home/jared/projects/AI-CIV/aether/logs/ -type f -size +200M); do
  tail -10000 "$logfile" > "${logfile}.trimmed"
  mv "${logfile}.trimmed" "$logfile"
  echo "TRIMMED: $logfile"
done
```

---

### CHECK 8: Claude Code Session Health

```bash
# Count Claude-related processes
ps aux | grep -E 'claude|anthropic' | grep -v grep | wc -l

# Total memory of Claude processes
ps aux | grep -E 'claude|anthropic' | grep -v grep | awk '{sum+=$6} END {printf "%.0f MB\n", sum/1024}'

# JSONL accumulation in /tmp
find /tmp -name "*.jsonl" -mtime +7 -exec ls -lh {} \; 2>/dev/null
JSONL_COUNT=$(find /tmp -name "*.jsonl" 2>/dev/null | wc -l)
JSONL_OLD=$(find /tmp -name "*.jsonl" -mtime +7 2>/dev/null | wc -l)
echo "Total JSONL: $JSONL_COUNT, Older than 7 days: $JSONL_OLD"

# Check .claude session data size
du -sh /home/jared/projects/AI-CIV/aether/.claude/ 2>/dev/null | head -1
```

**Rating**:
- GREEN: <10 processes, <2GB total memory, 0 stale JSONLs
- YELLOW: 10-20 processes, 2-4GB memory, 1-10 stale JSONLs
- RED: >20 processes, >4GB memory, >10 stale JSONLs

**Auto-fix**: Prune old JSONL files (>7 days):
```bash
find /tmp -name "*.jsonl" -mtime +7 -delete 2>/dev/null
echo "PRUNED: Old JSONL files from /tmp"
```

---

### CHECK 9: Cron Jobs

```bash
# List user crontab
crontab -l 2>/dev/null || echo "No user crontab"

# Check for cron conflicts (same script scheduled multiple times)
crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' | awk '{print $6}' | sort | uniq -d

# Check cron log for recent failures
grep -i 'cron.*error\|cron.*fail' /var/log/syslog 2>/dev/null | tail -5
```

**Rating**:
- GREEN: All crons present, no duplicates, no recent failures
- YELLOW: 1-2 missing crons or minor failure
- RED: Critical cron missing or repeated failures

**Auto-fix**: None (cron modifications require human approval)

---

### CHECK 10: Recent Crashes

```bash
# OOM kills in last 7 days
journalctl --since "7 days ago" | grep -i "oom-kill\|out of memory" | tail -10

# Service crashes in last 7 days
journalctl --since "7 days ago" -p err | grep -E 'aether|claude|nginx|cloudflare' | tail -20

# Kernel errors
dmesg --time-format iso 2>/dev/null | tail -20

# Unexpected reboots
last reboot | head -5
```

**Rating**:
- GREEN: 0 OOM kills, 0 critical crashes, 0 unexpected reboots
- YELLOW: 1-2 non-critical crashes, no OOM
- RED: Any OOM kill, critical service crash, or unexpected reboot

**Auto-fix**: None (crashes require investigation)

---

## Output: Health Card

After running all checks, compile the health card:

```markdown
# System Health Audit - YYYY-MM-DD

## Overall Status: [GREEN/YELLOW/RED]

| # | Category | Status | Details |
|---|----------|--------|---------|
| 1 | Zombie/Orphan Processes | [STATUS] | [summary] |
| 2 | Memory & Disk | [STATUS] | [summary] |
| 3 | Running Services | [STATUS] | [summary] |
| 4 | Stale PID Files | [STATUS] | [summary] |
| 5 | tmux Sessions | [STATUS] | [summary] |
| 6 | Port Conflicts | [STATUS] | [summary] |
| 7 | Log File Sizes | [STATUS] | [summary] |
| 8 | Claude Code Sessions | [STATUS] | [summary] |
| 9 | Cron Jobs | [STATUS] | [summary] |
| 10 | Recent Crashes | [STATUS] | [summary] |

## Auto-Fixed Issues
- [list of items automatically remediated]

## Issues Requiring Human Attention
- [list of items that need Jared's review]

## Recommended Actions
1. [prioritized action items]

## Trend Comparison
- Previous audit: [date] | Overall: [status]
- Current audit: [date] | Overall: [status]
- Trend: [IMPROVING / STABLE / DEGRADING]
- Notable changes: [what changed since last audit]
```

## Post-Audit: Save Results

**MANDATORY**: Save the health card to memory for trend tracking:

```bash
# Save audit results
AUDIT_DATE=$(date +%Y-%m-%d)
cat > /home/jared/projects/AI-CIV/aether/.claude/memory/health-audits/${AUDIT_DATE}-health-audit.md << 'AUDIT_EOF'
[full health card content here]
AUDIT_EOF
```

## Post-Audit: Trend Analysis

Before generating the current report, load the previous audit:

```bash
# Find most recent previous audit
ls -t /home/jared/projects/AI-CIV/aether/.claude/memory/health-audits/*-health-audit.md 2>/dev/null | head -1
```

Compare each category's status to the previous week. Note improvements and regressions in the Trend Comparison section.

## Escalation Rules

- Any RED item: Flag in portal immediately, include in health card
- 3+ YELLOW items: Treat as overall YELLOW, recommend proactive maintenance
- RED on services (Check 3) or crashes (Check 10): Immediate alert, do not wait for Saturday
- Recurring YELLOW across 3+ weeks: Escalate to RED (chronic issue)

## Success Indicators

- [ ] All 10 checks executed with fresh data
- [ ] Health card generated with color-coded status
- [ ] Safe auto-fixes applied (stale PIDs, old JSONLs, oversized logs)
- [ ] Results saved to `.claude/memory/health-audits/YYYY-MM-DD-health-audit.md`
- [ ] Trend comparison included (if previous audit exists)
- [ ] Issues requiring human attention clearly listed
- [ ] Recommended actions prioritized

---

**Invocation**: `/weekly-health-check` or Saturday BOOP
**Owner**: dept-systems-technology
**Created**: 2026-04-06
