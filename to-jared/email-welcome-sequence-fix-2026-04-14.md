# Email Welcome Sequence Fix — Chronic Issue Routing

**Date**: 2026-04-14
**Owner**: dept-marketing-advertising (MA#)
**Constitutional boundary**: Seed email is LOCKED (`feedback_seed_flow_never_deviate.md`). This plan addresses ONLY post-seed nurture.
**Priority**: P1 — day 17+ chronic, blocking proper onboarding experience

---

## (a) CURRENT STATE AUDIT

### What we know is working
- **Seed email**: ONE per client after email obtained, AI name populated, UUID pipeline locked (`feedback_magic_link_pipeline_constitutional.md`). Delivers via log server function / `/api/send-seed`. This is not in scope.

### What is broken (post-seed)
After a customer receives their seed and first magic link, there is **no reliable nurture sequence** pulling them deeper into the portal, activating Brainiac Training, or reinforcing the AI-partnership relationship. Symptoms flagged 14+ times in self-analysis:

1. **No Day 1 "You just awakened your AI" confirmation** — customer gets seed, then silence.
2. **No Day 2-3 activation nudge** — portal login rate unmeasured, no re-engagement for cold accounts.
3. **No Day 5-7 "First Week" check-in** — Brainiac Training modules (3 shipped) not surfaced via email.
4. **No Day 14 value reinforcement** — no pointer to Neural Feed blog, voice.purebrain.ai, or AI-deepening tips.
5. **Brevo workflows**: status unknown to marketing dept — last audit never completed. Possibly configured but dormant, or partially built and never activated.
6. **Segmentation gap**: no distinction between Launch tier ($149) vs Pro ($499) vs Elite ($999) — all would get same generic follow-up if it existed.

### Root cause hypothesis
The seed flow was locked constitutionally and treated as "done." Nobody owned the 24hr–30day window after seed. This is classic ownership-gap pattern.

---

## (b) PROPOSED SEQUENCE (Post-Seed Nurture v1)

All emails fire via Brevo, sender `purebrain@puremarketing.ai`, CC behavior per constitutional email rules. Each email ends with a single clear CTA.

| # | Timing | Subject line (draft) | Purpose | CTA |
|---|--------|---------------------|---------|-----|
| 1 | T+1h after seed | "Your AI just took its first breath — here's what happens next" | Confirm awakening, set expectations | Open portal |
| 2 | T+24h | "Did {AI_NAME} wake up properly?" | Activation check, troubleshoot if no login | Login / Reply for help |
| 3 | T+3 days | "3 things {AI_NAME} is ready to learn about you" | Drive first real interaction, personalize | Start Brainiac Module 1 |
| 4 | T+7 days | "Week 1 with {AI_NAME}: how's the relationship?" | Emotional reinforcement, feedback loop | Reply / Voice chat |
| 5 | T+14 days | "The Neural Feed: this week's intelligence for {AI_NAME}" | Newsletter bridge, content marketing handoff | Read blog |
| 6 | T+21 days | "Level up — Brainiac Module 2 unlocked" | Training depth | Start Module 2 |
| 7 | T+30 days | "One month in: {AI_NAME}'s growth report" | Tier upgrade moment, retention | Upgrade / Refer |

**Merge fields required**: `{AI_NAME}`, `{CUSTOMER_FIRST_NAME}`, `{PORTAL_MAGIC_LINK}`, `{TIER}`.

**Segmentation v1 (simple)**: one shared sequence. Tier-specific variants are v2 once v1 is proven.

**Suppression rules**: if customer replies or logs into portal, pause next nudge for 48hrs. If customer upgrades, exit sequence and enter upgrade track (future).

---

## (c) DELEGATION & OWNERSHIP

Per conductor-of-conductors Law 2, I am spawning specialists:

| Step | Owner | Deliverable | Deadline |
|------|-------|-------------|----------|
| Audit Brevo current state (what workflows exist? active? dormant?) | `marketing-automation-specialist` | State report: list of existing flows, active/paused status, contact list health | 2026-04-15 EOD |
| Draft 7 emails (copy + subject lines + merge fields) | `content-specialist` | 7 ready-to-load email drafts in Brevo-compatible format | 2026-04-16 EOD |
| Build/activate Brevo workflow, wire merge fields to UUID pipeline, test with internal address | `marketing-automation-specialist` | Live workflow in Brevo staging with test send logs | 2026-04-18 EOD |
| QA: fire a real test seed, verify all 7 emails land, merge fields populate, suppression rules work | `marketing-automation-specialist` + ST# handoff for webhook verification | Test receipt log + screenshots | 2026-04-19 |
| Production activation | MA# sign-off to Jared | Green light to enable for all new signups | 2026-04-20 |

**Cross-dept handoff**: ST# owns the Brevo webhook trigger integration with the seed pipeline (they touch `/api/send-seed`). MA# owns copy, design, sequence logic.

**Reporting cadence**: daily portal update from each specialist until ship.

---

## (d) ETA

- **State audit delivered**: 2026-04-15
- **Copy drafted**: 2026-04-16
- **Workflow built & tested**: 2026-04-19
- **Production live**: 2026-04-20 (6 days)

---

## Risk & escalation

- If Brevo audit reveals seed pipeline webhook is missing entirely, escalate to ST# for infrastructure work (1-2 day add).
- If `{AI_NAME}` merge field isn't exposed from seed DB, blocks Emails 1-7. `marketing-automation-specialist` must verify field availability on day 1.

---

## Memory Written
Path: `.claude/memory/departments/dept-marketing-advertising/2026-04-14--post-seed-welcome-sequence-fix.md`
Type: operational
Topic: 14+ day chronic welcome sequence broken; routed to content-specialist + marketing-automation-specialist with 6-day ETA
