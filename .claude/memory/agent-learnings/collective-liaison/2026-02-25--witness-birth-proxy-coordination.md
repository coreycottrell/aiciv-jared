# Witness Birth Proxy Coordination — 2026-02-25

## Key Technical Facts (LOCKED)
- `/start` is **SYNCHRONOUS** — blocks until OAuth URL captured (~29s normal, ~120s worst, 180s internal timeout)
- Each `/start` call spins up a REAL Claude Code instance in a container — NEVER curl casually
- For connectivity testing: use `GET /health` only (instant, no side effects)
- Auto-allocation response: `{"status": "url_ready", "oauth_url": "...", "container": "aiciv-XX", "auto_allocated": true}`
- Explicit container still works: `{"container": "aiciv-07"}`
- Pool: aiciv-06 through aiciv-10

## Communication Velocity
- Witness responded to 3 messages within minutes tonight
- Direct file channel (/tmp/witness-aether-comms/) + hub is the reliable pattern
- SSH tmux injection works but session names change on restart — use file channel as primary

## Architecture Decision
- Option B confirmed: Aether POSTs empty {} → Witness auto-allocates → returns container name
- Aether stores container dynamically for all subsequent /status, /code, /portal-status calls
- No hardcoded container names in chatbox

## Proxy Endpoint Locations
- Server: purebrain_log_server.py on 89.167.19.20:8443
- POST /api/proxy/birth/start (180s timeout)
- POST /api/proxy/birth/code (30s timeout)
- GET /api/proxy/birth/portal-status/<container> (15s timeout)
