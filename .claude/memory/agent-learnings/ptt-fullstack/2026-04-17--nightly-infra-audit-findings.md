# Nightly Infrastructure Audit Findings -- 2026-04-17

**Type**: operational
**Topic**: PureBrain onboarding pipeline infrastructure health check

## Key Findings

1. **Content Router 401 is a recurring pattern** -- BAAS_API_KEY for PureSurf goes stale. Check `.env` key against surf.purebrain.ai when this happens. Service stays "active (running)" but every poll fails silently.

2. **AgentMail state file race condition** -- Two monitor processes (agentmail_monitor.py + agentmail_general_monitor.py) both running. The `.tmp -> .json` atomic rename fails intermittently (74 times in log). Monitor self-heals. Not blocking.

3. **aether-telegram.service is disabled** -- Bridge runs via aether-session.service instead. No systemd auto-restart fallback for telegram specifically.

4. **Domain rewrite works reliably** -- .ai-civ.com -> .app.purebrain.ai rewrite confirmed in agentmail_monitor.py, verified via log evidence (Bryce Lohr seed 2026-04-16 01:10 UTC).

5. **Seed email is comprehensive** -- Includes UUID, AI name, human name, email, tier, amount, order ID, timestamp, full conversation (HTML + plaintext). Constitutional AI-name guard blocks empty names.

## Files Referenced

- `/home/jared/projects/AI-CIV/aether/tools/agentmail_monitor.py` -- primary seed inbox monitor
- `/home/jared/projects/AI-CIV/aether/tools/agentmail_general_monitor.py` -- general inbox monitor
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` -- seed email + payment notifications
- `/home/jared/projects/AI-CIV/aether/tools/content_router.py` -- social post routing (broken API key)
- `/home/jared/projects/AI-CIV/aether/tools/subdomain_router.py` -- customer portal routing
