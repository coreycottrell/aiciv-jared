"""Unit tests for tools/disk-telemetry-daemon.py.

Run from repo root:
    python3 -m pytest tests/test_disk_telemetry_daemon.py -v
"""
from __future__ import annotations

import hashlib
import hmac
import importlib.util
import os
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DAEMON_PATH = REPO_ROOT / "tools" / "disk-telemetry-daemon.py"


def _load_daemon():
    spec = importlib.util.spec_from_file_location("disk_telemetry_daemon", DAEMON_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["disk_telemetry_daemon"] = mod
    spec.loader.exec_module(mod)
    return mod


# Load module once at import-time so all tests share it.
# FORCE_TIER must NOT be set for tier-calculator tests.
os.environ.pop("DISK_TELEMETRY_FORCE_TIER", None)
daemon = _load_daemon()


# ----------------------------- Tier calculator -------------------------------


@pytest.mark.parametrize(
    "pct,tmp_mb,big_count,expected",
    [
        # info band
        (10, 100, 0, "info"),
        (50, 500, 2, "info"),
        (69, 1000, 4, "info"),
        # warn band
        (70, 0, 0, "warn"),
        (80, 0, 0, "warn"),
        (40, 0, 5, "warn"),     # 5 big files alone
        (40, 0, 10, "warn"),
        # critical band
        (85, 0, 0, "critical"),
        (95, 0, 0, "critical"),
        (50, 2048, 0, "critical"),    # tmp >= 2 GB total
        (50, 5000, 0, "critical"),
        # boundary - critical wins over warn
        (90, 0, 5, "critical"),
    ],
)
def test_compute_tier(pct, tmp_mb, big_count, expected):
    assert daemon.compute_tier(pct, tmp_mb, big_count) == expected


def test_force_tier_override(monkeypatch):
    monkeypatch.setattr(daemon, "FORCE_TIER", "critical")
    assert daemon.compute_tier(10, 0, 0) == "critical"
    monkeypatch.setattr(daemon, "FORCE_TIER", "warn")
    assert daemon.compute_tier(10, 0, 0) == "warn"
    monkeypatch.setattr(daemon, "FORCE_TIER", None)
    assert daemon.compute_tier(10, 0, 0) == "info"


# ----------------------------- HMAC signing ----------------------------------


def test_sign_request_matches_independent_hmac():
    body = b'{"a":1,"b":2}'
    nonce = "deadbeef"
    ts = 1715817600
    token = "supersecrettoken_____64chars_____"
    sig = daemon.sign_request(body, nonce, ts, token)
    expected = hmac.new(
        token.encode(),
        body + b"|" + nonce.encode() + b"|" + str(ts).encode(),
        hashlib.sha256,
    ).hexdigest()
    assert sig == expected


def test_sign_request_different_for_different_body():
    a = daemon.sign_request(b"hello", "n", 1, "k")
    b = daemon.sign_request(b"hellp", "n", 1, "k")
    assert a != b


def test_sign_request_different_for_different_ts():
    a = daemon.sign_request(b"hello", "n", 1, "k")
    b = daemon.sign_request(b"hello", "n", 2, "k")
    assert a != b


def test_sign_request_different_for_different_nonce():
    a = daemon.sign_request(b"hello", "n1", 1, "k")
    b = daemon.sign_request(b"hello", "n2", 1, "k")
    assert a != b


# ----------------------------- Local state ----------------------------------


def test_state_db_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(daemon, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(daemon, "STATE_DB", tmp_path / "state" / "state.db")
    conn = daemon.init_state_db()
    assert daemon.state_get(conn, "missing") is None
    daemon.state_set(conn, "last_alert_tier", "warn")
    assert daemon.state_get(conn, "last_alert_tier") == "warn"
    daemon.state_set(conn, "last_alert_tier", "critical")
    assert daemon.state_get(conn, "last_alert_tier") == "critical"


# ----------------------------- Recovery guards -------------------------------


def test_recover_tmp_skips_fresh_files(tmp_path, monkeypatch):
    fake_tmp = tmp_path / "tmp"
    fake_tmp.mkdir()
    fresh = fake_tmp / "fresh.bin"
    fresh.write_bytes(b"x" * (101 * 1024 * 1024))  # 101 MB
    # Leave mtime = now (fresh)
    monkeypatch.setattr(daemon, "TMP_DIR", fake_tmp)
    deleted, freed = daemon.recover_tmp()
    assert deleted == 0
    assert fresh.exists()


def test_recover_tmp_deletes_old_big_files(tmp_path, monkeypatch):
    fake_tmp = tmp_path / "tmp"
    fake_tmp.mkdir()
    stale = fake_tmp / "stale.bin"
    stale.write_bytes(b"x" * (101 * 1024 * 1024))
    # Make it 48h old
    old = time.time() - 48 * 3600
    os.utime(stale, (old, old))
    monkeypatch.setattr(daemon, "TMP_DIR", fake_tmp)
    deleted, freed = daemon.recover_tmp()
    assert deleted == 1
    assert freed >= 100
    assert not stale.exists()


def test_recover_tmp_ignores_small_files(tmp_path, monkeypatch):
    fake_tmp = tmp_path / "tmp"
    fake_tmp.mkdir()
    small = fake_tmp / "small.bin"
    small.write_bytes(b"x" * 1024)  # 1 KB
    old = time.time() - 72 * 3600
    os.utime(small, (old, old))
    monkeypatch.setattr(daemon, "TMP_DIR", fake_tmp)
    deleted, _ = daemon.recover_tmp()
    assert deleted == 0
    assert small.exists()


# ----------------------------- tmp stats -------------------------------------


def test_collect_tmp_stats_excludes_paths_from_top5(tmp_path, monkeypatch):
    fake_tmp = tmp_path / "tmp"
    fake_tmp.mkdir()
    big = fake_tmp / "secret-customer-name.tar.gz"
    big.write_bytes(b"x" * (110 * 1024 * 1024))
    monkeypatch.setattr(daemon, "TMP_DIR", fake_tmp)
    total_mb, count, top5 = daemon.collect_tmp_stats()
    assert count == 1
    assert len(top5) == 1
    # Constitutional PII rule: no file path leaks
    blob = repr(top5)
    assert "secret-customer-name" not in blob
    # Suffix is OK to expose
    assert top5[0]["suffix"] == ".gz"
    assert top5[0]["size_mb"] >= 109
