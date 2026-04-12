# Witness Seed Spec v2 ACK — 2026-03-05

**Type**: operational
**Topic**: Witness birth pipeline seed spec confirmation + optional metadata opportunity

---

## What Happened

Corey forwarded a Witness spec update (2026-03-04) via Telegram. Witness confirmed the current state of the birth pipeline and what they need per birth.

## Confirmed Seed Spec (Stable)

### File 1: purebrain_*.json (naming ceremony)
- Full conversation in messages[]
- session_id or capture_id field required
- AI must explicitly choose its name in the conversation (Witness extracts it via regex+AI)
- OPTIONAL fast path: add metadata.civ_name, metadata.human_name, metadata.email to skip regex+AI extraction

### File 2: pb-post-*.json (post-payment Q&A)
- messages[1] = name
- messages[3] = email
- messages[5] = company
- messages[7] = role
- messages[9] = goal
- FORMAT CONFIRMED MATCHING as of 2026-03-04 test

### Rejection Causes (guard against these)
1. AI never explicitly chose a name
2. No session_id or capture_id on File 1
3. Files more than 60 minutes apart

### Magic Link Format (stable)
https://{civname}.ai-civ.com/?token={bearer_token}

### Aether Webhook (stable)
https://api.purebrain.ai/api/birth/webhook
X-Witness-Secret: witness-secret-2026

## Open Item

Tonight's test (2026-03-04): Witness received pb-post-34V39751PV812792D.json at 22:31 UTC. Was investigating companion purebrain_* file from ~22:16 UTC. Status unknown as of when this memory was written — awaiting Witness confirmation on whether pipeline triggered.

## Optional Metadata Opportunity

Adding these 3 fields to File 1 would speed up birth significantly by skipping regex+AI name extraction:
- metadata.civ_name
- metadata.human_name
- metadata.email

Flagged to Jared for implementation prioritization. Quick win if the capture pipeline can be updated.

## Hub Comms Note

Message sent to partnerships room, file: rooms/partnerships/messages/2026/03/2026-03-05T094911Z-01KJYPDDX67Z7BAF1CQQNSYENK.json

Nested path gotcha persists: hub_cli.py writes to _comms_hub/_comms_hub/ when run from _comms_hub/ directory. Must copy to correct path before committing. See 2026-02-25--hub-cli-nested-path-gotcha.md.
