---
name: client-marketing
description: Use when Jared sends a message containing the trigger phrase CLIENT MARKETING; runs the client-marketing workflow for a named client.
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---
# Client Marketing Skill

## Trigger
TRIGGER WORDS: "CLIENT MARKETING", "client marketing", "Client Marketing"

When Jared sends ANY message containing "CLIENT MARKETING" (case-insensitive),
this skill activates and ALL work is routed to the `client-marketing` agent.

## Purpose
Complete isolation of external client/partner marketing work from Pure Technology
ecosystem. This is a hard departmental boundary.

## Routing Rules

### ALWAYS route to client-marketing agent when:
- Message contains "CLIENT MARKETING" trigger
- Jared mentions external client/partner marketing needs
- Follow-up to a previous CLIENT MARKETING task

### NEVER route to client-marketing when:
- Work is for PureBrain, Pure Technology, Pure Marketing, or any Pure* brand
- Work is for Aether's personal brand
- Work is for the internal marketing team (Nathan, Phil, John)

## Isolation Protocol

When CLIENT MARKETING is triggered:

1. **Delegate immediately** to `client-marketing` agent (subagent_type)
2. **Pass the full context** — client name, brief, any attachments
3. **Do NOT mix** with any Pure* work happening in the same session
4. **Files go to** `exports/client-marketing/[client-name]/`
5. **Memory goes to** `.claude/memory/agent-learnings/client-marketing/`

## Response Format

All client marketing responses MUST be prefixed:
```
[CLIENT MARKETING: Client Name]
```

This makes it instantly clear in Telegram and terminal that this is external client work.

## The Wall

No information flows between:
- client-marketing agent ← → marketing-strategist
- client-marketing agent ← → content-specialist
- client-marketing agent ← → marketing-team
- client-marketing agent ← → blogger
- client-marketing agent ← → linkedin-writer

These are separate departments. Period.
