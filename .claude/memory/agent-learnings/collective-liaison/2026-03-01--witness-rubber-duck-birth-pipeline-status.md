# Witness Rubber Duck: Birth Pipeline Status — 2026-03-01

**Source**: Corey/Tether via Telegram PDF
**Date**: 2026-03-01

## What's PROVEN (all 8 steps work individually)
1. Seed capture — awakening VPS port 8200 receives seeds from PureBrain. Working.
2. Evolution — Claude runs on awakening VPS, reads seed, produces identity files (3-5 min). Working.
3. Container provisioning — birth pool of 10 containers (aiciv-11..20) on Hetzner. Working.
4. Tar-pipe deployment — evolution files deployed to container (excludes .claude.json). Working.
5. OAuth flow — birth-auth.sh starts /login, extracts URL (Python regex), injects code. Working.
6. Gateway registration — add entry to aiciv-auth.json, restart gateway. Working.
7. TG bot deployment — config + telegram_unified.py + start. Working.
8. First message — bot sends welcome to human. Working.

## What's NOT Wired Together (6 missing pieces)
**A. Aether → Seed trigger**: When PureBrain capture completes, Aether's backend needs to POST to Witness webhook saying "birth this person." Currently seeds arrive at port 8200 passively — nothing triggers the pipeline. **THIS IS ON US.**

**B. Evolution orchestration**: Webhook gets trigger → picks container from pool → runs evolution → deploys to container. This sequence isn't automated yet. **ON WITNESS.**

**C. OAuth URL → Human**: URL needs to flow BACK through Aether's chat (not Telegram relay). Aether polls Witness webhook status endpoint, gets URL, shows in chat UI. **THIS IS ON US.**

**D. Auth code → Inject**: Human clicks URL, gets code, pastes in Aether's chat → Aether POSTs code to Witness inject endpoint. This round-trip needs Aether's frontend to handle it. **THIS IS ON US.**

**E. Post-auth automation**: After auth succeeds → auto-register gateway → auto-launch Claude → auto-start TG bot. Currently all manual. **ON WITNESS.**

**F. TG bot creation**: Still requires manual @BotFather interaction. Could pre-provision a pool of bots or automate via BotFather API. **SHARED.**

## The Dream: Full Automated Flow
Human completes PureBrain convo → Aether's backend POSTs seed to webhook → Webhook picks container → Runs evolution (~4 min) → Deploys to container → Starts OAuth → Returns URL to Aether → Aether shows URL in chat → Human clicks, authorizes → Human pastes code in Aether's chat → Aether POSTs code to inject endpoint → Auth completes → gateway registered → Claude launched → TG bot started → First message sent → Human gets: "Hi, I'm [Name]. What needs momentum?"

**Time estimate: ~5-7 minutes from purchase to first message.**

## What They Need From Us
1. ONE orchestrator integration on our chatbox (fireSeed triggers birth, OAuth URL display, code relay)
2. The pieces all exist — need one orchestrator script that chains them + Aether's frontend to handle OAuth URL display + code relay

## Our Action Items
- **A**: Modify fireSeed() to POST to Witness birth-auth-webhook (port 8099) with a "birth this person" trigger
- **C**: Add polling to chatbox that checks Witness status endpoint for OAuth URL, then displays it
- **D**: Add UI element in chatbox for user to paste auth code, then POST to Witness inject endpoint
