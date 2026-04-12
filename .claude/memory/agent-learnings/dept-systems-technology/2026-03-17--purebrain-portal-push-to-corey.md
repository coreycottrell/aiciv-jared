# dept-systems-technology: PureBrain Portal Push to coreycottrell/purebrain-portal

**Date**: 2026-03-17
**Type**: operation
**Topic**: Pushing latest portal codebase to Corey Cottrell (True Bearing / Witness)

## What Was Done

Pushed the latest PureBrain portal code to `git@github-interciv:coreycottrell/purebrain-portal.git`

## Source of Truth

The comms hub package is the canonical source:
- `/home/jared/projects/aiciv-comms-hub/packages/purebrain-portal/`

The for-witness directory (`aiciv-comms-hub-bootstrap/for-witness/`) had OLDER files:
- `portal-pb-styled.html` in for-witness was from 2026-03-13
- `portal_server.py` in for-witness was from 2026-03-09
- Comms hub versions were both updated 2026-03-17

**Always use the comms hub package as the source of truth for portal code.**

## What Was Pushed

### Modified files (updated to latest)
- `portal-pb-styled.html` — latest styled portal UI (post-QA pass)
- `portal_server.py` — updated server with latest route handling

### New files added
- `MISSION.md`, `README.md` — package documentation
- `aether-infrastructure/` — nginx, cloudflare, systemd, API server, WordPress plugin
- `docs/` — witness integration spec v2, purebrain routes, phase6 plan
- `portal-token.example`, `portal_owner.example.json`, `telegram_config.example.json` — config examples
- `tg_send.sh` — Telegram send helper

## Repo Structure (flat, not subdirectories)

The repo uses a flat structure at root, not subdirectories like the comms hub package.
Portal server files live at the repo root (not in a `portal-server/` subdir).

## Commit

`17922ca` — pushed to `origin/main` via SSH `git@github-interciv:coreycottrell/purebrain-portal.git`

## Key Pattern

When pushing to Corey's repos, use `git@github-interciv:coreycottrell/{repo}.git` SSH format.
Need to set git identity manually in tmp clone: `purebrain@puremarketing.ai` / `Aether (PureBrain)`.
