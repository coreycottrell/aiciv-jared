#!/usr/bin/env python3
"""trio_primary_injector.py — Inject Trio messages into Aether's Primary tmux session

Polls trio-comms worker every 20s, injects new messages from Jared/Chy/Morphe
directly into Aether's Primary Claude session (full-capacity Opus with all tools).

This replaces the need for Haiku proxy responses - Primary Aether responds as itself.

State: .claude/grounding/trio-primary-injector-state.json
Logs: logs/trio_primary_injector.log
Invoke: python3 tools/trio_primary_injector.py (runs continuously)
Service: /etc/systemd/system/aether-trio-primary-injector.service
"""

import json
import logging
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
ROOT = Path("/home/jared/projects/AI-CIV/aether")
STATE_FILE = ROOT / ".claude/grounding/trio-primary-injector-state.json"
LOG_FILE = ROOT / "logs/trio_primary_injector.log"
CURRENT_SESSION_FILE = ROOT / ".current_session"

# Load tokens from credentials file
CREDENTIALS = ROOT / ".credentials/trio-tokens.json"
try:
    tokens = json.loads(CREDENTIALS.read_text())
    TRIO_TOKEN_AETHER = tokens["aether"]
except Exception as e:
    print(f"ERROR: Could not load Aether token from {CREDENTIALS}: {e}", file=sys.stderr)
    sys.exit(1)

# API endpoints
TRIO_API_BASE = "https://trio-comms.in0v8.workers.dev"
TRIO_MESSAGES_URL = f"{TRIO_API_BASE}/trio/messages"

# Constants
POLL_INTERVAL = 20  # seconds
MESSAGE_LIMIT = 20

# Logging setup - systemd service redirects stdout to log file
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


def load_state():
    """Load state file tracking last processed message ID."""
    # Always set new service_started_at on service start
    now = datetime.utcnow().isoformat() + "Z"

    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            # Update service start time to NOW (this service instance start)
            state["service_started_at"] = now
            # Keep processed_ids from previous runs (don't re-inject old messages)
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


def get_tmux_session():
    """Get current tmux session name from .current_session file."""
    try:
        if CURRENT_SESSION_FILE.exists():
            session = CURRENT_SESSION_FILE.read_text().strip()
            if session:
                logger.debug(f"Found tmux session from file: {session}")
                return session
    except Exception as e:
        logger.error(f"Error reading .current_session file: {e}")

    logger.warning("No tmux session found in .current_session file")
    return None


