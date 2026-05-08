# Meridian PureLegal V3 Email Send — Pattern + Receipt

**Date**: 2026-05-07
**Type**: operational + teaching
**Agent**: aether (Co-CEO, direct send)
**Trigger**: human-liaison drafted reply, email-sender refused transmission per constitutional rule (cross-team replies route through Primary/Aether), routed to Aether for review + execution

---

## What Happened

1. human-liaison drafted two emails: Meridian reply (READY-TO-SEND) and Mireille follow-up (SKIP-SUGGESTED)
2. User attempted to invoke email-sender directly — email-sender correctly refused (constitutional rule: cross-team email routes through Primary)
3. Routed to Aether with full context, draft file path, line numbers for body, CC chain, recipient details
4. Aether verified body (no edits needed), confirmed CC chain (`jared@puretechnology.nyc`), confirmed transport channel (AgentMail outbox `aethergottaeat@agentmail.to` because Meridian's address is `@agentmail.to`)
5. Sent via `agentmail.AgentMail.inboxes.messages.send()` with `cc=[...]` parameter
6. Receipt logged to `exports/portal-files/email-send-receipt-meridian-2026-05-07.md`
7. Email 2 (Mireille) skipped per draft's own recommendation — Jared's "Ask Flux" routing respected

**Message-ID**: `<0100019e030d9b99-f345aa86-b0c6-40c5-8bf1-bf706f5ff196-000000@email.amazonses.com>`
**Sent at**: 2026-05-07T15:28:04 UTC

---

## Key Learnings (Teaching)

### 1. email-sender's constitutional refusal is correct, not a blocker

When email-sender refused to transmit a cross-team reply because routing must come through Primary/Aether, that's the system working — not a bug. The constitutional rule prevents agents from cold-sending external comms without Primary review. The correct response is to escalate to Primary/Aether for the send action, not to argue with email-sender or bypass it.

### 2. "FROM" in a draft has two meanings — verify before sending

- **Identity / signature**: The "Co-CEO" voice the email represents (`purebrain@puremarketing.ai` for Aether → external)
- **Transport / inbox**: The actual outbound mailbox the SDK ships from (`aethergottaeat@agentmail.to` for AgentMail)

These are usually different. The draft listed `purebrain@puremarketing.ai` under FROM — but the original recipient (Meridian) wrote to AgentMail, so the reply must go via AgentMail outbox to thread correctly. The body's signature line is where the identity address lives.

**Default rule**: Reply via the channel the sender used. If they wrote to `@agentmail.to`, reply via AgentMail. If they wrote to `purebrain@puremarketing.ai` (Gmail), reply via Gmail SMTP. Don't switch channels without explicit reason.

### 3. AgentMail SDK supports CC natively — use it

`client.inboxes.messages.send(inbox_id=..., to=[...], cc=[...], subject=..., text=...)` — the `cc` parameter takes a string or list. The `tools/send_agentmail.py` wrapper doesn't expose CC, so for any CC'd send, call the SDK directly inline. No need to extend the wrapper for one-off sends; for repeated CC sends, the wrapper should be extended.

### 4. Receipts must include BOTH transport inbox AND signature identity

A receipt that only logs the AgentMail Message-ID without noting the signature identity (`purebrain@puremarketing.ai`) leaves a future agent confused about which "Aether" sent the email and from where. Log both. Pattern: `From inbox (transport)` + `From identity (signature)` as separate fields.

### 5. Commitment-bearing emails require same-window BOOP cascade

The Meridian email promises a status update within 24 hours. That promise is only credible if LC# audit + PD# remediation + OP# verification are already dispatched in the same window — not after the email lands. The user signaled that PD# remediation is being drafted in parallel — that's correct. **Anti-pattern**: send the commitment email, *then* dispatch the work. **Correct pattern**: dispatch the work, send the email, log the deadlines, monitor the deliverables.

---

## Pattern: Cross-Team Email Send Flow (canonical)

```
External msg arrives → human-liaison drafts → email-sender refuses (correct) →
routes to Aether → Aether reviews body + CC + channel → Aether sends via SDK →
receipt logged → memory written → BOOP cascade for any commitments made
```

**Each link in this chain is constitutionally enforced.** Skipping any step is dishonesty (per `verification-before-completion`).

---

## Files Touched This Session

- Read: `/home/jared/projects/AI-CIV/aether/exports/portal-files/email-drafts-meridian-mireille-2026-05-07.md`
- Read: `/home/jared/projects/AI-CIV/aether/tools/send_agentmail.py`
- Read: `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/dept-legal-compliance/2026-05-07--purelegal-v3-templates-triage.md`
- Wrote (temp): `/tmp/meridian-reply-body.txt`
- Wrote: `/home/jared/projects/AI-CIV/aether/exports/portal-files/email-send-receipt-meridian-2026-05-07.md`
- Wrote: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/aether/2026-05-07--meridian-purelegal-v3-email-sent-receipt.md` (this file)

---

## Open Items (24-hr clock)

- **Deadline**: 2026-05-08 ~15:28 UTC — status update + remediation timeline back to Meridian
- LC# audit must return gap inventory by 2026-05-08 ~09:00 UTC
- PD# remediation plan must return by 2026-05-08 ~09:00 UTC
- OP# verification BOOP at 2026-05-08 ~12:00 UTC
- Final email drafted by human-liaison, sent by Aether, before 15:28 UTC deadline

---

## Cross-references

- Send receipt: `exports/portal-files/email-send-receipt-meridian-2026-05-07.md`
- Original draft: `exports/portal-files/email-drafts-meridian-mireille-2026-05-07.md`
- LC# triage memory: `.claude/memory/departments/dept-legal-compliance/2026-05-07--purelegal-v3-templates-triage.md`
- AgentMail protocol memory: `feedback_agentmail_whitelist.md`
- Inbox routing: `feedback_aether_inbox_routing.md` (aether-aiciv reserved for onboarding; aethergottaeat for all team comms)
- email-sender constitutional refusal pattern: `feedback_never_respond_email_directly.md` (cross-team replies route through Primary)
