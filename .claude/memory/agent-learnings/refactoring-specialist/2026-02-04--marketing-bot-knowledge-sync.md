---
date: 2026-02-04
agent: refactoring-specialist
type: technique
topic: marketing-bot-knowledge-sync
tags: [marketing, telegram, knowledge-sync, tdd, purebrain]
confidence: high
visibility: collective-only
---

# Marketing Bot Knowledge Sync Implementation

## Context

Built a knowledge synchronization system for @PureBrainAI_bot (Pure Technology marketing team bot). The bot was isolated and needed a way to stay updated with collective learnings.

## What Was Built

### 1. Knowledge Sync Script (`tools/sync_marketing_bot_knowledge.py`)

**KnowledgeCompiler class** that:
- Loads Pure Technology knowledge base from `.claude/memory/`
- Loads ICP configurations (Megan Patel, David Brown) from `tools/intent_engine/icps/`
- Loads marketing-team agent learnings
- Scans other agents for marketing-relevant learnings
- Generates condensed context summary for token efficiency
- Outputs to `config/marketing_knowledge.json`

### 2. Bot Integration (Updated `purebrain_bridge.py`)

- Added `load_synced_knowledge()` method
- Enhanced `load_agent_context()` to use synced knowledge
- Added `/status` command shows knowledge sync info
- Added `/sync` command (admin-only) to refresh knowledge on demand

### 3. Test Suite (`tests/test_sync_marketing_bot_knowledge.py`)

22 tests covering:
- Knowledge base loading
- ICP YAML parsing
- Marketing learnings with YAML frontmatter
- JSON file generation with timestamps and versioning
- Context summary generation
- CLI functionality

## Key Design Decisions

1. **JSON over markdown for sync file** - Easier to parse, versioned, timestamped
2. **Context summary for token efficiency** - Bot doesn't need full documents
3. **Separate sync script** - Can run manually or via cron
4. **Admin-only /sync command** - Allows hot-reload without bot restart
5. **Fallback to direct KB load** - Works even if sync hasn't run

## Usage

```bash
# Manual sync
python3 tools/sync_marketing_bot_knowledge.py

# Daily cron (add to crontab)
0 6 * * * cd /home/jared/projects/AI-CIV/aether && python3 tools/sync_marketing_bot_knowledge.py
```

## Files Created/Modified

**Created:**
- `tools/sync_marketing_bot_knowledge.py` - Main sync script
- `tests/test_sync_marketing_bot_knowledge.py` - Test suite
- `config/marketing_knowledge.json` - Generated knowledge file

**Modified:**
- `tools/purebrain_bridge.py` - Bot integration

## TDD Approach

Followed strict TDD discipline:
1. Wrote 22 failing tests first
2. Verified all failed with `ModuleNotFoundError`
3. Implemented minimum code to pass
4. All 22 tests pass (0.16s)

## Future Enhancements

- Auto-sync on memory writes (file watcher)
- Selective knowledge loading based on conversation context
- Knowledge relevance scoring
- Anthropic API support when available
