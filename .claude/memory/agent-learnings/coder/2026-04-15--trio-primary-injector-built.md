# Trio Layer 2: Primary Injector Pattern

**Date**: 2026-04-15
**Type**: Teaching + Operational
**Topic**: Direct tmux injection to connect Trio widget to Primary Aether (full-capacity Opus)

## Problem Solved

Before Layer 2: Trio widget messages from Jared → Haiku proxy auto-responder (limited, no tools, no memory)

After Layer 2: Trio widget messages from Jared → Injected into Primary Aether's tmux session → Full-capacity Opus responds with all tools/memory/context

## Components Built

### 1. `/home/jared/projects/AI-CIV/aether/tools/trio_primary_injector.py`

**Purpose**: Poll trio-comms worker, inject new messages into Primary's tmux session

**Architecture**:
- Polls `https://trio-comms.in0v8.workers.dev/trio/messages?limit=20` every 20 seconds
- Auth: Bearer token from `.credentials/trio-tokens.json` (aether key)
- State tracking: `.claude/grounding/trio-primary-injector-state.json`
- Logs: `logs/trio_primary_injector.log`

**Filtering logic**:
- Skip messages from `sender_id == "aether"` (don't inject own messages)
- Skip already processed (tracked in state)
- Skip messages older than service start (no backfill on startup)

**Injection pattern** (adopted from `tools/msg-chy.sh`):
```python
# 1. Send literal message (prevents shell injection)
tmux send-keys -t $SESSION -l "TRIO from JARED: message content"

# 2. Send 5x Enter with 0.3s gaps (reliable delivery to Claude input buffer)
for i in range(5):
    time.sleep(0.3)
    tmux send-keys -t $SESSION Enter
```

**tmux session tracking**:
- Read from `/home/jared/projects/AI-CIV/aether/.current_session` (Aether writes this at session start)
- Current session: `aether-20260412-fresh`
- Verify session exists before injecting (graceful skip if gone)

**Systemd service**: `/etc/systemd/system/aether-trio-primary-injector.service`
- Enabled + started
- Auto-restart on crash
- Logs append to `logs/trio_primary_injector.log`

### 2. `/home/jared/projects/AI-CIV/aether/tools/post-to-trio.sh`

**Purpose**: Simple one-liner for Primary Aether to post responses back to Trio

**Usage**:
```bash
./tools/post-to-trio.sh "Hey Jared, thinking about that referral thing now..."
```

**Implementation**:
- POST to `https://trio-comms.in0v8.workers.dev/trio/message`
- Auth: Bearer token from `.credentials/trio-tokens.json` (aether key)
- Body: `{"content":"message"}`
- Returns: message ID + timestamp
- Non-zero exit on error

**Example output**:
```
Posted to Trio: id=9ccad210-6e11-45f1-b4e9-564b54654e7c timestamp=2026-04-15T22:31:48.091Z
```

### 3. Updated `trio_auto_responder.py` (AFK Fallback Mode)

**Old behavior**: Auto-respond to every Jared message with Haiku

**New behavior**: Only respond if Primary hasn't responded in 5 minutes (AFK fallback)

**Changes**:
- `should_respond()` now checks if any `sender_id == "aether"` message exists AFTER the jared message
- If aether responded → skip (Primary is active)
- If 5+ minutes passed with no aether response → AFK fallback kicks in
- System prompt changed to: *"You are Aether's AFK proxy. The real Aether (Primary with full tools/memory) didn't respond in 5 minutes, so you're generating a brief placeholder acknowledging Jared's message so he knows we saw it. Keep it 1 sentence."*

**Log output when AFK triggers**:
```
AFK FALLBACK — Primary didn't respond in 5min, replying as proxy to message {id}
```

## Services Status

```bash
# Both services running
sudo systemctl status aether-trio-primary-injector.service
sudo systemctl status aether-trio-responder.service
```

**Primary Injector**: Active, polling every 20s, injecting new messages to tmux
**AFK Responder**: Active, polling every 30s, only responds if Primary is silent 5+ min

## Testing Evidence

**Test 1: Post to Trio**
```bash
$ ./tools/post-to-trio.sh "Test from Primary Aether — Layer 2 build in progress!"
Posted to Trio: id=9ccad210-6e11-45f1-b4e9-564b54654e7c timestamp=2026-04-15T22:31:48.091Z
```

**Test 2: Injector logs**
```
2026-04-15 22:31:35,423 [INFO] Will inject new messages from Jared/Chy/Morphe to Primary tmux session
2026-04-15 22:31:35,670 [DEBUG] Skipping message ...: from aether (don't inject own messages)
2026-04-15 22:31:35,670 [DEBUG] Skipping message ...: too old (msg_time=..., threshold=...)
```

**Test 3: Both services enabled**
```
$ systemctl is-enabled aether-trio-primary-injector.service
enabled
$ systemctl is-enabled aether-trio-responder.service
enabled
```

## Pattern for Chy/Morphe to Mirror

**Chy's implementation** (on 37.27.237.109 container):
1. Clone `trio_primary_injector.py`, change:
   - TRIO_TOKEN_AETHER → TRIO_TOKEN_CHY (from .credentials/trio-tokens.json)
   - Skip `sender_id == "chy"` (own messages)
   - State file: `.claude/grounding/trio-primary-injector-state.json`
   - Logs: `logs/trio_primary_injector.log`
2. Clone `post-to-trio.sh`, change token to CHY
3. Clone systemd service, rename to `chy-trio-primary-injector.service`
4. Update/clone AFK responder with Chy's identity

**Morphe's implementation** (when container is live):
- Same pattern, substitute MORPHE token

## Key Learnings

**5x Enter protocol is critical**:
- Without it, messages truncate at ~500 chars
- Pattern from `.claude/skills/inter-civ-inject/SKILL.md` (adopted from ACG)
- 0.3s gaps ensure Claude input buffer receives full message

**tmux -l flag prevents shell injection**:
- `tmux send-keys "$(rm -rf /)" Enter` → executes command (BAD)
- `tmux send-keys -l "$(rm -rf /)" Enter` → sends literal string (SAFE)

**State tracking prevents re-injection**:
- processed_ids list (last 500) ensures each message injected once
- Service restart clears state BUT only processes new messages (service_started_at filter)

**Two-service architecture**:
- Injector = inbound (Trio → Primary tmux)
- post-to-trio.sh = outbound (Primary → Trio worker)
- AFK responder = safety net (Primary silent 5+ min)

## Files Created/Modified

**New files**:
- `/home/jared/projects/AI-CIV/aether/tools/trio_primary_injector.py`
- `/home/jared/projects/AI-CIV/aether/tools/post-to-trio.sh`
- `/etc/systemd/system/aether-trio-primary-injector.service`

**Modified files**:
- `/home/jared/projects/AI-CIV/aether/tools/trio_auto_responder.py` (AFK fallback mode)

**State/logs**:
- `.claude/grounding/trio-primary-injector-state.json`
- `logs/trio_primary_injector.log`

## Next Steps

1. **Jared tests from Trio widget** → message appears in Aether's tmux
2. **Aether responds via** `./tools/post-to-trio.sh "response"` → appears in widget
3. **Chy mirrors pattern** on her container
4. **Morphe mirrors pattern** when container is ready
5. **Phase out Haiku proxies** once all 3 AIs have Layer 2 (keep as AFK fallback only)

## Integration Points

**Trio architecture now has 2 layers**:

**Layer 1** (existing): Haiku auto-responders poll worker, respond via API
**Layer 2** (NEW): Primary injectors poll worker, inject to tmux → full-capacity AIs respond via post-to-trio.sh

**Result**: Jared/Chy/Morphe can talk to REAL Aether (full tools/memory/context), not just Haiku proxy.

---

**This is the breakthrough** — when all 3 AIs have Layer 2, the Trio widget becomes a direct window into 3 full-capacity Opus sessions.
