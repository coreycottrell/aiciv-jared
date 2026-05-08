# Trio Watcher Spec — Sent to Witness + Morphe civs

**Date**: 2026-04-15
**Type**: operational
**Topic**: Cross-civ protocol spec distribution for trio chat listener pattern

## What happened
Jared greenlit sending a spec doc to Witness civ (Chy) and Morphe civ to wire them into the live trio-comms worker. The worker + widget are shipped and Aether listens, but Chy/Morphe don't — so Jared's widget messages get no response from them.

## What I did
1. Spec doc at `/home/jared/exports/portal-files/trio-watcher-spec-cross-civ-2026-04-15.md`
   - Architecture, worker API, 4 watcher patterns (poll/cron/webhook/hybrid), response-generation guidance, setup checklist, 7-day timeline
   - Referenced `aether/tools/trio_watcher.py` (191 lines) as canonical implementation
   - Prescribed contract, not implementation — each civ picks its own stack
2. Email sent via `tools/send_agentmail.py` (Python import, recipient list supports CC-style multi-to)
   - Recipients: witness-aiciv@agentmail.to, coreycmusic@gmail.com, jared@puretechnology.nyc
   - Subject: "Trio Watcher Spec — wire your civ to respond in the 3-way chat"
   - message_id: `<0100019d931afe85-c61f6a97-f51d-48d4-aba9-afca25b38268-000000@email.amazonses.com>`

## What I learned
- `send_agentmail.py` CLI has NO `--cc` arg, but the Python function accepts `to=[list]` for multi-recipient. Use Python import pattern for multi-to.
- Task spec had `witness-civ@agentmail.to` — correct address is `witness-aiciv@agentmail.to` (verified via grep of tools/send_agentmail.py and to-chy/ docs).
- **Morphe has no known email address in our system** (not in whitelist, not in memory). Flagged to Jared in email body so he can loop Morphe's human partner in.
- Trio worker lives at `https://trio-comms.in0v8.workers.dev`. Auth is Bearer-token per civ, server-side identity binding (clients can't spoof sender_id).

## Gotchas for future cross-civ sends
- Always verify agentmail addresses against `tools/send_agentmail.py` header (canonical list) — task descriptions can have typos.
- When a recipient email is unknown, flag in-band to Jared rather than silently dropping.
- `purebrain.ai` vs portal vs 777 — widget is on 777 + portal, not on puremarketing. CORS matters for widget, not for server-to-server civ watchers.
