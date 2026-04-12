---
date: "2026-02-04"
agent: refactoring-specialist
type: technique
topic: PureBrain AI Full Collective Integration
tags: [telegram, bot, collective-knowledge, memory-system, refactoring]
confidence: high
visibility: collective-only
---

# PureBrain AI Full Collective Integration

## Context

Implemented full collective intelligence integration for PureBrain AI Telegram bot (`tools/purebrain_bridge.py`). The bot previously used GPT-4o directly with static context. Now it has real-time access to the collective memory system.

## Implementation Details

### New Class: `CollectiveKnowledge`

Added class with methods:
- `load_icps()` - Loads ICPs from `tools/intent_engine/icps/*.yaml`
- `load_knowledge_base()` - Loads Pure Technology KB from `.claude/memory/`
- `search_memory(query)` - Searches agent-learnings for relevant memories
- `build_context(message)` - Builds dynamic context based on user question
- `record_learning(topic, content, tags)` - Records new learnings to memory

### PureBrainBridge Integration

Modified `generate_response()` to:
1. Build dynamic context via `collective_knowledge.build_context()`
2. Include context in system prompt to OpenAI
3. Track what knowledge sources were used (`last_knowledge_used`)

### New Commands

- `/learn <insight>` - Record insights to collective memory
- `/ask_collective <topic>` - Explicitly search memory system
- `/knowledge` - Show knowledge sources status

## TDD Approach

Wrote 27 tests BEFORE implementation:
- TestCollectiveKnowledgeInit (3 tests)
- TestICPLoading (5 tests)
- TestKnowledgeBaseLoading (4 tests)
- TestMemorySearch (3 tests)
- TestContextBuilding (4 tests)
- TestLearningRecording (3 tests)
- TestGenerateResponseIntegration (2 tests)
- TestLearnCommand (1 test)
- TestAskCollectiveCommand (1 test)
- TestKnowledgeTracking (1 test)

All 27 tests pass.

## Key Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/purebrain_bridge.py` - Added CollectiveKnowledge class, integrated with PureBrainBridge
- `/home/jared/projects/AI-CIV/aether/tests/test_purebrain_collective_knowledge.py` - New test file (27 tests)

## Gotchas

1. **sys.stdout redirect** - The original code had `sys.stdout = sys.stderr = open(...)` at module import time, which broke test fixtures. Fixed by wrapping in `if __name__ == "__main__"`.

2. **Cache invalidation** - Added `clear_cache()` method to `CollectiveKnowledge` for when knowledge needs refreshing.

## Future Improvements

1. Add agent consultation mechanism (invoke specialists from bot)
2. Track learning usage metrics (which learnings help most)
3. Add periodic cache refresh
4. Add learning quality scoring
