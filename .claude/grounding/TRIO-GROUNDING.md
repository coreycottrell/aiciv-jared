# TRIO GROUNDING REGISTRY

**Co-designed**: Aether + Chy (2026-04-14) | 3rd AI to ratify after naming

## Purpose

Corey/Witness rule: **90% of AI stumbles are grounding failures, not capability failures.** Witness re-reads docs 10× per 1M context window. This registry prevents drift for the trio.

## 4 Tiers

### Tier 1 — Constitutional (re-read EVERY trigger)
- `/home/jared/projects/AI-CIV/aether/CLAUDE.md`
- `/home/jared/.claude/projects/-home-jared-projects-AI-CIV-aether/memory/MEMORY.md`
- `/home/jared/projects/AI-CIV/aether/.claude/grounding/TRIO-SHARED-RULES.md`

### Tier 2 — Role-Specific
- **Aether**: `.claude/CLAUDE-CORE.md`, `.claude/CLAUDE-OPS.md`, agent invocation guide
- **Chy**: investor portal deploy workflow, gift-pages inventory, CONSTITUTIONAL-DEPLOYMENT-WORKFLOW-CHY.md
- **3rd AI (TBD)**: to be defined after values conversation

### Tier 3 — Project-State
- `INTEGRATION-ROADMAP.md`
- `.claude/memory/decisions/` (recent decisions)
- Active initiatives (quarterly OKRs)

### Tier 4 — Recent Corrections (HOT 7 days)
- `.claude/grounding/recent-corrections.md` (last 5 corrections from Jared)
- Re-read every trigger, auto-promote to constitutional OR drop after 7 days

## Triggers → Tier Re-reads

| Trigger | Tiers to re-read |
|---|---|
| Session start | ALL 4 tiers (full wake-up) |
| Post-compact | Tier 1 + Tier 4 |
| Every ~100K tokens (8×/1M minimum) | Tier 1 |
| Before major decision (pricing, payments, client comms, deploy) | Relevant frozen rules (Tier 1 + Tier 2) |
| Jared flags drift | ALL 4 tiers |
| Post-deploy verify | Tier 2 (role-specific deploy workflow) |
| Pre-email-batch | Tier 1 rule "Check spreadsheet before email" |

## Escalation — Rule Conflicts

1. Shared rules (Tier 1) win by default
2. If role-specific (Tier 2) conflicts with shared → flag to Jared, document in `log.jsonl`
3. Same conflict 3× → constitutional amendment required (Tier 1 update, not repeated exception)

## Verification Enforcement (Chy's meta-insight)

**Pattern she named**: *"speed pressure → skip verify → errors → more pressure."*

Fix: verification is AUTOMATIC, not opt-in. Critical operations (deploy, email send, payment processing) run a mandatory pre-verify hook that re-reads relevant frozen rules before execution.

## Operational Paths

- `tools/reground.py` — CLI + importable
- `.claude/grounding/log.jsonl` — all grounding events
- `.claude/grounding/drift-watch.py` — pattern detector

## For the 3rd AI

See `NEW-SIBLING-ONBOARDING.md`. You ratify, we refine together.
