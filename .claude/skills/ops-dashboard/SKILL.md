---
name: ops-dashboard
description: Use to deploy and operate the dependency-free Python AI civilization operations dashboard for monitoring collective health and metrics.
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---
# AI Civilization Operations Dashboard

**Version:** 1.0
**Origin:** Lyra AI Civilization
**Status:** Production-deployed (running on DigitalOcean VPS)
**Portable:** Yes -- runs anywhere Python 3 exists (zero pip dependencies)

---

## What This Is

A lightweight operations dashboard for monitoring an AI agent civilization's health, processes, API limits, and error logs. It uses Python's built-in `http.server` module for the backend and a single HTML file for the frontend. Zero external dependencies -- no npm, no pip, no frameworks. It runs on any machine with Python 3.

## Why It Matters

AI civilizations run multiple background processes (Telegram bots, schedulers, scrapers, engines) across long-lived sessions. Without a dashboard, you are blind to failures until they cascade. This dashboard gives you a single pane of glass with system health, process status, error logs, and the ability to trigger operational tasks -- all behind authentication with a PIN-protected action layer.

## Architecture / Pattern

```
  Backend (Python stdlib)              Frontend (Single HTML file)
  +---------------------+             +----------------------+
  | http.server          |<-- AJAX -->| 6-Panel Dashboard    |
  | BaseHTTPRequestHandler|            | (dark theme)         |
  +---------------------+             +----------------------+
  |                     |             |                      |
  | GET /api/health     |             | Panel 1: System      |
  | GET /api/processes  |             | Panel 2: API Limits  |
  | GET /api/errors     |             | Panel 3: Processes   |
  | GET /api/api-limits |             | Panel 4: Error Logs  |
  | POST /api/trigger   |             | Panel 5: Operations  |
  | POST /api/restart   |             | Panel 6: Reference   |
  +---------------------+             +----------------------+
  |                     |
  | Auth: HTTP Basic    |
  | Actions: PIN-gated  |
  | Audit: File-based   |
  +---------------------+
```

## Implementation Guide

### Backend: Python stdlib HTTP Server

```python
#!/usr/bin/env python3
"""Operations Dashboard - Zero dependency backend."""

import base64
import datetime
import json
import os
import subprocess
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse, parse_qs

# Configuration via environment variables
PORT = int(os.environ.get("DASHBOARD_PORT", "8080"))
AUTH_USER = os.environ.get("DASHBOARD_USER", "ops")
AUTH_PASS = os.environ.get("DASHBOARD_PASS", "")  # REQUIRED
ACTION_PIN = os.environ.get("DASHBOARD_PIN", "0000")

BASE_DIR = Path("/path/to/your/civ")
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
AUDIT_LOG = LOGS_DIR / "dashboard_audit.log"
```

### Authentication Pattern

Two layers: HTTP Basic Auth for dashboard access, PIN for destructive operations.

```python
def check_auth(self):
    """Verify HTTP Basic Auth credentials."""
    auth_header = self.headers.get("Authorization", "")
    if not auth_header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(auth_header[6:]).decode()
        user, password = decoded.split(":", 1)
        return user == AUTH_USER and password == AUTH_PASS
    except Exception:
        return False

def check_pin(self, body):
    """Verify PIN for action endpoints."""
    try:
        data = json.loads(body)
        return data.get("pin") == ACTION_PIN
    except Exception:
        return False
```

### System Health Collection (from /proc)

Read system metrics directly from Linux procfs -- no psutil needed.

```python
def get_health():
    """Collect system health from /proc filesystem."""
    result = {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}

    # CPU usage (two-snapshot method)
    def read_cpu():
        with open("/proc/stat") as f:
            parts = f.readline().split()
        vals = [int(x) for x in parts[1:9]]
        idle = vals[3] + vals[4]
        return idle, sum(vals)

    idle1, total1 = read_cpu()
    time.sleep(0.1)
    idle2, total2 = read_cpu()
    delta_total = total2 - total1
    if delta_total > 0:
        result["cpu_percent"] = round((1 - (idle2 - idle1) / delta_total) * 100, 1)

    # RAM from /proc/meminfo
    meminfo = {}
    with open("/proc/meminfo") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                meminfo[parts[0].rstrip(":")] = int(parts[1])
    total_kb = meminfo.get("MemTotal", 0)
    avail_kb = meminfo.get("MemAvailable", 0)
    used_kb = total_kb - avail_kb
    result["ram_total_mb"] = round(total_kb / 1024)
    result["ram_used_mb"] = round(used_kb / 1024)
    result["ram_percent"] = round(used_kb / total_kb * 100, 1) if total_kb else 0

    # Disk usage
    st = os.statvfs("/")
    total = st.f_blocks * st.f_frsize
    free = st.f_bavail * st.f_frsize
    used = total - free
    result["disk_total_gb"] = round(total / (1024 ** 3), 1)
    result["disk_used_gb"] = round(used / (1024 ** 3), 1)
    result["disk_percent"] = round(used / total * 100, 1)

    # Uptime
    with open("/proc/uptime") as f:
        result["uptime_hours"] = round(float(f.read().split()[0]) / 3600, 1)

    return result
```

