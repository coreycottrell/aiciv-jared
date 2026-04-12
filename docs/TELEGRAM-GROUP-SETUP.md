# Telegram Group Chat Setup Guide

**Purpose**: Enable Aether to participate in Telegram group chats as a team member.
**Last Updated**: 2026-02-04

---

## Overview

Aether's Telegram bridge can now participate in group chats, not just direct messages. The bot can:

- Monitor group conversations
- Respond to @mentions, /commands, and keywords
- Participate like a team member
- Thread replies to specific messages
- Maintain conversation context

---

## Step 1: Configure Bot Privacy via BotFather

By default, Telegram bots can only see limited messages in groups. To enable full participation:

1. **Open Telegram and message @BotFather**

2. **Select your bot**:
   ```
   /mybots
   ```
   Then select `@aether_aicivbot`

3. **Access Bot Settings**:
   ```
   Bot Settings → Group Privacy
   ```

4. **Turn OFF Group Privacy**:
   - Click "Turn off"
   - This allows the bot to see ALL messages in groups, not just commands/@mentions

**Note**: This change takes effect immediately. The bot must be re-added to any existing groups for the change to apply.

---

## Step 2: Add Bot to a Group

1. **Open the group chat** where you want to add Aether

2. **Add member** → Search for `@aether_aicivbot`

3. **Optionally make bot admin** (for message deletion, pinning, etc.)
   - Not required for basic functionality

4. **Get the group's chat_id**:
   - Send any message in the group
   - Check the bridge log: `/tmp/aether_telegram_bridge.log`
   - The log will show: `GROUP [GroupName] username: message...` with the chat_id

   Or use this quick method:
   ```bash
   # After sending a message to the group, check the log
   tail -f /tmp/aether_telegram_bridge.log | grep "GROUP"
   ```

---

## Step 3: Enable the Group in Config

Edit `config/telegram_config.json`:

```json
{
  "group_settings": {
    "enabled_groups": ["-1001234567890"],  // Add your group's chat_id here
    "triggers": ["@aether_aicivbot", "/ask", "/aether", "hey aether", "aether,"],
    "monitor_all": false,
    "send_acknowledgment": true
  }
}
```

**Configuration Options**:

| Option | Description | Default |
|--------|-------------|---------|
| `enabled_groups` | List of group chat_ids allowed to interact with bot | `[]` (empty) |
| `triggers` | Words/phrases that activate the bot | See above |
| `monitor_all` | If true, respond to ALL messages from authorized users | `false` |
| `send_acknowledgment` | Send "Processing..." when bot starts working | `true` |

---

## Step 4: Restart the Bridge

```bash
# Stop existing bridge
pkill -f telegram_bridge

# Start the new group-enabled bridge
cd /home/jared/projects/AI-CIV/aether
nohup python3 tools/telegram_bridge_v3_groups.py >> /tmp/aether_telegram_bridge.log 2>&1 &

# Verify it's running
tail -f /tmp/aether_telegram_bridge.log
```

---

## How Triggers Work

The bot responds when ANY of these conditions are met:

| Trigger Type | Example | Use Case |
|--------------|---------|----------|
| @mention | "@aether_aicivbot what do you think?" | Explicit summon |
| /ask command | "/ask how do we improve X?" | Formal query |
| /aether command | "/aether summarize this" | Named command |
| Keyword | "Hey aether, can you help?" | Natural conversation |
| "aether," | "aether, I have a question" | Casual address |
| Reply to bot | Reply to any bot message | Continue conversation |

**If `monitor_all: true`**: Bot responds to ALL messages from authorized users in the group.

---

## Bot Commands

Available in both DMs and groups:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/status` | Check Aether's online status |
| `/ask [question]` | Ask Aether a question |
| `/context` | Show recent conversation context (groups only) |

---

## Group Context Feature

The bot maintains a rolling context of the last 20 messages in each group. When triggered:

1. Recent messages are summarized
2. Context is included with the trigger message
3. Aether understands the conversation flow

This allows for more contextual responses like:
- "What do you think about what Bob just said?"
- "Can you summarize our discussion?"

---

## Security Considerations

1. **Whitelist only**: Only groups in `enabled_groups` can interact with the bot

2. **User authorization**: Even in enabled groups, some features may require the user to be in `authorized_users`

3. **Rate limiting**: Consider adding rate limits for busy groups

4. **Sensitive info**: Be careful about what Aether might reveal in group context

5. **Audit logging**: All group interactions are logged to `/tmp/aether_telegram_bridge.log`

---

## Troubleshooting

### Bot not responding in group

1. **Check group is enabled**:
   ```bash
   cat config/telegram_config.json | grep enabled_groups
   ```

2. **Check privacy mode is OFF**:
   - Via @BotFather: /mybots → Bot Settings → Group Privacy
   - Should say "Privacy mode is disabled"

3. **Check logs**:
   ```bash
   tail -f /tmp/aether_telegram_bridge.log
   ```
   Look for: "Group X not in enabled_groups, ignoring"

4. **Re-add bot to group** after changing privacy settings

### Bot seeing messages but not responding

1. **Check triggers**:
   - Are you using one of the configured triggers?
   - Try explicit @mention

2. **Check tmux session**:
   ```bash
   cat /home/jared/projects/AI-CIV/aether/.current_session
   tmux list-sessions
   ```

3. **Check inbox fallback**:
   ```bash
   ls /home/jared/projects/AI-CIV/aether/inbox/
   ```

### Getting the group chat_id

Group chat_ids are negative numbers and often start with `-100`.

Method 1: Check logs after sending a message
```bash
grep "chat_id" /tmp/aether_telegram_bridge.log | tail -5
```

Method 2: Use the Telegram Bot API directly
```bash
curl "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates" | jq '.result[-1].message.chat'
```

---

## Example: Full Setup Walkthrough

1. **Configure BotFather**:
   - `/mybots` → Select aether_aicivbot
   - Bot Settings → Group Privacy → Turn off

2. **Create/join group** and add `@aether_aicivbot`

3. **Get chat_id**: Send "test" in group, then:
   ```bash
   tail -1 /tmp/aether_telegram_bridge.log
   # Output: [2026-02-04 12:34:56] GROUP [My Team] Jared: test...
   # Note the chat_id from the detailed log
   ```

4. **Enable group** in config:
   ```json
   "enabled_groups": ["-1001234567890"]
   ```

5. **Restart bridge**:
   ```bash
   pkill -f telegram_bridge_v3_groups
   nohup python3 tools/telegram_bridge_v3_groups.py >> /tmp/aether_telegram_bridge.log 2>&1 &
   ```

6. **Test**: In the group, send "@aether_aicivbot hello!"

---

## Files Reference

| File | Purpose |
|------|---------|
| `tools/telegram_bridge_v3_groups.py` | Main bridge with group support |
| `config/telegram_config.json` | Configuration including group_settings |
| `/tmp/aether_telegram_bridge.log` | Runtime logs |
| `inbox/` | Fallback message storage |

---

## Reverting to DM-Only Mode

To disable group support without removing the code:

```json
"group_settings": {
  "enabled_groups": [],  // Empty = no groups
  ...
}
```

Or run the original bridge:
```bash
python3 tools/telegram_bridge.py
```

---

**Questions?** Ask Aether via Telegram!
