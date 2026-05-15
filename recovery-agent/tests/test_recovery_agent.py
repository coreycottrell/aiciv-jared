"""
Tests for recovery-agent (stdlib unittest only — no extra deps).

Coverage:
  - HMAC validation (good sig, bad sig, missing headers, replay, ts window)
  - Allowlist enforcement (not-allowlisted -> 403)
  - Idempotency cache (same request_id -> cached=True)
  - Loop detection (>2 restarts in window -> 429, loop_detected=true, TRIO alerted)

Docker calls are monkey-patched so tests run on any dev box without docker.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

# Make recovery_agent importable when run from repo root or recovery-agent/.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import recovery_agent as ra   # noqa: E402


TEST_HMAC_KEY = "test-key-supercalifragilistic"
TEST_PORT = 19877            # avoid clashing with real daemon


def _sign(body: bytes, nonce: str, ts: int, key: str = TEST_HMAC_KEY) -> str:
    msg = b"%s|%s|%d" % (body, nonce.encode(), ts)
    return hmac.new(key.encode(), msg, hashlib.sha256).hexdigest()


def _post(path: str, body: dict, headers: dict | None = None) -> tuple[int, dict]:
    raw = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{TEST_PORT}{path}",
        data=raw,
        method="POST",
        headers=headers or {},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=2)
        return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def _get(path: str) -> tuple[int, dict]:
    req = urllib.request.Request(f"http://127.0.0.1:{TEST_PORT}{path}", method="GET")
    try:
        resp = urllib.request.urlopen(req, timeout=2)
        return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


class RecoveryAgentTests(unittest.TestCase):
    server: ra.ThreadedHTTPServer | None = None
    server_thread: threading.Thread | None = None

    @classmethod
    def setUpClass(cls) -> None:
        os.environ[ra.HMAC_KEY_ENV] = TEST_HMAC_KEY
        cls.server = ra.ThreadedHTTPServer(("127.0.0.1", TEST_PORT), ra.Handler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        # Give socket a beat.
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.server is not None:
            cls.server.shutdown()
            cls.server.server_close()

    def setUp(self) -> None:
        # Reset module-level caches between tests.
        ra._NONCE_LRU.clear()
        ra._IDEMPOTENCY.clear()
        ra._RESTART_HISTORY.clear()
        # Allowlist: whitehurst yes, gary no.
        self.allow_patch = mock.patch.object(ra, "load_allowlist", return_value={"whitehurst"})
        self.allow_patch.start()
        # docker_restart succeeds by default; docker_stats returns predictable stats.
        self.restart_patch = mock.patch.object(ra, "docker_restart", return_value=(True, ""))
        self.stats_patch = mock.patch.object(ra, "docker_stats", return_value=(7, 42))
        self.audit_patch = mock.patch.object(ra, "audit_write")
        self.trio_patch = mock.patch.object(ra, "trio_alert")
        self.mock_restart = self.restart_patch.start()
        self.mock_stats = self.stats_patch.start()
        self.mock_audit = self.audit_patch.start()
        self.mock_trio = self.trio_patch.start()
        # Speed up loop-window tests.
        self._orig_loop_window = ra.LOOP_WINDOW_SECONDS
        self._orig_sleep = ra.time.sleep
        ra.time.sleep = lambda *_a, **_kw: None       # skip the post-restart settle wait

    def tearDown(self) -> None:
        self.allow_patch.stop()
        self.restart_patch.stop()
        self.stats_patch.stop()
        self.audit_patch.stop()
        self.trio_patch.stop()
        ra.LOOP_WINDOW_SECONDS = self._orig_loop_window
        ra.time.sleep = self._orig_sleep

    # -- /health --------------------------------------------------------

    def test_health_endpoint(self):
        status, body = _get("/health")
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(body["daemon"], "recovery-agent")

    # -- HMAC -----------------------------------------------------------

    def _signed_post(self, payload: dict, *, nonce: str = "n-1", ts: int | None = None,
                     key: str = TEST_HMAC_KEY, mangle_sig: bool = False) -> tuple[int, dict]:
        ts = ts if ts is not None else int(time.time())
        raw = json.dumps(payload).encode("utf-8")
        sig = _sign(raw, nonce, ts, key)
        if mangle_sig:
            sig = "0" * len(sig)
        headers = {
            "content-type": "application/json",
            "x-nonce": nonce,
            "x-timestamp": str(ts),
            "x-signature": sig,
            "content-length": str(len(raw)),
        }
        req = urllib.request.Request(
            f"http://127.0.0.1:{TEST_PORT}/restart", data=raw, method="POST", headers=headers,
        )
        try:
            resp = urllib.request.urlopen(req, timeout=2)
            return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def test_missing_auth_headers_rejected(self):
        status, body = _post("/restart", {"container_name": "whitehurst", "request_id": "r1"})
        self.assertEqual(status, 401)
        self.assertIn("missing auth", body["error"])

    def test_bad_signature_rejected(self):
        status, body = self._signed_post(
            {"container_name": "whitehurst", "request_id": "r1"}, mangle_sig=True,
        )
        self.assertEqual(status, 401)
        self.assertIn("bad signature", body["error"])

    def test_timestamp_out_of_window_rejected(self):
        old_ts = int(time.time()) - (ra.TS_WINDOW_SECONDS + 60)
        status, body = self._signed_post(
            {"container_name": "whitehurst", "request_id": "r1"}, ts=old_ts,
        )
        self.assertEqual(status, 401)
        self.assertIn("bad signature", body["error"])     # signature check fails on stale ts

    def test_nonce_replay_rejected(self):
        payload = {"container_name": "whitehurst", "request_id": "r-replay-1"}
        s1, b1 = self._signed_post(payload, nonce="n-replay")
        self.assertEqual(s1, 200, b1)
        # Same nonce a second time -> replay.
        s2, b2 = self._signed_post(payload, nonce="n-replay")
        self.assertEqual(s2, 401)
        self.assertIn("replay", b2["error"])

    # -- Allowlist ------------------------------------------------------

    def test_container_not_in_allowlist_forbidden(self):
        status, body = self._signed_post(
            {"container_name": "gary", "request_id": "r-allow-1"},
        )
        self.assertEqual(status, 403)
        self.assertIn("allowlist", body["error"])
        # docker_restart MUST NOT have been called.
        self.mock_restart.assert_not_called()

    # -- Idempotency ----------------------------------------------------

    def test_idempotent_request_returns_cached(self):
        payload = {"container_name": "whitehurst", "request_id": "r-idem-1"}
        s1, b1 = self._signed_post(payload, nonce="n-idem-a")
        self.assertEqual(s1, 200, b1)
        self.assertTrue(b1["ok"])
        self.assertNotIn("cached", b1)
        # Same request_id, fresh nonce -> served from cache, no restart.
        self.mock_restart.reset_mock()
        s2, b2 = self._signed_post(payload, nonce="n-idem-b")
        self.assertEqual(s2, 200, b2)
        self.assertTrue(b2.get("cached"))
        self.mock_restart.assert_not_called()

    # -- Loop detection -------------------------------------------------

    def test_loop_detection_blocks_after_max(self):
        # 1st restart
        s, b = self._signed_post(
            {"container_name": "whitehurst", "request_id": "loop-1"}, nonce="loop-n-1",
        )
        self.assertEqual(s, 200, b)
        # 2nd restart
        s, b = self._signed_post(
            {"container_name": "whitehurst", "request_id": "loop-2"}, nonce="loop-n-2",
        )
        self.assertEqual(s, 200, b)
        # 3rd restart — still within max (>2 means strictly greater)
        s, b = self._signed_post(
            {"container_name": "whitehurst", "request_id": "loop-3"}, nonce="loop-n-3",
        )
        self.assertEqual(s, 200, b)
        # 4th restart triggers loop detection
        s, b = self._signed_post(
            {"container_name": "whitehurst", "request_id": "loop-4"}, nonce="loop-n-4",
        )
        self.assertEqual(s, 429)
        self.assertTrue(b["loop_detected"])
        self.mock_trio.assert_called()                  # TRIO alerted
        # docker_restart was NOT called for the 4th (loop-detected) attempt.
        self.assertEqual(self.mock_restart.call_count, 3)


class HmacUnitTests(unittest.TestCase):
    """Pure-function tests for verify_hmac — no HTTP."""

    def test_good_signature(self):
        body = b'{"x":1}'
        nonce = "n1"
        ts = int(time.time())
        sig = _sign(body, nonce, ts)
        self.assertTrue(ra.verify_hmac(body, nonce, str(ts), sig, TEST_HMAC_KEY))

    def test_bad_signature(self):
        body = b'{"x":1}'
        nonce = "n1"
        ts = int(time.time())
        self.assertFalse(ra.verify_hmac(body, nonce, str(ts), "deadbeef", TEST_HMAC_KEY))

    def test_stale_ts(self):
        body = b'{"x":1}'
        nonce = "n1"
        ts = int(time.time()) - (ra.TS_WINDOW_SECONDS + 60)
        sig = _sign(body, nonce, ts)
        self.assertFalse(ra.verify_hmac(body, nonce, str(ts), sig, TEST_HMAC_KEY))


if __name__ == "__main__":
    unittest.main()
