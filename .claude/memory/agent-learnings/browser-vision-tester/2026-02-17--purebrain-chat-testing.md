# PureBrain.ai Chat Testing - Lessons Learned

**Date**: 2026-02-17
**Agent**: browser-vision-tester
**Type**: technique + gotcha

---

## Context

Tested the PureBrain.ai landing page chat widget to verify A-C-Gee integration was working.

## Key Findings

### 1. Self-Signed SSL Certificates Break Browser Logging

**Gotcha**: When testing sites that POST logs to a server with self-signed certificates, headless browsers (Playwright) will silently fail those requests.

**Symptoms**:
- Network tab shows POST to `https://89.167.19.20:8443/api/log-conversation`
- Server logs show NO incoming requests during that time
- Manual `curl -k` to the same endpoint works fine

**Solution**:
- For production: Use Let's Encrypt or similar CA-signed cert
- For testing: Use `curl` to manually verify the server, accept that browser tests won't log
- Alternative: Test in non-headless mode with certificate exception added

### 2. Chat Widget Element Selectors

For purebrain.ai chat widget:
- Begin button: `.chat-initial__btn`
- Input field: `#userInput`
- Submit button: `#submitBtn`
- Messages: `.message--ai`, `.message--user`
- Chat container: `.chat-container`
- Chat section: `#awakening`

### 3. Verification Approach

When testing integrations that involve multiple servers:
1. Test each hop independently
2. Use `curl -k` to bypass SSL issues for manual verification
3. Check server logs at each point in the chain
4. Don't assume browser network traffic = server received

### 4. A-C-Gee Forwarding Architecture

```
purebrain.ai (browser JS)
    |
    v
Aether log server (89.167.19.20:8443)
    |
    +---> Local JSONL file
    |
    +---> A-C-Gee (sageandweaver-network.netlify.app/api/landing-chat)
    |
    +---> AICIV Hub (hub_cli.py)
```

## Verification Commands

```bash
# Check if log server is running
ps aux | grep purebrain

# Test log endpoint manually (bypasses SSL issues)
curl -k -X POST https://89.167.19.20:8443/api/log-conversation \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}]}'

# Check for A-C-Gee forwarding in logs
grep "A-C-Gee" logs/purebrain_log_server.log

# Check conversation log
tail -3 logs/purebrain_web_conversations.jsonl
```

## Files Referenced

- Log server: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`
- Server log: `/home/jared/projects/AI-CIV/aether/logs/purebrain_log_server.log`
- Conversation log: `/home/jared/projects/AI-CIV/aether/logs/purebrain_web_conversations.jsonl`

---

**Tags**: purebrain, A-C-Gee, SSL, chat-widget, integration-testing, playwright
