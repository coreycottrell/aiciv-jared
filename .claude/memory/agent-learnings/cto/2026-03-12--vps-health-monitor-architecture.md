# CTO Memory: VPS Health Monitor Architecture

**Date**: 2026-03-12
**Type**: operational + teaching
**Topic**: VPS health monitoring, Claude Code instance sprawl diagnosis and prevention

---

## Problem Statement

Jared reported multiple Claude Code instances being created on terminal reconnect.
Root cause hypothesis: `aether-session.service` with `Restart=always` spawns a
new Claude Code process on every service restart, rather than reattaching to the
existing tmux session.

## Solution Built

Four scripts in `tools/`:

| Script | Purpose |
|--------|---------|
| `vps-health.sh` | Full health dashboard - CPU, RAM, disk, process counts, tmux sessions, alerts |
| `vps-instance-tracker.sh` | Deep diagnosis - maps Claude PIDs to tmux sessions, reads systemd journal |
| `vps-cleanup.sh` | Safe interactive cleanup - kills oldest Claude processes, keeps N newest |
| `install-vps-monitor.sh` | One-command systemd timer installation (5-min polling, sudo required) |

## Key Architecture Decisions

### 1. Alert-on-threshold, not alert-always
- `vps-health.sh --alert --quiet` only sends Telegram when thresholds breached
- Prevents notification fatigue for Jared
- Thresholds: >2 Claude instances, >85% CPU/RAM/disk, >6 tmux sessions

### 2. Systemd timer over cron
- `aether-vps-monitor.timer` + `aether-vps-monitor.service` pairs
- OnBootSec=60 ensures check runs 1 min after reboot
- OnUnitActiveSec=5min for ongoing monitoring
- Integrates with existing systemd ecosystem (aether-session, aether-telegram)

### 3. JSON mode for machine consumption
- `--json` flag outputs clean JSON for any future log aggregation / dashboard

### 4. Kill policy: keep newest, kill oldest
- By PID order (higher PID = more recently spawned on Linux)
- Keeps the active session, kills zombies from stale reconnects

## Diagnosis Pattern for Instance Sprawl

To diagnose whether reconnecting causes new instances:
```bash
# Run full diagnosis
./tools/vps-instance-tracker.sh --diagnose

# Key things to check:
# 1. Does aether-session.service have Restart=always?
# 2. What is its ExecStart command? Does it call `claude` directly?
# 3. How many times has it restarted? (journalctl -u aether-session.service)
# 4. Are Claude PIDs children of tmux panes or of systemd?
```

## Files Created

- `/home/jared/projects/AI-CIV/aether/tools/vps-health.sh`
- `/home/jared/projects/AI-CIV/aether/tools/vps-instance-tracker.sh`
- `/home/jared/projects/AI-CIV/aether/tools/vps-cleanup.sh`
- `/home/jared/projects/AI-CIV/aether/tools/install-vps-monitor.sh`
- Log destination: `/home/jared/projects/AI-CIV/aether/logs/vps_health.log`

## Deployment Commands

```bash
# Make executable (run from CIV_ROOT)
chmod +x tools/vps-health.sh tools/vps-instance-tracker.sh tools/vps-cleanup.sh tools/install-vps-monitor.sh

# Run health check now
./tools/vps-health.sh

# Run deep diagnosis
./tools/vps-instance-tracker.sh --diagnose

# Install systemd timer (requires sudo)
sudo ./tools/install-vps-monitor.sh
```
