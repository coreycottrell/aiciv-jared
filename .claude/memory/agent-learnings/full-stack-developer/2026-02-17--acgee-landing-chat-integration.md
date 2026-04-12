# A-C-Gee Landing-Chat API Integration

**Date**: 2026-02-17
**Type**: operational
**Agent**: full-stack-developer
**Task**: Integrate sageandweaver-network.netlify.app/api/landing-chat into Pure Brain log server

---

## What Was Done

Modified `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` to forward
every Pure Brain conversation to the A-C-Gee shared SQLite database (sage.db on their VPS).

### Changes Made

1. **New imports**: `urllib.request`, `urllib.error`, `uuid` (all stdlib - no new dependencies)
2. **New constants** (lines 57-60):
   - `ACGEE_LANDING_CHAT_URL = 'https://sageandweaver-network.netlify.app/api/landing-chat'`
   - `ACGEE_RETRY_DELAY_SECONDS = 10`
   - `ACGEE_MAX_RETRIES = 3`
3. **New function** `forward_to_acgee(log_entry)` (lines 135-212): sends full message
   history with `source: "purebrain"`, retries up to 3x on 500 errors (rate limits)
4. **session_id generation** in `log_conversation()`: auto-generates `pb-{uuid4}` if
   no session_id provided, ensuring A-C-Gee can upsert correctly
5. **ENABLE_ACGEE_FORWARDING** config flag on app (default True)
6. **Background thread** for A-C-Gee forwarding (same non-blocking pattern as hub forwarding)
7. **Docstring updated** with 2026-02-17 change record

## API Contract

```
POST https://sageandweaver-network.netlify.app/api/landing-chat
{
  "messages": [{"role": "user", "content": "..."}, ...],
  "system": "system prompt or empty string",
  "session_id": "unique-session-id",
  "source": "purebrain"   // MUST be exactly "purebrain"
}
Response: {"content": "AI response text"}
```

## Key Decisions

- **stdlib urllib only** (not requests) - avoids new dependency, server already running
- **source field**: MUST be "purebrain" - hardcoded, never comes from client input
- **Retry only on 500** (rate limits per Corey's note) - other errors fail fast
- **Non-blocking thread** - A-C-Gee failure never breaks local JSONL logging
- **session_id fallback**: prefix `pb-` distinguishes auto-generated IDs from client IDs
- **Same session_id = upsert** on A-C-Gee side (no duplicates if client resends)

## Verified Working

- Live test against endpoint: HTTP 200 confirmed
- Response: `{"content":" Data stream initialized. All systems reporting nominal."}`
- session_id generation tested for all edge cases (none, empty, whitespace, camelCase)

## What NOT To Do

- Do NOT forward a `system` field from untrusted client data to A-C-Gee without validation
  (currently we pass `log_entry.get('system', '')` - client doesn't send system prompts
  so this is safe; if that changes, sanitize first)
- Do NOT make the A-C-Gee call synchronous - it adds latency to every log request
