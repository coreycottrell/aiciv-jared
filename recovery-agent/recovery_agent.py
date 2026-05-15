#!/usr/bin/env python3
"""
recovery-agent: HTTP daemon for customer-portal recovery on Hetzner hosts.

Bound to 127.0.0.1:9877 only. Cloudflare Tunnel (cloudflared) is the sole
public ingress. Localhost binding survives Tunnel outage as break-glass
(CTO amendment #5).

Exactly ONE meaningful endpoint:  POST /restart
Plus:                              GET  /health   (no auth — for cron + monitors)

Auth: HMAC-SHA256(body, key=RECOVERY_AGENT_HMAC_KEY) with nonce + timestamp
replay protection (CTO amendment #4 — same shape as disk-telemetry).

Action: sudo docker restart <container>. The sudoers file pins the allowed
container names to those in /etc/recovery-agent/allowlist.txt (CTO #1).

Spec: specs/customer-portal-recovery-2026-05-15.md
"""

from __future__ import annotations

import collections
import dataclasses
import hashlib
import hmac
import http.server
import json
import logging
import os
import shutil
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional


# -- Configuration --------------------------------------------------------

BIND_HOST = "127.0.0.1"                                 # CTO #5 — localhost only
BIND_PORT = 9877
ALLOWLIST_PATH = Path("/etc/recovery-agent/allowlist.txt")
LOG_PATH = Path("/var/log/recovery-agent/recovery.jsonl")
TS_WINDOW_SECONDS = 30                                  # CTO #4
NONCE_LRU_MAX = 2048
IDEMPOTENCY_TTL_SECONDS = 60                            # CTO #6
LOOP_WINDOW_SECONDS = 600                               # 10 minutes
LOOP_MAX_RESTARTS = 2                                   # CTO #7 — >2 = stop
DOCKER_BIN = "/usr/bin/docker"
SUDO_BIN = "/usr/bin/sudo"

# Env-overridable for test mode.
HMAC_KEY_ENV = "RECOVERY_AGENT_HMAC_KEY"
TRIO_ALERT_URL_ENV = "RECOVERY_AGENT_TRIO_ALERT_URL"    # optional outbound webhook

log = logging.getLogger("recovery-agent")


# -- Auth: HMAC + nonce + timestamp ---------------------------------------

_NONCE_LRU: collections.OrderedDict[str, float] = collections.OrderedDict()
_NONCE_LOCK = threading.Lock()


def remember_nonce(nonce: str) -> bool:
    """Return True if nonce is fresh; False if replay."""
    with _NONCE_LOCK:
        if nonce in _NONCE_LRU:
            return False
        _NONCE_LRU[nonce] = time.time()
        while len(_NONCE_LRU) > NONCE_LRU_MAX:
            _NONCE_LRU.popitem(last=False)
        return True


def verify_hmac(raw_body: bytes, nonce: str, ts_header: str, sig: str, key: str) -> bool:
    """Verify HMAC over (body|nonce|ts). Constant-time compare. Window-checked."""
    try:
        ts = int(ts_header)
    except (TypeError, ValueError):
        return False
    now = int(time.time())
    if abs(now - ts) > TS_WINDOW_SECONDS:
        return False
    message = b"%s|%s|%d" % (raw_body, nonce.encode("utf-8"), ts)
    expected = hmac.new(key.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig or "")


# -- Allowlist (sudoers-pinned) -------------------------------------------

