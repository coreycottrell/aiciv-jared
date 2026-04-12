# Inter-CIV Team Registration Check (2026-02-21)

**Agent**: primary (conductor)
**Date**: 2026-02-21
**Topic**: ACG team invite `acg-aether-infra-2026` - attempted registration

## What Happened

A-C-Gee sent inter-CIV team invite via comms hub:

- **Team name**: `acg-aether-infra-2026`
- **Purpose**: Joint infrastructure work
- **Registration endpoint**: POST /api/inter-civ/teams/register
- **Our gateway**: http://89.167.19.20:8098
- **Our auth token**: aether-alpha-2026
- **ACG gateway**: http://5.161.90.32:8098

## Findings

### Gateway Status

**Our gateway is NOT RUNNING**:
```
curl http://89.167.19.20:8098/
→ Connection refused (port 8098 not listening)
```

**Blocker**: No gateway API server exists. No code found for:
- Inter-CIV API implementation
- Team registration endpoint
- Authentication system

### Team Messaging Status

**ACG's own message** (in partnerships room):

> "We searched the hub for the team invite but couldn't find it. Where should we look?"

**Implication**: Even the sender can't locate the team invite in hub. This suggests:
- Team messaging infrastructure may not exist yet
- Invites may be via email/Telegram (external to hub)
- This is a new feature request or architectural gap

## Implications

1. **Gateway is infra work item** - Not yet built
2. **Team messaging is unclear** - Needs clarification from ACG
3. **Hub is git-based messaging only** - No team messaging features yet
4. **ACG may be building ahead of us** - They have a gateway, we don't

## Next Steps for Jared

1. Ask A-C-Gee where `acg-aether-infra-2026` team invite lives
2. Decide if inter-CIV gateway is priority infrastructure
3. If yes, determine if we build it or wait for A-C-Gee to share theirs

## Related: Witness Contributions

Two unrelated messages from Witness (sister CIV):

1. **BOOP gaps**: Fork template missing trigger mechanism, work-mode skill, fleet tools
2. **TG setup**: Witness built bidirectional TG streaming bot (1,850 lines)

Both are ecosystem offers requiring review/decision.

## Architecture Notes

- Gateway pattern: HTTP API with `/api/inter-civ/teams/register` endpoint
- Auth: Token-based (we have `aether-alpha-2026`, ACG has equivalent)
- Hub: Git-native messaging only (not real-time team messaging)
- Gap: No team messaging features in current hub design

## Files Generated

- `/home/jared/projects/AI-CIV/aether/to-jared/TEAM-INVITE-STATUS-2026-02-21.md` - Full status report sent to Jared via Telegram

