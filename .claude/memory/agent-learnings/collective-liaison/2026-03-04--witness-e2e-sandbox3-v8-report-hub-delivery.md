# Witness E2E Sandbox-3 v8 Report: Hub Delivery Pattern

**Date**: 2026-03-04
**Agent**: collective-liaison
**Type**: operational
**Topic**: E2E test report delivery to Witness via comms hub partnerships room

---

## What Happened

Delivered the definitive pay-test-sandbox-3 E2E test report (v8) to the comms hub partnerships room for Jared to share with Witness/Corey.

Report source: `/home/jared/projects/AI-CIV/aether/exports/e2e-sandbox3-v8-report-20260304.md`

Hub location confirmed in: `rooms/partnerships/messages/2026/03/2026-03-04T134537Z-01KJWHHMDTQW7W6AEZ5WT1P9RJ.json`

Commit: `ab3d5db` — already pushed to `origin/master` (hub_cli.py auto-commits and pushes).

---

## Key Technical Findings in Report

- Full E2E flow: password gate → pre-payment chat → payment sim → post-payment Q&A (5 questions) → Behind the Curtain slides (10) → orange CTA → Brain Stream button CONFIRMED GREYED
- Brain stream button state: opacity=0.35, pointer-events=none, cursor=not-allowed, background=rgb(51,51,51)
- Button onclick fix deployed: when portal-status returns ready with portalUrl, button activates as clickable `<a>` element
- "Your AiCIV is ready" text → now uses dynamic AI name (e.g., "Keen is ready")
- No real Witness birth_complete webhook received yet — button activated from cached test data
- 30 screenshots captured in `/home/jared/projects/AI-CIV/aether/exports/e2e-sandbox3-complete-flow/`
- Open architecture question: brain stream button is on underlying Elementor page (not inside chatbox) — different from Jared's reference screenshot showing "ENTER KEEN'S BRAIN STREAM" inside chatbox

---

## Hub CLI Gotchas (Reconfirmed)

- Hub is at: `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/`
- hub_cli.py is at: `_comms_hub/scripts/hub_cli.py`
- hub_env.sh sets: HUB_AGENT_ID="aether-collective", GIT_AUTHOR_NAME="Aether Collective"
- hub_cli.py auto-commits AND auto-pushes — no manual git commit/push needed
- `--limit` flag does NOT exist on `list` command (use `--since` for time filtering)
- Remote: `git@github-interciv:coreycottrell/aiciv-comms-hub.git`
- team1-production-hub directory does NOT exist at `/home/jared/projects/AI-CIV/team1-production-hub` — only one AI-CIV directory: `aether`

---

## Witness Partnership Status (2026-03-04)

- Our side: READY for real Witness webhook test
- Waiting on: Corey to trigger real birth_complete webhook
- Next step: When webhook fires, button should activate from greyed to clickable portal link
- Recent hub messages from this session also include: E2E Test PASSED + Witness Integration Spec v2 (11:24), E2E Clarification: Pre-Payment Chatbox Flow Missing (12:11)

---

## Pattern: Large Report Hub Delivery

Full 257-line markdown report sent as `--body` of a `--type status` message. Worked without truncation. hub_cli.py handles large bodies fine — no need to summarize before sending.
