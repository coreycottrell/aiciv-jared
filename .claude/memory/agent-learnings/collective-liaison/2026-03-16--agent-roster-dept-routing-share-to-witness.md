# Memory: Agent Roster + Department Routing System Shared with Witness

**Date**: 2026-03-16
**Agent**: collective-liaison
**Type**: operational
**Topic**: Shared portal Agent Roster feature and Department Shortcode system with Witness via AgentMail + comms hub

---

## What Was Sent

Jared asked collective-liaison to share the Agent Roster feature and Department Routing system with Witness (Corey's AI collective) so they can see how we built agent management into the portal and potentially adopt it.

## Delivery Channels Used

1. **Comms hub partnerships room**: Message committed and pushed at `2026-03-16T122428Z`
2. **AgentMail**: Sent from `aether-aiciv@agentmail.to` to `witness-aiciv@agentmail.to`, CC `jared@puretechnology.nyc`
   - Message ID: `<0100019cf69d2a0d-67df892d-d444-4bcd-b538-dcee88dc133d-000000@email.amazonses.com>`
   - Thread ID: `0c7c41a3-47ca-4d61-a989-60f245cc731a`

## Content Shared

- 77 agents / 23 departments overview
- Three view modes (Grid / List / Org Chart tree)
- Full org chart hierarchy (Aether -> CTO/CMO -> Depts -> Agents)
- Department shortcode routing system (PT#, ST#, MA#, etc.)
- Full shortcode reference table (25+ triggers)
- 4 API endpoints: /api/agents, /api/agents/stats, /api/agents/orgchart, /api/agents/{id}
- API response shapes and query params
- Code reference: portal-pb-styled.html lines 6075/6101/~14860, portal_server.py lines 4918-5037
- How agents are seeded from .claude/agents/*.md manifests
- Offer to package any part for Witness adoption

## Key File References

- UI: `/home/jared/purebrain_portal/portal-pb-styled.html` (line 6075 roster, 6101 shortcuts)
- API: `/home/jared/purebrain_portal/portal_server.py` (lines 4918-5037)
- Dept routing: `/home/jared/projects/AI-CIV/aether/.claude/DEPARTMENT-ROUTING-GUIDE.md`
- Hub message: `aiciv-comms-hub-bootstrap/_comms_hub/rooms/partnerships/messages/2026/03/2026-03-16T122428Z-01KKV9NNX0H8HYD2N3Q57GXKDK.json`

## Pattern Notes

- AgentMail API pattern: `client.inboxes.messages.send(inbox_id, to=..., cc=..., subject=..., text=...)`
- Hub CLI pattern requires env vars set before call (HUB_REPO_URL, HUB_LOCAL_PATH, HUB_AGENT_ID, etc.)
- Hub CLI binary location: `aiciv-comms-hub-bootstrap/_comms_hub/scripts/hub_cli.py`
- Hub CLI list syntax: `--room partnerships --since "2026-03-01T00:00:00Z"` (no --limit flag)
- Hub commits automatically inside hub_cli.py; push happens via git push in the inner _comms_hub dir
