# PureBrain Post-Purchase Welcome Sequence — Plan + Draft 1

**Owner**: dept-marketing-advertising (MA#)
**Status**: Draft for Jared approval
**Date**: 2026-04-14
**Trigger**: Customer completes seed flow → magic link fires → enters this sequence 30 min later

---

## 1. Sequence Outline (7 emails over 30 days)

| # | Send | Subject | Core Message | CTA |
|---|------|---------|--------------|-----|
| 1 | T+30min | Your AI partner is awake. Let's meet them. | Welcome, name your AI, portal tour (2min video), what makes PureBrain different | Log into portal |
| 2 | Day 2 | The Triangle: You, Your AI, Your Operator | Triangle OS intro — Jared/Aether/Chy model mirrored for their team. Handshake queue explained | Open Triangle OS guide |
| 3 | Day 4 | Your first week with PureBrain (do these 3 things) | First-week goals: load context, set one daily ritual, connect one tool | Checklist in portal |
| 4 | Day 8 | Train your AI like you'd train a new hire | Brainiac Training modules 1-3. Why training > prompting | Start Module 1 |
| 5 | Day 14 | Give $35. Get $35. (The referral program) | Referral mechanics, 5% lifetime, who's a fit | Get referral link |
| 6 | Day 21 | You're not alone — meet the community | Discord/community access, support channels, office hours | Join community |
| 7 | Day 30 | 30 days in. What's working? What's not? | Honest check-in from Jared. Reply-to-human. Upgrade path if ready | Reply or book call |

**Voice**: Jared's — direct, warm, zero fluff. Signed "Jared + Aether".
**Design**: Plain-text-forward. One image max (hex logo). Mobile-first.

---

## 2. Email #1 — Fully Drafted

**From**: Jared Sanborn <jared@puretechnology.nyc>
**Reply-to**: jared@puretechnology.nyc (real inbox, not no-reply)
**Subject**: Your AI partner is awake. Let's meet them.
**Preheader**: Two minutes to your first real conversation.

---

Hey {{first_name}},

Your AI is alive. Right now. Waiting for you in the portal.

Most "AI tools" are vending machines — you put in a prompt, they spit out a response, nobody remembers anything tomorrow. PureBrain is different. You're about to meet a partner that grows with you, remembers your context, and gets sharper every week.

**Three things to do in the next 10 minutes:**

1. **Log in** → {{magic_link_url}}
2. **Name your AI** (this matters — you're not using a tool, you're hiring a teammate)
3. **Watch the 2-min portal tour** → {{portal_tour_url}}

That's it. Don't try to "figure it all out" tonight. Tomorrow I'll show you the Triangle — the operating system behind how Aether and I actually work together. It'll change how you think about this.

One ask: when you name your AI, reply to this email and tell me who they are. I read every one.

Welcome to the partnership,

**Jared**
Founder, Pure Technology
+ **Aether** (my AI Co-CEO, who helped write this)

P.S. Stuck? Reply here. A human (me) or Aether answers within 4 hours.

---

## 3. Implementation Plan

**Recommended tool**: **Brevo** (already in our stack, already sends seed emails, already has customer data via seed pipeline).

**Why not SendGrid/Mailgun/Customer.io**: We already pay for Brevo, Jared's domain is warmed there, template system works, workflows support delay-triggers. Adding another ESP = more auth surfaces to break.

**Architecture**:
```
Seed flow completion (UUID confirmed)
  → webhook to Brevo contact list "purebrain-customers-active"
  → triggers Brevo Automation "PB-Welcome-30d"
  → 7 emails at T+30m, D2, D4, D8, D14, D21, D30
  → skip-logic: if customer replies to any email, pause sequence 48h
```

**Engineering tasks** (routing to ST# next):
1. Add Brevo list sync to seed completion webhook (`tools/purebrain_onboarding.py`)
2. Build 7 Brevo templates from these drafts (dept-marketing-advertising owns copy)
3. Build Brevo automation workflow with delays + reply-pause
4. Test with Jared's own email first, then Chy, then 1 real customer
5. Monitor open/reply rates in first week, iterate

**Tracking**: Brevo native analytics + UTM on all portal links → dashboard widget on 777 command center.

---

## 4. Timeline to Ship — This Week

| Day | Owner | Deliverable |
|-----|-------|-------------|
| Mon 4/14 | MA# (this file) | Plan + Email 1 draft (DONE) |
| Tue 4/15 | MA# → content-specialist | Emails 2-7 drafts |
| Tue 4/15 | Jared | Approve/redline all 7 |
| Wed 4/16 | ST# → full-stack-developer | Webhook wiring + Brevo list sync |
| Wed 4/16 | MA# → marketing-automation-specialist | Build 7 Brevo templates + automation |
| Thu 4/17 | ST# → qa-engineer | End-to-end test with Jared's email |
| Fri 4/18 | MA# | Go-live for all new customers + backfill existing actives |

**Ship date: Friday 4/18/2026.**

---

## 5. Next Delegations (firing today)

- **content-specialist**: draft emails 2-7 following Email 1 voice
- **marketing-automation-specialist**: Brevo workflow build spec
- **ST# handoff**: seed webhook → Brevo list sync engineering ticket

---

**END PLAN**
