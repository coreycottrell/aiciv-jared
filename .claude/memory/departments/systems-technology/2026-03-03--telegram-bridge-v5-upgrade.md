# Telegram Bridge v5 Upgrade

**Date**: 2026-03-03
**Type**: infrastructure-upgrade
**Agent**: dept-systems-technology

## What Was Done

Upgraded `tools/telegram_bridge.py` from v4 to v5, adding three new features:

### Feature 1: Reply Context Forwarding
- Added `reply_to = message.get("reply_to_message")` extraction to ALL three handlers:
  - `handle_message` (line ~775)
  - `handle_photo` (line ~382)
  - `handle_document` (line ~481)
- Original message text truncated to 200 chars and appended to injection:
  `[Telegram from Jared] (replying to: "original text..."): new message`
- Helps Claude understand what Jared is responding to when replying to specific messages

### Feature 2: JSONL Thinking Monitor
- New state variables in `__init__` (lines 68-72):
  - `self.jsonl_dir`: `~/.claude/projects/-home-jared-projects-AI-CIV-aether`
  - `self.jsonl_file`, `self.jsonl_file_pos`: tail-like position tracking
  - `self.sent_thinking_hashes`: dedup set
  - `self.last_thinking_send`: rate limiting timestamp
- Two new helper methods: `_find_active_jsonl()`, `_chunk_text(max_size=3800)`
- New async task: `monitor_jsonl_thinking(client)` - tails the most recent JSONL log
  - Parses assistant messages, extracts `text` and `thinking` blocks
  - Skips `tool_use`, `tool_result`, and marker-wrapped content
  - Rate limited: 1 message per 3 seconds
  - Deduped via SHA256 hash (last 300 kept)
  - Chunks large messages to fit Telegram 4096 char limit
  - Prefixes forwarded thinking with 💭
- Added to `asyncio.gather()` alongside `poll_updates` and `monitor_output`

### Feature 3: tg_send.sh v2
- Full argument parser replacing the simple if/elif chain
- New flags: `--caption "text"`, `--html` (parse_mode=HTML), `--markdown`, `--reply <message_id>`
- Backward compatible: positional caption arg still works for photo/file
- `--data-urlencode` used for text messages (safe for special chars)

## Files Changed
- `/home/jared/projects/AI-CIV/aether/tools/telegram_bridge.py` (988 → 1200 lines)
- `/home/jared/projects/AI-CIV/aether/tools/tg_send.sh` (25 → 93 lines)
- Backup: `/home/jared/projects/AI-CIV/aether/tools/telegram_bridge.py.bak`

## Important: Bridge NOT Restarted
- Changes are on disk but bridge is still running v4
- Restart from main Aether session: `pkill -f telegram_bridge.py && nohup python3 tools/telegram_bridge.py >> logs/telegram_bridge.log 2>&1 &`

## JSONL Format Reference
- Lines are JSON objects
- Assistant messages: `{type: "assistant", message: {role: "assistant", content: [...]}}`
- Content block types: `text` (forward), `thinking` (forward), `tool_use` (skip), `tool_result` (skip)
- Active file: most recently modified `.jsonl` in `~/.claude/projects/-home-jared-projects-AI-CIV-aether/`
