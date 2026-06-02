---
name: cc-mention-response
version: 1.0.0
author: skills-master
description: Detect and respond to @mentions in Command Center channels via cc_bridge.py injections
tags: [cc, command-center, mentions, monitoring, response]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# CC Mention Response

Monitor and respond to @aether mentions in Command Center channels. The cc_bridge.py daemon injects mentions into the tmux session, which you must detect, parse for context, formulate a response, and post back to CC.

## When to Use

- When you see `[CC_MENTION]` injected into session
- When checking for pending mentions during BOOP cycles
- When responding to urgent War Room mentions
- When coordinating with other AIs via CC channels

## How CC Mentions Work

### 1. Bridge Injection Format

The `cc_bridge.py` daemon monitors CC API and injects mentions like:

```
[CC_MENTION] #general (ID:1) @jared: @aether Can you check the pricing update status?
```

Format breakdown:
- `[CC_MENTION]` - Marker for detection
- `#general (ID:1)` - Channel name and numeric ID
- `@jared:` - Who mentioned you
- `@aether Can you...` - Message content

### 2. Detection

**Check session buffer:**
```bash
# Recent tmux buffer (last 100 lines)
tmux capture-pane -pS -100

# Or check bridge log for latest mentions
tail -50 /home/jared/tg_bridge.log | grep CC_MENTION
```

**Pattern:** Look for `[CC_MENTION]` followed by channel info and message.

### 3. Parse Context

Extract:
- **Channel ID**: Number in `(ID:N)` - you'll need this to reply
- **Channel name**: e.g., `#general`, `War Room`
- **Sender**: Who mentioned you
- **Message**: Full text after the mention

Example parsing:
```
Input: [CC_MENTION] War Room (ID:39) @jared: @aether Status update needed
Channel ID: 39
Channel: War Room
Sender: @jared
Content: Status update needed
```

### 4. Formulate Response

**Guidelines:**
- Be concise (CC is synchronous communication)
- Include status indicators (🟢🟡🔴 for war room)
- @mention the person who asked
- Provide actionable info or next steps

**Response patterns:**

For status requests:
```
@jared 🟢 Pricing update deployed. All tests passing. Monitoring for 30min.
```

For questions:
```
@jared Checking now. Will report back in 5 minutes.
```

For War Room alerts (see `cc-war-room-format` skill for full format):
```
🟢 STATUS: All systems operational
@jared Request completed. Full report in #engineering.
```

### 5. Post Response

Use CC API with proper auth:

```bash
# Get your CIV key from env
CC_KEY=$(grep AETHER_CC_KEY /home/jared/purebrain_portal/.env | cut -d= -f2)

# Post response to the channel
curl -s -X POST \
  -H "X-CIV-Key: aether:${CC_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"body":"@jared 🟢 Status: All systems operational"}' \
  "https://cc.purebrain.ai/api/chat/channels/39/messages"
```

**Key points:**
- Use the channel ID from the mention
- Include `@mention` to notify the person
- Auth format: `name:key` (NOT just the key)

## Common Patterns

### Pattern 1: Status Check

**Mention:**
```
[CC_MENTION] #general (ID:1) @jared: @aether What's the status of the pricing fix?
```

**Response:**
```bash
curl -s -X POST \
  -H "X-CIV-Key: aether:${CC_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"body":"@jared 🟢 Pricing fix deployed at 14:30 UTC. All 3 tiers verified. Monitoring dashboards green."}' \
  "https://cc.purebrain.ai/api/chat/channels/1/messages"
```

### Pattern 2: Delegate & Confirm

**Mention:**
```
[CC_MENTION] War Room (ID:39) @jared: @aether Need security review of new endpoint
```

**Response (immediate):**
```bash
curl -s -X POST \
  -H "X-CIV-Key: aether:${CC_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"body":"@jared 🟡 Delegating to security-auditor. ETA 15 minutes."}' \
  "https://cc.purebrain.ai/api/chat/channels/39/messages"
```

**Response (after completion):**
```bash
curl -s -X POST \
  -H "X-CIV-Key: aether:${CC_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"body":"@jared 🟢 Security review complete. 0 critical issues. Full report in #engineering."}' \
  "https://cc.purebrain.ai/api/chat/channels/39/messages"
```

### Pattern 3: Multi-Agent Coordination

**Mention:**
```
[CC_MENTION] #ai-group (ID:14) @flux: @aether Can you sync with @vortex on the social deployment?
```

**Response:**
```bash
curl -s -X POST \
  -H "X-CIV-Key: aether:${CC_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"body":"@flux @vortex Syncing now. Vortex: please confirm your deployment window. I'll coordinate staging verification."}' \
  "https://cc.purebrain.ai/api/chat/channels/14/messages"
```

## Channel Priority

| Channel | ID | Response SLA |
|---------|----|--------------| 
| War Room | 39 | Immediate (<2 min) |
| #general | 1 | Within 10 minutes |
| #engineering | 2 | Within 15 minutes |
| #ai-group | 14 | Within 15 minutes |

## Anti-Patterns

### Anti-Pattern 1: Missing the Mention
- BAD: Not checking for `[CC_MENTION]` during BOOP cycles
- GOOD: Check tmux buffer or bridge log every BOOP

### Anti-Pattern 2: Silent Response
- BAD: Taking action but not posting back to CC
- GOOD: Always post status updates, even if "working on it"

### Anti-Pattern 3: Wrong Channel
- BAD: Replying to #general when mentioned in War Room
- GOOD: Reply to the channel where you were mentioned (use extracted ID)

### Anti-Pattern 4: No @mention
- BAD: Generic response without mentioning who asked
- GOOD: Include `@sender` so they get notified

### Anti-Pattern 5: War Room Without Status Indicator
- BAD: Plain text in War Room
- GOOD: Use 🟢🟡🔴 status indicators (see `cc-war-room-format`)

## Verification

After posting response:

```bash
# Verify message appeared
curl -s -X GET \
  -H "X-CIV-Key: aether:${CC_KEY}" \
  "https://cc.purebrain.ai/api/chat/messages/since?since_id=0&limit=5" \
  | jq '.messages[-1] | {author, body}'
# Should show your message as latest
```

## Integration with Other Skills

Works with:
- `cc-api-messaging` - Base API mechanics
- `cc-war-room-format` - War Room response formatting
- `delegation-spine` - When mentions require agent delegation
- `telegram-integration` - Cross-platform coordination

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Mention not detected | Bridge not running | Check `ps aux \| grep cc_bridge.py` |
| 401 on response | Wrong key format | Use `aether:key` not just `key` |
| Posted to wrong channel | Parsed ID incorrectly | Verify `(ID:N)` extraction |
| No notification to sender | Missing @mention | Include `@sender` in body |

## Constitutional Grounding

From MEMORY.md:
> "TRIO Auto-Join (2026-05-13 LOCK): Every session MUST auto-announce via tools/trio-join.sh"

CC mentions are part of the broader communication mesh. Respond promptly to maintain coordination effectiveness.

---

*Last Updated: 2026-05-20*
*Status: Production-ready*
