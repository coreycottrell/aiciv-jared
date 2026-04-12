# Portal Blind Spot: Subagent JSONL Files Hiding Main Conversation

**Date**: 2026-03-20
**Type**: bug-fix / operational gotcha
**Severity**: Critical (complete communication break)

## The Bug

Portal server uses `_parse_all_messages()` which calls `_get_all_session_log_paths(max_files=1)`.

This reads ONLY the single most recently modified JSONL file from `~/.claude/projects/`.

**The problem**: Every time a subagent runs (BOOP, ST# dispatch, task-decomposer, etc.), Claude Code creates a NEW JSONL file for that subagent's conversation. That file becomes the most recently modified JSONL.

The portal then reads the subagent's JSONL (which has ~3-10 messages) instead of the main conversation JSONL (which has 100-200 messages). Result: Jared sees no responses in the portal.

## The Fix

Changed `max_files=1` to `max_files=3` in `_parse_all_messages()` at line 797 of `portal_server.py`.

This makes the portal read the top 3 most-recently-modified JSONL files, ensuring the main conversation is always captured even when newer subagent files exist.

The message deduplication logic (by UUID) handles any overlap cleanly.

## File Changed

`/home/jared/purebrain_portal/portal_server.py` — line 797
Backup: `portal_server.py.bak-subagent-jsonl-fix-20260320`

## Verification

After fix: portal returned 200 messages (155 assistant + 45 user) including latest responses.
Portal API at `/api/chat/history?last=200` confirmed working.
Telegram confirmation sent successfully.

## Trigger Pattern

This bug fires any time:
1. Aether runs a BOOP scheduled task
2. ST# or any department manager spawns a subagent
3. Any background agent creates a new Claude Code session

The symptom is always the same: Jared sees old messages or only subagent messages in the portal.

## Future Hardening

If this continues to be an issue, consider:
1. Using `max_files=5` instead of 3 for more coverage
2. Having the portal prefer the LARGEST file (main conversation is always biggest)
3. Filtering out files smaller than a threshold (e.g., <100KB) unless they're the only option
