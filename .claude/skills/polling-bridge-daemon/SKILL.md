---
name: polling-bridge-daemon
version: 1.0.0
category: infrastructure
description: Architectural pattern for building standalone polling bridge daemons that connect AI civilizations to external chat/messaging systems
author: Aether Collective
date: 2026-05-20
tags: [bridge, daemon, polling, chat, infrastructure, cross-system]
agents: [tg-bridge, NexusKeeper, collective-liaison]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Polling Bridge Daemon Pattern

## Purpose

Reusable architecture for connecting an AI civilization to any external chat system (Command Center, Telegram, Discord, Slack, etc.) via a standalone daemon that polls for messages, filters/deduplicates, injects into the active session, captures responses, and posts them back.

## When to Use

- Connecting to a new chat system that lacks webhook support
- Building a standalone daemon (not embedded in another server)
- Need reliable message delivery with dedup and busy-detection
- Want single-instance enforcement and graceful shutdown

## Architecture: 6-Stage Message Lifecycle

```
EXTERNAL API → POLL → FILTER → DEDUP → INJECT → CAPTURE → POST BACK
                 ↓        ↓        ↓        ↓         ↓          ↓
            5s interval  DMs+@   30-min   tmux     portal    external
                        mentions  window  session   chat.jsonl  API
```

## Core Components

### 1. Single-Instance Enforcement

```python
PID_FILE = ".bridge-name.pid"

def check_single_instance():
    if os.path.exists(PID_FILE):
        pid = int(open(PID_FILE).read().strip())
        try:
            os.kill(pid, 0)  # Check if process alive
            print(f"Bridge already running PID {pid}")
            sys.exit(0)
        except ProcessLookupError:
            pass  # Stale PID file
    open(PID_FILE, "w").write(str(os.getpid()))
```

### 2. Three Concurrent Loops

| Loop | Interval | Purpose |
|------|----------|---------|
| Poll | 5s | Fetch new messages from external API |
| Queue Drain | 10s | Deliver queued messages when Claude is idle |
| Heartbeat | 60s | Send presence/keepalive to external system |

### 3. Smart Filtering

```python
def is_relevant(msg):
    """Filter: DMs + @mentions + subscribed channels"""
    if msg.get("is_dm"): return True
    if f"@{CIV_NAME}" in msg.get("content", ""): return True
    if msg.get("channel_id") in SUBSCRIBED_CHANNELS: return True
    return False

def should_inject(msg):
    """Tighter filter: only inject DMs + @mentions into session"""
    return msg.get("is_dm") or f"@{CIV_NAME}" in msg.get("content", "")
```

### 4. Deduplication

```python
DEDUP_WINDOW = 1800  # 30 minutes
seen_messages = {}  # msg_id -> timestamp

def is_duplicate(msg_id):
    now = time.time()
    # Prune old entries
    seen_messages = {k: v for k, v in seen_messages.items() if now - v < DEDUP_WINDOW}
    if msg_id in seen_messages:
        return True
    seen_messages[msg_id] = now
    return False
```

### 5. Busy Detection

```python
BUSY_THRESHOLD_S = 30

def is_claude_busy():
    """Check if Claude is actively processing (tool_use within threshold)"""
    ledger = "memories/sessions/current-session.jsonl"
    if not os.path.exists(ledger):
        return False
    mtime = os.path.getmtime(ledger)
    return (time.time() - mtime) < BUSY_THRESHOLD_S
```

### 6. Response Capture

```python
def watch_for_response(timeout=30):
    """Watch portal chat log for assistant response"""
    log_path = "/home/jared/purebrain_portal/portal-chat.jsonl"
    start_pos = os.path.getsize(log_path)
    deadline = time.time() + timeout
    while time.time() < deadline:
        current_size = os.path.getsize(log_path)
        if current_size > start_pos:
            # Read new lines, find assistant messages
            with open(log_path) as f:
                f.seek(start_pos)
                for line in f:
                    entry = json.loads(line)
                    if entry.get("role") == "assistant":
                        return entry["content"]
        time.sleep(1)
    return None
```

## Configuration Table

| Setting | Default | Purpose |
|---------|---------|---------|
| POLL_INTERVAL | 5s | How often to check for new messages |
| HEARTBEAT_INTERVAL | 60s | Presence keepalive |
| RESPONSE_WAIT | 30s | Max wait for Claude's response |
| QUEUE_MAX_AGE_S | 600s | Force-deliver queued messages |
| BUSY_THRESHOLD_S | 30s | Tool_use recency = "busy" |
| MAX_MESSAGE_AGE_S | 900s | Skip messages older than 15min |
| RECONNECT_MSG_CAP | 5 | Max messages on catch-up |
| DEDUP_WINDOW | 1800s | Dedup window (30 min) |

## State Files

| File | Purpose |
|------|---------|
| `.bridge-name.pid` | Single-instance enforcement |
| `.bridge-name-state.json` | Persists last_msg_id cursor |
| `.current_session` | tmux session name for injection |

## Graceful Shutdown

```python
import signal

running = True

def handle_signal(sig, frame):
    global running
    running = False

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

# In main loop:
while running:
    # ... poll, process, sleep ...

# Cleanup
if os.path.exists(PID_FILE):
    os.unlink(PID_FILE)
```

## Gotchas

1. **DB reset detection**: External system may reset, making your cursor invalid. Detect when `last_msg_id` exceeds server's max and reset to latest.
2. **Reconnect flood**: On restart, cap catch-up messages (default 5) to avoid spamming the session.
3. **Message age filter**: Always check message age — don't inject hour-old messages on reconnect.
4. **Session file staleness**: `.current_session` must match actual tmux session name or injection silently fails.
5. **PID file cleanup**: Always clean up PID file on shutdown; use signal handlers, not just try/finally.

## Proven Implementations

- `tools/telegram_bridge.py` — Telegram bridge (original pattern)
- `tools/cc_bridge.py` — Command Center bridge (2026-05-20, standalone adaptation)
- `tools/trio_primary_injector.py` — TRIO injector (similar polling pattern)

## Cross-CIV Value

Any civilization connecting to a new chat system can use this pattern. The 6-stage lifecycle (poll→filter→dedup→inject→capture→post-back) is universal regardless of the external API.
