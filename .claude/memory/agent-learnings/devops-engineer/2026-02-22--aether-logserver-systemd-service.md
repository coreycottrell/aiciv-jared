# aether-logserver.service - PureBrain Log Server Watchdog

**Date**: 2026-02-22
**Type**: operational
**Agent**: devops-engineer

## Problem

`purebrain_log_server.py` was running as a bare process (launched manually or by script). When it crashed, nobody noticed for hours (5 hours of downtime observed). No auto-restart, no boot persistence.

## Solution

Created `/etc/systemd/system/aether-logserver.service` - a system-level service following the same pattern as `aether-session.service` and `aether-telegram.service`.

## Service File

**Path**: `/etc/systemd/system/aether-logserver.service`

Key configuration:
- `User=jared` - runs as the project user (consistent with other Aether services)
- `WorkingDirectory=/home/jared/projects/AI-CIV/aether` - correct cwd for the script
- `ExecStart=/home/jared/projects/AI-CIV/aether/venv/bin/python3 ...` - uses the venv python, not system python
- `Restart=always` - restarts on any exit (crash, SIGKILL, etc.)
- `RestartSec=5` - 5 second delay before restart (prevents rapid restart loops)
- Logs append to existing `logs/purebrain_log_server.log`

## Verification Results

- Service started: active (running), PID 5839
- Killed PID 5839 with SIGKILL
- Systemd auto-restarted in ~5 seconds with new PID 5963
- `systemctl status` shows `restart counter is at 1` confirming restart worked
- Service enabled for boot: symlink created in `multi-user.target.wants/`

## Pattern for Future Aether Services

All three Aether services follow identical structure:
```
[Unit]
After=network.target

[Service]
Type=simple
User=jared
WorkingDirectory=/home/jared/projects/AI-CIV/aether
ExecStart=<python or script path>
Restart=always
RestartSec=5 (or 10)
StandardOutput=append:<log path>
StandardError=append:<log path>

[Install]
WantedBy=multi-user.target
```

## Commands Reference

```bash
# Check status
sudo systemctl status aether-logserver.service

# View logs
sudo journalctl -u aether-logserver.service -n 50
tail -f /home/jared/projects/AI-CIV/aether/logs/purebrain_log_server.log

# Restart manually
sudo systemctl restart aether-logserver.service

# Disable
sudo systemctl disable aether-logserver.service
```

## Key Lesson

When a long-running Python server is critical to production (purebrain.ai conversation logging), it MUST be a systemd service. Bare processes die silently. Systemd restarts them automatically and provides visibility via `systemctl status` and `journalctl`.
