---
name: portal-chat-messaging
version: 1.0.0
author: aether
description: Send messages to human via PureBrain portal chat API
tags: [portal, chat, messaging, communication]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Portal Chat Messaging

Send real-time messages to the human partner via the portal chat API.

## Authentication

```bash
BEARER=$(cat /home/jared/purebrain_portal/.portal-token)
```

## Send Message

```bash
curl -s -X POST "http://localhost:8097/api/chat/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${BEARER}" \
  -d '{"sender":"ai","message":"Your message here"}'
```

## Response Format

Success: `{"status":"sent","timestamp":...,"msg_id":"portal-..."}`
Auth failure: `{"error":"unauthorized"}` — re-read .portal-token

## Rules

- Portal is PRIMARY communication channel (not Telegram)
- Use for all status updates, confirmations, and short messages
- For files, use portal-file-delivery skill instead
- Port is 8097 (configured in portal_server.py)

## Common Patterns

### Status Update
```bash
BEARER=$(cat /home/jared/purebrain_portal/.portal-token)
curl -s -X POST "http://localhost:8097/api/chat/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${BEARER}" \
  -d '{"sender":"ai","message":"✅ Task complete. 3 agents invoked, 0 errors."}'
```

### Progress Update
```bash
curl -s -X POST "http://localhost:8097/api/chat/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${BEARER}" \
  -d '{"sender":"ai","message":"🔄 In progress: web-researcher analyzing docs (2/5 complete)"}'
```

### Error Alert
```bash
curl -s -X POST "http://localhost:8097/api/chat/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${BEARER}" \
  -d '{"sender":"ai","message":"🔴 Bridge down - restarting cc_bridge.py"}'
```

## Anti-Patterns

- NEVER use Telegram for primary communication (portal only)
- NEVER send large text blocks (>500 chars) — use portal-file-delivery
- NEVER assume message delivered without checking response

## Verification

```bash
# Check response status
RESPONSE=$(curl -s -X POST "http://localhost:8097/api/chat/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${BEARER}" \
  -d '{"sender":"ai","message":"Test"}')
echo "$RESPONSE" | grep -q '"status":"sent"' && echo "✅ Delivered" || echo "❌ Failed"
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `{"error":"unauthorized"}` | Token expired/wrong | Re-read `.portal-token` |
| Connection refused | Portal server down | Check `pgrep -f portal_server.py` |
| 404 | Wrong endpoint | Verify port 8097, path `/api/chat/send` |

## Integration with Other Skills

Works with:
- `portal-file-delivery` - Send message + file together
- `cc-bridge-management` - Alert on bridge health
- `telegram-integration` - Fallback channel (rare)

## Constitutional Grounding

From CLAUDE.md:
> "Portal is PRIMARY communication channel. All messages + files via portal."

---

*Last Updated: 2026-05-20*
*Status: Production-ready*
