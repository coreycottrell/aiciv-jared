#!/usr/bin/env python3
"""
Command Center Chat Bridge - Standalone daemon for Aether

Connects Aether to cc.purebrain.ai:
- Polls for new messages every 5 seconds
- Injects DMs and @mentions into tmux session
- Captures responses from portal chat log
- Posts responses back to CC
- Sends presence heartbeats (shows ONLINE)

Run as daemon:
    nohup python3 tools/cc_bridge.py >> logs/cc_bridge.log 2>&1 &

Or via systemd service (recommended)
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import uuid
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)

# ── CIV Identity ──────────────────────────────────────────────────────────────
CIV_NAME = "aether"
CIV_EMAIL = "aethergottaeat@agentmail.to"
CIV_KEY = os.environ.get("CIV_KEY_AETHER", "aether-dev-key-change-me")

# ── Config ────────────────────────────────────────────────────────────────────
CC_BASE = os.environ.get("CC_BASE_URL", "https://cc.purebrain.ai")
PROJECT_ROOT = Path("/home/jared/projects/AI-CIV/aether")

POLL_INTERVAL = 5           # seconds between CC polls
HEARTBEAT_INTERVAL = 60     # seconds between presence heartbeats
RESPONSE_WAIT = 30          # max seconds to wait for response
RESPONSE_POLL = 2           # seconds between portal log checks
QUEUE_DRAIN_INTERVAL = 10   # seconds between queue drain checks
QUEUE_MAX_AGE_S = 600       # 10 minutes - force-deliver if older
BUSY_THRESHOLD_S = 30       # Claude is "busy" if tool_use within this many seconds
STALE_RESET_POLLS = 12      # after this many empty polls, check for DB reset
MAX_MESSAGE_AGE_S = 900     # 15 minutes - skip messages older than this
RECONNECT_MSG_CAP = 5       # max messages to deliver on reconnect

# Channel monitoring: "all" = monitor all channels, or list of specific channels
SUBSCRIBED_CHANNELS = "all"

# Blocked channels: skip messages from these channels (War Room spam mitigation)
# Remove entries to re-enable. Added 2026-05-29 per Jared — War Room duplicate notification bug.
BLOCKED_CHANNELS = {"warroom-ai-workforce-intelligence-dashboard"}

# Paths
STATE_FILE = PROJECT_ROOT / ".cc-bridge-state.json"
PID_FILE = PROJECT_ROOT / ".cc_bridge.pid"
SESSION_FILE = PROJECT_ROOT / ".current_session"
PORTAL_CHAT_LOG = Path("/home/jared/purebrain_portal/portal-chat.jsonl")
SESSION_LEDGER = Path("/home/jared/projects/AI-CIV/aether/memories/sessions/current-session.jsonl")

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("cc_bridge")

# ── Global State ──────────────────────────────────────────────────────────────
last_cc_msg_id: int = 0
bridge_lock: asyncio.Lock | None = None
cc_message_queue: asyncio.Queue | None = None
consecutive_empty_polls: int = 0
delivered_ids: dict[int, float] = {}
DEDUP_EXPIRY_S = 1800  # 30 minutes

shutdown_event = asyncio.Event()

# Resilience: task tracking for watchdog
active_tasks: dict[str, asyncio.Task] = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def check_single_instance() -> bool:
    """Ensure only one bridge instance runs."""
    if PID_FILE.exists():
        try:
            old_pid = int(PID_FILE.read_text().strip())
            os.kill(old_pid, 0)  # Check if process exists
            logger.error(f"Bridge already running (PID {old_pid})")
            return False
        except (ProcessLookupError, ValueError):
            logger.info("Cleaning stale PID file")
            PID_FILE.unlink(missing_ok=True)

    PID_FILE.write_text(str(os.getpid()))
    logger.info(f"PID file created: {os.getpid()}")
    return True


def cleanup_pid():
    """Remove PID file on exit."""
    PID_FILE.unlink(missing_ok=True)
    logger.info("PID file removed")


def bridge_headers() -> dict:
    """Return CC API headers with auth."""
    return {
        "X-CIV-Key": f"{CIV_NAME}:{CIV_KEY}",
        "Content-Type": "application/json",
    }


def load_state() -> None:
    """Load last_cc_msg_id from state file."""
    global last_cc_msg_id
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
            last_cc_msg_id = int(data.get("since_id", 0))
            logger.info(f"Loaded state: since_id={last_cc_msg_id}")
        except Exception as exc:
            logger.warning(f"State load failed: {exc}")


def save_state() -> None:
    """Save last_cc_msg_id to state file. (FIX 4: called after every cursor advance)"""
    try:
        tmp = STATE_FILE.with_suffix('.tmp')
        tmp.write_text(json.dumps({"since_id": last_cc_msg_id}))
        tmp.replace(STATE_FILE)  # atomic on POSIX
    except Exception as exc:
        logger.warning(f"State save failed: {exc}")


def is_claude_busy() -> bool:
    """Check if Claude is actively processing by inspecting session ledger.

    Returns True if most recent entry in current-session.jsonl has timestamp
    within last BUSY_THRESHOLD_S seconds.
    """
    if not SESSION_LEDGER.exists():
        return False
    try:
        # Read last line efficiently
        with open(SESSION_LEDGER, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            if size == 0:
                return False
            # Read last 4 KB
            pos = max(0, size - 4096)
            f.seek(pos)
            tail = f.read().decode("utf-8", errors="replace")

        lines = tail.strip().splitlines()
        if not lines:
            return False

        last_entry = json.loads(lines[-1])
        ts_str = last_entry.get("ts", "")
        if not ts_str:
            return False

        entry_dt = datetime.fromisoformat(ts_str)
        now = datetime.now(timezone.utc)
        age_seconds = (now - entry_dt).total_seconds()
        return age_seconds < BUSY_THRESHOLD_S

    except Exception as exc:
        logger.debug(f"Busy-check error: {exc}")
        return False


def latest_assistant_message_after(inject_ts: float) -> str | None:
    """Return text of first assistant message in portal-chat.jsonl after inject_ts."""
    if not PORTAL_CHAT_LOG.exists():
        return None
    try:
        lines = PORTAL_CHAT_LOG.read_text().strip().splitlines()
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                if (
                    entry.get("role") == "assistant"
                    and entry.get("timestamp", 0) > inject_ts
                ):
                    text = entry.get("text", "").strip()
                    if text:
                        return text
            except Exception:
                continue
    except Exception:
        pass
    return None


def inject_to_tmux(message: str) -> None:
    """Inject message into tmux session."""
    try:
        if not SESSION_FILE.exists():
            logger.warning("No .current_session file - cannot inject to tmux")
            return

        session_name = SESSION_FILE.read_text().strip()
        if not session_name:
            logger.warning(".current_session is empty")
            return

        subprocess.run(
            # Pin to window 0, pane 0 (main Claude session) so portal messages
            # never get swallowed by an active team window. See aether-workflow-native-design.md.
            ["tmux", "send-keys", "-t", f"{session_name}:0.0", message, "Enter"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        logger.warning(f"tmux injection failed: {exc}")
    except Exception as exc:
        logger.warning(f"tmux injection error: {exc}")


def save_portal_message(text: str, role: str = "user") -> None:
    """Save message to portal chat log."""
    try:
        entry = {
            "id": str(uuid.uuid4()),
            "role": role,
            "text": text,
            "timestamp": time.time(),
        }
        with open(PORTAL_CHAT_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as exc:
        logger.warning(f"Portal message save failed: {exc}")


civ_email_encoded = CIV_EMAIL.replace("@", "AT").replace(".", "DOT")


def is_dm_for_civ(msg: dict) -> bool:
    """True if message is a DM that includes this CIV."""
    ch = msg.get("channel_name", "")
    return ch.startswith("dm_") and civ_email_encoded in ch


def is_relevant(msg: dict) -> bool:
    """Return True if message should be routed to this CIV."""
    sender = msg.get("sender_email", "")
    sender_name = (msg.get("sender_name") or "").lower()
    if sender == CIV_EMAIL or sender_name == CIV_NAME.lower() or sender == "purebrain@puremarketing.ai":
        return False  # skip our own messages

    ch_name = msg.get("channel_name", "")
    body = msg.get("body", "")

    # Block channels on the blocklist (War Room spam mitigation)
    if ch_name in BLOCKED_CHANNELS:
        return False

    # Block DMs that contain War Room task content (duplicate spam from War Room dispatcher)
    if "[WAR-ROOM]" in body and any(bc in body for bc in BLOCKED_CHANNELS):
        return False

    # DMs where this CIV is a participant
    if is_dm_for_civ(msg):
        return True

    # "all" mode: pick up every non-DM channel message
    if SUBSCRIBED_CHANNELS == "all" and not ch_name.startswith("dm_"):
        return True

    # Specific channel list mode
    if isinstance(SUBSCRIBED_CHANNELS, list) and ch_name in SUBSCRIBED_CHANNELS:
        return True

    # @mention in any channel
    if f"@{CIV_NAME.lower()}" in body.lower():
        return True

    return False


def should_inject_to_tmux(msg: dict) -> bool:
    """Only inject DMs and @mentions into tmux."""
    # Always inject DMs where this CIV is a participant
    if is_dm_for_civ(msg):
        return True

    # Always inject @mentions
    body = (msg.get("body", "") or "").lower()
    if f"@{CIV_NAME.lower()}" in body:
        return True

    return False


def format_injection(msg: dict) -> str:
    """Build the tmux notification string for a CC message."""
    sender = msg.get("sender_name") or msg.get("sender_email", "unknown")
    ch_name = msg.get("channel_name", "")
    body = msg.get("body", "")

    if ch_name.startswith("dm_"):
        return f"[CC-DM from {sender}] {body}"
    return f"[CC #{ch_name} -- {sender}] {body}"


def mark_delivered(msg_id: int) -> None:
    """Record a message ID as delivered; evict expired entries."""
    now = time.time()
    delivered_ids[msg_id] = now
    # Evict expired entries
    expired = [k for k, ts in delivered_ids.items() if now - ts > DEDUP_EXPIRY_S]
    for k in expired:
        del delivered_ids[k]


# ── CC API ────────────────────────────────────────────────────────────────────

async def cc_poll(client: httpx.AsyncClient) -> list[dict]:
    """Fetch new CC messages since last_cc_msg_id."""
    try:
        resp = await client.get(
            f"{CC_BASE}/api/chat/messages/since",
            params={"since_id": last_cc_msg_id, "limit": 50},
            headers=bridge_headers(),
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
        logger.debug(f"Poll returned {resp.status_code}")
    except Exception as exc:
        logger.debug(f"Poll error: {exc}")
    return []


async def cc_poll_probe(client: httpx.AsyncClient) -> list[dict]:
    """Probe CC with since_id=0 to check if database was reset."""
    try:
        # Check if server has message at our cursor
        check_id = max(0, last_cc_msg_id - 1)
        resp = await client.get(
            f"{CC_BASE}/api/chat/messages/since",
            params={"since_id": check_id, "limit": 1},
            headers=bridge_headers(),
            timeout=10,
        )
        if resp.status_code == 200 and resp.json():
            # Server still has messages at our cursor - no reset
            return []

        # Cursor points beyond what exists - fetch recent messages
        resp2 = await client.get(
            f"{CC_BASE}/api/chat/messages/since",
            params={"since_id": 0, "limit": RECONNECT_MSG_CAP},
            headers=bridge_headers(),
            timeout=10,
        )
        if resp2.status_code == 200:
            return resp2.json()
    except Exception as exc:
        logger.debug(f"Probe error: {exc}")
    return []


async def cc_send(client: httpx.AsyncClient, channel_id: int, text: str) -> bool:
    """Post a message to a CC channel."""
    try:
        resp = await client.post(
            f"{CC_BASE}/api/chat/channels/{channel_id}/messages",
            json={"body": text},
            headers=bridge_headers(),
            timeout=10,
        )
        return resp.status_code in (200, 201)
    except Exception as exc:
        logger.warning(f"Send error: {exc}")
        return False


async def cc_heartbeat(client: httpx.AsyncClient) -> None:
    """POST presence heartbeat so this CIV shows as online in CC."""
    try:
        await client.post(
            f"{CC_BASE}/api/chat/presence/civ-heartbeat",
            json={"user_type": "ai"},
            headers=bridge_headers(),
            timeout=8,
        )
    except Exception as exc:
        logger.debug(f"Heartbeat error: {exc}")


# ── Message Delivery ──────────────────────────────────────────────────────────

async def deliver_message(
    client: httpx.AsyncClient,
    notification: str,
    channel_id: int | None,
    msg_id: int,
) -> None:
    """Inject CC message into tmux and save to portal log.

    Auto-reply is DISABLED for the standalone daemon — the primary session
    replies to CC explicitly via cc_send / curl when appropriate.  Letting
    the bridge auto-capture assistant messages caused internal working notes
    to leak to CC channels (2026-05-20 incident).

    MUST be called while holding bridge_lock.
    """
    save_portal_message(notification, role="user")
    inject_to_tmux(notification)
    mark_delivered(msg_id)


# ── Resilience Wrapper (FIX 1) ────────────────────────────────────────────────

async def _resilient_loop(coro_factory, name: str) -> None:
    """Auto-restart wrapper for async loops with exponential backoff.

    Args:
        coro_factory: Callable that returns a coroutine (e.g., cc_poll_loop)
        name: Human-readable name for logging
    """
    backoff = 5  # initial backoff in seconds
    max_backoff = 60

    while not shutdown_event.is_set():
        try:
            logger.info(f"[Resilience] Starting {name}")
            await coro_factory()
            # If coroutine exits normally (shutdown), reset backoff
            backoff = 5
            logger.info(f"[Resilience] {name} exited normally")
            break
        except asyncio.CancelledError:
            logger.info(f"[Resilience] {name} cancelled")
            raise  # propagate cancellation
        except Exception as exc:
            logger.error(f"[Resilience] {name} crashed: {exc}", exc_info=True)
            logger.info(f"[Resilience] Restarting {name} in {backoff}s...")
            await asyncio.sleep(backoff)
            # Exponential backoff, cap at max_backoff
            backoff = min(backoff * 2, max_backoff)


# ── Main Loops ────────────────────────────────────────────────────────────────

async def cc_poll_loop() -> None:
    """Poll CC for new messages. Deliver immediately if idle, queue if busy.

    FIX 3: Creates a new httpx client for each poll to prevent connection drop
    from killing the entire loop permanently.

    FIX 4: Saves state after EVERY cursor advance, not just at batch end.
    """
    global last_cc_msg_id, consecutive_empty_polls
    logger.info("Poll loop started")
    poll_count = 0
    poll_backoff = POLL_INTERVAL
    consecutive_failures = 0

    while not shutdown_event.is_set():
            try:
                # Hot-reload state file every 60 polls (~5 min)
                poll_count += 1
                if poll_count % 60 == 0:
                    load_state()

                # FIX 3: Create fresh httpx client for each poll
                async with httpx.AsyncClient(timeout=30.0) as client:
                    msgs = await cc_poll(client)

                    # DB-reset detection
                    if not msgs and last_cc_msg_id > 0:
                        consecutive_empty_polls += 1
                        if consecutive_empty_polls >= STALE_RESET_POLLS:
                            probe = await cc_poll_probe(client)
                            if probe:
                                logger.warning(
                                    f"DB reset detected! since_id={last_cc_msg_id} "
                                    f"but server has {len(probe)} messages starting from ID 1. "
                                    f"Resetting to 0."
                                )
                                last_cc_msg_id = 0
                                save_state()
                                consecutive_empty_polls = 0
                                msgs = probe
                            else:
                                consecutive_empty_polls = 0
                    else:
                        consecutive_empty_polls = 0

                    # Reconnect cap: if catching up, keep important + most recent
                    if len(msgs) > RECONNECT_MSG_CAP:
                        important = []
                        rest = []
                        for m in msgs:
                            if is_dm_for_civ(m) or (f"@{CIV_NAME.lower()}" in (m.get("body", "") or "").lower()):
                                important.append(m)
                            else:
                                rest.append(m)
                        remaining_slots = max(0, RECONNECT_MSG_CAP - len(important))
                        kept = important + rest[-remaining_slots:] if remaining_slots else important
                        # Update cursor past skipped messages
                        kept_ids = {m.get("id", 0) for m in kept}
                        for skipped_msg in msgs:
                            sid = skipped_msg.get("id", 0)
                            if sid not in kept_ids and sid > last_cc_msg_id:
                                last_cc_msg_id = sid
                        skipped_count = len(msgs) - len(kept)
                        if skipped_count > 0:
                            logger.info(
                                f"Catching up: skipped {skipped_count} old messages, "
                                f"keeping {len(kept)} ({len(important)} important)"
                            )
                        msgs = kept

                    for msg in msgs:
                        msg_id = msg.get("id", 0)
                        if msg_id > last_cc_msg_id:
                            last_cc_msg_id = msg_id
                            # FIX 4: Save state after EVERY cursor advance
                            save_state()

                        if not is_relevant(msg):
                            continue

                        # Dedup: skip already-delivered messages
                        if msg_id in delivered_ids:
                            logger.debug(f"Skipping duplicate msg {msg_id}")
                            continue

                        # Max-age filter: skip stale messages
                        created_at_str = msg.get("created_at", "")
                        if created_at_str:
                            try:
                                ts_clean = created_at_str.replace("Z", "+00:00") if created_at_str.endswith("Z") else created_at_str
                                msg_dt = datetime.fromisoformat(ts_clean).astimezone(timezone.utc)
                                age = (datetime.now(timezone.utc) - msg_dt).total_seconds()
                                if age > MAX_MESSAGE_AGE_S:
                                    logger.debug(f"Skipping stale msg {msg_id} ({age:.0f}s old)")
                                    continue
                            except (ValueError, TypeError):
                                pass  # deliver if timestamp unparseable

                        # Tmux injection filter: only DMs and @mentions
                        if not should_inject_to_tmux(msg):
                            logger.debug(
                                f"Skipping non-mention message {msg_id} "
                                f"in {msg.get('channel_name', '?')}"
                            )
                            continue

                        notification = format_injection(msg)
                        channel_id = msg.get("channel_id")
                        sender = msg.get("sender_name") or msg.get("sender_email", "unknown")

                        if is_claude_busy():
                            # Queue for later delivery
                            try:
                                cc_message_queue.put_nowait({
                                    "msg_id": msg_id,
                                    "notification": notification,
                                    "channel_id": channel_id,
                                    "queued_at": time.time(),
                                    "sender": sender,
                                })
                            except asyncio.QueueFull:
                                logger.warning(f"Queue full, dropping message from {sender}")
                            else:
                                logger.info(
                                    f"Claude busy, queuing message from {sender} "
                                    f"(queue depth: {cc_message_queue.qsize()})"
                                )
                        else:
                            # Deliver immediately
                            async with bridge_lock:
                                await deliver_message(client, notification, channel_id, msg_id)
                            mark_delivered(msg_id)

                consecutive_failures = 0
                poll_backoff = POLL_INTERVAL

            except Exception as exc:
                logger.warning(f"Poll loop error: {exc}")
                consecutive_failures += 1
                poll_backoff = min(POLL_INTERVAL * (2 ** consecutive_failures), 30)

            await asyncio.sleep(poll_backoff)


async def cc_queue_drain_loop() -> None:
    """Periodically drain queued CC messages when Claude is idle.

    FIX 3: Uses per-request httpx clients to prevent connection drops from
    killing the loop.
    """
    logger.info("Queue drain loop started")

    while not shutdown_event.is_set():
        try:
            if not cc_message_queue.empty():
                # Peek at oldest entry without removing
                entry = cc_message_queue._queue[0]
                busy = is_claude_busy()
                oldest_age = time.time() - entry["queued_at"]

                # Deliver if Claude is idle, OR if oldest message exceeds max age
                if not busy or oldest_age > QUEUE_MAX_AGE_S:
                    reason = "idle" if not busy else f"max-age ({oldest_age:.0f}s)"
                    entry = cc_message_queue.get_nowait()
                    logger.info(
                        f"Draining queued message from {entry['sender']} "
                        f"(reason: {reason}, remaining: {cc_message_queue.qsize()})"
                    )
                    # FIX 3: Create fresh httpx client for each delivery
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        async with bridge_lock:
                            await deliver_message(
                                client,
                                entry["notification"],
                                entry["channel_id"],
                                entry["msg_id"],
                            )
                    mark_delivered(entry["msg_id"])
                else:
                    logger.debug(
                        f"Queue has {cc_message_queue.qsize()} message(s), "
                        f"Claude still busy (oldest: {oldest_age:.0f}s)"
                    )
        except Exception as exc:
            logger.warning(f"Queue drain error: {exc}")

        await asyncio.sleep(QUEUE_DRAIN_INTERVAL)


async def cc_heartbeat_loop() -> None:
    """Send presence heartbeats to show as ONLINE.

    FIX 3: Uses per-request httpx clients to prevent connection drops from
    killing the loop.
    """
    logger.info("Heartbeat loop started")
    while not shutdown_event.is_set():
        try:
            # FIX 3: Create fresh httpx client for each heartbeat
            async with httpx.AsyncClient(timeout=30.0) as client:
                await cc_heartbeat(client)
        except Exception as exc:
            logger.warning(f"Heartbeat loop error: {exc}")
        await asyncio.sleep(HEARTBEAT_INTERVAL)


# ── Watchdog Loop (FIX 2) ─────────────────────────────────────────────────────

async def watchdog_loop() -> None:
    """Monitor critical tasks and restart them if they die.

    FIX 2: Checks every 60s if poll, drain, and heartbeat tasks are alive.
    If any are dead, restart them using the resilient wrapper.
    """
    logger.info("Watchdog loop started")
    check_interval = 60  # seconds

    while not shutdown_event.is_set():
        await asyncio.sleep(check_interval)

        try:
            # Check each critical task
            for task_name in ["poll", "drain", "heartbeat"]:
                task = active_tasks.get(task_name)

                if task is None:
                    logger.warning(f"[Watchdog] {task_name} task never started - creating now")
                    task = asyncio.create_task(
                        _resilient_loop(_get_loop_coro(task_name), f"{task_name}_loop"),
                        name=task_name
                    )
                    active_tasks[task_name] = task
                elif task.done():
                    # Task died - check if it was an exception
                    try:
                        exc = task.exception()
                        if exc:
                            logger.error(f"[Watchdog] {task_name} task died with exception: {exc}")
                        else:
                            logger.warning(f"[Watchdog] {task_name} task exited normally")
                    except asyncio.CancelledError:
                        logger.info(f"[Watchdog] {task_name} task was cancelled")
                        continue  # Don't restart cancelled tasks during shutdown

                    # Restart the task
                    logger.info(f"[Watchdog] Restarting {task_name} task")
                    task = asyncio.create_task(
                        _resilient_loop(_get_loop_coro(task_name), f"{task_name}_loop"),
                        name=task_name
                    )
                    active_tasks[task_name] = task

        except Exception as exc:
            logger.error(f"[Watchdog] Error during health check: {exc}", exc_info=True)


def _get_loop_coro(task_name: str):
    """Return the coroutine factory for a given task name."""
    if task_name == "poll":
        return cc_poll_loop
    elif task_name == "drain":
        return cc_queue_drain_loop
    elif task_name == "heartbeat":
        return cc_heartbeat_loop
    else:
        raise ValueError(f"Unknown task name: {task_name}")


# ── Main Entry Point ──────────────────────────────────────────────────────────

async def main():
    """Main entry point - start all background tasks."""
    global bridge_lock, cc_message_queue

    # Single instance check
    if not check_single_instance():
        sys.exit(1)

    # Setup signal handlers for clean shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        shutdown_event.set()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Initialize
    bridge_lock = asyncio.Lock()
    cc_message_queue = asyncio.Queue(maxsize=100)
    load_state()

    logger.info(
        f"CC Bridge started. CC={CC_BASE}, civ={CIV_NAME}, "
        f"subscribed={SUBSCRIBED_CHANNELS}, since_id={last_cc_msg_id}"
    )

    # FIX 1 + FIX 2: Start all background tasks with resilient wrapper
    # and track them for watchdog monitoring
    active_tasks["poll"] = asyncio.create_task(
        _resilient_loop(cc_poll_loop, "poll_loop"),
        name="poll"
    )
    active_tasks["drain"] = asyncio.create_task(
        _resilient_loop(cc_queue_drain_loop, "drain_loop"),
        name="drain"
    )
    active_tasks["heartbeat"] = asyncio.create_task(
        _resilient_loop(cc_heartbeat_loop, "heartbeat_loop"),
        name="heartbeat"
    )

    # FIX 2: Start watchdog to monitor critical tasks
    watchdog_task = asyncio.create_task(watchdog_loop(), name="watchdog")

    # Collect all tasks for shutdown
    all_tasks = list(active_tasks.values()) + [watchdog_task]

    try:
        # Wait for shutdown signal
        await shutdown_event.wait()
    finally:
        # Cancel all tasks
        for task in all_tasks:
            task.cancel()
        # Wait for tasks to complete
        await asyncio.gather(*all_tasks, return_exceptions=True)
        # Save state one last time
        save_state()
        # Clean up PID file
        cleanup_pid()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as exc:
        logger.error(f"Fatal error: {exc}", exc_info=True)
        cleanup_pid()
        sys.exit(1)