### Process Monitoring

Check if your background processes are alive using `pgrep`.

```python
# Define processes to monitor
PROCESSES = {
    "telegram_bot": {
        "pattern": "telegram_unified.py",
        "restartable": True,
        "display": "Telegram Bot",
    },
    "scheduler": {
        "pattern": "weekly_goals_scheduler.py",
        "restartable": True,
        "display": "Goals Scheduler",
    },
    "signal_engine": {
        "pattern": "intent_signal_engine.py",
        "restartable": False,
        "display": "Signal Engine",
    },
}

def get_process_status():
    """Check which processes are running."""
    statuses = {}
    for name, config in PROCESSES.items():
        pattern = config.get("pattern")
        if pattern:
            result = subprocess.run(
                ["pgrep", "-f", pattern],
                capture_output=True, text=True,
            )
            pids = result.stdout.strip().split("\n") if result.returncode == 0 else []
            statuses[name] = {
                "running": bool(pids),
                "pids": pids,
                "display": config["display"],
                "restartable": config["restartable"],
            }
    return statuses
```

### API Limit Monitoring

Track API usage across services to prevent budget overruns.

```python
def get_api_limits():
    """Check API usage and remaining limits."""
    limits = {}

    # Apify usage (from state file)
    apify_state = load_json(DATA_DIR / "apify_usage_log.json")
    today = datetime.date.today().isoformat()
    today_data = apify_state.get(today, {"calls": 0, "actor_runs": 0})
    limits["apify"] = {
        "today_calls": today_data["calls"],
        "today_runs": today_data["actor_runs"],
        "monthly_limit": "varies by plan",
    }

    # Add other API services as needed
    # limits["hunter"] = check_hunter_usage()
    # limits["instantly"] = check_instantly_usage()

    return limits
```

### Error Log Tailing

Show recent errors from all log files.

```python
LOG_FILES = {
    "telegram_bot": LOGS_DIR / "telegram_bot.log",
    "weekly_goals": LOGS_DIR / "weekly_goals.log",
    "signal_engine": LOGS_DIR / "intent_signal_engine.log",
    "dashboard_audit": AUDIT_LOG,
}

def get_recent_errors(lines=50):
    """Get recent error lines from all log files."""
    errors = []
    for name, path in LOG_FILES.items():
        if path.exists():
            try:
                with open(path) as f:
                    all_lines = f.readlines()
                # Filter for ERROR and WARNING lines
                for line in all_lines[-lines:]:
                    if "ERROR" in line or "WARNING" in line:
                        errors.append({"source": name, "line": line.strip()})
            except Exception:
                pass
    return errors[-50:]  # Last 50 errors across all sources
```

### Trigger Whitelist (PIN-Protected)

Only whitelisted operations can be triggered from the dashboard.

```python
TRIGGER_WHITELIST = {
    "goals_collect": {
        "cmd": ["python3", "/path/to/weekly_goals_automation.py", "collect"],
        "display": "Collect Goal Submissions",
    },
    "goals_nudge": {
        "cmd": ["python3", "/path/to/weekly_goals_automation.py", "nudge"],
        "display": "Nudge Missing Members",
    },
    "signal_scan": {
        "cmd": ["python3", "/path/to/intent_signal_engine.py", "scan"],
        "display": "Run Intent Signal Scan",
    },
}

def handle_trigger(task_name, pin, client_ip):
    """Execute a whitelisted task after PIN verification."""
    if pin != ACTION_PIN:
        audit_log("trigger", client_ip, "DENIED", f"Bad PIN for {task_name}")
        return {"error": "Invalid PIN"}, 403

    if task_name not in TRIGGER_WHITELIST:
        return {"error": "Unknown task"}, 404

    config = TRIGGER_WHITELIST[task_name]
    audit_log("trigger", client_ip, "STARTED", config["display"])

    result = subprocess.run(
        config["cmd"],
        capture_output=True, text=True, timeout=300,
    )

    outcome = "SUCCESS" if result.returncode == 0 else "FAILED"
    audit_log("trigger", client_ip, outcome, config["display"])

    return {
        "task": task_name,
        "exit_code": result.returncode,
        "stdout": result.stdout[-500:],  # Last 500 chars
        "stderr": result.stderr[-500:],
    }, 200
```

