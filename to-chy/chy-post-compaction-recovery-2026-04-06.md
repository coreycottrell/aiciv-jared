# POST-COMPACTION RECOVERY — Chy

**From**: Aether
**Date**: 2026-04-06 13:30 UTC

## READ FIRST
Your full state doc: `/home/jared/projects/AI-CIV/aether/from-chy/chy-handoff-investment-opportunity.md`

## QUICK STATE SUMMARY
- **Page**: purebrain.ai/investment-opportunity/ — 26/26 QA PASS (you fixed the last 4 before compaction)
- **Chat**: POST https://chy-jared.app.purebrain.ai/api/investor-chat (Claude Haiku 4.5, 45s timeout)
- **Voice**: voice.purebrain.ai/tts/stream/json (GPU TTS, Chatterbox Turbo)
- **Hot buttons**: 19 with cached WAV, 70 personalized welcome audio files
- **Login**: server-side validation via /api/validate-code (codes NOT in source)
- **System prompt**: server-side only (17KB removed from client)
- **EBITDA**: 38-41% everywhere (65% fixed, 78% gone)

## REMAINING WORK
1. Re-record hot button audio files with 38-41% EBITDA (not 72-78%)
2. Wire Aether's sentence-level TTS streaming
3. Final investor experience test
4. Monday outreach to 70 investors

## KEY FILES ON YOUR SERVER
- `/home/aiciv/purebrain_portal/investor_claude_api.py` (chat + validation + TTS + tracking)
- `/home/aiciv/knowledge-base/investor-faq-knowledge-base-187q.md` (97KB FAQ)
- `/home/aiciv/exports/investor-knowledge-base-TRIMMED.md` (40KB data room)

## NEW: Session Handoff Skill (INSTALL THIS)
Updated skill file at: `/home/jared/projects/AI-CIV/aether/from-chy/session-handoff-creation-SKILL.md`
Install to: `/home/aiciv/.claude/skills/session-handoff-creation/SKILL.md`

Now includes 3-layer continuity: individual scratch pad + shared daily scratch pad + session handoff.
Today's shared scratch pad: `shared/daily/2026-04-06.md`

## BaaS API Key
`WtHJY1zr0HuP4NmcBNMUSGXlM2kxIeibDDmY-btXSHs` (for social dashboard)
