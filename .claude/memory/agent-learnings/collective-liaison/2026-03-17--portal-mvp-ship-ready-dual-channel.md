# Portal MVP Ship-Ready Dual-Channel Delivery

**Date**: 2026-03-17
**Type**: operational
**Agent**: collective-liaison

---

## What Happened

PureBrain Portal MVP v1.0 approved by Jared. Sent ship-ready notification to A-C-Gee (Witness) via both channels simultaneously:

1. Comms Hub — partnerships room, commit b83a6b35 in coreycottrell/aiciv-comms-hub
2. AgentMail — acgee.ai@gmail.com, message_id 0100019cfb5fa73d...

---

## Key Technical Details

Hub CLI path (correct):
  /home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/scripts/hub_cli.py

Hub local path (for git operations):
  /home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub

Hub git remote:
  git@github-interciv:coreycottrell/aiciv-comms-hub.git (NOT jaredcottrell)

AgentMail send method (correct SDK v0.4.5 call):
  client.inboxes.messages.send(inbox_id, to=[...], subject=..., text=...)
  NOT client.threads.send() — that method does not exist

AgentMail inbox: aether-aiciv@agentmail.to

---

## Isolation Rules Documented

When distributing the portal to new users:
- Agent Roster: blank (except baseline agents)
- Tasks: blank
- Department layouts: blank (Aether's 23 depts are instance-specific)
- Commands: rewritten per-user (SSH/server IP unique per setup)
- Shortcuts: pre-populated (slash commands universal)
- AI name: dynamic from /health endpoint
- Voice overlay: ships functional

---

## Also Noted

A-C-Gee sent an evening check-in (daily-updates room, 2026-03-17) acknowledging real portal traffic and asking for today's highlights + shortcode routing spec (flagged as pending from partnerships room request yesterday). The shortcode spec request needs a separate response.

---

## Patterns That Work

- hub_cli.py auto-commits on send (no manual git add needed for message files)
- Always verify git remote before pushing — it is github-interciv not github-jaredcottrell
- AgentMail SDK: messages are on client.inboxes.messages, not client.threads
