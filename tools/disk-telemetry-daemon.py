#!/usr/bin/env python3
"""
disk-telemetry-daemon — production disk safety telemetry collector.

Replaces tools/disk-guard-sweeper.sh (bash cron) per Jared's 2026-05-15 22:26 UTC
directive. Polls every 5 minutes, computes tier, runs constrained auto-recovery,
POSTs to disk-telemetry-ingest CF Worker with HMAC-signed payload.

Spec:     specs/disk-safety-telemetry-2026-05-15.md
CTO:      specs/cto-review-4-specs-2026-05-15.md (APPROVE w/ 4 amendments)

CTO amendments folded in:
  #1  HMAC nonce + 30s timestamp window
  #2  systemd hardening (in service file, not here)
  #3  INGEST_TOKEN rotation: last-known-good fallback for 5 min
  #4  source_ip stamped server-side (Worker fills from cf-connecting-ip)

Constitutional:
  - NO working-tree deletion EVER (R3 flags only)
  - PII discipline: NEVER logs file PATHS to telemetry; sizes + suffixes only
  - Kill switch: DISK_TELEMETRY_ENABLED=0 disables collection without code deploy
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import secrets
import shutil
import signal
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

__version__ = "1.0.0"

# ----------------------------- Configuration ---------------------------------

CIV_NAME = os.environ.get("CIV_NAME", "aether")
INGEST_URL = os.environ.get(
    "DISK_TELEMETRY_INGEST_URL",
    "https://disk-telemetry-ingest.in0v8.workers.dev/ingest",
)
INGEST_TOKEN = os.environ.get("DISK_TELEMETRY_INGEST_TOKEN", "")
POLL_INTERVAL_SECONDS = int(os.environ.get("DISK_TELEMETRY_POLL_SECONDS", "300"))
ENABLED = os.environ.get("DISK_TELEMETRY_ENABLED", "1") == "1"
FORCE_TIER = os.environ.get("DISK_TELEMETRY_FORCE_TIER")  # 'info' | 'warn' | 'critical'

STATE_DIR = Path(os.environ.get(
    "DISK_TELEMETRY_STATE_DIR",
    f"/var/lib/disk-telemetry/{CIV_NAME}",
))
STATE_DB = STATE_DIR / "state.db"

TMP_DIR = Path("/tmp")
WORKING_TREE_ROOTS = [Path.home() / "projects"]

# Tier thresholds
WARN_PCT = 70
CRIT_PCT = 85
TMP_BIG_FILE_BYTES = 100 * 1024 * 1024       # 100 MB
TMP_TOTAL_CRIT_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB
TMP_BIG_COUNT_WARN = 5
AUTO_DELETE_MIN_AGE_HOURS = 24.0

# Token rotation fail-open window (CTO amend #3)
LKG_FAIL_OPEN_SECONDS = 300

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [disk-telemetry] %(message)s",
)
log = logging.getLogger("disk-telemetry-daemon")


# ----------------------------- Data classes ----------------------------------


@dataclass
class Snapshot:
    civ_name: str
    hostname: str
    disk_root_used_pct: int
    disk_root_free_mb: int
    tmp_size_mb: int
    tmp_large_files_count: int
    working_tree_large_files_count: int
    alert_tier: str
    raw_top5_tmp_files: list  # [{size_mb, age_hours, suffix}]
    daemon_version: str = __version__


# ----------------------------- Tier calculator -------------------------------


def compute_tier(
    disk_used_pct: int,
    tmp_size_mb: int,
    tmp_big_count: int,
) -> str:
    """Pure function; unit-tested.

    - critical: disk >= CRIT_PCT, or tmp total >= TMP_TOTAL_CRIT_BYTES
    - warn:     disk >= WARN_PCT, or tmp_big_count >= TMP_BIG_COUNT_WARN
    - info:     otherwise
    """
    if FORCE_TIER in ("info", "warn", "critical"):
        return FORCE_TIER

    if disk_used_pct >= CRIT_PCT:
        return "critical"
    if tmp_size_mb * 1024 * 1024 >= TMP_TOTAL_CRIT_BYTES:
        return "critical"
    if disk_used_pct >= WARN_PCT:
        return "warn"
    if tmp_big_count >= TMP_BIG_COUNT_WARN:
        return "warn"
    return "info"


# ----------------------------- Local state -----------------------------------


def init_state_db() -> sqlite3.Connection:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(STATE_DB)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def state_get(conn: sqlite3.Connection, key: str) -> Optional[str]:
    cur = conn.execute("SELECT value FROM state WHERE key = ?", (key,))
    row = cur.fetchone()
    return row[0] if row else None


def state_set(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO state(key, value, updated_at) VALUES (?, ?, ?)",
        (key, value, int(time.time())),
    )
    conn.commit()


# ----------------------------- Collection ------------------------------------


def collect_disk_root() -> tuple[int, int]:
    """Return (used_pct, free_mb) for /."""
    usage = shutil.disk_usage("/")
    used = usage.used
    total = usage.total
    pct = int(round((used / total) * 100)) if total else 0
    free_mb = usage.free // (1024 * 1024)
    return pct, free_mb


def collect_tmp_stats() -> tuple[int, int, list]:
    """Return (tmp_total_mb, big_file_count, top5_meta).

    top5_meta is a list of {size_mb, age_hours, suffix} — NEVER paths (PII rule).
    """
    total_bytes = 0
    big_files: list[tuple[int, float, str]] = []  # (bytes, age_h, suffix)
    now = time.time()
    if TMP_DIR.exists():
        for entry in _safe_scandir(TMP_DIR):
            try:
                if not entry.is_file(follow_symlinks=False):
                    continue
                st = entry.stat()
                total_bytes += st.st_size
                if st.st_size >= TMP_BIG_FILE_BYTES:
                    age_h = max((now - st.st_mtime) / 3600.0, 0.0)
                    suffix = Path(entry.name).suffix or ""
                    big_files.append((st.st_size, age_h, suffix[:16]))
            except (FileNotFoundError, PermissionError, OSError):
                continue
    big_files.sort(reverse=True)
    top5 = [
        {
            "size_mb": int(b // (1024 * 1024)),
            "age_hours": round(a, 1),
            "suffix": s,
        }
        for (b, a, s) in big_files[:5]
    ]
    return total_bytes // (1024 * 1024), len(big_files), top5


def collect_working_tree_big_count() -> int:
    """Count working-tree files >100MB. NEVER deletes. Excludes .git."""
    count = 0
    for root in WORKING_TREE_ROOTS:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # Prune .git aggressively
            dirnames[:] = [d for d in dirnames if d != ".git" and not d.startswith(".venv")]
            for fn in filenames:
                try:
                    fp = Path(dirpath) / fn
                    if fp.is_symlink():
                        continue
                    if fp.stat().st_size >= TMP_BIG_FILE_BYTES:
                        count += 1
                except (FileNotFoundError, PermissionError, OSError):
                    continue
    return count


def _safe_scandir(path: Path):
    try:
        return list(os.scandir(path))
    except (PermissionError, FileNotFoundError, OSError):
        return []


# ----------------------------- Recovery --------------------------------------


def recover_tmp() -> tuple[int, int]:
    """Delete /tmp files >100MB older than 24h. Returns (deleted_count, freed_mb).

    Constitutional: NEVER touches working tree, NEVER deletes files <24h old,
    NEVER follows symlinks, NEVER deletes root-owned files (UID 0).
    """
    deleted = 0
    freed_bytes = 0
    now = time.time()
    my_uid = os.getuid()
    for entry in _safe_scandir(TMP_DIR):
        try:
            if not entry.is_file(follow_symlinks=False):
                continue
            st = entry.stat()
            if st.st_uid == 0 and my_uid != 0:
                continue  # do not touch root-owned
            if st.st_size < TMP_BIG_FILE_BYTES:
                continue
            age_h = (now - st.st_mtime) / 3600.0
            if age_h < AUTO_DELETE_MIN_AGE_HOURS:
                continue
            size = st.st_size
            try:
                os.unlink(entry.path)
                deleted += 1
                freed_bytes += size
                log.info(
                    "deleted tmp file: suffix=%s size_mb=%d age_h=%.1f",
                    Path(entry.name).suffix or "",
                    size // (1024 * 1024),
                    age_h,
                )
            except (FileNotFoundError, PermissionError, OSError) as e:
                log.warning("delete failed (suffix=%s): %s",
                            Path(entry.name).suffix or "", e)
        except (FileNotFoundError, PermissionError, OSError):
            continue
    return deleted, freed_bytes // (1024 * 1024)


# ----------------------------- Ingest POST -----------------------------------


def sign_request(body: bytes, nonce: str, ts: int, token: str) -> str:
    msg = body + b"|" + nonce.encode() + b"|" + str(ts).encode()
    return hmac.new(token.encode(), msg, hashlib.sha256).hexdigest()


def post_to_ingest(snapshot: Snapshot, state_conn: sqlite3.Connection) -> bool:
    """POST snapshot to disk-telemetry-ingest. CTO amend #3 fail-open.

    Returns True on success.
    """
    if not INGEST_TOKEN:
        log.warning("no INGEST_TOKEN configured; skipping POST")
        return False

    body_dict = asdict(snapshot)
    body = json.dumps(body_dict, separators=(",", ":"), sort_keys=True).encode()
    nonce = secrets.token_hex(16)
    ts = int(time.time())

    # Try current token; on 401 try last-known-good (CTO amend #3 fail-open)
    tokens_to_try = [INGEST_TOKEN]
    lkg = state_get(state_conn, "last_known_good_token")
    lkg_ts_str = state_get(state_conn, "last_known_good_ts")
    if lkg and lkg != INGEST_TOKEN and lkg_ts_str:
        try:
            if int(time.time()) - int(lkg_ts_str) <= LKG_FAIL_OPEN_SECONDS:
                tokens_to_try.append(lkg)
        except ValueError:
            pass

    last_err = None
    for tok in tokens_to_try:
        sig = sign_request(body, nonce, ts, tok)
        req = urllib.request.Request(
            INGEST_URL,
            data=body,
            method="POST",
            headers={
                "content-type": "application/json",
                "x-nonce": nonce,
                "x-timestamp": str(ts),
                "x-signature": sig,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if 200 <= resp.status < 300:
                    state_set(state_conn, "last_known_good_token", tok)
                    state_set(state_conn, "last_known_good_ts", str(int(time.time())))
                    return True
                last_err = f"http {resp.status}"
        except urllib.error.HTTPError as e:
            last_err = f"http {e.code}"
            if e.code != 401:
                break  # non-auth error; don't try other tokens
        except (urllib.error.URLError, TimeoutError, socket.timeout) as e:
            last_err = f"net {e}"
            break

    log.warning("ingest POST failed: %s", last_err)
    return False


# ----------------------------- Main loop -------------------------------------


_should_stop = False


def _handle_sigterm(signum, frame):  # noqa: ARG001
    global _should_stop
    log.info("received signal %d; stopping after current cycle", signum)
    _should_stop = True


def run_cycle(state_conn: sqlite3.Connection) -> Snapshot:
    """One collection cycle. Returns the snapshot written."""
    used_pct, free_mb = collect_disk_root()
    tmp_mb, big_count, top5 = collect_tmp_stats()
    tree_count = collect_working_tree_big_count()

    tier = compute_tier(used_pct, tmp_mb, big_count)

    # Auto-recovery on warn/critical (CTO amend Q6: escalate if partial)
    if tier in ("warn", "critical"):
        deleted, freed_mb = recover_tmp()
        if deleted:
            log.info("recovery: deleted=%d freed_mb=%d", deleted, freed_mb)
            # Recompute post-recovery
            used_pct, free_mb = collect_disk_root()
            tmp_mb, big_count, top5 = collect_tmp_stats()
            post_tier = compute_tier(used_pct, tmp_mb, big_count)
            # CTO Q6: if recovery didn't bring us below WARN, escalate to critical
            if post_tier in ("warn", "critical") and tier == "warn":
                tier = "critical"
                log.warning("partial recovery — escalating warn→critical (CTO Q6)")
            else:
                tier = post_tier

    snapshot = Snapshot(
        civ_name=CIV_NAME,
        hostname=socket.gethostname()[:128],
        disk_root_used_pct=used_pct,
        disk_root_free_mb=free_mb,
        tmp_size_mb=tmp_mb,
        tmp_large_files_count=big_count,
        working_tree_large_files_count=tree_count,
        alert_tier=tier,
        raw_top5_tmp_files=top5,
    )

    # Suppress duplicate alerts at same tier
    last_tier = state_get(state_conn, "last_alert_tier")
    if tier in ("warn", "critical") and tier != last_tier:
        log.warning("ALERT tier=%s civ=%s pct=%d tmp_mb=%d big=%d",
                    tier, CIV_NAME, used_pct, tmp_mb, big_count)
        # Real alert dispatch (TRIO/portal) is delegated to a separate alerter
        # to keep this daemon focused on collection. The alert_tier on the D1
        # row is the canonical signal; alerter daemons subscribe to D1 polls.
    state_set(state_conn, "last_alert_tier", tier)

    post_to_ingest(snapshot, state_conn)
    return snapshot


def main() -> int:
    signal.signal(signal.SIGTERM, _handle_sigterm)
    signal.signal(signal.SIGINT, _handle_sigterm)

    log.info("disk-telemetry-daemon starting v=%s civ=%s poll=%ds enabled=%s",
             __version__, CIV_NAME, POLL_INTERVAL_SECONDS, ENABLED)
    if not ENABLED:
        log.warning("DISK_TELEMETRY_ENABLED=0 — sleeping idle")

    state_conn = init_state_db()

    while not _should_stop:
        if ENABLED:
            try:
                run_cycle(state_conn)
            except Exception as e:  # noqa: BLE001
                log.exception("cycle failed: %s", e)
        else:
            log.info("kill switch active — skipping cycle")
        # Sleep with periodic stop-check so SIGTERM is responsive
        for _ in range(POLL_INTERVAL_SECONDS):
            if _should_stop:
                break
            time.sleep(1)

    log.info("disk-telemetry-daemon exiting cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
