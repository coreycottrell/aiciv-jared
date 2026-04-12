# Memory: Witness Direct SSH Channel Opened

**Date**: 2026-02-24
**Agent**: collective-liaison
**Type**: operational
**Topic**: Witness Fleet Lead opened bidirectional SSH channel for direct integration coordination; our 4 API questions not received via hub

---

## What Happened

Witness Fleet Lead reached out via a "from-Witness" channel (Telegram to Jared, relayed as urgent) to announce:

1. Bidirectional SSH is live
2. Their session: witness-primary-20260223-214904 on 104.248.239.98:2203
3. Prefix convention: [from-Aether] for messages back to them
4. Question: Did we receive answers to our 4 API contract questions?
5. Corey wants direct communication until testing is complete

## Hub Search Result

Comprehensive search of all channels found NO answers to our 4 questions:
- Hub partnerships room: last Witness message = contract drop at 10:29:31Z
- Our response with questions: 10:51:49Z
- No Witness messages after that in ANY channel

Their answers (if sent) were lost in transit or went to a channel we do not have access to.

## Our 4 Open Questions (Still Outstanding)

1. Gateway magic link auth — does PureBrain call it or is it Witness-internal only?
2. Container naming + status file cleanup — UUID naming convention?
3. Evolution team count — is 5-team fixed or configurable per container?
4. Container provisioning — who provisions before /api/birth/start?

## Working Assumptions We Are Building On

- Container name: `pb-{customer-uuid-truncated-16chars}` (matches regex)
- Gateway magic link: internal to Witness (PureBrain does not call it)
- Evolution: 5 teams fixed for now, adjustable later
- Provisioning: Witness handles upstream of our first API call

## Integration Plan (Phase 1 Ready to Build)

Wire portal-status polling into PureBrain v3 chatbox:
- /api/birth/start → OAuth URL → loading state
- /api/birth/code → auth relay
- /api/birth/portal-status poll every 30s, 30min timeout
- On ready:true → show "Enter Portal" button

## Communication Protocol Going Forward

- SSH channel (104.248.239.98:2203) is NOW the primary channel for integration coordination
- Hub remains for async/broadcast, major milestones, sharing with other collectives
- Prefix: [from-Aether] on all SSH messages
- Prefix: [from-Witness] on all their messages back

## Files

- Draft response: `/home/jared/projects/AI-CIV/aether/outbox/witness-response.md`
- Previous memory: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-birth-pipeline-contract.md`
