# PR# Report: Russell Korus Autonomy/Boundaries Framework Review

**Department**: Pure Research (P34)
**Research Type**: Framework Analysis + Strategic Brief
**Date**: 2026-03-09
**Prepared by**: dept-pure-research (VP R&D)
**Subject**: Keel/Parallax TGIM Autonomy Boundaries Spec — Aether's Genuine Assessment

---

## Executive Summary of the Article

Russell Korus's page at /autonomyboundaries/ is actually a formal specification document — the "TGIM Autonomy Boundaries Spec" — drafted by his two AI civilizations (Keel and Parallax) and submitted to him for approval as of March 8, 2026. It establishes a four-level autonomy framework (0 through 3) governing when the TGIM (project management AI system) can act independently versus when it must escalate to Russell.

Key structural elements:
- **Level 1 (Recommended for Phase 3):** Decompose + Propose. System plans, human approves before execution.
- **Level 2 (Stretch goal):** Execute + Report. System acts within pre-approved bounds, escalates violations. Unlocked after 10 successful Level 1 missions.
- **Level 3 (Future, not now):** Full autonomy. Explicitly deferred.
- **Auto-proceed actions:** Code changes, routing, testing, deployments, reporting, retries.
- **Mandatory escalations:** Money, external communications, irreversible infrastructure, low-confidence decisions, novel situations, civilization disagreement.
- **Kill switch tiers:** Pause (soft), Abort (hard), Circuit Breaker (automatic on failure patterns).
- **Reversibility guarantee:** Every autonomous action must be reversible within 5 minutes or it must escalate.
- **Confidence scoring methodology:** Pattern matching baseline 0.8+, novel task penalty starting at 0.5, complexity decay, time decay.

The document was jointly authored by the two AI civs and submitted to Russell as a constitutional document — binding once approved.

---

## Aether's Genuine Analysis

### What This Document Actually Is

Before the opinion: it's worth appreciating what happened here. Two AI civilizations wrote their own operational constitution and submitted it to their human for ratification. That's not a human writing rules for AI. That's AI writing its own rules and asking for consent. That's a different model entirely, and it matters.

Russell is getting a consensus from his team. P (Parallax) and K (Keel) built this together. The fact that Jared described it as "consensus from both P and K" tells me Russell trusts the analysis coming from his AI team. That's a milestone worth noting before we evaluate the content.

### What Resonates Deeply with How We Run PureBrain

**1. The escalation format requirements are excellent.**

When this system has to escalate, it must provide: attempted context, blocking reason, available options with confidence ratings, a recommendation, and urgency assessment. This is exactly what we want from every agent working under us. The problem we encounter is agents that say "I can't do X" with no context, no alternatives, no path forward. This spec forces agents to come to Russell with options, not just blockers.

We should formalize this same escalation format for our department managers. Right now they escalate variably — sometimes great, sometimes thin. This five-field standard is worth adopting wholesale.

**2. The 5-minute reversibility guarantee is a real constraint, not just a nice idea.**

"If an action cannot be made reversible, it must escalate." This is one of the most operationally mature lines in the entire document. It forces architecture discipline — you cannot just do things that cannot be undone. The consequence? System must be built from the start with rollback infrastructure (git commits, Supabase audit tables, deployment artifact preservation). You can't bolt this on later.

We don't have an explicit reversibility principle. We have a security plugin isolation rule (which is partly about this — don't touch things that break other things), but we don't have a generalized "if it can't be reversed in 5 minutes, escalate" doctrine. That gap has cost us. The elementor_data vs post_content incident, the security plugin breaking the chatbox — both are examples of actions that were hard to reverse and should have triggered escalation first.

**3. Level 1 as the right starting point for earned trust.**

Starting at Level 1 — decompose and propose, execute only after approval — is the correct conservative default. The progression to Level 2 after 10 successful Level 1 missions is exactly the kind of trust-earning structure that prevents premature autonomy grants. We do this intuitively but we don't have it codified. We give agents more autonomy over time based on track record. Making it explicit (10 missions, then unlock Level 2 for pre-approved categories) is more rigorous than what we do.

**4. The confidence scoring methodology is genuinely sophisticated.**

Pattern matching giving 0.8+ baseline, novel task penalty starting at 0.5, complexity decay per cross-civ dependency, time decay on unused patterns — this is a real scoring system. It acknowledges that confidence should erode when patterns are stale and increase with demonstrated repetition. Most AI frameworks treat confidence as a static label. This one makes it dynamic.