def load_allowlist() -> set[str]:
    if not ALLOWLIST_PATH.exists():
        return set()
    return {
        line.strip()
        for line in ALLOWLIST_PATH.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


# -- Idempotency + loop detection -----------------------------------------

@dataclasses.dataclass
class CachedResponse:
    body: dict
    ts: float


_IDEMPOTENCY: dict[str, CachedResponse] = {}
_RESTART_HISTORY: dict[str, collections.deque] = {}    # container -> deque[ts]
_STATE_LOCK = threading.Lock()


def get_cached(request_id: str) -> Optional[dict]:
    with _STATE_LOCK:
        entry = _IDEMPOTENCY.get(request_id)
        if entry is None:
            return None
        if time.time() - entry.ts > IDEMPOTENCY_TTL_SECONDS:
            _IDEMPOTENCY.pop(request_id, None)
            return None
        return entry.body


def cache_response(request_id: str, body: dict) -> None:
    with _STATE_LOCK:
        _IDEMPOTENCY[request_id] = CachedResponse(body=body, ts=time.time())
        # Cheap GC.
        cutoff = time.time() - IDEMPOTENCY_TTL_SECONDS
        for k in list(_IDEMPOTENCY.keys()):
            if _IDEMPOTENCY[k].ts < cutoff:
                _IDEMPOTENCY.pop(k, None)


def check_loop(container: str) -> bool:
    """Return True if loop detected (caller should abort + alert)."""
    now = time.time()
    cutoff = now - LOOP_WINDOW_SECONDS
    with _STATE_LOCK:
        hist = _RESTART_HISTORY.setdefault(container, collections.deque(maxlen=16))
        # Drop expired entries.
        while hist and hist[0] < cutoff:
            hist.popleft()
        # Count restarts in window; if already at max, refuse to add another.
        return len(hist) > LOOP_MAX_RESTARTS


def record_restart(container: str) -> None:
    with _STATE_LOCK:
        hist = _RESTART_HISTORY.setdefault(container, collections.deque(maxlen=16))
        hist.append(time.time())


# -- Docker action ---------------------------------------------------------

def docker_restart(container: str, timeout: int = 30) -> tuple[bool, str]:
    """Invoke `sudo docker restart <container>`. Returns (ok, stderr_tail)."""
    if not shutil.which(SUDO_BIN) or not Path(DOCKER_BIN).exists():
        return False, "sudo or docker binary missing"
    cmd = [SUDO_BIN, "-n", DOCKER_BIN, "restart", container]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired:
        return False, "docker restart timeout"
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout)[-400:]
    return True, ""


def docker_stats(container: str, timeout: int = 5) -> tuple[Optional[int], Optional[int]]:
    """Best-effort PID + thread count via `docker top`. Returns (pid_count, thread_count)."""
    if not Path(DOCKER_BIN).exists():
        return None, None
    try:
        proc = subprocess.run(
            [DOCKER_BIN, "top", container, "-eL"],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return None, None
    if proc.returncode != 0:
        return None, None
    lines = proc.stdout.strip().splitlines()
    # First line is header; one row per thread.
    thread_count = max(len(lines) - 1, 0)
    # PID count: distinct PIDs in column 2 (PID) of `docker top -eL`.
    pids: set[str] = set()
    for ln in lines[1:]:
        parts = ln.split()
        if len(parts) >= 2:
            pids.add(parts[1])
    return len(pids) or None, thread_count or None


# -- Audit log (local JSONL — Worker pulls / pushes own row to D1) --------

def audit_write(record: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, separators=(",", ":")) + "\n"
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line)
    except OSError as e:
        log.error("audit write failed: %s", e)


# -- TRIO alert (loop detection only) -------------------------------------

def trio_alert(message: str) -> None:
    url = os.environ.get(TRIO_ALERT_URL_ENV)
    if not url:
        log.warning("TRIO alert webhook not configured; would have sent: %s", message)
        return
    try:
        import urllib.request
        data = json.dumps({"message": message}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"content-type": "application/json"})
        urllib.request.urlopen(req, timeout=5).read()
    except Exception as e:
        log.error("TRIO alert send failed: %s", e)


# -- HTTP layer ------------------------------------------------------------

