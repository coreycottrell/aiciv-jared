#!/usr/bin/env python3
"""
CONSTITUTIONAL money-path guard test — EMPTY-CONVERSATION FAIL-CLOSED BLOCK.

Incident: an /api/send-seed ADDENDUM-path seed was emailed to a paying customer
(Jason / "Verun") with NO conversation content — conv_text rendered
'(no conversation history)' and the seed sent anyway. The PAYMENT-seed path
already fails closed (finish-wakeup 425 + logs/blocked_seeds.jsonl dead-letter);
the /api/send-seed path did NOT. That asymmetry was the bug.

Fix under test (tools/purebrain_log_server.py):
  * module-level predicate `_seed_conversation_is_empty(conversation)`
  * a guard in `_send_seed_core`, AFTER the ai_name guard and BEFORE the
    in-flight gate, that HOLDs (422, held:True) an empty-conversation seed,
    dead-letters it to logs/blocked_seeds.jsonl (reason='empty_conversation'),
    and fires a PORTAL alert (Jared is portal-primary).

Proves:
  1. predicate is True for every "no real content" shape, False when any message
     has non-whitespace content;
  2. empty conversation + valid ai_name  -> 422 held, AgentMail NEVER reached
     (NOT sent), blocked_seeds row written, portal alert attempted;
  3. a Pure Migrate `migration_bundle` present does NOT bypass the guard —
     empty still blocks (a migrated user still needs a real naming ceremony);
  4. a NON-EMPTY conversation is NOT blocked by this guard — control reaches the
     real AgentMail send path (byte-identical seed production is separately
     proven by the migrate-seed-fold suite).

The functional cases NEVER perform a real send: `agentmail` is stubbed to raise
inside its constructor, so the non-empty path reaches the send call and fails
closed (502 retryable) with no email, no dedup claim, no post-send side effects.
logs/blocked_seeds.jsonl is snapshotted and restored around every functional test.

Run:  pytest -q exports/departments/systems-technology/empty-conversation-guard/test_empty_conversation_seed_guard.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import types
import uuid as _uuid

import pytest

REPO_ROOT = subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"],
    cwd=os.path.dirname(os.path.abspath(__file__)),
).decode().strip()
MODULE_PATH = os.path.join(REPO_ROOT, "tools", "purebrain_log_server.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("pls_empty_guard_under_test", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pls = _load_module()

BLOCKED_PATH = os.path.join(pls.DEFAULT_LOG_DIR, "blocked_seeds.jsonl")


# ---------------------------------------------------------------------------
# 1. UNIT: the empty-detection predicate
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("conv", [
    [],
    None,
    [{"role": "user"}],                                          # no content key
    [{"role": "user", "content": ""}],                          # empty string
    [{"role": "user", "content": "   \n\t "}],                  # whitespace only
    [{"role": "user", "content": None}],                        # None content
    [{"role": "user", "content": ""}, {"role": "assistant", "content": "  "}],
])
def test_predicate_is_empty_true(conv):
    assert pls._seed_conversation_is_empty(conv) is True


@pytest.mark.parametrize("conv", [
    [{"role": "user", "content": "Hello there"}],
    [{"role": "user", "content": ""}, {"role": "assistant", "content": "a real reply"}],
    [{"role": "assistant", "content": "x"}],
])
def test_predicate_is_empty_false(conv):
    assert pls._seed_conversation_is_empty(conv) is False


# ---------------------------------------------------------------------------
# Functional fixtures (Flask test client, stubbed agentmail, no real I/O)
# ---------------------------------------------------------------------------
@pytest.fixture
def probes(monkeypatch):
    """Stub every real side effect so the send path is exercised WITHOUT any
    real email, telegram, or tmux injection. Returns recorders for assertions."""
    state = {"agentmail_instantiated": 0, "popen_calls": [], "telegram_calls": 0}

    # (a) Fake `agentmail` module: constructor records + raises => the real send
    #     call is *reached* (proving the guard passed) but NO email is sent.
    class _StubAgentMail:
        def __init__(self, *a, **k):
            state["agentmail_instantiated"] += 1
            raise RuntimeError("stub-agentmail: send path reached; no real send performed")

    fake_agentmail = types.ModuleType("agentmail")
    fake_agentmail.AgentMail = _StubAgentMail
    saved_agentmail = sys.modules.get("agentmail")
    sys.modules["agentmail"] = fake_agentmail
    monkeypatch.setenv("AGENTMAIL_API_KEY", "stub-key")  # skip .env parse

    # (b) Telegram no-op (fail-loud gate would otherwise alert on the stub error).
    monkeypatch.setattr(pls, "_send_telegram_notification", lambda *a, **k: state.__setitem__("telegram_calls", state["telegram_calls"] + 1))

    # (c) Capture the portal-alert tmux injection instead of spawning it.
    class _FakePopen:
        def __init__(self, args, *a, **k):
            state["popen_calls"].append(args)

    monkeypatch.setattr(pls.subprocess, "Popen", _FakePopen)

    yield state

    if saved_agentmail is not None:
        sys.modules["agentmail"] = saved_agentmail
    else:
        sys.modules.pop("agentmail", None)


@pytest.fixture
def blocked_snapshot():
    """Snapshot logs/blocked_seeds.jsonl and restore it after the test, so a
    dead-letter row written by the guard/fail-loud path never pollutes prod."""
    existed = os.path.exists(BLOCKED_PATH)
    original = None
    if existed:
        with open(BLOCKED_PATH, "rb") as f:
            original = f.read()
    baseline_len = len(original) if original else 0

    def new_rows():
        if not os.path.exists(BLOCKED_PATH):
            return []
        with open(BLOCKED_PATH, "rb") as f:
            data = f.read()
        tail = data[baseline_len:].decode("utf-8", "replace")
        return [json.loads(ln) for ln in tail.splitlines() if ln.strip()]

    yield new_rows

    if existed:
        with open(BLOCKED_PATH, "wb") as f:
            f.write(original)
    elif os.path.exists(BLOCKED_PATH):
        os.remove(BLOCKED_PATH)


@pytest.fixture
def client():
    app = pls.create_app(enable_hub_forwarding=False, enable_acgee_forwarding=False)
    app.config["TESTING"] = True
    return app.test_client()


def _base_payload(**over):
    p = {
        "session_uuid": f"test-{_uuid.uuid4()}",
        "ai_name": "Verun",
        "human_name": "Jason",
        "human_email": "jason.test@example.com",
        "tier": "Awakened",
        "order_id": f"I-TEST-{_uuid.uuid4().hex[:8]}",
        "is_sandbox": True,
        "conversation": [],
    }
    p.update(over)
    return p


# ---------------------------------------------------------------------------
# 2. Empty conversation -> BLOCKED (held), NOT sent, dead-lettered, portal alert
# ---------------------------------------------------------------------------
def test_empty_conversation_is_blocked_and_not_sent(client, probes, blocked_snapshot):
    payload = _base_payload(conversation=[])
    resp = client.post("/api/send-seed", json=payload)

    assert resp.status_code == 422
    body = resp.get_json()
    assert body["ok"] is False
    assert body["held"] is True
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"

    # NOT sent: the AgentMail client was never even constructed.
    assert probes["agentmail_instantiated"] == 0

    # Dead-lettered with the canonical reason + this session.
    rows = blocked_snapshot()
    hit = [r for r in rows if r.get("reason") == "empty_conversation"
           and r.get("session_uuid") == payload["session_uuid"]]
    assert len(hit) == 1, f"expected exactly one empty_conversation dead-letter, got {rows}"
    assert hit[0]["payer_email"] == payload["human_email"]
    assert hit[0]["ai_name"] == payload["ai_name"]

    # Portal alert attempted (tmux send-keys), Jared is portal-primary.
    portal = [c for c in probes["popen_calls"] if "tmux" in c and any("SEED BLOCKED" in str(x) for x in c)]
    assert portal, f"expected a portal tmux alert, got {probes['popen_calls']}"


@pytest.mark.parametrize("conv", [
    [],
    [{"role": "user", "content": "   "}],
    [{"role": "assistant", "content": ""}, {"role": "user", "content": None}],
])
def test_various_empty_shapes_blocked(client, probes, blocked_snapshot, conv):
    resp = client.post("/api/send-seed", json=_base_payload(conversation=conv))
    assert resp.status_code == 422
    assert resp.get_json()["held"] is True
    assert probes["agentmail_instantiated"] == 0


# ---------------------------------------------------------------------------
# 3. migration_bundle present must NOT bypass the empty guard
# ---------------------------------------------------------------------------
def test_migration_bundle_does_not_bypass_empty_guard(client, probes, blocked_snapshot):
    bundle = {
        "schema": "purebrain.memory-bundle/v1",
        "identity": {"name": "Jason"},
        "source": {"provider": "chatgpt", "route": "export"},
    }
    # Empty naming conversation, but a migration bundle is supplied.
    payload = _base_payload(conversation=[], migration=bundle)
    resp = client.post("/api/send-seed", json=payload)

    assert resp.status_code == 422
    assert resp.get_json()["held"] is True
    # A migrated user STILL needs a real naming ceremony -> no send.
    assert probes["agentmail_instantiated"] == 0
    rows = blocked_snapshot()
    assert any(r.get("reason") == "empty_conversation"
               and r.get("session_uuid") == payload["session_uuid"] for r in rows)


# ---------------------------------------------------------------------------
# 4. Non-empty conversation is NOT blocked -> reaches the real send path
# ---------------------------------------------------------------------------
def test_nonempty_conversation_reaches_send_path(client, probes, blocked_snapshot):
    payload = _base_payload(conversation=[
        {"role": "user", "content": "I would like to name you Verun."},
        {"role": "assistant", "content": "I accept the name Verun. Thank you."},
    ])
    resp = client.post("/api/send-seed", json=payload)

    # The empty-guard did NOT fire: control reached the AgentMail send call
    # (stub raised inside the constructor => counted). This proves a real,
    # content-bearing naming ceremony is unaffected by the new guard.
    assert probes["agentmail_instantiated"] >= 1

    # It is NOT the empty-held 422 response — it is the send-failure fail-loud
    # gate (502 retryable) produced by the stubbed send. No 'held' flag.
    assert resp.status_code == 502
    body = resp.get_json()
    assert body.get("retryable") is True
    assert body.get("held") is not True

    # The dead-letter for this session is a SEND-FAILURE, never 'empty_conversation'.
    rows = [r for r in blocked_snapshot() if r.get("session_uuid") == payload["session_uuid"]]
    assert rows, "expected a send-failure dead-letter for the non-empty case"
    assert all(r.get("reason") != "empty_conversation" for r in rows)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
