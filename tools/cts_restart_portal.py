#!/usr/bin/env python3
"""
CTS Remote Portal Restart Script
Client Tech Support Team — Pure Technology

SSHs into a customer's server and restarts their portal/Claude session.
Verifies services came back up. Logs the restart event.
Rate limit: max 1 restart per customer per 5 minutes.

Usage:
    python3 tools/cts_restart_portal.py --customer joe
    python3 tools/cts_restart_portal.py --customer joe --force

Author: dept-systems-technology / client-tech-support-team
Created: 2026-03-16
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CIV_ROOT = Path(__file__).parent.parent
KEYS_DIR = CIV_ROOT / "exports" / "departments" / "client-tech-support" / "keys"
REGISTRY_META = KEYS_DIR / "_registry.json"
LOG_FILE = CIV_ROOT / "logs" / "cts_actions.log"
RESTART_STATE_FILE = CIV_ROOT / "logs" / "cts_restart_state.json"

RESTART_COOLDOWN_SECONDS = 5 * 60  # 5 minutes
SSH_TIMEOUT = 45


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log_action(action: str, customer: str, detail: str = ""):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} | aether | {action} | {customer} | {detail}\n")
    print(f"[log] {ts} | {action} | {customer} | {detail}")


def load_customer(name: str) -> dict:
    slug = f"{name.lower().replace(' ', '_')}_portal"
    if not REGISTRY_META.exists():
        print(f"[ERROR] Registry not found. Run: python3 tools/cts_provision_keys.py provision --name {name}")
        sys.exit(1)
    data = json.loads(REGISTRY_META.read_text())
    info = data.get("customers", {}).get(slug)
    if not info:
        print(f"[ERROR] No customer found with slug '{slug}'")
        sys.exit(1)
    return info


def check_rate_limit(slug: str) -> tuple[bool, int]:
    """
    Returns (is_allowed, seconds_remaining).
    Rate limit: max 1 restart per customer per 5 minutes.
    """
    if not RESTART_STATE_FILE.exists():
        return True, 0

    try:
        state = json.loads(RESTART_STATE_FILE.read_text())
    except Exception:
        return True, 0

    last_restart = state.get(slug, {}).get("last_restart_ts", 0)
    elapsed = time.time() - last_restart
    if elapsed < RESTART_COOLDOWN_SECONDS:
        remaining = int(RESTART_COOLDOWN_SECONDS - elapsed)
        return False, remaining
    return True, 0


def record_restart(slug: str):
    """Record a restart event for rate limiting."""
    RESTART_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        state = json.loads(RESTART_STATE_FILE.read_text()) if RESTART_STATE_FILE.exists() else {}
    except Exception:
        state = {}
    state[slug] = {
        "last_restart_ts": time.time(),
        "last_restart_human": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    RESTART_STATE_FILE.write_text(json.dumps(state, indent=2))


def ssh_run(info: dict, command: str, timeout: int = SSH_TIMEOUT) -> tuple[int, str, str]:
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
    rc, stdout, _ = ssh_run(info, "echo __cts_ok__", timeout=15)
    return rc == 0 and "__cts_ok__" in stdout


def is_portal_up(info: dict) -> bool:
    """Quick check if portal is responding."""
    checks = [
        "pgrep -f 'portal_server' > /dev/null 2>&1",
        "ss -tlnp 2>/dev/null | grep -q ':8097'",
        "docker ps --filter 'name=purebrain' --filter 'status=running' -q 2>/dev/null | grep -q .",
        "systemctl is-active purebrain 2>/dev/null | grep -q active",
    ]
    for cmd in checks:
        rc, _, _ = ssh_run(info, cmd, timeout=10)
        if rc == 0:
            return True
    return False


# ---------------------------------------------------------------------------
# Restart Strategies
# ---------------------------------------------------------------------------

def try_restart_systemd(info: dict) -> bool:
    """Attempt restart via systemd."""
    print("  [strategy] Trying systemd restart...")
    rc, stdout, stderr = ssh_run(info, "sudo systemctl restart purebrain 2>&1 && echo 'systemd-restarted'")
    if rc == 0 and "systemd-restarted" in stdout:
        print("  [ok] systemd restart successful")
        return True
    print(f"  [skip] systemd: {stderr or stdout or 'not available'}")
    return False


def try_restart_docker(info: dict) -> bool:
    """Attempt restart via docker."""
    print("  [strategy] Trying docker restart...")
    # Find running/stopped purebrain containers
    rc, container_id, _ = ssh_run(
        info,
        "docker ps -a --filter 'name=purebrain' -q 2>/dev/null | head -1"
    )
    if rc != 0 or not container_id:
        print("  [skip] No docker container named 'purebrain' found")
        return False

    rc, stdout, stderr = ssh_run(info, f"docker restart {container_id} 2>&1")
    if rc == 0:
        print(f"  [ok] Docker container {container_id[:12]} restarted")
        return True
    print(f"  [skip] docker restart failed: {stderr or stdout}")
    return False


def try_restart_process(info: dict) -> bool:
    """Attempt to restart portal_server.py process directly."""
    print("  [strategy] Trying process restart (kill + relaunch)...")

    # Kill existing process
    ssh_run(info, "pkill -f portal_server.py 2>/dev/null; sleep 1")

    # Find the portal server script
    rc, script_path, _ = ssh_run(
        info,
        "find ~ /opt /srv -name 'portal_server.py' 2>/dev/null | head -1"
    )
    if rc != 0 or not script_path:
        print("  [skip] Could not locate portal_server.py on remote server")
        return False

    # Launch in background
    portal_dir = str(Path(script_path).parent)
    rc, stdout, stderr = ssh_run(
        info,
        f"cd {portal_dir} && nohup python3 portal_server.py >> ~/logs/portal_server.log 2>&1 & echo 'launched'"
    )
    if rc == 0 and "launched" in stdout:
        print(f"  [ok] portal_server.py relaunched from {script_path}")
        return True
    print(f"  [skip] process relaunch failed: {stderr or stdout}")
    return False


def try_restart_aether_session(info: dict) -> bool:
    """Attempt to restart via aether-restart.sh script if present."""
    print("  [strategy] Trying aether restart script...")
    rc, stdout, stderr = ssh_run(
        info,
        "test -f ~/tools/aether-restart.sh && bash ~/tools/aether-restart.sh && echo 'aether-restarted'"
    )
    if rc == 0 and "aether-restarted" in stdout:
        print("  [ok] aether-restart.sh ran successfully")
        return True
    print("  [skip] aether-restart.sh not found or failed")
    return False


# ---------------------------------------------------------------------------
# Main restart flow
# ---------------------------------------------------------------------------

def restart_portal(info: dict, force: bool = False) -> bool:
    """
    Execute restart sequence. Tries multiple strategies in order.
    Returns True if portal came back up.
    """
    slug = info["slug"]

    # Rate limit check
    if not force:
        allowed, remaining = check_rate_limit(slug)
        if not allowed:
            print(f"[RATE LIMIT] Last restart was less than 5 minutes ago.")
            print(f"             {remaining}s remaining before next restart is allowed.")
            print(f"             Use --force to override.")
            return False

    # Record this restart attempt
    record_restart(slug)
    log_action("RESTART_INITIATED", slug, f"server={info['server_ip']}")

    print(f"[restart] Attempting portal restart for: {info['customer_name']}")
    print(f"[restart] Server: {info['server_ip']}:{info['ssh_port']}")
    print()

    # Try strategies in order
    strategies = [
        try_restart_aether_session,
        try_restart_systemd,
        try_restart_docker,
        try_restart_process,
    ]

    restarted = False
    for strategy in strategies:
        if strategy(info):
            restarted = True
            break

    if not restarted:
        print()
        print("[FAIL] All restart strategies failed.")
        print("       Manual intervention may be required.")
        log_action("RESTART_FAILED", slug, "all strategies failed")
        return False

    # Wait for services to come up
    print()
    print("[restart] Waiting for services to initialize (15s)...")
    time.sleep(15)

    # Verify portal came back up
    print("[restart] Verifying portal is up...")
    for attempt in range(3):
        if is_portal_up(info):
            print(f"[OK]  Portal is UP after restart.")
            log_action("RESTART_SUCCESS", slug, "portal verified up")
            return True
        if attempt < 2:
            print(f"       Not up yet, retrying in 10s... ({attempt + 1}/3)")
            time.sleep(10)

    print("[WARN] Restart executed but portal not confirmed up.")
    print("       Check manually: ssh -i {key} -p {port} {user}@{host} 'pgrep -f portal_server'")
    log_action("RESTART_UNVERIFIED", slug, "restart ran but portal not confirmed up")
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CTS Remote Portal Restart — Pure Technology Client Tech Support"
    )
    parser.add_argument("--customer", required=True, help="Customer name (e.g. 'joe')")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Override rate limit (use with caution)"
    )
    args = parser.parse_args()

    print(f"[restart] Loading customer: {args.customer}")
    info = load_customer(args.customer)

    # Connectivity check
    print(f"[restart] Testing SSH connectivity to {info['server_ip']}:{info['ssh_port']}...")
    if not check_connectivity(info):
        print(f"[ERROR] Cannot connect to {info['server_ip']}:{info['ssh_port']}")
        print(f"        Check SSH key installation and connectivity.")
        sys.exit(1)
    print("[OK]  Connected.")
    print()

    # Check current state
    portal_was_up = is_portal_up(info)
    print(f"[restart] Portal state before restart: {'UP' if portal_was_up else 'DOWN'}")

    if portal_was_up and not args.force:
        print("[INFO] Portal appears to be running. Use --force to restart anyway.")
        print("       For diagnostics run: python3 tools/cts_remote_diag.py --customer " + args.customer)
        sys.exit(0)

    # Execute restart
    success = restart_portal(info, force=args.force)

    print()
    if success:
        print("[DONE] Portal restart completed successfully.")
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"       Restart time: {ts}")
        print(f"       Customer: {info['customer_name']} ({info['server_ip']})")
    else:
        print("[FAIL] Portal restart failed or unverified.")
        print("       Run diagnostics: python3 tools/cts_remote_diag.py --customer " + args.customer)
        sys.exit(1)


if __name__ == "__main__":
    main()
