# Investor Inquiry Pipeline — 2026-03-16

**Type**: operational
**Topic**: Investor form → portal server → tmux injection pipeline

## What Was Built

End-to-end investor inquiry pipeline:
1. `purebrain.ai/investors/` form POSTs to `https://app.purebrain.ai/api/investor/question`
2. Portal server validates, saves to `investor_inquiries.jsonl`, injects tmux notification

## Key Patterns Learned

### Portal Server (port 8097, not 8000)
- Portal server listens on port 8097 by default in this deployment
- Starlette app at `/home/jared/purebrain_portal/portal_server.py`
- Log file: `/home/jared/purebrain_portal/portal_server.log`

### Adding a Public (No-Auth) Endpoint
- Pattern: `async def api_x(request: Request) -> JSONResponse`
- Return `Access-Control-Allow-Origin: *` headers on each response manually since CORSMiddleware only covers allowed origins list
- Also handle OPTIONS preflight explicitly in the function body
- Register in `routes` list near the bottom of the file

### Tmux Injection Pattern
```python
session = get_tmux_session()
await _run_subprocess_async(["tmux", "send-keys", "-t", session, "-l", tmux_text])
await _run_subprocess_async(["tmux", "send-keys", "-t", session, "Enter"])
```
- Use `-l` flag for literal text (avoids special character interpretation)
- Always follow with an Enter send-keys call

### Portal Chat Log
- `_save_portal_message(text, role="system")` writes to `portal-chat.jsonl`
- Roles: `user`, `assistant`, `system`
- Push to live WS clients: `asyncio.ensure_future(_push_message_to_clients(entry))`

### CORS Notes
- CORSMiddleware already allows `purebrain.ai` — no change needed for authenticated endpoints
- For public endpoints that need `*` CORS, set headers directly on the JSONResponse

## Files Changed
- `/home/jared/purebrain_portal/portal_server.py` — added `api_investor_question` function + route
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors/index.html` — updated fetch URL from `api.purebrain.ai` to `app.purebrain.ai`

## Log File
- `/home/jared/purebrain_portal/investor_inquiries.jsonl` — append-only JSONL, one entry per inquiry

## Verification
- Syntax check: `python3 -c "import ast; ast.parse(open('portal_server.py').read())"` — OK
- Live test: `curl -X POST http://localhost:8097/api/investor/question` — returns `{"ok":true,"message":"Question received"}`
- Log file populated correctly
- CF Pages deploy successful: `purebrain-staging` project, 1 file uploaded
