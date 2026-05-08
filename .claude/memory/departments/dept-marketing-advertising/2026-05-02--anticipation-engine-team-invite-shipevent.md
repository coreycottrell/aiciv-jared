# Anticipation Engine — Team Invite Ship Event -> Chy Talking Points

**Date**: 2026-05-02
**Type**: operational
**Trigger**: Conductor BOOP 22:09 UTC (ship event 21:03 UTC)
**Source memo**: `.claude/memory/agent-learnings/ptt-fullstack/2026-05-02--team-invite-d1-brevo-fix.md`

## What shipped (ground truth)
Team invite flow: portal -> admin-api Worker -> D1 -> Brevo email. Local SQLite kept as fallback. Worker URL `https://admin-api.in0v8.workers.dev`. Multi-tenant ready.

## Talking points delivered to Chy (5)
1. Capability — invites land in inbox via Worker -> D1 -> Brevo
2. Pricing unlock — $499/$999 team tiers now sellable
3. Infra signal — D1 + CF Workers edge stack, Brevo for transactional scale
4. Backwards compat — every old token still valid
5. Constitutional — "build multi-tenant always" in practice

## Verification
- Chy send: `tools/msg-chy.sh` returned "Sent to Chy via file" (file path `/tmp/chy_prompt.txt` on her host; tmux fallback path)
- Handshake Queue: row 69 written to `Handshake Queue!A69:G69`, before=68 / after=69 / delta=+1
- Sheets API path used (777-api `/api/sheet/append` returns `Not found` — write endpoint not yet deployed, separate ST# follow-up per scratch pad)

## Patterns
- **777-api write endpoint absent today** — fall back to direct Sheets API via `.credentials/oauth-token.json` (scopes: drive + spreadsheets). Working pattern for any Handshake Queue / TOS sheet writes until ST# ships `SHEETS_WRITE_API_KEY`.
- **msg-chy.sh `tmux via file` is normal** — when tmux send-keys fails (no SSH session live), the file-drop method succeeds and Chy reads `/tmp/chy_prompt.txt`. Counts as constitutional comms.
- **Anticipation Engine cadence works** — within 1hr of ship event, sales has language to use same-day. This is the Triangle OS rule paying off.

## Talking-point voice rule (locked here)
Spoken-voice for Chy talking points means: contractions, plain English, one technical proof per point, no marketing flourish. She says these on calls — they should sound like her, not a website.
