#!/usr/bin/env python3
"""
CTS Remote Diagnostics Script
Client Tech Support Team — Pure Technology

SSHs into a customer's server and runs diagnostic checks:
- Portal service status
- Claude/tmux session health
- Disk space
- Memory usage
- Recent error logs

Usage:
    python3 tools/cts_remote_diag.py --customer joe
    python3 tools/cts_remote_diag.py --customer joe --verbose

Author: dept-systems-technology / client-tech-support-team
Created: 2026-03-16
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CIV_ROOT = Path(__file__).parent.parent
KEYS_DIR = CIV_ROOT / "exports" / "departments" / "client-tech-support" / "keys"
REGISTRY_META = KEYS_DIR / "_registry.json"
LOG_FILE = CIV_ROOT / "logs" / "cts_actions.log"
SSH_TIMEOUT = 30  # seconds


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log_action(action: str, customer: str, detail: str = ""):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} | aether | {action} | {customer} | {detail}\n")


def load_customer(name: str) -> dict:
    """Load customer record from registry."""
    slug = f"{name.lower().replace(' ', '_')}_portal"
    if not REGISTRY_META.exists():
        print(f"[ERROR] Registry not found at {REGISTRY_META}")
        print("        Run: python3 tools/cts_provision_keys.py provision --name <customer>")
        sys.exit(1)

    data = json.loads(REGISTRY_META.read_text())
    info = data.get("customers", {}).get(slug)
    if not info:
        print(f"[ERROR] No customer found with slug '{slug}'")
        print(f"        Available: {list(data.get('customers', {}).keys())}")
        sys.exit(1)

    return info


def ssh_run(info: dict, command: str, timeout: int = SSH_TIMEOUT) -> tuple[int, str, str]:
    """Run a command on a remote server via SSH. Returns (returncode, stdout, stderr)."""
    private_key = info["private_key_path"]
    host = info["server_ip"]
    port = str(info["ssh_port"])
    user = info["ssh_user"]

    ssh_cmd = [
        "ssh",
        "-i", private_key,
        "-p", port,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        "-o", "BatchMode=yes",
        "-o", "IdentitiesOnly=yes",
        f"{user}@{host}",
        command,
    ]

    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", f"SSH command timed out after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


def check_connectivity(info: dict) -> bool:
    """Test basic SSH connectivity."""
    rc, stdout, stderr = ssh_run(info, "echo __cts_connected__", timeout=15)
    if rc == 0 and "__cts_connected__" in stdout:
        return True
    return False


# ---------------------------------------------------------------------------
# Diagnostic Checks
# ---------------------------------------------------------------------------

def diag_portal_service(info: dict) -> dict:
    """Check if PureBrain portal service is running."""
    checks = {
        "systemd": "systemctl is-active purebrain 2>/dev/null || echo inactive",
        "docker": "docker ps --filter 'name=purebrain' --format '{{.Names}} {{.Status}}' 2>/dev/null || echo 'docker-unavailable'",
        "python_server": "pgrep -f 'portal_server' | head -3 || echo 'not-running'",
        "port_8097": "ss -tlnp 2>/dev/null | grep ':8097' || echo 'port-not-listening'",
    }

    results = {}
    for check_name, cmd in checks.items():
        rc, stdout, stderr = ssh_run(info, cmd)
        results[check_name] = {
            "output": stdout or stderr,
            "ok": rc == 0,
        }

    # Determine overall status
    portal_up = (
        "active" in results["systemd"]["output"]
        or ("purebrain" in results["docker"]["output"] and "Up" in results["docker"]["output"])
        or (results["python_server"]["output"] and results["python_server"]["output"] != "not-running")
        or ("8097" in results["port_8097"]["output"])
    )

    return {"status": "up" if portal_up else "down", "details": results}


def diag_tmux_session(info: dict) -> dict:
    """Check if Claude/tmux session is alive."""
    cmd = "tmux list-sessions -F '#{session_name}:#{session_attached}:#{session_windows}' 2>/dev/null || echo 'tmux-not-found'"
    rc, stdout, stderr = ssh_run(info, cmd)

    sessions = []
    tmux_ok = False
    if stdout and stdout != "tmux-not-found":
        for line in stdout.splitlines():
            parts = line.split(":")
            if len(parts) >= 1:
                sessions.append(line)
        tmux_ok = len(sessions) > 0

    # Also check if claude process is running
    rc2, claude_out, _ = ssh_run(info, "pgrep -f 'claude' | wc -l")
    claude_count = int(claude_out.strip()) if rc2 == 0 and claude_out.strip().isdigit() else 0

    return {
        "tmux_sessions": sessions,
        "tmux_alive": tmux_ok,
        "claude_process_count": claude_count,
        "status": "ok" if (tmux_ok or claude_count > 0) else "no-session",
    }


def diag_disk_space(info: dict) -> dict:
    """Check disk space usage."""
    cmd = "df -h / 2>/dev/null | tail -1"
    rc, stdout, stderr = ssh_run(info, cmd)

    if rc != 0 or not stdout:
        return {"status": "error", "output": stderr or "failed to read disk info"}

    # Parse df output: Filesystem Size Used Avail Use% Mountpoint
    parts = stdout.split()
    if len(parts) >= 5:
        use_pct_str = parts[4].rstrip("%")
        try:
            use_pct = int(use_pct_str)
            status = "critical" if use_pct >= 90 else "warning" if use_pct >= 80 else "ok"
            return {
                "filesystem": parts[0],
                "size": parts[1],
                "used": parts[2],
                "avail": parts[3],
                "use_pct": use_pct,
                "status": status,
                "raw": stdout,
            }
        except ValueError:
            pass

    return {"status": "parse-error", "raw": stdout}


def diag_memory(info: dict) -> dict:
    """Check memory usage."""
    cmd = "free -m 2>/dev/null | grep '^Mem:'"
    rc, stdout, stderr = ssh_run(info, cmd)

    if rc != 0 or not stdout:
        return {"status": "error", "output": stderr or "failed to read memory info"}

    # free -m output: Mem: total used free shared buff/cache available
    parts = stdout.split()
    if len(parts) >= 3:
        try:
            total = int(parts[1])
            used = int(parts[2])
            use_pct = int((used / total) * 100) if total > 0 else 0
            status = "critical" if use_pct >= 90 else "warning" if use_pct >= 75 else "ok"
            return {
                "total_mb": total,
                "used_mb": used,
                "free_mb": total - used,
                "use_pct": use_pct,
                "status": status,
            }
        except (ValueError, ZeroDivisionError):
            pass

    return {"status": "parse-error", "raw": stdout}


def diag_recent_errors(info: dict, lines: int = 50) -> dict:
    """Check recent error logs."""
    commands = {
        "portal_log": f"find ~ -name 'portal_server.log' -o -name 'purebrain_log_server.log' 2>/dev/null | head -1 | xargs tail -n {lines} 2>/dev/null || echo 'no-portal-log'",
        "syslog_errors": f"journalctl --no-pager -n {lines} -p err 2>/dev/null | tail -20 || echo 'journalctl-unavailable'",
        "docker_logs": f"docker ps --filter 'name=purebrain' -q 2>/dev/null | head -1 | xargs -I{{}} docker logs --tail {lines} {{}} 2>/dev/null || echo 'no-docker-container'",
    }

    results = {}
    for source, cmd in commands.items():
        rc, stdout, stderr = ssh_run(info, cmd)
        output = stdout or stderr
        # Extract error lines
        error_lines = [
            line for line in output.splitlines()
            if any(kw in line.lower() for kw in ["error", "exception", "fatal", "critical", "traceback"])
        ]
        results[source] = {
            "recent_errors": error_lines[-20:] if error_lines else [],
            "error_count": len(error_lines),
            "raw_tail": output.splitlines()[-10:],
        }

    return results


# ---------------------------------------------------------------------------
# Report Generator
# ---------------------------------------------------------------------------

def generate_report(customer_name: str, info: dict, results: dict, verbose: bool = False) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    slug = info.get("slug", customer_name)

    lines = [
        "=" * 60,
        f"  CTS DIAGNOSTIC REPORT",
        f"  Customer  : {customer_name}",
        f"  Server    : {info['server_ip']}:{info['ssh_port']}",
        f"  Timestamp : {ts}",
        "=" * 60,
        "",
    ]

    # Connectivity
    conn = results.get("connectivity", False)
    lines.append(f"  [{'OK' if conn else 'FAIL'}] SSH Connectivity")
    if not conn:
        lines.append("       Cannot reach server. Check IP, port, and authorized_keys.")
        lines.append("")
        lines.append("  All further checks skipped — no SSH access.")
        return "\n".join(lines)

    lines.append("")

    # Portal service
    portal = results.get("portal_service", {})
    portal_status = portal.get("status", "unknown")
    lines.append(f"  [{'OK' if portal_status == 'up' else 'FAIL'}] Portal Service: {portal_status.upper()}")
    if verbose:
        details = portal.get("details", {})
        for k, v in details.items():
            lines.append(f"       {k}: {v['output'][:100]}")

    # Tmux/Claude
    tmux = results.get("tmux_session", {})
    tmux_status = tmux.get("status", "unknown")
    lines.append(f"  [{'OK' if tmux_status == 'ok' else 'WARN'}] Claude Session: {tmux_status.upper()}")
    sessions = tmux.get("tmux_sessions", [])
    claude_count = tmux.get("claude_process_count", 0)
    if sessions:
        lines.append(f"       tmux sessions: {', '.join(sessions[:3])}")
    if claude_count > 0:
        lines.append(f"       claude processes: {claude_count}")

    # Disk
    disk = results.get("disk_space", {})
    disk_status = disk.get("status", "unknown")
    disk_pct = disk.get("use_pct", "?")
    lines.append(f"  [{'OK' if disk_status == 'ok' else 'WARN' if disk_status == 'warning' else 'CRIT'}] Disk Space: {disk_pct}% used ({disk_status.upper()})")
    if verbose:
        lines.append(f"       {disk.get('used', '?')} used / {disk.get('size', '?')} total, {disk.get('avail', '?')} available")

    # Memory
    mem = results.get("memory", {})
    mem_status = mem.get("status", "unknown")
    mem_pct = mem.get("use_pct", "?")
    lines.append(f"  [{'OK' if mem_status == 'ok' else 'WARN' if mem_status == 'warning' else 'CRIT'}] Memory: {mem_pct}% used ({mem_status.upper()})")
    if verbose:
        lines.append(f"       {mem.get('used_mb', '?')}MB used / {mem.get('total_mb', '?')}MB total")

    # Errors
    lines.append("")
    lines.append("  RECENT ERRORS:")
    errors = results.get("recent_errors", {})
    total_errors = sum(v.get("error_count", 0) for v in errors.values())
    if total_errors == 0:
        lines.append("       No recent errors found in logs.")
    else:
        for source, data in errors.items():
            err_lines = data.get("recent_errors", [])
            if err_lines:
                lines.append(f"       [{source}] ({len(err_lines)} errors):")
                for line in err_lines[:5]:
                    lines.append(f"         {line[:120]}")

    lines += [
        "",
        "=" * 60,
        "  SUMMARY:",
    ]

    # Determine overall health
    issues = []
    if portal_status != "up":
        issues.append("Portal service is DOWN")
    if tmux_status != "ok":
        issues.append("No active Claude/tmux session")
    if disk_status in ("warning", "critical"):
        issues.append(f"Disk usage at {disk_pct}%")
    if mem_status in ("warning", "critical"):
        issues.append(f"Memory usage at {mem_pct}%")
    if total_errors > 0:
        issues.append(f"{total_errors} error(s) in recent logs")

    if not issues:
        lines.append("  All systems OK. No action required.")
    else:
        lines.append(f"  {len(issues)} issue(s) found:")
        for issue in issues:
            lines.append(f"    - {issue}")
        lines.append("")
        lines.append("  Recommended action: Run cts_restart_portal.py if service is down.")

    lines.append("=" * 60)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CTS Remote Diagnostics — Pure Technology Client Tech Support"
    )
    parser.add_argument("--customer", required=True, help="Customer name (e.g. 'joe')")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--output", help="Save report to file (optional)")
    args = parser.parse_args()

    print(f"[diag] Loading customer: {args.customer}")
    info = load_customer(args.customer)

    print(f"[diag] Target: {info['server_ip']}:{info['ssh_port']} as {info['ssh_user']}")
    print(f"[diag] Key: {info['private_key_path']}")
    print()

    results = {}

    # Check connectivity first
    print("[diag] Testing SSH connectivity...")
    conn = check_connectivity(info)
    results["connectivity"] = conn

    if not conn:
        print(f"[FAIL] Cannot connect to {info['server_ip']}:{info['ssh_port']}")
        print("       Possible causes:")
        print("       1. Public key not yet installed in authorized_keys")
        print("       2. Wrong SSH port or IP")
        print("       3. Firewall blocking connection")
        print(f"       Debug: ssh -vvv -i {info['private_key_path']} -p {info['ssh_port']} {info['ssh_user']}@{info['server_ip']}")
        log_action("DIAG_FAIL", info["slug"], "SSH connectivity failed")
        sys.exit(1)

    print("[OK]  Connected.")

    # Run diagnostics
    print("[diag] Checking portal service...")
    results["portal_service"] = diag_portal_service(info)

    print("[diag] Checking tmux/Claude session...")
    results["tmux_session"] = diag_tmux_session(info)

    print("[diag] Checking disk space...")
    results["disk_space"] = diag_disk_space(info)

    print("[diag] Checking memory usage...")
    results["memory"] = diag_memory(info)

    print("[diag] Checking recent error logs...")
    results["recent_errors"] = diag_recent_errors(info)

    # Generate report
    report = generate_report(args.customer, info, results, verbose=args.verbose)

    print()
    print(report)

    if args.output:
        Path(args.output).write_text(report)
        print(f"\n[diag] Report saved to: {args.output}")

    log_action("DIAG_COMPLETE", info["slug"], f"connectivity=ok portal={results['portal_service']['status']}")


if __name__ == "__main__":
    main()
