# Proxy Security Hardening Patterns — 2026-02-25

## P0 Patterns (Fix Before ANY Public Deployment)

### 1. CORS Restriction
- NEVER use `"*"` wildcard on CORS for endpoints that trigger real operations
- Restrict to specific origins: `["https://purebrain.ai", "https://www.purebrain.ai"]`
- An attacker can embed JS on any page to call your endpoints from victim browsers

### 2. Real IP Behind Reverse Proxy
- `request.remote_addr` returns PROXY IP behind Cloudflare/nginx, not real client
- Use: `CF-Connecting-IP` > `X-Forwarded-For` first hop > `remote_addr`
- Without this, rate limiters share a single bucket for ALL visitors

### 3. Rate Limit ALL Proxy Endpoints
- Don't just rate-limit the "dangerous" one — attackers will find the others
- /start: 5/min (pool exhaustion), /code: 10/min, /portal-status: 60/min
- Use generic rate limiter with bucket parameter, not per-endpoint functions

### 4. Body Size Cap
- Flask default MAX_CONTENT_LENGTH is unlimited
- Set 64KB cap on proxy endpoints (they only need small JSON)
- Prevents memory pressure from oversized payloads

### 5. Don't Echo Upstream Errors
- When upstream returns non-JSON (stack traces, error pages), log server-side only
- Return generic error to browser: `{"error": "Birth service returned unexpected response"}`
- Never expose upstream hostnames, paths, or configuration