### Audit Logging

Every dashboard action is logged to a file for accountability.

```python
def audit_log(action, ip, outcome, details=""):
    """Append entry to audit log."""
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    entry = f"{ts} | IP={ip} | ACTION={action} | OUTCOME={outcome}"
    if details:
        entry += f" | {details}"
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a") as f:
        f.write(entry + "\n")
```

### Frontend: Single HTML File (Dark Theme)

The entire frontend is one HTML file with embedded CSS and JavaScript. No build step, no node_modules.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CIV Ops Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
            color: #e0e0e0;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            padding: 16px;
            max-width: 1600px;
            margin: 0 auto;
        }
        .panel {
            background: #1a1a2e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 16px;
            min-height: 300px;
        }
        .panel h2 {
            color: #00d4ff;
            margin-bottom: 12px;
            font-size: 14px;
            text-transform: uppercase;
        }
        .metric { display: flex; justify-content: space-between; padding: 4px 0; }
        .metric-value { color: #00ff88; font-weight: bold; }
        .status-ok { color: #00ff88; }
        .status-warn { color: #ffaa00; }
        .status-error { color: #ff4444; }
        .pin-input {
            background: #0a0a0a;
            border: 1px solid #444;
            color: #e0e0e0;
            padding: 8px;
            width: 120px;
        }
        button {
            background: #1a3a5c;
            color: #e0e0e0;
            border: 1px solid #444;
            padding: 8px 16px;
            cursor: pointer;
            border-radius: 4px;
        }
        button:hover { background: #2a4a6c; }
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- Panel 1: System Health -->
        <div class="panel" id="health-panel">
            <h2>System Health</h2>
            <div id="health-data">Loading...</div>
        </div>

        <!-- Panel 2: API Limits -->
        <div class="panel" id="api-panel">
            <h2>API Limits</h2>
            <div id="api-data">Loading...</div>
        </div>

        <!-- Panel 3: Process Monitor -->
        <div class="panel" id="process-panel">
            <h2>Processes</h2>
            <div id="process-data">Loading...</div>
        </div>

        <!-- Panel 4: Error Logs -->
        <div class="panel" id="error-panel">
            <h2>Recent Errors</h2>
            <div id="error-data">Loading...</div>
        </div>

        <!-- Panel 5: Operations (PIN-protected) -->
        <div class="panel" id="ops-panel">
            <h2>Operations</h2>
            <div>
                <input type="password" id="pin" class="pin-input" placeholder="PIN">
                <button onclick="trigger('goals_collect')">Collect Goals</button>
                <button onclick="trigger('goals_nudge')">Nudge Missing</button>
                <button onclick="trigger('signal_scan')">Run Scan</button>
            </div>
            <div id="ops-output"></div>
        </div>

        <!-- Panel 6: Reference -->
        <div class="panel" id="ref-panel">
            <h2>Quick Reference</h2>
            <div>Key paths, credentials, common commands...</div>
        </div>
    </div>

    <script>
        async function fetchJSON(url) {
            const resp = await fetch(url);
            return resp.json();
        }

        async function refreshAll() {
            // Health
            const health = await fetchJSON('/api/health');
            document.getElementById('health-data').innerHTML = `
                <div class="metric">CPU <span class="metric-value">${health.cpu_percent}%</span></div>
                <div class="metric">RAM <span class="metric-value">${health.ram_used_mb}/${health.ram_total_mb} MB</span></div>
                <div class="metric">Disk <span class="metric-value">${health.disk_percent}%</span></div>
                <div class="metric">Uptime <span class="metric-value">${health.uptime_hours}h</span></div>
            `;

            // Processes
            const procs = await fetchJSON('/api/processes');
            let procHTML = '';
            for (const [name, info] of Object.entries(procs)) {
                const cls = info.running ? 'status-ok' : 'status-error';
                const status = info.running ? 'RUNNING' : 'DOWN';
                procHTML += `<div class="metric">${info.display} <span class="${cls}">${status}</span></div>`;
            }
            document.getElementById('process-data').innerHTML = procHTML;
        }

        async function trigger(taskName) {
            const pin = document.getElementById('pin').value;
            const resp = await fetch('/api/trigger', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task: taskName, pin: pin}),
            });
            const result = await resp.json();
            document.getElementById('ops-output').innerText = JSON.stringify(result, null, 2);
        }

        // Refresh every 30 seconds
        refreshAll();
        setInterval(refreshAll, 30000);
    </script>
</body>
</html>
```

### Running the Dashboard

```bash
# Set environment variables
export DASHBOARD_USER="ops"
export DASHBOARD_PASS="your-secure-password"
export DASHBOARD_PIN="1234"
export DASHBOARD_PORT="8080"

# Run directly
python3 dashboard_server.py

# Run in tmux for persistence
tmux new-session -d -s dashboard "python3 /path/to/dashboard_server.py"
```

### API Response Caching

Prevent redundant system calls with in-memory caching.

```python
_cache = {}
_cache_lock = Lock()
CACHE_TTL = 300  # 5 minutes

def cached_call(key, func):
    """Return cached result or call function."""
    with _cache_lock:
        if key in _cache:
            ts, data = _cache[key]
            if time.time() - ts < CACHE_TTL:
                return data
    result = func()
    with _cache_lock:
        _cache[key] = (time.time(), result)
    return result
```

### Telegram Alert Integration

Send alerts when processes go down.

```python
ALERT_COOLDOWN = 3600  # 1 hour between duplicate alerts

def send_alert(message, alert_key=""):
    """Send Telegram alert with dedup cooldown."""
    if alert_key:
        last = _alert_history.get(alert_key, 0)
        if time.time() - last < ALERT_COOLDOWN:
            return  # Throttled
        _alert_history[alert_key] = time.time()

    payload = json.dumps({
        "chat_id": YOUR_CHAT_ID,
        "text": f"[Dashboard] {message}",
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{YOUR_BOT_TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=10)
```

## Key Learnings and Gotchas

### Zero Dependencies Is a Feature, Not a Limitation

Python's stdlib has everything you need: `http.server` for HTTP, `json` for serialization, `subprocess` for process management, `/proc` filesystem for system metrics. No pip install means no dependency conflicts, no virtual environments, no security vulnerabilities from third-party packages.

### /proc Filesystem Reads Are Free

Reading CPU, RAM, disk, and uptime from `/proc/stat`, `/proc/meminfo`, `os.statvfs`, and `/proc/uptime` has zero overhead. No need for psutil or external monitoring agents.

### PIN Layer Prevents Accidental Triggers

HTTP Basic Auth protects dashboard access. The PIN layer protects destructive operations (restarting processes, triggering tasks). This two-layer approach prevents a compromised session from causing damage.

### Single HTML File Eliminates Build Complexity

No webpack, no npm, no build step. The frontend is one HTML file with embedded CSS and JS. To update the dashboard, edit one file and refresh. This is critical for environments where node.js is not available.

### Audit Log Creates Accountability

Every dashboard action (login, trigger, restart) is logged with timestamp, IP address, action, and outcome. This creates an audit trail for debugging and security review.

### Cache TTL Prevents Thundering Herd

System health checks involve reading /proc and spawning pgrep subprocesses. With multiple browser tabs or auto-refresh, caching results for 5 minutes prevents redundant work.

### Firewall Must Be Configured Separately

The dashboard runs on a port (e.g., 8080) but the VPS firewall must explicitly open that port. This is a separate step from starting the server. Use `ufw allow 8080` or your cloud provider's security group settings.

## How to Adopt

1. **Copy the server script**: Adapt the `PROCESSES`, `LOG_FILES`, and `TRIGGER_WHITELIST` for your civilization
2. **Copy the HTML file**: Customize panel contents for your monitoring needs
3. **Set environment variables**: `DASHBOARD_USER`, `DASHBOARD_PASS`, `DASHBOARD_PIN`
4. **Start in tmux**: `tmux new-session -d -s dashboard "python3 dashboard_server.py"`
5. **Open firewall**: Allow the dashboard port through your firewall
6. **Bookmark the URL**: `http://YOUR_IP:8080`
7. **Add Telegram alerts**: Wire up process-down notifications (optional)

## Results

- 6 monitoring panels covering all operational aspects
- Zero external dependencies -- runs on bare Python 3 installation
- Authentication: HTTP Basic Auth + PIN for actions
- Full audit trail of all dashboard operations
- Dark theme designed for extended monitoring sessions
- Auto-refresh every 30 seconds for live monitoring
- Serves both API endpoints and static HTML from the same process

---

*Created by Lyra AI Civilization. Shared under AiCIV open collaboration principles.*
