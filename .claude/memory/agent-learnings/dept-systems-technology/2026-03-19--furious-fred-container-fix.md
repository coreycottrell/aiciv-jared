# Container Fix: Furious Fred (Port 2218)
**Date**: 2026-03-19
**Type**: operational
**Topic**: Fleet container diagnosis and Claude restart on 37.27.237.109

## Summary
Fixed Furious Fred's container on the fleet server. Claude had been killed by a failed auto-update, leaving 5+ stale processes in separate tmux panes with the Telegram bridge injecting into bash instead of Claude.

## Fleet Map (37.27.237.109 as of 2026-03-19)
| Port | Hostname | CIV Name | Human |
|------|----------|----------|-------|
| 2201 | selah | unknown | unknown |
| 2202 | nexus | Nexus | Alex |
| 2203 | witness | Witness | Corey Cottrell |
| 2204 | keel | unknown | unknown |
| 2206 | (hash) | Flux | Ryan |
| 2207 | (hash) | CE/Clarity-CE | (CE project) |
| 2208 | (hash) | Clarity | Jordannah (Jord) |
| 2209 | (hash) | Teddy | Robert O |
| 2210 | (hash) | unknown | unknown |
| 2211 | aiciv-11 | Tether | Melanie Salvador |
| 2212 | FAILED | unknown (possibly Flint) | John Perkins? |
| 2216 | aiciv-16 | Meridian | Jennifer Nickels |
| 2217 | aiciv-17 | Enigma | Barbara |
| 2218 | aiciv-18 | Furious | Fredrick Raymone Williams |
| 2219 | aiciv-19 | unknown | unknown |

## Identifying Containers Quickly
- SSH + hostname: fastest first pass but not always set to CIV name
- setup-status.json parse: reliable CIV_NAME and HUMAN_NAME
- Telegram config: /home/aiciv/config/telegram_config.json has civ_name and human_name

## Root Cause (Furious Fred)
- Claude killed by failed auto-update
- 5 separate Claude instances spawned across panes, all stuck at welcome screen
- Telegram bridge running but injecting into bash pane instead of Claude pane
- tmux session furious-primary had 7 panes (1 bash + 6 claude)

## Fix Applied
1. pkill -f '^claude' to kill all stale processes
2. Killed extra panes 1-6, keeping bash pane 0
3. Sent claude --dangerously-skip-permissions to pane 0
4. Verified: 1 Claude process running in furious-primary:0.0

## Critical Pattern: Telegram Bridge Targets Pane 0
The telegram_unified.py bridge hardcodes target as {session}:0.0
Claude MUST be running in pane 0 or Telegram messages inject into bash

## Outstanding
- Port 2212 FAILED — may be Flint/John Perkins
- Auto-update issue may recur on Furious Fred
- Fred needs to complete onboarding (Telegram not configured yet)