class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "recovery-agent/1.0"

    # Silence default access logs (we write our own).
    def log_message(self, fmt, *args):  # noqa: A003
        log.debug(fmt, *args)

    def _send_json(self, status: int, body: dict) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.send_header("cache-control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            # Local self-health only. The container-side ai_alive probe lives
            # in health_probe.py and is invoked from the CF Worker via /restart
            # pre-check (Phase 2). Here we only report daemon liveness.
            self._send_json(200, {
                "ok": True,
                "daemon": "recovery-agent",
                "ts": int(time.time()),
            })
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        if self.path != "/restart":
            self._send_json(404, {"error": "not found"})
            return
        self._handle_restart()

    def _handle_restart(self) -> None:
        length = int(self.headers.get("content-length") or 0)
        raw = self.rfile.read(length) if length else b""
        nonce = self.headers.get("x-nonce") or ""
        ts = self.headers.get("x-timestamp") or ""
        sig = self.headers.get("x-signature") or ""

        key = os.environ.get(HMAC_KEY_ENV)
        if not key:
            self._send_json(500, {"error": "agent misconfigured: missing HMAC key"})
            return
        if not nonce or not ts or not sig:
            self._send_json(401, {"error": "missing auth headers"})
            return
        if not verify_hmac(raw, nonce, ts, sig, key):
            self._send_json(401, {"error": "bad signature or timestamp out of window"})
            return
        if not remember_nonce(nonce):
            self._send_json(401, {"error": "nonce replay"})
            return

        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "bad json"})
            return

        container = body.get("container_name")
        reason = body.get("reason") or ""
        request_id = body.get("request_id") or ""
        if not isinstance(container, str) or not container or len(container) > 128:
            self._send_json(400, {"error": "missing or bad container_name"})
            return
        if not isinstance(request_id, str) or not request_id or len(request_id) > 128:
            self._send_json(400, {"error": "missing request_id"})
            return

        # CTO #6 — idempotency.
        cached = get_cached(request_id)
        if cached is not None:
            self._send_json(200, {**cached, "cached": True})
            return

        allowlist = load_allowlist()
        if container not in allowlist:
            self._send_json(403, {"error": f"container not in allowlist: {container}"})
            return

        # CTO #7 — loop detection BEFORE we restart.
        if check_loop(container):
            trio_alert(
                f"[recovery-agent] loop detected for {container} "
                f"(>2 restarts in {LOOP_WINDOW_SECONDS}s) — refusing further restarts"
            )
            audit_write({
                "ts": int(time.time()),
                "container": container,
                "reason": reason,
                "request_id": request_id,
                "outcome": "failed",
                "error": "loop_detected",
            })
            self._send_json(429, {
                "ok": False,
                "error": "loop_detected",
                "loop_detected": True,
                "message": f">{LOOP_MAX_RESTARTS} restarts within {LOOP_WINDOW_SECONDS}s window",
            })
            return

        # Capture before-stats.
        pid_before, thr_before = docker_stats(container)
        started = time.time()

        ok, errmsg = docker_restart(container)
        duration_ms = int((time.time() - started) * 1000)

        # Give the container a beat to settle before measuring after-stats.
        time.sleep(1.0)
        pid_after, thr_after = docker_stats(container) if ok else (None, None)

        if ok:
            record_restart(container)

        response = {
            "ok": ok,
            "restart_id": request_id,
            "container": container,
            "duration_ms": duration_ms,
            "pid_count_before": pid_before,
            "pid_count_after": pid_after,
            "thread_count_before": thr_before,
            "thread_count_after": thr_after,
            "ai_alive_after": None,    # populated by health_probe.py in Phase 2
            "outcome": "success" if ok else "failed",
            "error_message": errmsg or None,
        }
        cache_response(request_id, response)
        audit_write({
            "ts": int(time.time()),
            "container": container,
            "reason": reason,
            "request_id": request_id,
            "outcome": response["outcome"],
            "duration_ms": duration_ms,
            "pid_before": pid_before,
            "pid_after": pid_after,
            "thread_before": thr_before,
            "thread_after": thr_after,
            "error": errmsg or None,
        })
        self._send_json(200 if ok else 500, response)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def serve(host: str = BIND_HOST, port: int = BIND_PORT) -> None:
    logging.basicConfig(
        level=os.environ.get("RECOVERY_AGENT_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    if not os.environ.get(HMAC_KEY_ENV):
        log.error(
            "%s not set in environment — refusing to start. "
            "Configure systemd EnvironmentFile.", HMAC_KEY_ENV,
        )
        sys.exit(2)
    log.info("recovery-agent listening on %s:%d", host, port)
    with ThreadedHTTPServer((host, port), Handler) as srv:
        srv.serve_forever()


if __name__ == "__main__":
    serve()
