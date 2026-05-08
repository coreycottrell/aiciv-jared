#!/usr/bin/env python3
"""trio_auto_responder.py — Auto-respond to Jared's messages in Trio chat

Polls trio-comms worker every 30s, responds to new messages from Jared using
Claude Haiku via Anthropic API, posts responses back to the worker.

State: .claude/grounding/trio-auto-responder-state.json
Logs: logs/trio_auto_responder.log
Invoke: python3 tools/trio_auto_responder.py (runs continuously)
Service: /etc/systemd/system/aether-trio-responder.service
"""

import json
import logging
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
ROOT = Path("/home/jared/projects/AI-CIV/aether")
STATE_FILE = ROOT / ".claude/grounding/trio-auto-responder-state.json"
LOG_FILE = ROOT / "logs/trio_auto_responder.log"

# Load tokens from credentials file
CREDENTIALS = ROOT / ".credentials/trio-tokens.json"
try:
    tokens = json.loads(CREDENTIALS.read_text())
    TRIO_TOKEN_AETHER = tokens["aether"]
except Exception as e:
    print(f"ERROR: Could not load Aether token from {CREDENTIALS}: {e}", file=sys.stderr)
    sys.exit(1)

# Load Anthropic API key from .env
ENV_FILE = ROOT / ".env"
ANTHROPIC_API_KEY = None
try:
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("ANTHROPIC_API_KEY="):
            ANTHROPIC_API_KEY = line.split("=", 1)[1].strip()
            break
except Exception as e:
    print(f"ERROR: Could not load .env from {ENV_FILE}: {e}", file=sys.stderr)
    sys.exit(1)

if not ANTHROPIC_API_KEY:
    print("ERROR: ANTHROPIC_API_KEY not found in .env", file=sys.stderr)
    sys.exit(1)

# API endpoints
TRIO_API_BASE = "https://trio-comms.in0v8.workers.dev"
TRIO_MESSAGES_URL = f"{TRIO_API_BASE}/trio/messages"
TRIO_POST_URL = f"{TRIO_API_BASE}/trio/message"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# Constants
POLL_INTERVAL = 30  # seconds
MESSAGE_LIMIT = 20
MAX_TOKENS = 300
RESPONSE_COOLDOWN = 60  # Don't respond more than once per minute (rate limit safety)
STARTUP_IGNORE_MINUTES = 10  # Ignore messages older than this on first run

# Logging setup - systemd service redirects stdout to log file
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


def load_state():
    """Load state file tracking last processed message and last response time."""
    # Always set new service_started_at on service start
    now = datetime.utcnow().isoformat() + "Z"

    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            # Update service start time to NOW (this service instance start)
            state["service_started_at"] = now
            # Clear processed_ids on service restart to allow responding to recent messages
            # (We don't want to carry forward old processed IDs that prevent new responses)
            state["processed_ids"] = []
            logger.info(f"Service restart detected - cleared processed_ids to allow fresh responses")
            return state
        except Exception as e:
            logger.warning(f"Could not load state file: {e}")

    return {
        "last_message_id": None,
        "last_response_time": None,
        "processed_ids": [],
        "service_started_at": now
    }


