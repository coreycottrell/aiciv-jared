# Telegram Bridge: Reply-To Context Feature

**Date**: 2026-02-24
**Type**: teaching
**Topic**: Added reply_to_message context injection to telegram_bridge.py

## What Was Built

When Jared replies to one of Aether's past Telegram messages, the bridge now extracts the original message text and includes it as context in the injected tmux message.

## What Aether Now Sees

When Jared replies to a past message, Aether sees:

```
[Telegram from Jared]: (replying to: "SANDBOX 688 READY FOR E2E TEST..."):
D BG - fix this thing
```

Without the feature, Aether would only see `"D BG - fix this thing"` with no context about what message Jared was responding to.

## Implementation Location

**File**: `/home/jared/projects/AI-CIV/aether/tools/telegram_bridge.py`

**Function modified**: `handle_message` (line ~821)

## Key Code Pattern

```python
# Extract reply-to context if this is a reply to a previous message
reply_to_message = message.get("reply_to_message")
reply_context = None
if reply_to_message:
    original_text = reply_to_message.get("text", "")
    if original_text:
        truncated = original_text[:200]
        if len(original_text) > 200:
            truncated += "..."
        reply_context = truncated
```

The `inject_text` is then built as:
```python
inject_text = text
if reply_context:
    inject_text = f"(replying to: \"{reply_context}\"):\n{text}"
```

This `inject_text` is used in ALL paths: tmux inject, inbox fallback, and live channel write.

## Telegram API Structure

The Telegram API includes reply context natively in the update JSON:
```json
{
  "message": {
    "text": "the reply text",
    "reply_to_message": {
      "message_id": 1234,
      "text": "the original message being replied to"
    }
  }
}
```

Note: `reply_to_message` is only present when the user explicitly replies to a message in Telegram. Regular new messages do not have this field.

## Edge Cases Handled

- `reply_to_message` absent: no context added, normal behavior preserved
- `reply_to_message.text` absent (e.g., replied to a photo/document): reply_context stays None
- Original text > 200 chars: truncated with "..." appended
- Smart commands (/help, /ping, /status, etc.) still work unchanged since reply_context is only applied to the inject_text built after the commands block

## Deployment

Bridge restarted after edit:
```bash
kill -15 <old_pid>
nohup python3 tools/telegram_bridge.py >> logs/telegram_bridge.log 2>&1 &
```

Verified running: `pgrep -f telegram_bridge.py` returned PID 695572
