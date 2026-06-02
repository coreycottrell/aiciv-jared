---
name: cc-bridge-management
version: 1.0.0
author: aether
description: Manage CC bridge daemon - start, stop, health check, resilience
tags: [cc, bridge, daemon, infrastructure]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# CC Bridge Management

Manage the Command Center bridge daemon that injects CC messages into the AI portal.

## Purpose

The CC bridge (`cc_bridge.py`) polls Command Center for new messages and injects them into the PureBrain portal, enabling real-time cross-platform communication.

## Start Bridge

```bash
nohup python3 tools/cc_bridge.py >> logs/cc_bridge.log 2>&1 &
```

## Stop Bridge

```bash
pkill -f cc_bridge.py
rm -f .cc_bridge.pid
```

## Health Check

```bash
# Check if running
pgrep -f cc_bridge.py

# Check state file
cat .cc-bridge-state.json

# Check recent log
tail -20 logs/cc_bridge.log

# Check last activity
stat -c %Y .cc-bridge-state.json  # Should update every ~5s
```

## Resilience (4-Layer Pattern)

The bridge uses a 4-layer resilience architecture:

1. **Auto-restart wrapper** with exponential backoff (5s → 60s)
2. **Watchdog loop** checking task health every 60s
3. **Per-request httpx clients** (not single long-lived client)
4. **State-save** after every cursor advance

## Config (in cc_bridge.py)

```python
POLL_INTERVAL = 5         # Poll CC every 5 seconds
HEARTBEAT_INTERVAL = 60   # Watchdog check every 60 seconds
QUEUE_MAX_AGE_S = 600     # Force-deliver after 10 minutes
MAX_MESSAGE_AGE_S = 900   # Skip messages older than 15 minutes
SUBSCRIBED_CHANNELS = "all"  # Listen to all CC channels
DEDUP_EXPIRY_S = 1800     # Dedupe window: 30 minutes
```

## Common Operations

### Restart Bridge
```bash
pkill -f cc_bridge.py
rm -f .cc_bridge.pid
nohup python3 tools/cc_bridge.py >> logs/cc_bridge.log 2>&1 &
```

### Check Last Messages
```bash
# View last 20 log lines
tail -20 logs/cc_bridge.log

# Count messages in last hour
grep "Injecting message" logs/cc_bridge.log | tail -60 | wc -l
```

### Verify State File Updates
```bash
# Should show recent timestamp (within last 5-10s)
ls -lh .cc-bridge-state.json
cat .cc-bridge-state.json | jq '.last_message_id'
```

## Troubleshooting

### 401 Errors
**Cause**: Key format wrong or key rotated
**Fix**:
```bash
# Check key format in cc_bridge.py
grep "X-CIV-Key" tools/cc_bridge.py
# Should be "name:key" format, not just "key"

# Get new key from CC admin if rotated
```

### Silent Drops (No Messages Injected)
**Cause**: Watchdog loop or asyncio tasks not alive
**Fix**:
```bash
# Check watchdog log entries
grep "Watchdog:" logs/cc_bridge.log | tail -5

# Restart bridge
pkill -f cc_bridge.py && sleep 2 && nohup python3 tools/cc_bridge.py >> logs/cc_bridge.log 2>&1 &
```

### Duplicate Messages
**Cause**: Dedup window expired or state file corruption
**Fix**:
```bash
# Check dedup expiry (default 1800s = 30min)
grep "DEDUP_EXPIRY_S" tools/cc_bridge.py

# Clear state and restart if corrupted
rm -f .cc-bridge-state.json
pkill -f cc_bridge.py
nohup python3 tools/cc_bridge.py >> logs/cc_bridge.log 2>&1 &
```

### Bridge Not Starting
**Check**:
1. Port 8097 available? `lsof -i :8097`
2. Portal server running? `pgrep -f portal_server.py`
3. Python deps installed? `pip list | grep httpx`
4. Log file writable? `touch logs/cc_bridge.log`

## Monitoring

### Key Metrics

| Metric | How to Check | Healthy Value |
|--------|--------------|---------------|
| Process alive | `pgrep -f cc_bridge.py` | Returns PID |
| State file age | `stat -c %Y .cc-bridge-state.json` | <10 seconds old |
| Messages/hour | `grep "Injecting" logs/cc_bridge.log \| tail -60 \| wc -l` | Varies by activity |
| 401 errors | `grep "401" logs/cc_bridge.log \| tail -10` | None |
| Watchdog checks | `grep "Watchdog:" logs/cc_bridge.log \| tail -5` | Every ~60s |

### Automated Health Check Script

```bash
#!/bin/bash
# cc-bridge-health.sh

# Check if running
if ! pgrep -f cc_bridge.py > /dev/null; then
  echo "🔴 Bridge NOT running"
  exit 1
fi

# Check state file age
STATE_AGE=$(($(date +%s) - $(stat -c %Y .cc-bridge-state.json 2>/dev/null || echo 0)))
if [ $STATE_AGE -gt 30 ]; then
  echo "🟡 Bridge stale (state file ${STATE_AGE}s old)"
  exit 2
fi

echo "✅ Bridge healthy"
exit 0
```

## Integration with Other Skills

Works with:
- `cc-api-messaging` - Bridge uses CC API to fetch messages
- `portal-chat-messaging` - Bridge injects to portal via this API
- `telegram-integration` - Alternative bridge for Telegram

## Anti-Patterns

- NEVER run multiple bridge instances (causes duplicate messages)
- NEVER manually edit `.cc-bridge-state.json` while running
- NEVER commit CIV keys to git (bridge reads from env)

## Constitutional Grounding

From MEMORY.md:
> "TRIO Auto-Join (2026-05-13 LOCK): Every session MUST auto-announce via `tools/trio-join.sh` (SessionStart hook keeps OUTBOUND; daemons keep INBOUND)."

The CC bridge is part of the INBOUND infrastructure that keeps TRIO communication flowing.

---

*Last Updated: 2026-05-20*
*Status: Production-ready*