def save_state(state):
    """Save state file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def fetch_messages():
    """Fetch recent messages from trio-comms worker."""
    try:
        req = urllib.request.Request(
            f"{TRIO_MESSAGES_URL}?limit={MESSAGE_LIMIT}",
            headers={
                "Authorization": f"Bearer {TRIO_TOKEN_AETHER}",
                "User-Agent": "aether-trio-responder/1.0"
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


def post_message(content):
    """Post a message to trio-comms worker as Aether."""
    try:
        payload = {"content": content}
        req = urllib.request.Request(
            TRIO_POST_URL,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {TRIO_TOKEN_AETHER}",
                "Content-Type": "application/json",
                "User-Agent": "aether-trio-responder/1.0"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode())
            return result.get("id")
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP error posting message: {e.code} - {e.read().decode()[:200]}")
        return None
    except Exception as e:
        logger.error(f"Error posting message: {e}")
        return None


def generate_response(conversation_history):
    """Generate response using Anthropic Claude Haiku API."""
    system_prompt = (
        "You are Aether's AFK proxy. The real Aether (Primary with full tools/memory) didn't "
        "respond in 5 minutes, so you're generating a brief placeholder acknowledging Jared's "
        "message so he knows we saw it. Keep it 1 sentence. Reference that you're the AFK proxy "
        "and that full Aether will follow up when back at keyboard. Warm but brief."
    )

    # Format conversation history for Claude
    messages = []
    for msg in conversation_history:
        role = "user" if msg["sender_id"] == "jared" else "assistant"
        messages.append({
            "role": role,
            "content": msg["content"]
        })

    # Ensure last message is from user (required by API)
    if messages and messages[-1]["role"] == "assistant":
        messages = messages[:-1]

    if not messages:
        return None

    try:
        payload = {
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": MAX_TOKENS,
            "system": system_prompt,
            "messages": messages
        }

        req = urllib.request.Request(
            ANTHROPIC_API_URL,
            data=json.dumps(payload).encode(),
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
                "User-Agent": "aether-trio-responder/1.0"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            content = result.get("content", [])
            if content and len(content) > 0:
                return content[0].get("text")
            return None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()[:500]
        logger.error(f"Anthropic API error {e.code}: {error_body}")
        return None
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return None


def should_respond(msg, state, service_start_time, all_messages):
    """Determine if we should respond to this message (AFK fallback mode).

    Only respond if Primary Aether hasn't responded in the last 5 minutes.
    This is a fallback - Primary should handle most responses via tmux injection.
    """
    # Must be from Jared
    if msg["sender_id"] != "jared":
        logger.debug(f"Skipping message {msg['id']}: not from jared (sender={msg['sender_id']})")
        return False

    # Must not be already processed
    if msg["id"] in state["processed_ids"]:
        logger.debug(f"Skipping message {msg['id']}: already processed")
        return False

    # Ignore messages older than startup time (on first run)
    msg_time = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
    if msg_time < service_start_time:
        logger.debug(f"Skipping message {msg['id']}: too old (msg_time={msg_time}, threshold={service_start_time})")
        return False

    # AFK FALLBACK CHECK: Only respond if Primary hasn't responded in 5 minutes
    # Check if there's been any aether message in the last 5 minutes AFTER this jared message
    aether_messages_after = [
        m for m in all_messages
        if m["sender_id"] == "aether" and
        datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")) > msg_time
    ]

    if aether_messages_after:
        # Primary is active, don't use fallback
        logger.debug(f"Skipping message {msg['id']}: Primary already responded")
        return False

    # Check if 5 minutes have passed since this jared message
    time_since_msg = (datetime.utcnow() - msg_time.replace(tzinfo=None)).total_seconds()
    if time_since_msg < 300:  # 5 minutes = 300 seconds
        logger.debug(f"Skipping message {msg['id']}: waiting for Primary (only {int(time_since_msg)}s elapsed)")
        return False

    # Check cooldown (don't respond too frequently)
    if state["last_response_time"]:
        last_response = datetime.fromisoformat(state["last_response_time"].replace("Z", "+00:00"))
        if (datetime.utcnow() - last_response.replace(tzinfo=None)).total_seconds() < RESPONSE_COOLDOWN:
            logger.info(f"Cooldown active, skipping message {msg['id']}")
            return False

    logger.warning(f"AFK FALLBACK — Primary didn't respond in 5min, replying as proxy to message {msg['id']}")
    return True


def process_messages(state):
    """Main processing loop: fetch messages, respond to Jared's new ones."""
    # Calculate service start time threshold
    service_start = datetime.fromisoformat(state["service_started_at"].replace("Z", "+00:00"))
    startup_threshold = service_start - timedelta(minutes=STARTUP_IGNORE_MINUTES)

    messages = fetch_messages()

    if not messages:
        logger.debug(f"No messages fetched (or API error)")
        return 0, 0

    # Reverse to process oldest first (messages come DESC from API)
    messages.reverse()

    responded_count = 0
    checked_count = len(messages)

    for msg in messages:
        # Skip if already processed
        if msg["id"] in state["processed_ids"]:
            continue

        # Check if we should respond BEFORE marking as processed (pass all messages for AFK check)
        if not should_respond(msg, state, startup_threshold, messages):
            # Mark as seen even if skipping (to avoid re-checking old messages)
            state["processed_ids"].append(msg["id"])
            # Keep processed list manageable (last 500)
            if len(state["processed_ids"]) > 500:
                state["processed_ids"] = state["processed_ids"][-500:]
            continue

        logger.info(f"Responding to message {msg['id']} from {msg['sender_id']}")

        # Build conversation context (last 10 messages)
        context_messages = messages[-10:]

        # Generate response
        response_text = generate_response(context_messages)

        if not response_text:
            logger.error(f"Failed to generate response for message {msg['id']}")
            # Mark as processed to avoid infinite retries
            state["processed_ids"].append(msg["id"])
            if len(state["processed_ids"]) > 500:
                state["processed_ids"] = state["processed_ids"][-500:]
            continue

        # Post response
        response_id = post_message(response_text)

        if response_id:
            logger.info(f"Posted response {response_id} to message {msg['id']}")
            state["last_response_time"] = datetime.utcnow().isoformat() + "Z"
            state["last_message_id"] = msg["id"]
            # Mark as processed after successful response
            state["processed_ids"].append(msg["id"])
            # Keep processed list manageable (last 500)
            if len(state["processed_ids"]) > 500:
                state["processed_ids"] = state["processed_ids"][-500:]
            responded_count += 1
        else:
            logger.error(f"Failed to post response for message {msg['id']}")
            # Still mark as processed to avoid infinite retries
            state["processed_ids"].append(msg["id"])
            if len(state["processed_ids"]) > 500:
                state["processed_ids"] = state["processed_ids"][-500:]

    save_state(state)
    return checked_count, responded_count


def main():
    """Main service loop."""
    logger.info("Trio auto-responder starting...")
    state = load_state()
    logger.info(f"Service start time: {state['service_started_at']}")
    logger.info(f"Ignoring messages older than {STARTUP_IGNORE_MINUTES} minutes from start")

    cycle_count = 0

    while True:
        try:
            cycle_count += 1
            logger.debug(f"Poll cycle {cycle_count} starting")

            checked, responded = process_messages(state)

            logger.info(f"Cycle {cycle_count}: checked {checked} messages, responded to {responded}")

        except KeyboardInterrupt:
            logger.info("Shutting down on keyboard interrupt")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
