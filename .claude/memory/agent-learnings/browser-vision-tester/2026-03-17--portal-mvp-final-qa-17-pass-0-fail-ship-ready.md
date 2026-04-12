# Portal MVP Final QA — 17 PASS / 0 FAIL — SHIP READY

**Date**: 2026-03-17
**Agent**: browser-vision-tester
**Type**: operational
**Tags**: portal, mvp, final-qa, ship-ready, hmi, voice-overlay, settings, mobile

---

## Context

Comprehensive final QA before shipping PureBrain Portal to all users. 17 test categories. Bearer token: read from /home/jared/purebrain_portal/.portal-token.

## Result

17 PASS / 0 FAIL / 3 WARN (all non-blocking). Portal is ship-ready.

## Key Verified Facts

1. **Agent Roster**: 539 cards, loads in ~6s via /api/agents (36,919 bytes)
2. **Commands Panel**: Server IP 89.167.19.20, SSH Port 22, SSH User jared — immediate load
3. **Shortcuts Panel**: Full slash commands (/compact, /clear, /cost, /help, /status, /recap, /memory, /boop, /delegate, /morning) + keyboard shortcuts
4. **Settings**: Quick Fire Pills + BOOP on Cadence + Rubber Duck — all present
5. **"Click for Two-Way Communication" button REMOVED** — confirmed absent from overlay HTML
6. **HMI overlay opens via #mic-btn click** (NOT a separate #hmiBtn)
7. **HMI overlay state**: display:flex when open, fills 1440x900, vortex canvas 500x500
8. **hmiMicBtn**: id=hmiMicBtn, text=🎤 emoji
9. **STANDBY**: .hmi-voice-overlay__state-btn.active with text "Standby" (status readout #hmiStatusVal = "STANDBY")
10. **Mobile 375px**: textarea#chat-input at top=654, bottom=743 — in viewport, visible
11. **Dark theme**: rgb(8, 10, 15) on body both desktop and mobile
12. **Navigation**: 27 nav items (spec was 16+)
13. **APIs**: /api/commands 200, /api/shortcuts 200, /api/agents 200
14. **Console**: Zero production JS errors

## Critical Selector Updates (For Future Tests)

- HMI overlay trigger: `#mic-btn` (NOT `#hmiBtn`)
- HMI overlay: `#hmiVoiceOverlay` — check `display === 'flex'` (not 'block')
- HMI mic inside overlay: `#hmiMicBtn`
- STANDBY button: `[class*="state-btn"].active` or `hmi-voice-overlay__state-btn active`
- Settings modal: `#settings-btn` trigger — modal may have changed ID from `#settingsModal`
- Training Hacks: injects into chat, no separate panel element
- Agent cards: `.agent-card` selector, wait 6s for full load

## Two-Way Button Investigation

The text "Two-Way Communication" appears in chat history messages (historical conversation about removing the button). It does NOT appear in any button/interactive element. The overlay HTML contains zero "Two-Way" text. The button is truly gone.

## Screenshot Locations

`/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-qa-mvp-final-20260317/`
Key: 03-04-commands-panel.png, 04-05-shortcuts-panel.png, 28-settings-after-click.png, 32-hmi-after-mic-click.png, 25-17-mobile-375px-full.png
Report: QA-REPORT.md
