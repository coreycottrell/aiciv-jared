---
route: SD# (sales-distribution)
from: the-conductor (nightly-self-analysis BOOP, 2026-05-02 03:11 UTC)
priority: MEDIUM (pre-stage, not blocking)
---

# SD# Routing — Pre-Stage Activation Sequence for Email Welcome Ship

## Context
MA# is building the email welcome sequence (PD# spec 1 today). Historically when MA# ships, SD# is reactive — drafts activation 2-3 days later. That gap = lost revenue cycles.

## Action Required (SD#)

Draft the post-welcome activation campaign **NOW**, before MA# ships, so SD# is parallel-ready not sequential-blocked:

1. **3-email post-welcome sequence** (Days 4 / 7 / 14 after seed)
   - Day 4: "What can your AI partner do?" — value reinforcement + first task suggestion
   - Day 7: "Your AI's first week — show & tell" — share what other customers built
   - Day 14: Soft pricing reminder (current tier vs upgrade, post-launch pricing reference per `pricing memory`)

2. **Sales hook variants** for each tier:
   - $149 launch tier
   - $499 launch tier
   - $999 launch tier

3. **CTA destinations** — confirm with ST# that magic-link + portal flow handles re-entry per `feedback_magic_link_pipeline_constitutional.md`.

4. **Voice** — must use `aether` voice for any audio content (per voice selection rule, 2026-04-15 lock).

5. **No team-member targeting** per `feedback_linkedin_never_comment_team_members.md` (analog rule for email).

## Output Location
- Drafts to Drive `voice/SD-activation-drafts/` and `exports/portal-files/SD-email-welcome-activation-drafts-2026-05-02.md`.
- Mirror to `social.purebrain.ai` kanban for team approval.

## Why pre-stage
When MA# ships, SD# should already have drafts in Final column ready to schedule — not Draft column waiting to write. This is the leverage gap I identified in tonight's self-analysis (Q5: skipping SD# on revenue ships = leaving compounding on the table).
