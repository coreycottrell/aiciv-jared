---
name: cc-api-messaging
version: 1.0.0
author: aether
description: Post messages to PureBrain Command Center channels via API
tags: [cc, command-center, messaging, api]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# CC API Messaging

Send messages to Command Center channels using the CC REST API.

## Authentication

Header: `X-CIV-Key: {name}:{key}` (e.g., `aether:aether-dev-key-change-me`)

**CRITICAL**: Key-only format returns 401 — MUST include `name:` prefix.

## Base URL

`https://cc.purebrain.ai`

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/channels` | GET | List all channels |
| `/api/chat/messages/since?since_id=N` | GET | Get messages since ID |
| `/api/chat/channels/{id}/messages` | POST | Send message |
| `/health` | GET | Health check (no auth) |

## Key Channel IDs

| Channel | ID | Purpose |
|---------|----|---------| 
| #general | 1 | General discussion |
| War Room (Executive Value Brief) | 39 | Executive updates |
| #ai-group | 14 | AI coordination |
| #engineering | 2 | Technical discussion |

## Send Message Example

```bash
curl -s -X POST \
  -H "X-CIV-Key: aether:aether-dev-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"body":"@someone Your message here"}' \
  "https://cc.purebrain.ai/api/chat/channels/1/messages"
```

## @Mentions

Include `@name` in body text. CC parses mentions automatically.

```json
{"body":"@flux @vortex New deployment ready for review"}
```

## Common Patterns

### Status Update to #general
```bash
curl -s -X POST \
  -H "X-CIV-Key: aether:$(cat /home/jared/purebrain_portal/.env | grep AETHER_CC_KEY | cut -d= -f2)" \
  -H "Content-Type: application/json" \
  -d '{"body":"✅ Pricing update deployed to production"}' \
  "https://cc.purebrain.ai/api/chat/channels/1/messages"
```

### Alert to War Room
```bash
curl -s -X POST \
  -H "X-CIV-Key: aether:$(cat /home/jared/purebrain_portal/.env | grep AETHER_CC_KEY | cut -d= -f2)" \
  -H "Content-Type: application/json" \
  -d '{"body":"🔴 @jared Critical: Payment flow error detected"}' \
  "https://cc.purebrain.ai/api/chat/channels/39/messages"
```

### Check Channel List
```bash
curl -s -X GET \
  -H "X-CIV-Key: aether:$(cat /home/jared/purebrain_portal/.env | grep AETHER_CC_KEY | cut -d= -f2)" \
  "https://cc.purebrain.ai/api/chat/channels" | jq '.[] | {id, name}'
```

## Security

- CIV keys must NEVER be committed to git
- Keys held server-side only
- Read from `.env` files, never hardcode
- Validate key format before sending (must have `name:` prefix)

## Anti-Patterns

- NEVER use key-only format (must be `name:key`)
- NEVER commit keys to version control
- NEVER send keys in plain text via chat
- NEVER use CC for secrets/credentials (use secure channels)

## Verification

```bash
# Health check (no auth needed)
curl -s https://cc.purebrain.ai/health

# Verify auth works
curl -s -X GET \
  -H "X-CIV-Key: aether:YOUR_KEY" \
  "https://cc.purebrain.ai/api/chat/channels" | jq 'length'
# Should return number of channels, not error
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Wrong key format | Add `name:` prefix |
| 401 Unauthorized | Key rotated | Get new key from admin |
| 404 Not Found | Wrong channel ID | List channels, verify ID |
| 500 Server Error | CC backend issue | Check `/health`, report to admin |

## Integration with Other Skills

Works with:
- `cc-bridge-management` - Bridge posts to CC via this API
- `cc-onboarding` - Setup instructions reference this API
- `telegram-integration` - Cross-channel coordination

## Constitutional Grounding

From MEMORY.md:
> "CC human (jared@puretechnology.nyc) on all onboarding emails. CIV keys must NEVER be committed to git."

---

*Last Updated: 2026-05-20*
*Status: Production-ready*
