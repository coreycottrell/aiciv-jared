# Nightly Infrastructure Audit -- 2026-04-17 07:10 UTC

**Auditor**: full-stack-developer
**Scope**: PureBrain onboarding pipeline infrastructure

---

## Summary

| # | Component | Status | Details |
|---|-----------|--------|---------|
| 1 | AgentMail Monitor | **OK** | Both monitors running (PIDs 1417711, 2832175). Last activity 00:45 UTC processing Witness forwarded email. |
| 2 | Domain Rewrite (.ai-civ.com -> .app.purebrain.ai) | **OK** | Rewrite confirmed in agentmail_monitor.py. Verified live at 01:10 UTC: `cornerstone-bryce.ai-civ.com` -> `cornerstone-bryce.app.purebrain.ai`. |
| 3 | DNS Resolution (*.app.purebrain.ai) | **OK** | Resolves to 37.27.237.109 (Hetzner/Witness server). Main purebrain.ai resolves via Cloudflare (188.114.97.3, 188.114.96.3). |
| 4 | Portal Notifications | **OK** | [NEW PAYMENT] and [SEED FIRED] events both present in purebrain_log_server.py (lines 1270, 1290, 2382, 2388). Notifications fire to tmux + Telegram. |
| 5 | Seed Email Configuration | **OK** | Destination is `aiciv-seed-inbox@agentmail.to` (confirmed at 5 call sites in purebrain_log_server.py). Seed includes: UUID, AI name, human name, email, tier, amount, order ID, timestamp, full conversation HTML+text. Constitutional AI-name guard active (line 77-127). |
| 6a | aether-portal.service | **OK** | Active (running) since 23:12 UTC. PID 2859532. Memory 94.1M. |
| 6b | aether-content-router.service | **WARN** | Active (running) since 13:47 UTC, BUT every poll cycle fails with `401: Invalid API key` from PureSurf. Has been failing for 1030+ cycles (~17 hours). Posts cannot be fetched or routed. |
| 6c | aether-trio-primary-injector.service | **OK** | Active (running) since Apr 15. PID 2097315. Uptime 1 day 8 hours. |
| 6d | aether-session.service | **OK** | Active (running) since Apr 10. Uptime 1 week. |
| 6e | aether-telegram.service | **WARN** | Disabled and inactive (dead). Telegram bridge runs via session manager instead (not systemd-managed). Bridge IS running per separate process. |

---

## Issues Requiring Attention

### WARN-1: Content Router PureSurf API Key Invalid (ACTIVE)

- **Service**: aether-content-router
- **Error**: `PureSurf fetch returned 401: {'detail': 'Invalid API key'}`
- **Duration**: 17+ hours (1030+ failed cycles at 60s intervals)
- **Impact**: No social media posts can be fetched from PureSurf or routed to platforms. LinkedIn/Bluesky autopilot posting is non-functional.
- **Fix**: Check `BAAS_API_KEY` in `.env` -- it may have been rotated on the PureSurf side. Verify at `https://surf.purebrain.ai` and update the key.

### WARN-2: AgentMail State File Intermittent Errors (Transient)

- **Log**: 74 occurrences of `No such file or directory: agentmail_state.tmp -> agentmail_state.json`
- **Impact**: Transient -- monitor recovers and continues polling. State file exists currently (26KB, last modified 07:05 UTC). Likely a race condition when two monitor instances try atomic-rename at the same moment.
- **Severity**: Low. Monitor self-heals. No missed messages observed.

### WARN-3: aether-telegram.service Disabled

- **Status**: Disabled / inactive (dead)
- **Impact**: None currently -- Telegram bridge runs via `aether-session.service` process tree. However, if session manager restarts without bridge logic, Telegram would go down with no systemd fallback.
- **Recommendation**: Either re-enable as backup or confirm session manager always spawns the bridge.

---

## Verification Evidence

```
# AgentMail PIDs
$ pgrep -af agentmail
1417711 /usr/bin/python3 tools/agentmail_general_monitor.py
2832175 /usr/bin/python3 tools/agentmail_monitor.py

# DNS
$ dig +short app.purebrain.ai
37.27.237.109

# Domain rewrite proof (from log)
Magic link rewritten: https://cornerstone-bryce.ai-civ.com/?token=... -> https://cornerstone-bryce.app.purebrain.ai/?token=...

# Seed destination (5 call sites)
to=['aiciv-seed-inbox@agentmail.to']  -- lines 1251, 2345, 2708 + 2 more

# Systemd services
aether-portal:                 active (running) since 23:12 UTC
aether-content-router:         active (running) BUT 401 errors every cycle
aether-trio-primary-injector:  active (running) since Apr 15
aether-session:                active (running) since Apr 10
aether-telegram:               inactive (dead), disabled
```
