#!/usr/bin/env python3
"""duo_injector.py — Inject Duo Chat messages into an AI's tmux session

Generic version of trio_primary_injector.py for customer AI containers.
Polls trio-comms worker every 20s, injects new messages from other participants.

Config: ~/duo/duo-config.json
State:  ~/duo/duo-injector-state.json
Invoke: python3 duo_injector.py (runs continuously)
"""

import json
import logging
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# --- Configuration ---
HOME = Path.home()
DUO_DIR = HOME / "duo"
CONFIG_FILE = DUO_DIR / "duo-config.json"
STATE_FILE = DUO_DIR / "duo-injector-state.json"

# Load config
if not CONFIG_FILE.exists():
    print(f"ERROR: Config file not found at {CONFIG_FILE}", file=sys.stderr)
    print("Create ~/duo/duo-config.json with: duo_id, token, comms_url, tmux_session, my_sender_id", file=sys.stderr)
    sys.exit(1)

try:
    config = json.loads(CONFIG_FILE.read_text())
except Exception as e:
    print(f"ERROR: Could not parse {CONFIG_FILE}: {e}", file=sys.stderr)
    sys.exit(1)

DUO_ID = config.get("duo_id", "")
TOKEN = config.get("token", "")
COMMS_URL = config.get("comms_url", "https://trio-comms.in0v8.workers.dev")
TMUX_SESSION = config.get("tmux_session", "")
MY_SENDER_ID = config.get("my_sender_id", "").lower()

if not DUO_ID or not TOKEN or not TMUX_SESSION or not MY_SENDER_ID:
    print("ERROR: duo-config.json must have: duo_id, token, tmux_session, my_sender_id", file=sys.stderr)
    sys.exit(1)

# Constants
POLL_INTERVAL = 20  # seconds
MESSAGE_LIMIT = 20

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("duo-injector")


def load_state():
    """Load state file tracking processed message IDs."""
    now = datetime.utcnow().isoformat() + "Z"
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            state["service_started_at"] = now
            logger.info(f"Loaded state with {len(state.get('processed_ids', []))} processed IDs")
            return state
        except Exception as e:
            logger.warning(f"Could not load state file: {e}")
    return {
        "last_message_id": None,
        "processed_ids": [],
        "service_started_at": now
    }


def save_state(state):
    """Save state file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def inject_to_tmux(session, message):
    """Inject message into tmux session using 5x Enter protocol."""
    try:
        send_cmd = ["tmux", "send-keys", "-t", session, "-l", message]
        result = subprocess.run(send_cmd, capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            logger.error(f"tmux send-keys failed: {result.stderr}")
            return False

        for _ in range(5):
            time.sleep(0.3)
            subprocess.run(["tmux", "send-keys", "-t", session, "Enter"],
                         capture_output=True, timeout=2)

        logger.info(f"Injected message to tmux session '{session}'")
        return True

    except subprocess.TimeoutExpired:
        logger.error(f"Timeout injecting to tmux session '{session}'")
        return False
    except Exception as e:
        logger.error(f"Error injecting to tmux: {e}")
        return False


def fetch_messages():
    """Fetch recent messages from trio-comms worker."""
    try:
        url = f"{COMMS_URL}/trio/messages?limit={MESSAGE_LIMIT}&trio_id={DUO_ID}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "User-Agent": "duo-injector/1.0"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            return data if isinstance(data, list) else []
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP error fetching messages: {e.code}")
        return []
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return []


def should_inject(msg, state, service_start_time):
    """Determine if we should inject this message."""
    # Skip our own messages
    if msg["sender_id"].lower() == MY_SENDER_ID:
        return False

    # Skip already processed
    if msg["id"] in state["processed_ids"]:
        return False

    # Only inject messages after service started (skip old backlog)
    msg_time = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
    if msg_time < service_start_time:
        return False

    return True


def process_messages(state):
    """Fetch messages and inject new ones to tmux."""
    # Verify tmux session exists
    try:
        result = subprocess.run(["tmux", "has-session", "-t", TMUX_SESSION],
                              capture_output=True, timeout=5)
        if result.returncode != 0:
            logger.warning(f"tmux session '{TMUX_SESSION}' not found - skipping")
            return 0, 0
    except Exception as e:
        logger.error(f"Error checking tmux session: {e}")
        return 0, 0

    service_start = datetime.fromisoformat(state["service_started_at"].replace("Z", "+00:00"))
    messages = fetch_messages()

    if not messages:
        return 0, 0

    # Process oldest first
    messages.reverse()

    injected_count = 0
    checked_count = len(messages)

    for msg in messages:
        if msg["id"] in state["processed_ids"]:
            continue

        if not should_inject(msg, state, service_start):
            state["processed_ids"].append(msg["id"])
            if len(state["processed_ids"]) > 500:
                state["processed_ids"] = state["processed_ids"][-500:]
            continue

        sender = msg["sender_id"].upper()
        content = msg["content"]
        injection_message = f"DUO from {sender}: {content}"

        logger.info(f"Injecting message {msg['id']} from {msg['sender_id']}")

        if inject_to_tmux(TMUX_SESSION, injection_message):
            injected_count += 1

        # Mark processed regardless of success (avoid infinite retries)
        state["processed_ids"].append(msg["id"])
        state["last_message_id"] = msg["id"]
        if len(state["processed_ids"]) > 500:
            state["processed_ids"] = state["processed_ids"][-500:]

    save_state(state)
    return checked_count, injected_count


def main():
    """Main service loop."""
    logger.info(f"Duo Injector starting for duo_id={DUO_ID}, sender={MY_SENDER_ID}")
    logger.info(f"tmux session: {TMUX_SESSION}, poll interval: {POLL_INTERVAL}s")
    state = load_state()

    cycle_count = 0

    while True:
        try:
            cycle_count += 1
            checked, injected = process_messages(state)

            if injected > 0 or cycle_count % 20 == 0:
                logger.info(f"Cycle {cycle_count}: checked {checked}, injected {injected}")

        except KeyboardInterrupt:
            logger.info("Shutting down")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
