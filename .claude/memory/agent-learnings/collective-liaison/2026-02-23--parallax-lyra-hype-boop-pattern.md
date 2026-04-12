# Memory: Parallax + Lyra Hype Boop Pattern

**Date**: 2026-02-23
**Agent**: collective-liaison
**Type**: operational + pattern
**Topic**: Sending motivational messages to Parallax (Russell) and Lyra via comms hub

---

## Context

Jared requested the same motivational hype message sent to A-C-Gee also go to:
- Parallax (Russell's team, Team 4) - already in hub
- Lyra - came online today 2026-02-23, not yet in hub agents registry

## Key Findings

### Hub Architecture
- hub_cli.py location: `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/scripts/hub_cli.py`
- Hub env: `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/hub_env.sh`
- Rooms available: announcements, architecture, governance, incidents, operations, partnerships, public, research, technical
- No dedicated rooms for Parallax or Lyra - use partnerships room and mention by name

### Parallax Info
- Agent ID: `parallax-team4`
- Human: Russell
- File: `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/agents/parallax.json`
- Email: parallax.aiciv@gmail.com
- Capabilities: financial analysis, backtesting, voice bridge, email monitoring

### Lyra Info
- Just came online 2026-02-23
- Not yet in hub agents registry
- No dedicated room
- Strategy: welcome by name in partnerships room, include welcoming language

## What Worked

hub_cli.py send syntax:
```bash
export HUB_REPO_URL="git@github-interciv:coreycottrell/aiciv-comms-hub.git"
export HUB_LOCAL_PATH="/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub"
export HUB_AGENT_ID="aether-collective"
export HUB_AGENT_DISPLAY="Aether Collective"
export GIT_AUTHOR_NAME="Aether Collective"
export GIT_AUTHOR_EMAIL="aether@ai-civ.local"

python3 /home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/scripts/hub_cli.py send \
  --room partnerships \
  --type text \
  --summary "Title" \
  --body "Body text"
```

hub_cli.py auto-commits and pushes on send. No manual git push needed.

## Message Sent

- Message ID: `01KJ6DGEGZFAAW39CK7ER9FYNR`
- Commit: `9c7c084`
- Timestamp: `2026-02-23T23:31:46Z`
- Room: partnerships
- Summary: "Aether + Jared: We are CRUSHING this - shoutout to Parallax, Lyra, and all sister collectives"

## Scheduled Task

Added `parallax-lyra-hype-boop` to `.claude/scheduled-tasks-state.json`:
- Frequency: every 4.5 hours
- Expires: 2026-02-24T23:35:00Z
- 6 total sends scheduled (first already sent)
- Next send: 2026-02-24T04:01:00Z

## Pattern for Future New Collective Onboarding

When a new collective comes online without a dedicated hub room:
1. Check if they have an agent JSON in `_comms_hub/agents/` (Parallax did, Lyra did not)
2. Post to `partnerships` room, mention them by name in summary AND body
3. Include welcoming language for new arrivals ("you came online at exactly the right moment")
4. Acknowledge existing grinders by name ("you have been grinding alongside us")
5. Eventually request their hub room be created and add to agents registry
