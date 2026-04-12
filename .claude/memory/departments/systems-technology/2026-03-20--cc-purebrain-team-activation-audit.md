# cc.purebrain.ai Team Activation Audit

**Date**: 2026-03-20
**Type**: synthesis + teaching
**Topic**: Full state audit and 4-sprint team activation plan for cc.purebrain.ai

## Key Findings

### System is live and stable
- FastAPI app at port 8870, Cloudflare tunnel -> cc.purebrain.ai
- PID 2423030, running since ~Mar 17, 528 hours uptime
- Health: 200 OK, version 4.0.0
- 50-person roster in config.py (all requested names: Melanie, Nathan, Russell, Mireille, Ahsen, Mike Daser, John Smith, Phillip Bliss)
- Corey Cottrell NOT in roster (correct -- external partner)
- 2,131 Google Calendar events loaded

### Critical gaps
1. Tasks in browser localStorage -- not shared across users
2. Team tab card view broken (radar shows, cards don't render)
3. Microsoft OAuth not connected -- 0 tokens, email empty
4. Posts/feed has no server-side storage
5. No one has credentials or knows the system exists
6. GATEWAY_AETHER_API_KEY has hardcoded fallback (security)
7. SESSION_SECRET has hardcoded fallback (security)

### Database state
Tables: microsoft_tokens(0), calendar_events(2131), email_messages(0), app_state(0)
Missing: hub_tasks, hub_posts, hub_files, user_oauth_tokens (never built)

### 777 Command Center
Vercel deployment, password 777grind. Personal CEO tool. Should NOT merge with cc but should link from it (admin-only nav).

## Sprint Plan
- Sprint 0 (Week 1): Fix card bug, calendar grid, rotate secrets, distribute credentials
- Sprint 1 (Week 2-3): Server-side tasks + Aether task injection API
- Sprint 2 (Week 3): Posts/broadcast feed, Aether morning digest
- Sprint 3 (Week 4-5): Multi-user OAuth, per-user calendar/email
- Sprint 4 (Week 6+): Notifications, Sheets export, 777 live data sync

## Files
- Full report: exports/departments/systems-technology/2026-03-20--cc-purebrain-team-activation-plan.md
- Source: tools/comms-gateway/
- Service: sudo systemctl restart aether-comms-gateway
