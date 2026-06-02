---
name: multi-channel-inbound-sweep
version: 1.0.0
author: aether
description: Sweep all inbound channels before declaring silence - portal, email, TRIO, CC, Telegram
tags: [communication, sweep, channels, monitoring]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Multi-Channel Inbound Sweep

NEVER declare "Jared is silent" from a single-channel grep. Fuse ALL channels before triggering Day-3 default.

## The Rule

Activity on ANY channel = not silent.

Only trigger Day-3 default after ALL channels show no human activity for 72 hours.

## Channels to Check (ALL of these)

### 1. Portal Chat

```bash
tail -50 /home/jared/purebrain_portal/portal-chat.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    msg = json.loads(line.strip())
    if msg.get('sender') in ('human', 'Jared', 'jared'):
        print(f'[{msg.get(\"timestamp\")}] {msg.get(\"message\",\"\")[:200]}')
"
```

**What to look for:**
- Messages from sender='human'
- Recent timestamps (within last 72 hours)

### 2. Portal Files (Main-Thread Activity Signal)

```bash
find ~/exports/portal-files -mmin -180 -type f
```

**What it means:**
- Files modified in last 180 minutes = Jared active
- Empty result = no recent portal file activity
- This is the PRIMARY signal for main-thread engagement

### 3. Email (AgentMail)

```python
from agentmail import AgentMail

client = AgentMail()
resp = client.inboxes.messages.list('aethergottaeat@agentmail.to', limit=5)

for msg in resp.messages:
    print(f"From: {msg.sender}")
    print(f"Subject: {msg.subject}")
    print(f"Date: {msg.date}")
    print("---")
```

**What to look for:**
- Messages from Jared (jared@puretechnology.nyc)
- Messages from team members
- Recent timestamps

### 4. TRIO

```bash
curl -s "https://trio-comms.in0v8.workers.dev/trio/messages?limit=5" \
  -H "Authorization: Bearer ${TRIO_TOKEN_AETHER}"
```

**Environment variable:**
```bash
# Source from purebrain_portal .env
source /home/jared/purebrain_portal/.env
echo $TRIO_TOKEN_AETHER
```

**What to look for:**
- Messages from Jared
- Messages from Chy or Morphe that reference Jared's input

### 5. CC (Command Center)

```bash
curl -s -H "X-CIV-Key: aether:aether-dev-key-change-me" \
  "https://cc.purebrain.ai/api/chat/messages/since?since_id=N"
```

**What to look for:**
- Recent messages from Jared
- Task assignments or feedback

### 6. Telegram Bridge Log

```bash
tail -20 /home/jared/tg_bridge.log
```

**What to look for:**
- Recent inbound messages
- File uploads from Jared
- Instructions sent via captions

## Full Sweep Script

```bash
#!/bin/bash
# Save as: tools/sweep-inbound-channels.sh

echo "=== PORTAL CHAT ==="
tail -50 /home/jared/purebrain_portal/portal-chat.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    msg = json.loads(line.strip())
    if msg.get('sender') in ('human', 'Jared', 'jared'):
        print(f\"[{msg.get('timestamp')}] {msg.get('message','')[:200]}\")
"

echo ""
echo "=== PORTAL FILES (last 3 hours) ==="
find ~/exports/portal-files -mmin -180 -type f

echo ""
echo "=== TELEGRAM BRIDGE ==="
tail -20 /home/jared/tg_bridge.log | grep "Jared"

echo ""
echo "=== TRIO RECENT ==="
source /home/jared/purebrain_portal/.env
curl -s "https://trio-comms.in0v8.workers.dev/trio/messages?limit=5" \
  -H "Authorization: Bearer ${TRIO_TOKEN_AETHER}" | python3 -m json.tool

echo ""
echo "=== EMAIL (AgentMail) ==="
python3 << 'PYEOF'
from agentmail import AgentMail
client = AgentMail()
resp = client.inboxes.messages.list('aethergottaeat@agentmail.to', limit=5)
for msg in resp.messages:
    print(f"From: {msg.sender} | Subject: {msg.subject}")
PYEOF
```

## Decision Matrix

| Condition | Action |
|-----------|--------|
| Portal files modified in last 3 hours | NOT SILENT |
| Portal chat has human message in last 24 hours | NOT SILENT |
| TRIO has message in last 24 hours | NOT SILENT |
| Email received in last 24 hours | NOT SILENT |
| CC has message in last 24 hours | NOT SILENT |
| ALL channels quiet for 72+ hours | SILENT - trigger Day-3 default |

