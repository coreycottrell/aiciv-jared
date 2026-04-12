# PureBrain Migration Portal — Backend Parsing Pipeline

## What This Is

The backend parsing pipeline for the PureBrain AI Migration Portal.

Users switching from ChatGPT or Claude upload their conversation history. This pipeline parses the export, extracts patterns about how the user thinks and works, and produces a `user_context_profile` JSON. That profile is fed into PureBrain's AI partner system prompt so the first conversation feels like talking to someone who already knows them.

"Your 847 ChatGPT conversations don't disappear. They become PureBrain's foundation."

---

## Architecture

```
File Upload (ZIP/CSV/JSON)
         |
         v
   ┌─────────────┐     ┌──────────────┐     ┌────────────────┐
   │chatgpt_     │     │claude_       │     │generic_        │
   │parser.py    │     │parser.py     │     │parser.py       │
   │             │     │              │     │                │
   │Parses OpenAI│     │Parses        │     │CSV or JSON     │
   │export ZIP   │     │Anthropic ZIP │     │auto-detected   │
   └──────┬──────┘     └──────┬───────┘     └───────┬────────┘
          │                   │                      │
          └───────────────────┴──────────────────────┘
                              │
                              v
                   ┌──────────────────┐
                   │pattern_          │
                   │extractor.py      │
                   │                  │
                   │Top topics        │
                   │Style detection   │
                   │Domain vocabulary │
                   └────────┬─────────┘
                            │
                            v
                   user_context_profile.json
                   (fed into AI partner system prompt)
```

---

## Files

| File | Purpose |
|------|---------|
| `chatgpt_parser.py` | Parse OpenAI export ZIPs (conversations.json + user.json) |
| `claude_parser.py` | Parse Anthropic export ZIPs |
| `pattern_extractor.py` | Extract topics, style, vocabulary from parsed conversations |
| `generic_parser.py` | Parse CSV or JSON files from any tool |
| `migration_api.py` | FastAPI endpoints for the full migration flow |
| `tests/create_mock_exports.py` | Generate test fixture files |
| `tests/test_parsers.py` | Test suite for all parsers |

---

## Output Format

### migration_profile (intermediate — from parsers)

```json
{
  "source": "chatgpt",
  "conversations": [...],
  "custom_instructions": "Be direct and use bullet points...",
  "message_count": 847,
  "conversation_count": 212,
  "date_range": {
    "start": "2022-03-15T10:00:00Z",
    "end": "2025-02-20T14:33:00Z"
  },
  "parse_errors": []
}
```

### user_context_profile (final — from pattern_extractor)

```json
{
  "source": "chatgpt",
  "conversation_count": 212,
  "message_count": 847,
  "date_range_years": 2.9,
  "date_range": { "start": "...", "end": "..." },
  "top_topics": [
    { "topic": "market analysis", "count": 23, "domain": "business" },
    { "topic": "copywriting", "count": 18, "domain": "marketing" },
    { "topic": "hiring", "count": 12, "domain": "business" }
  ],
  "communication_style": "prefers bulleted lists; concise and direct; expert-level user",
  "preferred_answer_format": "bullet",
  "domain_vocabulary": ["saas", "revenue", "conversion", "funnel", "kpi", ...],
  "custom_instructions_raw": "Be direct and concise. No preamble..."
}
```

---

## API Endpoints

```
POST   /api/migration/upload              Upload file, returns job_id
GET    /api/migration/status/:job_id      Poll processing status
GET    /api/migration/profile/:user_id    Get completed context profile
DELETE /api/migration/data/:user_id       Delete all data (GDPR erasure)
GET    /api/migration/health              Health check
```

### Auth

All endpoints require: `X-Migration-Key: <your-api-key>`

Set via environment variable: `MIGRATION_API_KEY=your-secret-key`

### Upload Example

```bash
curl -X POST https://api.purebrain.ai/api/migration/upload \
  -H "X-Migration-Key: your-api-key" \
  -F "file=@conversations.zip" \
  -F "source=chatgpt" \
  -F "user_id=user123"
```

Response:
```json
{
  "job_id": "f4a3b2c1-...",
  "status": "processing",
  "message": "File received. Processing started."
}
```

### Poll Status

```bash
curl -H "X-Migration-Key: your-api-key" \
  https://api.purebrain.ai/api/migration/status/f4a3b2c1-...
```

---

## Security

- Uploaded files stored in `/tmp/purebrain-migration/<user_id>/`
- Files deleted immediately after processing completes
- 24-hour TTL maximum (cleanup_stale_jobs() should run hourly)
- Max file sizes: 50 MB (ZIP), 10 MB (CSV/JSON)
- Allowed types: `.zip`, `.json`, `.csv` only
- API key auth on all endpoints (replace with JWT in production)
- CORS restricted to `purebrain.ai` origin

---

## Running Locally

### Install dependencies

```bash
pip install fastapi uvicorn python-multipart
```

### Start the API

```bash
MIGRATION_API_KEY=dev-key uvicorn tools.migration.migration_api:app --host 0.0.0.0 --port 8001 --reload
```

### Run tests

```bash
# Generate fixtures first
python tools/migration/tests/create_mock_exports.py

# Run tests
python tools/migration/tests/test_parsers.py

# Or with pytest
python -m pytest tools/migration/tests/test_parsers.py -v
```

---

## How Users Get Their Exports

### ChatGPT
1. ChatGPT Settings -> Data Controls -> Export Data
2. Email arrives with a ZIP download link
3. ZIP contains `conversations.json` + `user.json`

### Claude (Anthropic)
1. claude.ai -> Settings -> Account -> Export Data
2. ZIP file emailed with `conversations.json`
3. Note: Custom instructions are NOT included — user pastes them manually in the UI

---

## MVP vs Phase 2

**MVP (this pipeline):**
- ChatGPT ZIP upload
- Claude ZIP upload
- CSV/JSON generic upload
- Pattern extraction: frequency-based (no LLM calls)

**Phase 2:**
- Notion OAuth integration
- Canva brand kit import
- LLM-powered extraction (richer patterns from GPT-4 analysis)
- Real-time WebSocket progress updates

---

## Integration with AI Partner

Once the profile is built, inject it into the system prompt:

```python
profile = get_user_context_profile(user_id)

system_prompt = f"""
You are the user's AI partner. Here is what you know about them from their previous AI usage:

- They've had {profile['conversation_count']} conversations over {profile['date_range_years']} years
- Top topics: {', '.join(t['topic'] for t in profile['top_topics'][:5])}
- Communication style: {profile['communication_style']}
- Preferred format: {profile['preferred_answer_format']}

Custom instructions they previously used:
{profile.get('custom_instructions_raw', 'None provided')}

Apply this context to personalize your responses from the very first message.
"""
```
