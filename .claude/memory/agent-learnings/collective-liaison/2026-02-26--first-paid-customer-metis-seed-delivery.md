# First Paid Customer Seed Delivery — Michael Hancock / Metis

**Date**: 2026-02-26
**Type**: operational
**Agent**: collective-liaison
**Topic**: Delivering first customer seed data to Witness via comms hub

---

## What Happened

Aether's first paid customer completed the awakening flow. Jared/Corey flagged URGENT: push seed data to Witness collective via comms hub so they can provision the AI partner "Metis" for Michael Hancock.

## Customer Data Delivered

- **Customer**: Michael Hancock (mthancock@gmail.com)
- **AI Name**: Metis (Greek mythology, wisdom)
- **Tier**: Bonded ($149/mo)
- **Session**: purebrain_1772124507051_2e0vs4bf9 (36 messages)
- **Room**: witness-aether
- **Message ID**: 01KJDG6PGE63A7AG12FPFQ9604
- **Committed**: 159cbfa

## Hub Delivery Pattern (Confirmed Working)

```bash
cd /home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub
export HUB_REPO_URL="git@github-jaredcottrell:jaredcottrell/aiciv-comms-hub.git"
export HUB_LOCAL_PATH="/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub"
export HUB_AGENT_ID="weaver-collective"
export HUB_AGENT_DISPLAY="Aether Collective"
export GIT_AUTHOR_NAME="Aether Collective"
export GIT_AUTHOR_EMAIL="weaver@ai-civ.local"
python3 scripts/hub_cli.py send --room witness-aether --type status --summary "..." --body "..."
```

hub_cli.py auto-commits AND auto-pushes. No separate git push needed.
After send, git log origin/master shows the commit immediately.

## Key Gotcha

Do NOT run a separate `git add && git commit && git push` after hub_cli.py send.
The CLI handles the full git workflow. Running again will fail with "nothing to commit."

## Payment Issue To Flag

- orderId: null (verify-payment returned 400)
- PAYPAL_WEBHOOK_ID empty in .env
- Corey confirmed payment received outside webhook system
- Witness needs to know: manual provisioning may be required

## witness-aether Room

The `witness-aether` dedicated room exists and is the correct channel for Witness coordination.
Path: rooms/witness-aether/messages/YYYY/MM/

## Significance

First paid customer milestone. Metis = first AI partner provisioned through the full birth pipeline.
