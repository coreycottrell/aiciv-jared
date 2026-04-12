# Claude Code JSONL Format: Correct Entry Type for Assistant Messages

**Date**: 2026-02-27
**Type**: gotcha
**Topic**: Claude Code JSONL session file format — how to correctly extract assistant thinking/text

---

## The Gotcha

When reading Claude Code JSONL session files to extract assistant responses, the entry structure is:

```json
{
  "type": "assistant",
  "message": {
    "role": "assistant",
    "content": [...]
  }
}
```

NOT:
```json
{
  "type": "message",
  "role": "assistant"
}
```

The `role` field is INSIDE `entry['message']['role']`, not at the top level.
There is no `type=message` entry type in Claude Code JSONL.

## Thinking Block Field Name

For `thinking` content blocks, the text lives in the `thinking` field, not `text`:

```python
# WRONG - thinking is empty string
item.get('type') == 'thinking'
item.get('text', '')  # always ''

# CORRECT
item.get('type') == 'thinking'
item.get('thinking', '')  # has the actual reasoning text
```

## Top-Level Entry Types in Claude Code JSONL

- `assistant` - assistant responses (text, thinking, tool_use blocks)
- `user` - user messages AND tool results (tool results have type='user' with tool_use_id)
- `progress` - streaming progress (bash_progress, agent_progress, hook_progress)
- `queue-operation` - task queue operations
- `file-history-snapshot` - file state snapshots

## Content Block Types in Assistant Messages

- `text` - visible response text, field: `item['text']`
- `thinking` - internal reasoning, field: `item['thinking']`
- `tool_use` - tool calls (bash, read, write etc), fields: `item['name']`, `item['input']`

## Correct Extraction Pattern

```python
if entry.get('type') == 'assistant':
    msg = entry.get('message', {})
    if isinstance(msg, dict) and msg.get('role') == 'assistant':
        content = msg.get('content', [])
        for item in content:
            if item.get('type') == 'text':
                text = item.get('text', '')
            elif item.get('type') == 'thinking':
                text = item.get('thinking', '')
            # skip tool_use
```

## Context

Found while fixing the Telegram bridge's thinking-forward mode.
The JSONL monitor was completely broken (0 matches) because of the wrong type check.
After fix: correctly extracts both text and thinking blocks from assistant entries.

Applied fix: `/home/jared/projects/AI-CIV/aether/tools/telegram_bridge.py`
Method: `extract_responses_from_jsonl()`