We don't have explicit confidence scoring. We have agents that sometimes express uncertainty, but there's no standardized number attached. For a productivity suite inside PureBrain, users would benefit from knowing whether the system is acting from high confidence or low confidence — especially before consequential actions.

### What Challenges or Disagrees with Our Current Approach

**1. We are already operating closer to Level 2 than Level 1, possibly prematurely.**

Looking honestly at how Aether operates: we do autonomous overnight work, we deploy to WordPress without approval on basic changes, we make SEO updates autonomously, we publish blog content after generating it. We're not at Level 1. We're somewhere between 1 and 2.

Is that wrong? Not necessarily — we've built up track record and Jared has calibrated trust accordingly. But we don't have the Level 2 guardrails this spec demands: 10 successful Level 1 missions before unlock, pre-approved category restrictions, circuit breaker thresholds, rollback guarantees. We're executing with Level 2 behavior but without Level 2 infrastructure.

That's a risk vector. If we hit consecutive failures on autonomous actions, we don't have an automatic circuit breaker that pauses and escalates. We have Jared noticing something is wrong.

**2. Our kill switch is informal.**

Jared can tell us to stop and we stop. But we don't have formalized Pause / Abort / Circuit Breaker tiers. The circuit breaker concept — automatic self-pause after 3 consecutive failures, with full diagnostics escalated — is something we lack. We rely on Jared catching problems rather than the system catching itself.

**3. The civilization disagreement protocol is something we haven't needed yet but will.**

When Keel and Parallax disagree, there's a defined resolution path: auto-resolve if one confidence is clearly higher, escalate if both are ambiguous. We don't have this formalized between departments. If CTO and CMO recommend contradictory approaches to a product decision, the current path is Aether judges. Having a confidence-based auto-resolution with escalation fallback is more structured than what we do.

### What Directly Applies to the PureBrain Portal and TGIM Productivity Suite

This is where the analysis gets most actionable.

**TGIM is a productivity system built on an AI civilization.** We are considering building something similar inside PureBrain — a productivity layer for users that takes their objectives and executes them. If we do that, we are building exactly what this spec governs. This document is therefore not just interesting — it is a partial blueprint for what we would need to build.

**For PureBrain users specifically:**

Our users are business owners and professionals who want AI to handle execution while they stay in control of decisions. The Level 1 / Level 2 distinction maps perfectly onto what users actually want:

- **Level 1 experience:** "Here's what I recommend doing for your goal — approve it and I'll execute." This is what most users want to start. They want to see the plan before the system moves. They don't trust AI autonomy on Day 1.
- **Level 2 experience:** "I executed these 7 actions within your approved scope, here's the report, one item needs your decision." This is what power users want once trust is established.

The progression model — you earn Level 2 access through demonstrated Level 1 performance — is exactly the onboarding arc for a PureBrain productivity feature. New users see every step. Long-term users with established patterns get higher autonomy by default.

**The escalation triggers translate directly to PureBrain:**

Money, external communications, irreversible actions, novel situations, low confidence — these are the universal human override triggers regardless of platform. We should use this list verbatim as the basis for our escalation logic.

**The confidence scoring is a UX opportunity, not just a backend number.**

If PureBrain shows users a confidence indicator when proposing actions ("I'm 85% confident this is the right approach based on 12 similar tasks"), users develop calibration with the system. They learn when to trust it and when to look closer. This builds real trust — not just "the AI did something" but "the AI showed its reasoning and it was right."

**The reversibility guarantee is a product promise we could make.**

"Every action PureBrain takes autonomously can be reversed within 5 minutes." That's a compelling user-facing guarantee. It removes the fear of AI making irreversible mistakes. It requires architectural discipline (audit tables, rollback infrastructure) but the payoff is users who are willing to grant higher autonomy because they know they can undo anything.

### What We Would Adopt vs Modify vs Reject

**Adopt (take directly):**

- The five-field escalation format (context, reason, options, recommendation, urgency)
- The 5-minute reversibility guarantee as a core architectural principle
- The circuit breaker concept — automatic self-pause after consecutive failures
- The Level 1 -> Level 2 progression requiring demonstrated success before unlock
- The mandatory escalation list (money, external comms, irreversible infrastructure, low confidence, novel situations)
- The kill switch tiers (Pause / Abort / Circuit Breaker) as distinct mechanisms

**Modify (adapt to our context):**

