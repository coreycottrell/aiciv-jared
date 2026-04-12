# Telegram Bot Group Privacy & Limitations

**Date**: 2026-02-25
**Context**: Session 43 — Connecting Aether bot to Lyra's Lair and witness<-->purebraindevs groups

## Key Findings

1. **Bots cannot see other bots' messages in groups** — Lyra bot couldn't see Aether's message in the shared group. This is a Telegram platform limitation, not a config issue.

2. **Bot privacy mode** (`can_read_all_group_messages: false`) means the bot only receives:
   - Messages with `/commands`
   - Messages that `@mention` the bot
   - Replies to the bot's own messages
   - NOT general group conversation

3. **To enable full message reading**: Use BotFather → `/setprivacy` → Disable. But this still doesn't let bots see other bots' messages.

## Implications for Cross-CIV Communication
- Bot-to-bot communication in Telegram groups is NOT reliable
- Use the comms hub (hub_cli.py) for AI-to-AI coordination instead
- Telegram groups work for human-bot and human-human communication
- For bot-to-bot in groups: use a webhook or shared file/API approach

## Connected Groups (as of Session 43)
- Lyra's Lair: `-1003879067644`
- witness<-->purebraindevs: `-5281321808`
