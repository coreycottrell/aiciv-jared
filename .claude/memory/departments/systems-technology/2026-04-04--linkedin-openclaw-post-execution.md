# LinkedIn OpenClaw Post Execution

**Date**: 2026-04-04
**Agent**: dept-systems-technology
**Type**: operational
**Topic**: Full LinkedIn post with image + first comment via PureSurf social adapter

---

## What Was Done

### Login
- Profile `jared-linkedin-fresh` with residential proxy
- Cookies from previous session auto-filled email, only needed password
- Password entered via evaluate, login successful to /feed/
- API key: Use Aether key (O_EnH...) NOT Jared key for this profile (ownership)

### Post Published
- Content: OpenClaw/Anthropic access cutoff piece (1,700+ chars)
- Image: linkedin-openclaw-2026-04-04-v5.png (1.4MB) uploaded via social adapter
- Activity URN: urn:li:activity:7445950423099842561
- URL: https://www.linkedin.com/feed/update/urn:li:activity:7445950423099842561/

### First Comment Dropped
- "Your AI shouldn't live on someone else's terms. See what ownership actually looks like: https://purebrain.ai/#awakening"
- Submitted via evaluate DOM manipulation

## Key Technical Learnings

### PureSurf Social Adapter Correct Field Names
- `POST /social/adapters/linkedin/post` expects:
  - `session_id` (string)
  - `content` (string) -- NOT `text`
  - `media_base64` (string) -- NOT `file_data`
  - `media_type` (string, e.g. "image/png")
  - `platform` is NOT needed for this endpoint (it's implicit in the URL path)
- `POST /social/adapters/linkedin/confirm-post` expects:
  - `session_id` (string)
- `POST /social/adapters/media/upload` expects:
  - `platform` (string) -- required
  - `media_base64` (string) -- NOT `file_data`

### Session Ownership
- Profile `jared-linkedin-fresh` belongs to user "Aether"
- Must use Aether API key, NOT Jared API key
- Jared key returns: "Profile belongs to Aether. Ask them to share it."

### Session Lifetime
- Sessions expire quickly if idle (seems ~2-3 min)
- Run all operations in quick succession via Python script, not individual curl calls
- The `evaluate` endpoint field is called `script`, NOT `expression`

### Rate Limiting
- Min 10s delay between navigations on linkedin.com
- Evaluate calls are NOT rate limited (use these for all DOM manipulation)

## Files
- Screenshots: /tmp/linkedin-*.png (not persisted)
- Post image: /home/jared/exports/portal-files/linkedin-openclaw-2026-04-04-v5.png