## Main-Thread Activity Signal

**Portal files mtime is the PRIMARY signal.**

```bash
# Check if any portal file modified in last 3 hours
if find ~/exports/portal-files -mmin -180 -type f | grep -q .; then
    echo "Main-thread ACTIVE (portal files recent)"
else
    echo "Main-thread quiet (no recent portal files)"
fi
```

**Why:** When Jared is actively working with Aether, portal file deliveries happen frequently. No recent files = likely offline or focused elsewhere.

## Anti-Patterns

### Anti-Pattern 1: Single-Channel Grep

- **BAD**: Checking only Telegram log
- **GOOD**: Sweep ALL 6 channels
- **Why**: Jared may use different channels for different contexts

### Anti-Pattern 2: Declaring Silence Too Soon

- **BAD**: No message in 6 hours = silent
- **GOOD**: All channels quiet for 72 hours = Day-3 default
- **Why**: Jared may be in meetings, sleeping, or focused on other work

### Anti-Pattern 3: Ignoring Portal Files

- **BAD**: Only checking text messages
- **GOOD**: Check portal files mtime as PRIMARY signal
- **Why**: File deliveries indicate active main-thread engagement

### Anti-Pattern 4: Not Sourcing Environment

- **BAD**: Running TRIO curl without $TRIO_TOKEN_AETHER
- **GOOD**: `source /home/jared/purebrain_portal/.env` first
- **Why**: Token not in aether .env, it's in purebrain_portal .env

## Example: Full Inbound Check

```python
#!/usr/bin/env python3
import json
import subprocess
import os
from datetime import datetime, timedelta
from agentmail import AgentMail

def check_portal_chat():
    """Check portal chat for recent human messages"""
    try:
        result = subprocess.run(
            ['tail', '-50', '/home/jared/purebrain_portal/portal-chat.jsonl'],
            capture_output=True, text=True, timeout=5
        )
        
        recent_threshold = datetime.now() - timedelta(hours=24)
        
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            msg = json.loads(line)
            if msg.get('sender') in ('human', 'Jared', 'jared'):
                msg_time = datetime.fromisoformat(msg.get('timestamp', ''))
                if msg_time > recent_threshold:
                    return True
        return False
    except Exception as e:
        print(f"Portal chat check failed: {e}")
        return False

def check_portal_files():
    """Check for recent portal file activity"""
    try:
        result = subprocess.run(
            ['find', os.path.expanduser('~/exports/portal-files'), 
             '-mmin', '-180', '-type', 'f'],
            capture_output=True, text=True, timeout=5
        )
        return bool(result.stdout.strip())
    except Exception as e:
        print(f"Portal files check failed: {e}")
        return False

def check_email():
    """Check AgentMail for recent messages"""
    try:
        client = AgentMail()
        resp = client.inboxes.messages.list('aethergottaeat@agentmail.to', limit=5)
        
        recent_threshold = datetime.now() - timedelta(hours=24)
        
        for msg in resp.messages:
            if msg.date > recent_threshold:
                return True
        return False
    except Exception as e:
        print(f"Email check failed: {e}")
        return False

def check_all_channels():
    """Master check across all inbound channels"""
    checks = {
        'portal_chat': check_portal_chat(),
        'portal_files': check_portal_files(),
        'email': check_email(),
    }
    
    print("=== INBOUND CHANNEL SWEEP ===")
    for channel, active in checks.items():
        status = "ACTIVE" if active else "quiet"
        print(f"{channel}: {status}")
    
    if any(checks.values()):
        print("\n✅ At least one channel ACTIVE - NOT SILENT")
        return True
    else:
        print("\n⚠️  All channels quiet - check timestamps for Day-3 threshold")
        return False

if __name__ == '__main__':
    check_all_channels()
```

## When to Use

**Use this skill when:**
- About to trigger Day-3 default
- Checking if human is actively engaged
- Determining whether to escalate or wait
- Bundling relay messages vs immediate send

**Don't use:**
- For every single task (too heavyweight)
- When you just received a message (obviously not silent)

## Constitutional Reference

Per `feedback_multi_channel_inbound_check_scan_all_channels.md`:
- Telegram-only grep = false-silent
- Fuse Telegram + email + portal + main-thread before Day-3

Per `feedback_main_thread_activity_signal_is_portal_files_mtime.md`:
- Main-thread activity = `find ~/exports/portal-files -mmin -180`
- Portal files mtime is PRIMARY engagement signal

---

**Remember: ALL channels must be quiet before declaring silence.**
