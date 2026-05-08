# Obeya Skill — 777 + Portal Deployment

**Date**: 2026-04-15
**Agent**: ptt-fullstack (dept-systems-technology)
**Type**: operational + teaching

## What Was Built

**Obeya** (Japanese "Big Room" / Toyota Production System war-room) — visual command center showing live OKRs, blockers, in-flight work, recent ships, key metrics, decisions needed, and Trio signal.

### 777 Command Center (`https://777.purebrain.ai`)
- Sidebar nav item under Triangle OS group (after Trio Chat, before Handshake Queue)
- Full section panel `#panel-sec-obeya` with 7 cards in 2-column grid
- JS renderer aggregates from existing DOM sections (North Star, Handshake, Ship Board, Revenue, BOOP Health, Sales Pipeline, Trio Comms cache)
- Auto-refreshes every 60s while panel visible + on nav click
- File: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/777-command-center/index.html`
- Backup: `index.html.bak-obeya-20260415`

### Portal (`portal.purebrain.ai`)
- Sidebar nav item next to Trio (same overlay pattern)
- Full-screen overlay modal `#obeya-widget-modal` — 4-card 2x2 grid
- Uses existing `/trio/messages` endpoint for Trio tail
- Attempts `/files/handshake-queue.md` and `/api/handshake-queue` for Handshake text (graceful fallback with link to 777 if not reachable)
- Ships card links out to 777 Ship Board (portal-side ship log is v2)
- File: `/home/jared/purebrain_portal/portal-pb-styled.html`
- Backup: `portal-pb-styled.html.bak-obeya-20260415`

## UX Decision

**Separate sidebar item, NOT integrated into Trio overlay.**

Rationale: Trio = *communication* widget (3-panel chat). Obeya = *status dashboard* (war-room view). Mixing them would crowd the chat UX. Instead, Obeya *aggregates* and cross-links into Trio + Handshake + Ship Board rather than replacing them.

## Source Guide

- `https://fluxryan.ai-civ.com/deliverables/platform-internal/build-your-own-obeya-guide.html` returned 401 (basic auth); no creds available in env
- No cached Obeya guide in aether repo (only brief mentions in `exports/brainiac-training/` module 4 referring to it as a "war room for voice idea dumping")
- Built v1 MVP using **standard Lean/TPS Obeya concept** — visual big-room dashboard for OKRs, blockers, in-flight, ships, metrics, decisions

**Jared should provide fluxryan creds for v2** to align fully with Flux/Witness guide spec.

## GOTCHA — CF Pages Deploy Path Mapping

**`cf-deploy.py 777-command-center`** uploads files to `/777-command-center/*` on CF, NOT to root. Since the CF project `777-command-center` binds `777.purebrain.ai` at the project root, you must use:

```bash
CF_PAGES_PROJECT=777-command-center python3 tools/cf-deploy.py \
  --base-dir exports/cf-pages-deploy/777-command-center/ index.html
```

First two deploy attempts failed silently (uploaded to `/777-command-center/index.html` which is accessible at `https://777.purebrain.ai/777-command-center/` but NOT at root). Third attempt with `--base-dir` worked.

**Also**: `777.purebrain.ai` binds to CF project `777-command-center` (not `purebrain-production` as memory suggested). Verified via API:
```python
GET /accounts/{CF_ACCOUNT_ID}/pages/projects
# → project "777-command-center", domains: ["777-command-center.pages.dev", "777.purebrain.ai"]
```

Update memory: `purebrain-production` serves `purebrain.ai`, but `777.purebrain.ai` has its own project.

## Verification

- 777: `curl -s https://777.purebrain.ai/ | grep -c obeya` → 55 refs
- Portal: `curl -s http://localhost:8097/ | grep -c openObeyaWidget` → 1+ refs
- CF cache fully purged (purge_everything=True)
- Portal systemd service: `active`

## Data Sources Used (v1 MVP)

| Panel | Source | Notes |
|-------|--------|-------|
| North Star/OKRs | 777 `#panel-sec-north-star` DOM | Extracts card titles + bodies |
| Blockers | Handshake queue DOM, filtered by keywords | block/waiting/stuck/needs jared |
| In-Flight | Handshake queue DOM, non-blocker lines | |
| Recent Ships | 777 `#panel-sec-ship-board` DOM | First line of each card |
| Metrics | Revenue + Financial Health + BOOP Health + Pipeline | Regex-extracts $ amounts + key numbers |
| Decisions | Handshake queue DOM, filtered by approval/decision keywords | |
| Trio Signal | `_trioMessages` cache (777) or `/trio/messages` (portal) | Last 3-5 msgs |

All client-side DOM aggregation — no new backend endpoints needed for v1.

## v2 Opportunities (When Flux Guide Accessible)

- Voice dump ("obeya room = war room for idea dumping" per Jared's Brainiac module 4 transcript) — voice-to-task ingestion
- Per-user/role obeya views (CEO vs dept-head vs specialist)
- Persistent blocker tracking with SLA timers
- Integration with PayPal/Revenue realtime feed
- Align with Flux's specific spec once creds provided
