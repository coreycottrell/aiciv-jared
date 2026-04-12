# CF Tunnel HA — Research & Plan Summary

**Date**: 2026-03-12
**Type**: implementation-plan
**Topic**: Cloudflare tunnel high availability for portal 502 prevention

## Key Findings

### What Cloudflare Offers for Tunnels

1. **Replicas** (free): Multiple cloudflared processes pointing at same Tunnel UUID.
   Each replica makes 4 new connections to CF edge.
   CF auto-routes away from dead replicas.
   Works on a single server — no extra cost.

2. **Load Balancer** ($5+/mo): Requires DIFFERENT tunnel UUIDs per server.
   Cannot put same UUID in a pool twice.
   Adds health checks, geolocation routing, active-passive failover.
   Only meaningful with 2+ physical servers.

### Current Setup
- Tunnel ID: fa55839c-e753-4a96-935c-cc58cf24b4b8
- Single server: 89.167.19.20
- Single cloudflared process (one replica = 4 connections to CF PoPs)
- Portal: Starlette server on port 8097, nginx proxy on 8099
- 2026-03-09 fix already addressed: port kill on restart, 120s timeout, keepalive

### 502 Root Causes
- cloudflared.service crash → all 4 connections drop → CF returns 502/1033
- portal_server.py crash + slow restart → nginx gets ECONNREFUSED → 502
- Port 8097 TIME_WAIT during restart (mostly fixed)

## Recommended Actions (priority order)

1. **Add cloudflared-replica2.service** on same server — eliminates tunnel-crash 502s (free, 10 min)
2. **Add portal-watchdog.timer** — 30-second health check + auto-restart with Telegram alert
3. **Future**: Second server + Load Balancer when/if scaling horizontally

## Full Plan Location
`/home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/2026-03-12--cf-tunnel-load-balancer-implementation-plan.md`