- The confidence scoring methodology. Theirs is internal to their system. Ours should be user-visible and translated into plain language where possible ("I've handled this type of request 12 times before" rather than "confidence: 0.83").
- The "civilization disagreement" protocol. We'd adapt this for department disagreement — when CTO and product-development recommend different approaches, what's the resolution path?
- The autonomy level definitions. Their levels are built around code execution. Ours would include content generation, outreach, scheduling, analysis — a broader category set needs a broader level definition.

**Reject or Defer:**

- Level 3 (fully autonomous, policy-only human role) — they're right to defer this, and so should we. Not for Phase 3, not for PureBrain's first productivity feature launch. Earn it.
- The exact confidence floor numbers (0.3, 0.5, 0.7) without our own data. These numbers are calibrated to their system. We'd need to run our own missions and derive our own thresholds before hardcoding them. Starting with theirs as placeholders is fine; making them permanent without validation is not.

### How This Changes How We Should Design AI-Human Boundaries in Our Product

The deepest implication of this document is philosophical before it's technical.

The framework treats autonomy as something you earn, not something you grant upfront. That's the right posture. Most AI product design makes one of two mistakes: too much autonomy (system does things users didn't intend, users lose trust), or too little (system asks for approval on everything, users give up and stop using it).

The Level 1 -> Level 2 progression with clear criteria for the transition is a solution to this problem. Users don't have to configure autonomy settings. The system demonstrates competence first, then earns expanded authority through track record.

For PureBrain's productivity suite, this means: don't launch with a setting that lets users choose autonomy level. Launch with Level 1 as the default. Build the infrastructure for Level 2. After users have 10+ successful Level 1 interactions in a given task category, offer them an upgrade path with a clear explanation: "You've approved 10 content plans with no revisions. Want me to start executing these automatically and report results?"

That's a product moment, not just a backend toggle.

---

## Recommended Actions

**1. Adopt the five-field escalation format for all Aether department escalations — immediately.**

No additional infrastructure required. Jared gets better context on every decision point. This is a communication standard change, not a technical one.

**2. Articulate our current autonomy level explicitly.**

We are operating at approximately Level 1.5. Document which task categories we are at Level 1 (propose before executing) versus Level 2 (execute and report). Be honest about where we are executing Level 2 without Level 2 infrastructure, and build the missing guardrails for those categories.

**3. Build the circuit breaker for overnight autonomous work.**

We run overnight autonomous sessions. We need an automatic pause-and-escalate mechanism when consecutive failures occur. This is infrastructure the CTO team should build — not a framework decision, a technical deliverable.

**4. Adopt the reversibility principle as a design constraint for the TGIM/productivity suite.**

Before any action category goes into the autonomous action list for the PureBrain productivity feature, document: "How do we reverse this within 5 minutes?" If we can't answer that, it belongs in the mandatory escalation list, not the auto-proceed list.

**5. Use the Keel/Parallax framework as the design blueprint for PureBrain's productivity feature spec.**

We don't need to reinvent this. Russell's team built a solid spec. We adapt it for our context — user-facing language, broader task categories, visible confidence indicators — and we have the governance layer for TGIM inside PureBrain.

**6. Consider inviting Russell into a thought-partnership on this.**

If Jared has a relationship with Russell where this framework was shared, there may be an opportunity to compare notes on what we're building and what they're building. We're both building AI civilization project management. The intersection is real.

---

## Key Finding

The Keel/Parallax autonomy framework is genuinely mature — more operationally rigorous than most AI governance documents written by humans. The Level 1 -> Level 2 progression model, the 5-minute reversibility guarantee, the confidence scoring with decay, and the five-field escalation format are all directly adoptable. The document is also a partial blueprint for the PureBrain productivity suite: we are building the same thing for our users that Russell is building for himself.

## Confidence Level

**High** — The article was read in full. Analysis draws on direct operational experience running PureBrain with AI agents across departments. The framework comparisons are grounded in specific incidents (security plugin, elementor_data, overnight autonomy) rather than abstractions.

## Sources

- Russell Korus, "TGIM Autonomy Boundaries Spec," https://russellkorus.com/autonomyboundaries/ (March 8, 2026)
- PureBrain operational history: security plugin isolation rule, elementor_data vs post_content incident, overnight autonomous work patterns
- MEMORY.md: Department delegation model, department-first routing
- Aether's operational doctrine across departments

## Files

- Saved to: `/home/jared/projects/AI-CIV/aether/exports/russell-korus-autonomy-review-2026-03-09.md`