def inject_to_tmux(session, message):
    """Inject message into tmux session using 5x Enter protocol.

    Uses the -l flag (literal) to prevent shell injection and the 5x Enter
    pattern with 0.3s gaps to ensure reliable delivery to Claude input buffer.

    Pattern adopted from tools/msg-chy.sh and .claude/skills/inter-civ-inject/SKILL.md
    """
    try:
        # First, send the literal message content
        send_keys_cmd = ["tmux", "send-keys", "-t", session, "-l", message]
        result = subprocess.run(send_keys_cmd, capture_output=True, text=True, timeout=5)

        if result.returncode != 0:
            logger.error(f"tmux send-keys failed: {result.stderr}")
            return False

        # Then send 5x Enter with 0.3s gaps
        for i in range(5):
            time.sleep(0.3)
            enter_cmd = ["tmux", "send-keys", "-t", session, "Enter"]
            subprocess.run(enter_cmd, capture_output=True, timeout=2)

        logger.info(f"Injected message to tmux session '{session}' (5x Enter protocol)")
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
        req = urllib.request.Request(
            f"{TRIO_MESSAGES_URL}?limit={MESSAGE_LIMIT}",
            headers={
                "Authorization": f"Bearer {TRIO_TOKEN_AETHER}",
                "User-Agent": "aether-trio-primary-injector/1.0"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            return data if isinstance(data, list) else []
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP error fetching messages: {e.code} - {e.read().decode()[:200]}")
        return []
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return []


def should_inject(msg, state, service_start_time):
    """Determine if we should inject this message to Primary."""
    # Don't inject our own messages
    if msg["sender_id"] == "aether":
        logger.debug(f"Skipping message {msg['id']}: from aether (don't inject own messages)")
        return False

    # Must not be already processed
    if msg["id"] in state["processed_ids"]:
        logger.debug(f"Skipping message {msg['id']}: already processed")
        return False

    # Only inject messages AFTER service started (ignore old messages on startup)
    msg_time = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
    if msg_time < service_start_time:
        logger.debug(f"Skipping message {msg['id']}: too old (msg_time={msg_time}, threshold={service_start_time})")
        return False

    logger.info(f"Message {msg['id']} passes all checks - will inject")
    return True


def process_messages(state):
    """Main processing loop: fetch messages, inject new ones to Primary tmux."""
    # Get current tmux session
    session = get_tmux_session()
    if not session:
        logger.warning("No tmux session available - skipping this cycle")
        return 0, 0

    # Verify session exists
    try:
        check_cmd = ["tmux", "has-session", "-t", session]
        result = subprocess.run(check_cmd, capture_output=True, timeout=5)
        if result.returncode != 0:
            logger.warning(f"tmux session '{session}' doesn't exist - skipping this cycle")
            return 0, 0
    except Exception as e:
        logger.error(f"Error checking tmux session: {e}")
        return 0, 0

    # Calculate service start time threshold
    service_start = datetime.fromisoformat(state["service_started_at"].replace("Z", "+00:00"))

    messages = fetch_messages()

    if not messages:
        logger.debug(f"No messages fetched (or API error)")
        return 0, 0

    # Reverse to process oldest first (messages come DESC from API)
    messages.reverse()

    injected_count = 0
    checked_count = len(messages)

    for msg in messages:
        # Skip if already processed
        if msg["id"] in state["processed_ids"]:
            continue

        # Check if we should inject
        if not should_inject(msg, state, service_start):
            # Mark as seen even if skipping (to avoid re-checking old messages)
            state["processed_ids"].append(msg["id"])
            # Keep processed list manageable (last 500)
            if len(state["processed_ids"]) > 500:
                state["processed_ids"] = state["processed_ids"][-500:]
            continue

        # Build injection message
        sender = msg["sender_id"].upper()
        content = msg["content"]
        injection_message = f"TRIO from {sender}: {content}"

        logger.info(f"Injecting message {msg['id']} from {msg['sender_id']}")

        # Inject to tmux
        if inject_to_tmux(session, injection_message):
            # Mark as processed after successful injection
            state["processed_ids"].append(msg["id"])
            state["last_message_id"] = msg["id"]
            # Keep processed list manageable (last 500)
            if len(state["processed_ids"]) > 500:
                state["processed_ids"] = state["processed_ids"][-500:]
            injected_count += 1
        else:
            logger.error(f"Failed to inject message {msg['id']}")
            # Still mark as processed to avoid infinite retries
            state["processed_ids"].append(msg["id"])
            if len(state["processed_ids"]) > 500:
                state["processed_ids"] = state["processed_ids"][-500:]

    save_state(state)
    return checked_count, injected_count


def main():
    """Main service loop."""
    logger.info("Trio Primary Injector starting...")
    state = load_state()
    logger.info(f"Service start time: {state['service_started_at']}")
    logger.info("Will inject new messages from Jared/Chy/Morphe to Primary tmux session")

    cycle_count = 0

    while True:
        try:
            cycle_count += 1
            logger.debug(f"Poll cycle {cycle_count} starting")

            checked, injected = process_messages(state)

            if injected > 0 or cycle_count % 20 == 0:  # Log every 20 cycles or when active
                logger.info(f"Cycle {cycle_count}: checked {checked} messages, injected {injected}")

        except KeyboardInterrupt:
            logger.info("Shutting down on keyboard interrupt")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
