# Telegram Group Chat Integration

**Type**: technique
**Date**: 2026-02-04
**Agent**: tg-bridge
**Topic**: Enabling bot participation in Telegram group chats

---

## Context

Jared requested the ability for Aether to participate in Telegram group chats, not just direct messages. This enables team collaboration scenarios where the AI can monitor discussions and respond when summoned.

## What Worked

### 1. Group Privacy Mode Configuration

Telegram bots have "privacy mode" enabled by default, which limits what messages they see in groups:
- With privacy ON: Only commands (/) and @mentions
- With privacy OFF: ALL messages in the group

**Configuration via BotFather**:
```
/mybots -> select bot -> Bot Settings -> Group Privacy -> Turn OFF
```

Note: Bot must be re-added to groups after changing this setting.

### 2. Trigger System Design

Implemented flexible trigger detection:
```python
def should_respond_to_group_message(self, text, message):
    # @mention: "@aether_aicivbot question"
    # Commands: "/ask question" or "/aether question"
    # Keywords: "hey aether, ..." or "aether, ..."
    # Reply: responding to bot's previous message
```

This balances:
- Not spamming the group (requires explicit trigger)
- Natural conversation flow (multiple trigger styles)
- Continuity (reply threading)

### 3. Group Context Tracking

Maintained rolling context of last 20 messages per group:
```python
self.group_contexts = defaultdict(list)  # {chat_id: [recent_messages]}
```

This enables contextual responses like "What do you think about Bob's point?"

### 4. Threaded Replies

Used `reply_to_message_id` to thread bot responses:
```python
await self.send_message(client, chat_id, response,
                       reply_to_message_id=trigger_message_id)
```

This keeps group conversations organized.

### 5. Security: Whitelist-Only Groups

Groups must be explicitly enabled in config:
```json
"group_settings": {
  "enabled_groups": ["-1001234567890"]
}
```

Bot ignores messages from non-whitelisted groups.

## Key Learnings

1. **Group chat_ids are negative**: Usually start with `-100` for supergroups
2. **Privacy changes require re-add**: Bot must be removed and re-added to groups after changing privacy
3. **Context injection format matters**: Added group name and username to help Claude understand the source
4. **Acknowledgment messages are optional**: Some groups may want silent processing

## File Locations

| File | Purpose |
|------|---------|
| `tools/telegram_bridge_v3_groups.py` | Main implementation with group support |
| `config/telegram_config.json` | Config with `group_settings` section |
| `tools/get_telegram_group_id.py` | Helper to discover group chat_ids |
| `docs/TELEGRAM-GROUP-SETUP.md` | Complete setup documentation |

## Usage

### Enable a Group

1. Turn off privacy via @BotFather
2. Add bot to group
3. Get chat_id using helper script or logs
4. Add to `enabled_groups` in config
5. Restart bridge with: `python3 tools/telegram_bridge_v3_groups.py`

### Test

In enabled group:
- "@aether_aicivbot hello!"
- "/ask what time is it?"
- "Hey aether, summarize our discussion"

## Future Enhancements

- Rate limiting per group
- Per-group trigger customization
- Admin-only commands
- Mute/unmute functionality
- Message reactions (thumbs up, etc.)

---

**Recommendation**: Start with `monitor_all: false` and explicit triggers. Enable `monitor_all` only for small, trusted groups where constant participation is desired.
