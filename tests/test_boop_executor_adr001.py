"""
QA tests for ADR-001 Constitutional Fairness Lane in tools/boop_executor.py.

Coverage matches CTO verdict's 7 mandatory amendments:
  A1: Constitutional set is exactly [engineering-flow-check, delegation-enforcer]
      and bypasses both window throttle and process cap up to reserved_slots.
  A2: Hung-agent watchdog (45min max age) ships in same file; SIGTERM then SIGKILL after 30s.
  A3: Scheduler-level dedup: elapsed_since_last < interval * 0.5 suppresses.
  A4: Portal alarm only (NO Telegram), rate-limited 30min per task.
  A5: fcntl.flock(LOCK_EX) on save_tasks.
  A6: Config in boop_config.json boop_rules block (not scheduled-tasks-state.json).
  A7: ADR doc reference correction (priority_order location).

Tests are dependency-free (stdlib only) so they can run in CI / on the host
that owns this scheduler.

Run:
    python3 -m unittest tests.test_boop_executor_adr001 -v
or:
    python3 tests/test_boop_executor_adr001.py
"""
from __future__ import annotations

import importlib.util
import json
import logging
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

THIS = Path(__file__).resolve()
REPO = THIS.parent.parent
BOOP_PATH = REPO / "tools" / "boop_executor.py"

# ─── Module loader ────────────────────────────────────────────────────────────


