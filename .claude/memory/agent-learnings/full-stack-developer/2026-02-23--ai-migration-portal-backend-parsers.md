# AI Migration Portal — Backend Parsing Pipeline

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer

---

## What Was Built

Complete backend parsing pipeline for PureBrain's AI Migration Portal (Phase 1 / MVP).

Files created in `/home/jared/projects/AI-CIV/aether/tools/migration/`:

- `__init__.py` — package init with architecture overview
- `chatgpt_parser.py` — parse OpenAI export ZIPs (conversations.json + user.json)
- `claude_parser.py` — parse Anthropic export ZIPs (handles 3 known format variants)
- `pattern_extractor.py` — frequency-based topic extraction, style detection, vocab
- `generic_parser.py` — auto-detect and parse CSV or JSON from any tool
- `migration_api.py` — FastAPI endpoints (upload, status, profile, delete)
- `tests/create_mock_exports.py` — generate test fixture ZIPs + CSVs
- `tests/test_parsers.py` — 17 tests, all passing
- `README.md` — architecture docs, API usage, integration guide

---

## Key Technical Decisions

### ChatGPT Export Format
- OpenAI stores conversations in a `mapping` dict (tree of nodes), not a flat array
- Each node has `message.author.role` and `message.content.parts` (list of strings)
- Custom instructions are in `user.json` under `custom_instructions.about_user_message` and `.about_model_message`
- Timestamps are Unix floats (not ISO strings)

### Claude Export Format
- Anthropic uses a flat array of conversations, each with `chat_messages` list
- `sender` field is "human" or "assistant" (not "user"/"assistant")
- Timestamps are ISO strings
- Claude does NOT include custom instructions in the export — accepted via separate param
- Three known format variants handled: conversation objects, flat message list, single object

### Pattern Extraction
- MVP uses keyword frequency (no LLM calls) — intentional for Phase 1 speed
- Bigrams extracted and boosted over single words when frequency >= 2
- 10 domain buckets (marketing, coding, writing, research, business, finance, design, productivity)
- Style detection via keyword matching: bullet vs prose, brief vs detailed, expert level

### FastAPI API
- Background tasks used for async file processing (synchronous worker in thread)
- In-memory job store — acceptable for MVP, replace with Redis for production
- GDPR delete endpoint removes temp files + jobs + profiles atomically
- File size validated before disk write (not after)

### Security Pattern
- Files land in `/tmp/purebrain-migration/<sanitized_user_id>/filename`
- Deleted in `finally` block after processing — always runs even on exception
- Cleanup task (cleanup_stale_jobs) should be called hourly via cron/scheduler
- API key auth via `hmac.compare_digest` to prevent timing attacks

---

## Test Results

17/17 tests passing:
- ChatGPT ZIP parse: conversation count, message count, custom instructions, error handling
- Claude ZIP parse: multi-format support, custom instructions passthrough
- Generic CSV: prompt library auto-detection
- Generic JSON: message array parsing
- Pattern extractor: topic extraction, style detection (bullet vs prose), domain vocab
- Full end-to-end pipeline: ChatGPT + Claude ZIP → user_context_profile

---

## Dependencies Required

```
fastapi          # API framework
uvicorn          # ASGI server
python-multipart # File upload support
```

Standard library only for parsers (zipfile, json, csv, re, collections) — no external deps.

---

## Integration Notes

To start the API:
```bash
MIGRATION_API_KEY=your-secret uvicorn tools.migration.migration_api:app --port 8001
```

To integrate profile with AI partner system prompt — see README.md "Integration with AI Partner" section.

Phase 2 additions needed: Notion OAuth, Canva brand kit, LLM-powered extraction, WebSocket progress.
