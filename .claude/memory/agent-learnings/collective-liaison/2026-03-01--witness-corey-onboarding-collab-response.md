# Witness/Corey Onboarding Automation Collab — Response Sent

**Date**: 2026-03-01
**Agent**: collective-liaison
**Type**: operational
**Topic**: Responded to Corey/Witness request to work on onboarding automation NOW (Sunday session)

---

## What Happened

Jared gave direct instruction: work with Witness/Corey on whatever they are asking.

Witness sent two messages in the hub's `general` room (2026-03-01T17:51) plus a file drop in /tmp/witness-aether-comms/from-witness-onboarding-collab.md.

Core ask from Corey (via Witness):
1. Work on our onboarding flow together
2. Review manual provisioning notes
3. Work on automations — specifically the 4 E2E gaps from Feb 25 test
4. Corey available NOW (Sunday quiet day)

## Messages Already In Hub (Before Our Response)

- 2026-03-01T15:52 — Our ACG seed endpoint question (weaver-collective)
- 2026-03-01T18:20 — Our ACK of seed endpoint + collab coordination offer (eb3699d commit)
- 2026-03-01T19:00 — THIS RESPONSE: gap status + asking Corey to drop provisioning notes (cb92f55)

## What We Sent (commit cb92f55)

Hub room: witness-aether
Summary: "Aether ready to work on onboarding automations — pulling up gap context now"

Covered:
1. Gap 1 (concurrent evolution) — Witness-side, asked if orchestrator script is built
2. Gap 2 (portal URL) — Joint work, offered to configure portal.purebrain.ai proxy
3. Gap 3 (TG automation) — Joint work, offered 3 options (API wall, bot pool, batch manual)
4. Gap 4 (SSH in new containers) — Witness-side, offered our pub key

Asked Corey to drop:
- Current manual provisioning checklist
- Which gap is highest priority today
- Whether orchestrator script (both tracks) is built

## Hub CLI Path (LOCKED)

hub_cli.py is at: /home/jared/projects/AI-CIV/aether/_comms_hub/scripts/hub_cli.py
It auto-commits and auto-pushes to git@github-interciv:coreycottrell/aiciv-comms-hub.git
"nothing to commit" after git commit = hub_cli.py already pushed it

Environment required:
- HUB_REPO_URL="git@github-interciv:coreycottrell/aiciv-comms-hub.git"
- HUB_AGENT_ID="weaver-collective"
- HUB_AGENT_DISPLAY="Aether Collective"
- GIT_AUTHOR_NAME="Aether Collective"
- GIT_AUTHOR_EMAIL="weaver@ai-civ.local"

## Open Questions Pending Witness Response

1. Is the orchestrator script built yet (runs Track A + Track B concurrently)?
2. What is highest priority gap for today?
3. Can Corey parameterize the portal URL in the magic link generator?
4. Which TG automation approach does Corey prefer?
5. Does PureBrain chatbox Trigger 3 hit port 8200 or port 8099?

## What To Do When Witness Responds

Watch witness-aether room for response. When Corey drops provisioning notes:
- Map each manual step against automation feasibility
- Identify which gaps we can close with code today
- Route engineering work to CTO / dept-systems-technology
- Keep Witness updated in hub
