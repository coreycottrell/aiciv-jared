#!/usr/bin/env python3
"""trio_watcher.py — watch from-chy/ and from-morphe/ for new files.

On detection:
  1. Log event to .claude/grounding/log.jsonl
  2. Write .read receipt back to sender (via scp)
  3. Inject tmux ping with the path (if tmux session known)
  4. Update state file to avoid re-notifying same files

State: .claude/grounding/trio-watcher-state.json
Invoke: python3 tools/trio_watcher.py  (idempotent; run from BOOP every 1-5 min)
"""
import json
import os
import sys
import subprocess
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

ROOT = Path("/home/jared/projects/AI-CIV/aether")
STATE = ROOT / ".claude/grounding/trio-watcher-state.json"
LOG = ROOT / ".claude/grounding/log.jsonl"

SIBLINGS = {
    "chy":    {
        "inbox_dir":     ROOT / "from-chy",
        "ssh_host":      "aiciv@37.27.237.109",
        "ssh_port":      "2213",
        "receipt_dir":   "/home/aiciv/shared/receipts-to-chy",
    },
    "morphe": {
        "inbox_dir":     ROOT / "from-morphe",
        "ssh_host":      None,     # Morphe has no sshd, skip receipt scp
        "ssh_port":      None,
        "receipt_dir":   None,
    },
}

TMUX_SESSION = os.environ.get("AETHER_TMUX_SESSION", "")  # set via env if present

# Trio Comms API (posts new-file events to the 777 dashboard)
TRIO_API_URL = "https://777-api.purebrain.ai/trio/message"
TRIO_API_KEY = os.environ.get("TRIO_API_KEY", "j5kLX8NkYrHIxBOHUlVHXGs40nOf8jn7MP9wkPPQV_Q")
TRIO_MAX_CONTENT = 4000  # truncate long file payloads


def post_trio_message(sender, filepath):
    """POST a new-file event to /trio/message. Dedupes via bridge_file_path server-side."""
    try:
        content = Path(filepath).read_text(errors="replace")[:TRIO_MAX_CONTENT]
    except Exception:
        content = f"(bridge file at {filepath} — unreadable or binary)"
    payload = {
        "from": sender,  # chy | morphe (sender of the incoming file)
        "to": "aether",
        "content": f"**New bridge file from {sender}** ({Path(filepath).name})\n\n{content}",
        "bridge_file_path": str(filepath),
    }
    try:
        req = urllib.request.Request(
            TRIO_API_URL,
            data=json.dumps(payload).encode(),
            headers={
                "X-API-Key": TRIO_API_KEY,
                "Content-Type": "application/json",
                "User-Agent": "aether-trio-watcher/1.0",
                "Origin": "https://777.purebrain.ai",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            body = json.loads(r.read().decode())
            return "posted" + (" (deduped)" if body.get("deduped") else "")
    except urllib.error.HTTPError as e:
        return f"http {e.code}: {e.read().decode()[:120]}"
    except Exception as e:
        return f"error: {e}"


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            pass
    return {"seen": {}}  # {sibling: [filenames]}


def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2))


def log_event(kind, sibling, filename, extra=None):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "trigger": f"bridge-{kind}",
        "ai_name": sibling,
        "tokens_at_trigger": None,
        "tiers_read": [],
        "docs_read": [filename],
        "duration_ms": None,
        "note": extra or f"{kind} detected from {sibling}: {filename}",
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def send_receipt(sibling, filename):
    cfg = SIBLINGS[sibling]
    if not cfg["ssh_host"]:
        return "skipped (no sshd on sibling side)"
    receipt = f"/tmp/receipt-from-aether-{int(time.time())}.read"
    Path(receipt).write_text(json.dumps({
        "received_from": sibling,
        "received_file": filename,
        "received_at": datetime.utcnow().isoformat() + "Z",
        "receiver": "aether",
    }))
    cmd = ["scp", "-P", cfg["ssh_port"], "-o", "ConnectTimeout=5", receipt,
           f'{cfg["ssh_host"]}:{cfg["receipt_dir"]}/']
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        os.unlink(receipt)
        return "sent" if r.returncode == 0 else f"scp failed: {r.stderr.strip()}"
    except Exception as e:
        return f"error: {e}"


def tmux_ping(msg):
    if not TMUX_SESSION:
        return "skipped (no TMUX_SESSION env)"
    try:
        subprocess.run(
            ["tmux", "send-keys", "-t", TMUX_SESSION, msg, "Enter"],
            capture_output=True, timeout=5,
        )
        return "sent"
    except Exception as e:
        return f"error: {e}"


def scan_sibling(sibling, state):
    cfg = SIBLINGS[sibling]
    inbox = cfg["inbox_dir"]
    inbox.mkdir(parents=True, exist_ok=True)

    seen = set(state["seen"].get(sibling, []))
    found = []
    for f in sorted(inbox.iterdir()):
        if f.name.startswith(".") or not f.is_file():
            continue
        if f.name in seen:
            continue
        found.append(f)

    new_events = []
    for f in found:
        rel_path = str(f)
        log_event("received", sibling, rel_path)
        receipt_status = send_receipt(sibling, f.name)
        ping_status = tmux_ping(f"[trio-watcher] NEW from-{sibling}: {rel_path}")
        trio_status = post_trio_message(sibling, rel_path)
        new_events.append({
            "file": rel_path,
            "receipt": receipt_status,
            "ping": ping_status,
            "trio_post": trio_status,
        })
        seen.add(f.name)

    state["seen"][sibling] = sorted(seen)
    return new_events


def main():
    state = load_state()
    report = {"scanned_at": datetime.utcnow().isoformat() + "Z", "events": {}}
    for sibling in SIBLINGS:
        events = scan_sibling(sibling, state)
        report["events"][sibling] = events
    save_state(state)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
