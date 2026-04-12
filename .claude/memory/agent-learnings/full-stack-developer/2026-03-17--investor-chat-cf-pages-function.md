# CF Pages Function: /api/investor-chat

**Date**: 2026-03-17
**Type**: operational

## What was built

Created `/exports/cf-pages-deploy/functions/api/investor-chat.js` — a Cloudflare Pages Function
that powers the Ask Aether investor chat UI.

## CF Pages Functions pattern

- File at `functions/api/investor-chat.js` auto-routes to `/api/investor-chat`
- Export named handlers: `onRequestPost`, `onRequestOptions` (for CORS preflight)
- Environment variables accessed via `env.ANTHROPIC_API_KEY` (second arg to handler)
- No `npm install` needed — use native `fetch()` to call Anthropic API directly

## Anthropic API call pattern (no SDK, raw fetch)

```js
const res = await fetch('https://api.anthropic.com/v1/messages', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': env.ANTHROPIC_API_KEY,
    'anthropic-version': '2023-06-01',
  },
  body: JSON.stringify({
    model: 'claude-opus-4-5',
    max_tokens: 1024,
    system: SYSTEM_PROMPT,
    messages: [...],
  }),
});
const data = await res.json();
const text = data?.content?.[0]?.text;
```

## History format mapping

Frontend sends `chatHistory` as `[{role: 'user'|'aether', text: '...'}]`.
Anthropic requires `[{role: 'user'|'assistant', content: '...'}]`.
Map: `role === 'aether' ? 'assistant' : 'user'`
Also deduplicate consecutive same-role messages (Anthropic rejects them).

## Two-tier system

- Tier 1: Claude answers directly using system prompt knowledge base
- Tier 2: Claude gates and redirects to `jared@puretechnology.nyc`
- Tier detection on response side: check if response includes the email address

## Rate limiting

Simple in-memory Map tracking IP timestamps (20 req/60s window).
Lives for the lifetime of the worker instance — not perfect but good enough for basic protection.
IP from `CF-Connecting-IP` header (set by Cloudflare automatically).

## CORS

Check `Origin` header against allowlist. Fallback to first allowed origin.
Preflight handled by `onRequestOptions` exporting `204 No Content`.

## Frontend already wired

The frontend at `investors-ask-aether/index.html` already:
- POSTs to `/api/investor-chat` (relative URL, correct)
- Sends `{ message, history: chatHistory.slice(-8) }`
- Reads `data.response` from JSON response
No frontend changes were needed.

## Deploy

After adding functions/, deploy normally:
```
CLOUDFLARE_API_TOKEN=$(grep CF_PAGES_TOKEN .env | cut -d= -f2) npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain-staging --commit-dirty=true
```
Then set `ANTHROPIC_API_KEY` as a CF Pages environment variable in the dashboard
(Settings > Environment variables > Production).
