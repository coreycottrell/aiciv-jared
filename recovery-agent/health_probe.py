#!/usr/bin/env python3
"""
health_probe.py — companion utility that runs the `ai_alive: bool` probe
INSIDE a customer container via `docker exec`. Invoked by the CF Worker
pre-restart and by the systemd timer that feeds the cron-driven /health
endpoint (CTO amendment #3).

ai_alive heuristic (intentionally simple to keep false-negatives low):
  1. PID for `claude` (or `/usr/bin/claude`) exists in the container.
  2. Container thread count is below 80 % of the cgroup pids.max ceiling
     (split-brain guard — runaway threads imply uvicorn alive but Claude
     thread-bombed).

Designed to run on the Hetzner host as the recovery-agent user; relies on
the same sudoers entry that grants `sudo docker exec` for the allowlisted
containers. Read-only — never restarts anything.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


DOCKER_BIN = "/usr/bin/docker"
SUDO_BIN = "/usr/bin/sudo"
THREAD_CEILING_RATIO = 0.80


def _run(cmd: list[str], timeout: int = 8) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def claude_pid_present(container: str) -> bool:
    """True if a `claude` PID exists inside the container."""
    # `pgrep -f claude` is robust to argv variants (claude, /usr/bin/claude, claude code, ...).
    rc, out, _ = _run([SUDO_BIN, "-n", DOCKER_BIN, "exec", container, "pgrep", "-f", "claude"])
    if rc == 0 and out.strip():
        return True
    # Fallback: look directly at /proc/*/comm.
    rc, out, _ = _run([
        SUDO_BIN, "-n", DOCKER_BIN, "exec", container,
        "sh", "-c", "ls /proc/*/comm 2>/dev/null | xargs -I{} cat {} 2>/dev/null | grep -c '^claude$'",
    ])
    if rc == 0:
        try:
            return int((out.strip() or "0").splitlines()[-1]) > 0
        except (ValueError, IndexError):
            return False
    return False


def thread_count_under_ceiling(container: str) -> tuple[bool, Optional[int], Optional[int]]:
    """Return (under_ceiling, threads, pids_max)."""
    rc, out, _ = _run([
        SUDO_BIN, "-n", DOCKER_BIN, "exec", container,
        "sh", "-c", "ls /proc | grep -c '^[0-9]\\+$'",
    ])
    if rc != 0:
        return False, None, None
    try:
        threads = int(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return False, None, None

    rc2, out2, _ = _run([
        SUDO_BIN, "-n", DOCKER_BIN, "exec", container,
        "sh", "-c", "cat /sys/fs/cgroup/pids.max 2>/dev/null || echo max",
    ])
    pids_max_raw = (out2 or "").strip().splitlines()[-1] if rc2 == 0 else "max"
    if pids_max_raw == "max" or not pids_max_raw.isdigit():
        # No ceiling configured — treat as healthy on this dimension.
        return True, threads, None
    pids_max = int(pids_max_raw)
    return threads < int(pids_max * THREAD_CEILING_RATIO), threads, pids_max


def probe(container: str) -> dict:
    if not shutil.which(SUDO_BIN) or not Path(DOCKER_BIN).exists():
        return {"ai_alive": False, "error": "sudo or docker missing"}
    pid_ok = claude_pid_present(container)
    threads_ok, threads, pids_max = thread_count_under_ceiling(container)
    return {
        "ai_alive": bool(pid_ok and threads_ok),
        "claude_pid_present": pid_ok,
        "thread_count": threads,
        "pids_max": pids_max,
        "thread_ceiling_ratio": THREAD_CEILING_RATIO,
        "container": container,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Probe a customer container for ai_alive.")
    p.add_argument("container", help="Container name (must be in /etc/recovery-agent/allowlist.txt).")
    args = p.parse_args(argv)
    result = probe(args.container)
    print(json.dumps(result, separators=(",", ":")))
    return 0 if result.get("ai_alive") else 1


if __name__ == "__main__":
    sys.exit(main())
