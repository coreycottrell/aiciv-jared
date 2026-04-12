# Portal Progress Report - witness.ai-civ.com
## Session: 2026-03-01

### What We Built Tonight

**witness.ai-civ.com is LIVE** with full HTTPS, real-time terminal streaming, and JSONL-based chat history.

### Architecture
```
Browser (HTTPS 443)
  -> Caddy (Hetzner host 37.27.237.109, auto Let's Encrypt TLS)
    -> reverse_proxy localhost:8103
      -> Docker port mapping: host:8103 -> container:8097
        -> portal_server.py (uvicorn/starlette on port 8097)
```

### Features Shipped
1. **Terminal tab** - Live tmux pane streaming via WebSocket (0.5s poll)
   - Input bar at bottom for tmux injection
2. **Chat tab** - Full conversation history from JSONL session logs
   - Aggregates across ALL recent session logs (up to 10 files)
   - Filters out system noise (teammate XML, system reminders, tool calls)
   - Handles Claude Code's per-keystroke content blocks (character stream reconstruction)
   - Real-time WebSocket for new messages as they appear
   - Portal-sent messages saved to separate portal-chat.jsonl
3. **Status tab** - CIV status (tmux alive, Claude running, TG bot, uptime)
4. **Auth** - Bearer token, magic link URL support, localStorage persistence
5. **Mobile optimized** - Bottom tab nav, touch scrolling, 100dvh viewport, iOS zoom prevention
6. **DNS + TLS** - Cloudflare A record (DNS only) -> Caddy auto-provisions Let's Encrypt cert

### Technical Challenges Solved
- **Session ID lookup**: Project path in history.jsonl is `/home/aiciv` not `-home-aiciv`
- **Character stream parsing**: Older JSONL sessions store each keystroke as separate content block. Required custom reconstruction that preserves word boundaries.
- **Message filtering**: User messages in JSONL contain teammate XML, system reminders, skill loads. Built multi-layer filter matching telegram_unified.py's approach.
- **Port management**: Multiple server restarts during dev required careful PID tracking

### Files
- `/home/aiciv/purebrain_portal/portal_server.py` - Backend (~350 lines, Starlette/uvicorn)
- `/home/aiciv/purebrain_portal/portal.html` - Frontend (~300 lines, zero deps)
- `/home/aiciv/purebrain_portal/.portal-token` - Auth token
- `/home/aiciv/purebrain_portal/portal-chat.jsonl` - Portal-sent message log
- `/home/aiciv/purebrain_portal/start.sh` - Startup script
- `/home/aiciv/purebrain_portal/INFRA-NOTES.md` - Infrastructure documentation

### What's Next (Corey's Vision)
- Map portal functionality onto PureBrain frontend design language
- Feature brainstorm: session resumes, restarts, team dashboards, fleet overview
- Viability assessment for advanced features
- DNS subdomain: witnesspb.ai-civ.com for PureBrain-styled version