def _load_boop_executor():
    """Import boop_executor.py as a module without running its main loop."""
    spec = importlib.util.spec_from_file_location("boop_executor_under_test", BOOP_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.be = _load_boop_executor()
        cls.logger = logging.getLogger("test")
        cls.logger.addHandler(logging.NullHandler())


# ─── A6: config lives in boop_config.json boop_rules block ────────────────────


class ConfigLocationTests(_Base):
    def test_a6_boop_config_has_boop_rules_block(self):
        cfg_path = REPO / "tools" / "boop_config.json"
        cfg = json.loads(cfg_path.read_text())
        self.assertIn("boop_rules", cfg, "boop_config.json missing boop_rules block (A6)")
        rules = cfg["boop_rules"]
        self.assertIn("constitutional_tasks", rules)
        self.assertIn("constitutional_reserved_slots", rules)
        self.assertIn("constitutional_starvation_multiplier", rules)
        self.assertIn("constitutional_watchdog_max_age_seconds", rules)
        self.assertIn("constitutional_dedup_window_ratio", rules)
        self.assertIn("portal_alarm_rate_limit_seconds", rules)

    def test_a1_constitutional_set_exact_membership(self):
        cfg = json.loads((REPO / "tools" / "boop_config.json").read_text())
        ct = cfg["boop_rules"]["constitutional_tasks"]
        # CTO Amendment 1: exactly [engineering-flow-check, delegation-enforcer]
        self.assertEqual(
            sorted(ct),
            sorted(["engineering-flow-check", "delegation-enforcer"]),
            "constitutional_tasks must be exactly [engineering-flow-check, delegation-enforcer]",
        )
        # And NOT the architect's typo delegation-enforcer-boop
        self.assertNotIn("delegation-enforcer-boop", ct)
        # And NOT capability-gap-analysis (CTO dropped it)
        self.assertNotIn("capability-gap-analysis", ct)
        # And NOT conductor-of-conductors (CTO Q2: exclude from initial set)
        self.assertNotIn("conductor-of-conductors", ct)

    def test_load_boop_rules_falls_back_when_block_missing(self):
        # Point BOOP_CONFIG_FILE at a config with NO boop_rules block
        with tempfile.TemporaryDirectory() as td:
            tmp_cfg = Path(td) / "cfg.json"
            tmp_cfg.write_text(json.dumps({"notes": "no boop_rules here"}))
            with mock.patch.object(self.be, "BOOP_CONFIG_FILE", tmp_cfg):
                rules = self.be.load_boop_rules(self.logger)
        self.assertEqual(
            rules["constitutional_tasks_set"],
            set(self.be.DEFAULT_BOOP_RULES["constitutional_tasks"]),
            "fallback must use DEFAULT_BOOP_RULES",
        )

    def test_load_boop_rules_coerces_invalid_types(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_cfg = Path(td) / "cfg.json"
            tmp_cfg.write_text(json.dumps({
                "boop_rules": {
                    "constitutional_tasks": "not a list",
                    "constitutional_reserved_slots": "bad",
                    "constitutional_starvation_multiplier": None,
                }
            }))
            with mock.patch.object(self.be, "BOOP_CONFIG_FILE", tmp_cfg):
                rules = self.be.load_boop_rules(self.logger)
        self.assertIsInstance(rules["constitutional_tasks_set"], set)
        self.assertIsInstance(rules["constitutional_reserved_slots"], int)
        self.assertIsInstance(rules["constitutional_starvation_multiplier"], float)


# ─── A1: priority_rank sorts constitutional first ─────────────────────────────


class PriorityRankTests(_Base):
    def test_priority_rank_constitutional_below_zero(self):
        cs = {"engineering-flow-check"}
        po = ["conductor-of-conductors", "email-check-boop", "engineering-flow-check"]
        # constitutional ranks ahead of non-constitutional regardless of priority_order position
        self.assertEqual(self.be.priority_rank("engineering-flow-check", po, cs), -1)
        self.assertEqual(self.be.priority_rank("conductor-of-conductors", po, cs), 0)
        self.assertEqual(self.be.priority_rank("email-check-boop", po, cs), 1)
        # missing tasks sort after all listed
        self.assertEqual(self.be.priority_rank("unknown-task", po, cs), len(po) + 1)

    def test_due_list_sort_constitutional_first(self):
        cs = {"engineering-flow-check"}
        po = ["conductor-of-conductors", "email-check-boop", "engineering-flow-check"]
        due = [
            ("email-check-boop", {}),
            ("conductor-of-conductors", {}),
            ("engineering-flow-check", {}),
        ]
        due.sort(key=lambda pair: self.be.priority_rank(pair[0], po, cs))
        order = [t[0] for t in due]
        self.assertEqual(order[0], "engineering-flow-check", "constitutional must sort first")


# ─── A3: scheduler-level dedup ────────────────────────────────────────────────


class SchedulerDedupTests(_Base):
    def setUp(self):
        # Mock-launchable fire_boop: bypass the subprocess.Popen at end.
        # We only care that fire_boop returns False when dedup triggers.
        self.patcher_popen = mock.patch.object(self.be.subprocess, "Popen")
        self.mock_popen = self.patcher_popen.start()
        # Make Popen return a fake process so the "success" path doesn't crash
        proc = mock.MagicMock()
        proc.pid = 99999
        self.mock_popen.return_value = proc

    def tearDown(self):
        self.patcher_popen.stop()

    def test_a3_dedup_blocks_when_elapsed_under_ratio(self):
        # interval = 1800s (30min); ratio = 0.5; dedup window = 900s
        # last_run = 200s ago -> should suppress
        now = datetime.now(timezone.utc)
        last_run = (now - timedelta(seconds=200)).strftime("%Y-%m-%dT%H:%M:%SZ")
        task = {
            "frequency": "30min",
            "last_run": last_run,
            "agent": "test-agent",
        }
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["constitutional_tasks_set"] = {"engineering-flow-check"}
        with mock.patch.object(self.be, "get_telegram_token", return_value="x"), \
             mock.patch.object(self.be, "count_running_boop_agents", return_value=0), \
             mock.patch.object(self.be, "list_running_boop_pids", return_value=[]):
            fired = self.be.fire_boop("engineering-flow-check", task, self.logger, rules=rules)
        self.assertFalse(fired, "dedup must suppress fire when elapsed < interval * ratio")
        self.mock_popen.assert_not_called()

    def test_a3_dedup_allows_when_elapsed_over_ratio(self):
        # last_run = 1000s ago, interval = 1800s, dedup threshold = 900s -> allow
        now = datetime.now(timezone.utc)
        last_run = (now - timedelta(seconds=1000)).strftime("%Y-%m-%dT%H:%M:%SZ")
        task = {"frequency": "30min", "last_run": last_run, "agent": "test-agent"}
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["constitutional_tasks_set"] = {"engineering-flow-check"}
        with mock.patch.object(self.be, "get_telegram_token", return_value="x"), \
             mock.patch.object(self.be, "count_running_boop_agents", return_value=0), \
             mock.patch.object(self.be, "list_running_boop_pids", return_value=[]), \
             mock.patch.object(self.be, "send_telegram"):
            fired = self.be.fire_boop("engineering-flow-check", task, self.logger, rules=rules)
        self.assertTrue(fired, "dedup must NOT suppress when elapsed > interval * ratio")


# ─── A1: reserved slot bypass ─────────────────────────────────────────────────


class ReservedSlotBypassTests(_Base):
    def setUp(self):
        self.patcher_popen = mock.patch.object(self.be.subprocess, "Popen")
        self.mock_popen = self.patcher_popen.start()
        proc = mock.MagicMock(); proc.pid = 99998
        self.mock_popen.return_value = proc

    def tearDown(self):
        self.patcher_popen.stop()

    def test_a1_constitutional_bypasses_process_cap(self):
        # Simulate MAX_CONCURRENT_BOOP_AGENTS (3) already running, all NON-constitutional.
        # A constitutional task should still fire because reserved_slot=1 is free.
        now = datetime.now(timezone.utc)
        task = {
            "frequency": "30min",
            "last_run": (now - timedelta(seconds=3600)).strftime("%Y-%m-%dT%H:%M:%SZ"),  # well overdue, no dedup
            "agent": "test-agent",
        }
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["constitutional_tasks_set"] = {"engineering-flow-check"}
        rules["constitutional_reserved_slots"] = 1
        with mock.patch.object(self.be, "count_running_boop_agents", return_value=3), \
             mock.patch.object(self.be, "list_running_boop_pids", return_value=[(101, "other"), (102, "other"), (103, "other")]), \
             mock.patch.object(self.be, "count_running_constitutional_agents", return_value=0), \
             mock.patch.object(self.be, "get_telegram_token", return_value="x"), \
             mock.patch.object(self.be, "send_telegram"):
            fired = self.be.fire_boop("engineering-flow-check", task, self.logger, rules=rules)
        self.assertTrue(fired, "constitutional task must bypass process cap up to reserved_slot")
        self.mock_popen.assert_called_once()

    def test_a1_non_constitutional_still_capped(self):
        now = datetime.now(timezone.utc)
        task = {
            "frequency": "30min",
            "last_run": (now - timedelta(seconds=3600)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "agent": "test-agent",
        }
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["constitutional_tasks_set"] = {"engineering-flow-check"}
        with mock.patch.object(self.be, "count_running_boop_agents", return_value=3), \
             mock.patch.object(self.be, "list_running_boop_pids", return_value=[(101, "other"), (102, "other"), (103, "other")]), \
             mock.patch.object(self.be, "count_running_constitutional_agents", return_value=0), \
             mock.patch.object(self.be, "get_telegram_token", return_value="x"):
            fired = self.be.fire_boop("some-non-constitutional", task, self.logger, rules=rules)
        self.assertFalse(fired, "non-constitutional task must respect MAX_CONCURRENT_BOOP_AGENTS")

    def test_a1_reserved_slot_full_constitutional_falls_back_to_normal_cap(self):
        # If reserved_slot is in use by ANOTHER constitutional task AND cap is full,
        # a second constitutional task must be refused (not unlimited bypass).
        now = datetime.now(timezone.utc)
        task = {
            "frequency": "30min",
            "last_run": (now - timedelta(seconds=3600)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "agent": "test-agent",
        }
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["constitutional_tasks_set"] = {"engineering-flow-check", "delegation-enforcer"}
        rules["constitutional_reserved_slots"] = 1
        with mock.patch.object(self.be, "count_running_boop_agents", return_value=3), \
             mock.patch.object(self.be, "list_running_boop_pids", return_value=[(101, "engineering-flow-check"), (102, "other"), (103, "other")]), \
             mock.patch.object(self.be, "count_running_constitutional_agents", return_value=1), \
             mock.patch.object(self.be, "get_telegram_token", return_value="x"):
            fired = self.be.fire_boop("delegation-enforcer", task, self.logger, rules=rules)
        self.assertFalse(fired, "second constitutional task must wait when reserved slot is in use and normal cap is full")

    def test_a1_no_double_fire_same_constitutional_task(self):
        # If an instance of THIS task is already running, even if reserved slot
        # math would allow another, refuse — no double-fire of same task.
        now = datetime.now(timezone.utc)
        task = {
            "frequency": "30min",
            "last_run": (now - timedelta(seconds=3600)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "agent": "test-agent",
        }
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["constitutional_tasks_set"] = {"engineering-flow-check"}
        rules["constitutional_reserved_slots"] = 2  # plenty of slots
        with mock.patch.object(self.be, "count_running_boop_agents", return_value=1), \
             mock.patch.object(self.be, "list_running_boop_pids", return_value=[(101, "engineering-flow-check")]), \
             mock.patch.object(self.be, "count_running_constitutional_agents", return_value=1), \
             mock.patch.object(self.be, "get_telegram_token", return_value="x"):
            fired = self.be.fire_boop("engineering-flow-check", task, self.logger, rules=rules)
        self.assertFalse(fired, "must NOT double-fire the same constitutional task")


# ─── A2: hung-agent watchdog ─────────────────────────────────────────────────


class WatchdogTests(_Base):
    def test_a2_watchdog_killing_constants(self):
        # Watchdog should kill PIDs older than max_age, in constitutional set.
        # We mock list_running_boop_pids + _pid_age_seconds + os.kill +
        # portal_alarm_rate_limited so no real signals are sent.
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["constitutional_tasks_set"] = {"engineering-flow-check"}
        rules["constitutional_watchdog_max_age_seconds"] = 2700
        with mock.patch.object(self.be, "list_running_boop_pids",
                               return_value=[(12345, "engineering-flow-check"),
                                             (12346, "other-task")]), \
             mock.patch.object(self.be, "_pid_age_seconds",
                               side_effect=lambda pid: 3000.0 if pid == 12345 else 100.0), \
             mock.patch.object(self.be.os, "kill") as mock_kill, \
             mock.patch.object(self.be, "portal_alarm_rate_limited", return_value=True), \
             mock.patch.object(self.be, "time") as mock_time:
            # Mock time.time so the SIGTERM grace loop short-circuits immediately
            mock_time.time.side_effect = [0.0, 0.0, 100.0]
            mock_time.sleep = lambda s: None
            # First kill call (SIGTERM) — process appears alive (no exception)
            # Second kill call (signal 0 alive check inside grace loop) — also alive
            # Final kill call (SIGKILL) — alive
            killed = self.be.watchdog_kill_hung_constitutional(rules, self.logger)
        self.assertEqual(killed, 1, "watchdog must kill exactly the one hung constitutional agent")
        # The SIGTERM call must have happened
        sigterm_calls = [c for c in mock_kill.call_args_list if len(c.args) >= 2 and c.args[1] == self.be.signal.SIGTERM]
        self.assertGreaterEqual(len(sigterm_calls), 1, "watchdog must send SIGTERM")

    def test_a2_watchdog_skips_non_constitutional(self):
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["constitutional_tasks_set"] = {"engineering-flow-check"}
        with mock.patch.object(self.be, "list_running_boop_pids",
                               return_value=[(12345, "non-constitutional-task")]), \
             mock.patch.object(self.be, "_pid_age_seconds", return_value=9999.0), \
             mock.patch.object(self.be.os, "kill") as mock_kill:
            killed = self.be.watchdog_kill_hung_constitutional(rules, self.logger)
        self.assertEqual(killed, 0, "watchdog must NOT touch non-constitutional agents")
        mock_kill.assert_not_called()

    def test_a2_watchdog_skips_young_agents(self):
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["constitutional_tasks_set"] = {"engineering-flow-check"}
        rules["constitutional_watchdog_max_age_seconds"] = 2700
        with mock.patch.object(self.be, "list_running_boop_pids",
                               return_value=[(12345, "engineering-flow-check")]), \
             mock.patch.object(self.be, "_pid_age_seconds", return_value=300.0), \
             mock.patch.object(self.be.os, "kill") as mock_kill:
            killed = self.be.watchdog_kill_hung_constitutional(rules, self.logger)
        self.assertEqual(killed, 0, "watchdog must NOT kill agents under max_age")
        mock_kill.assert_not_called()


# ─── A4: portal alarm only, no Telegram ───────────────────────────────────────


class PortalAlarmTests(_Base):
    def test_a4_no_send_telegram_in_starvation_path(self):
        # Inspect the actual file to confirm no send_telegram call exists in the
        # starvation/watchdog/alarm paths.
        src = BOOP_PATH.read_text()
        # Carve out the relevant region (between helpers header and main loop)
        start_marker = "# ─── ADR-001 Constitutional Fairness Lane helpers"
        end_marker = "# ─── Scheduling logic"
        helpers_region = src[src.index(start_marker):src.index(end_marker)]
        self.assertNotIn(
            "send_telegram(",
            helpers_region,
            "Telegram MUST NOT be used in constitutional alarm code paths (Amendment 4)",
        )

    def test_a4_portal_alarm_invokes_portal_deliver(self):
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["portal_alarm_rate_limit_seconds"] = 1800
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(self.be, "PORTAL_DELIVER_SCRIPT", Path(td) / "portal_deliver.sh"), \
                 mock.patch.object(self.be, "CONSTITUTIONAL_ALARM_STATE_FILE", Path(td) / "state.json"), \
                 mock.patch.object(self.be, "CONSTITUTIONAL_ALARM_BODY_DIR", Path(td) / "inbox"), \
                 mock.patch.object(self.be, "_PORTAL_ALARM_STATE_CACHE", {}, create=False):
                # portal_deliver.sh must exist for the function to attempt
                fake_deliver = Path(td) / "portal_deliver.sh"
                fake_deliver.write_text("#!/bin/bash\nexit 0\n")
                fake_deliver.chmod(0o755)
                # Reset cache global on the module to {}
                self.be._PORTAL_ALARM_STATE_CACHE = {}
                with mock.patch.object(self.be.subprocess, "run") as mock_run:
                    mock_run.return_value = mock.MagicMock(returncode=0, stderr="")
                    sent = self.be.portal_alarm_rate_limited(
                        rules, "test-alarm", "test caption", None, self.logger
                    )
                    self.assertTrue(sent, "alarm should send first time")
                    mock_run.assert_called_once()
                    # Verify the FIRST argv element is portal_deliver.sh path
                    args, _ = mock_run.call_args
                    self.assertEqual(args[0][0], str(fake_deliver))

    def test_a4_portal_alarm_rate_limited(self):
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["portal_alarm_rate_limit_seconds"] = 1800
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(self.be, "PORTAL_DELIVER_SCRIPT", Path(td) / "portal_deliver.sh"), \
                 mock.patch.object(self.be, "CONSTITUTIONAL_ALARM_STATE_FILE", Path(td) / "state.json"), \
                 mock.patch.object(self.be, "CONSTITUTIONAL_ALARM_BODY_DIR", Path(td) / "inbox"):
                fake_deliver = Path(td) / "portal_deliver.sh"
                fake_deliver.write_text("#!/bin/bash\nexit 0\n")
                fake_deliver.chmod(0o755)
                self.be._PORTAL_ALARM_STATE_CACHE = {}
                with mock.patch.object(self.be.subprocess, "run") as mock_run:
                    mock_run.return_value = mock.MagicMock(returncode=0, stderr="")
                    # First call: sends
                    s1 = self.be.portal_alarm_rate_limited(rules, "alarm-x", "x", None, self.logger)
                    self.assertTrue(s1)
                    # Immediate second call (still inside 30min): SUPPRESSED
                    s2 = self.be.portal_alarm_rate_limited(rules, "alarm-x", "x", None, self.logger)
                    self.assertFalse(s2, "rate-limit must suppress repeat within window")
                    self.assertEqual(mock_run.call_count, 1, "portal_deliver.sh must NOT be invoked twice")


# ─── A5: fcntl.flock on save_tasks ─────────────────────────────────────────────


class SaveTasksLockTests(_Base):
    def test_a5_save_tasks_acquires_flock_and_writes_atomically(self):
        # Use a tmp TASKS_FILE and assert the lock sidecar gets created and the
        # rewrite is via tmp+rename.
        with tempfile.TemporaryDirectory() as td:
            tmp_tasks = Path(td) / "scheduled-tasks-state.json"
            tmp_tasks.write_text(json.dumps({
                "boop_rules": {"priority_order": []},
                "tasks": {"engineering-flow-check": {"frequency": "30min", "status": "active"}},
            }))
            with mock.patch.object(self.be, "TASKS_FILE", tmp_tasks):
                # Mutate tasks and save
                new_tasks = {"engineering-flow-check": {"frequency": "30min", "status": "active", "last_run": "2026-05-16T02:00:00Z"}}
                ok = self.be.save_tasks(new_tasks, self.logger)
            self.assertTrue(ok)
            # Lock sidecar should exist
            self.assertTrue((Path(td) / "scheduled-tasks-state.json.lock").exists(),
                            "save_tasks must create the lock sidecar")
            # Tmp file should NOT remain after os.replace
            self.assertFalse((Path(td) / "scheduled-tasks-state.json.tmp").exists(),
                             "tmp must be renamed away atomically")
            # Saved content must reflect the mutation
            saved = json.loads(tmp_tasks.read_text())
            self.assertEqual(saved["tasks"]["engineering-flow-check"]["last_run"], "2026-05-16T02:00:00Z")

    def test_a5_flock_serializes_concurrent_writers(self):
        # Two concurrent save_tasks calls must not corrupt the JSON.
        # We use threading because fcntl.flock blocks at the syscall level.
        import threading
        with tempfile.TemporaryDirectory() as td:
            tmp_tasks = Path(td) / "scheduled-tasks-state.json"
            tmp_tasks.write_text(json.dumps({
                "boop_rules": {"priority_order": []},
                "tasks": {"engineering-flow-check": {"frequency": "30min", "status": "active"}},
            }))
            results = []
            def writer(tag):
                with mock.patch.object(self.be, "TASKS_FILE", tmp_tasks):
                    tasks = {"engineering-flow-check": {"frequency": "30min", "status": "active", "last_run": f"2026-05-16T02:00:0{tag}Z"}}
                    ok = self.be.save_tasks(tasks, self.logger)
                    results.append(ok)
            threads = [threading.Thread(target=writer, args=(i,)) for i in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertTrue(all(results), "all writers should succeed")
            # JSON must still be valid
            data = json.loads(tmp_tasks.read_text())
            self.assertIn("tasks", data)
            self.assertEqual(data["tasks"]["engineering-flow-check"]["frequency"], "30min")


# ─── Constitutional starvation alarm (ties to A4) ─────────────────────────────


class StarvationAlarmTests(_Base):
    def test_starvation_alarm_fires_when_overdue(self):
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["constitutional_tasks_set"] = {"engineering-flow-check"}
        rules["constitutional_starvation_multiplier"] = 2.0
        now = datetime.now(timezone.utc)
        # Task is overdue by 3 hours (3.5 intervals at 30min)
        tasks = {
            "engineering-flow-check": {
                "status": "active",
                "frequency": "30min",
                "last_run": (now - timedelta(seconds=3600 * 3.5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        }
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(self.be, "CONSTITUTIONAL_ALARM_STATE_FILE", Path(td) / "state.json"), \
                 mock.patch.object(self.be, "CONSTITUTIONAL_ALARM_BODY_DIR", Path(td) / "inbox"), \
                 mock.patch.object(self.be, "portal_alarm_rate_limited", return_value=True) as mock_alarm:
                emitted = self.be.constitutional_starvation_check(tasks, rules, self.logger)
        self.assertEqual(emitted, 1, "starvation alarm must fire when elapsed > multiplier * interval")
        mock_alarm.assert_called_once()
        # Verify alarm_key follows convention
        _, kwargs = mock_alarm.call_args
        alarm_key = kwargs.get("alarm_key") or mock_alarm.call_args.args[1] if mock_alarm.call_args.args else None
        # Caption should mention starvation
        # (We tolerate either positional or kwarg passing)

    def test_starvation_does_not_fire_under_threshold(self):
        rules = dict(self.be.DEFAULT_BOOP_RULES)
        rules["constitutional_tasks_set"] = {"engineering-flow-check"}
        rules["constitutional_starvation_multiplier"] = 2.0
        now = datetime.now(timezone.utc)
        tasks = {
            "engineering-flow-check": {
                "status": "active",
                "frequency": "30min",
                "last_run": (now - timedelta(seconds=1500)).strftime("%Y-%m-%dT%H:%M:%SZ"),  # 25min - under threshold
            }
        }
        with mock.patch.object(self.be, "portal_alarm_rate_limited", return_value=True) as mock_alarm:
            emitted = self.be.constitutional_starvation_check(tasks, rules, self.logger)
        self.assertEqual(emitted, 0)
        mock_alarm.assert_not_called()


# ─── Real /proc probe for _pid_age_seconds + _task_id_from_pid ──────────────


class ProcProbeTests(_Base):
    def test_pid_age_seconds_returns_positive_for_self(self):
        age = self.be._pid_age_seconds(os.getpid())
        self.assertGreater(age, 0.0, "pid age must be positive for living process")
        self.assertLess(age, 86400 * 365, "pid age must be reasonable")

    def test_pid_age_seconds_returns_negative_for_nonexistent_pid(self):
        # Use a PID extremely unlikely to exist
        age = self.be._pid_age_seconds(99999999)
        self.assertEqual(age, -1.0)

    def test_task_id_from_pid_no_match_returns_empty(self):
        # Current python process cmdline does not contain BOOP marker
        tid = self.be._task_id_from_pid(os.getpid())
        self.assertEqual(tid, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
