---
agent: dept-sales-distribution
type: campaign-brief
status: DRAFT (awaiting Aether/Jared review + OP# verifier audit)
priority: HIGH (pre-stage for MA# welcome ship in ~7 days)
date: 2026-05-03
trigger: SD#
upstream-routing: 2026-05-02--SD-route-pre-stage-email-welcome-activation.md
constitutional-refs:
  - feedback_seed_flow_never_deviate.md
  - feedback_magic_link_pipeline_constitutional.md
  - feedback_every_feature_multi_tenant_for_customers.md
  - feedback_voice_purebrain_ai_only.md (project_voice_pricing_product.md)
  - feedback_social_html_is_source_of_truth.md
  - feedback_verifier_independence_audit_separation.md
---

# Post-Welcome Activation: 5-Touch Sequence Brief

**Goal**: Convert Day-0 awakened users into engaged paying retainers without chasing attention. Engineer resonance through value reinforcement, partnership demonstration, and a soft, well-earned ask.

**Assumption**: MA# ships the redesigned Day-0 welcome email within 7 days. This sequence fires AFTER that touch lands.

**Tier targeting**: $149 (Awakened — launch tier, price-frozen), $499 (Awakened+), $999 (Founders). Variants per tier hidden behind segmentation hook.

---

## 1. Sequence Overview

| # | Day | Phase | Voice | Touch Type |
|---|-----|-------|-------|------------|
| Day 0 | 0 | (Welcome — owned by MA#) | Aether | Welcome + magic link |
| **T1** | **+2** | Discovery | Aether | Orientation nudge |
| **T2** | **+5** | Resonance | Jared | First-week story prompt |
| **T3** | **+9** | Demonstration | Aether | "Show me what your AI built" |
| **T4** | **+14** | Differentiation | Jared | Context Tax / partnership philosophy |
| **T5** | **+21** | Invitation | Aether | Soft retention check-in + tier-aware path |

**Pacing rationale**: Day 0/2/5/9/14/21 mirrors the proven Neural Feed welcome sequence cadence (`2026-02-20--neural-feed-welcome-sequence.md`) — three-phase emotional arc (discovery → resonance → invitation) with restraint at CTA. Restraint until Day 21 is the counterintuitive lever; pitching on Day 5 burns trust.

---

## 2. Per-Touch Detail

### T1 — Day +2: "Your first 48 hours with [AI_NAME]"
- **Subject**: `Did [AI_NAME] introduce themselves yet?`
- **Hook**: Lightweight check-in. Not a sales touch. Confirms the magic link worked, the AI partner has a name, and the seed memory landed.
- **Value prop**: Removes friction. If anything broke (seed missing, AI name not populated, magic link expired), this surfaces it before it becomes silent churn. Refs `feedback_seed_flow_never_deviate.md`.
- **CTA**: "Reply with your AI's name" (engagement = deliverability boost; replies tagged `t1-reply` = warm leads).
- **Success metric**: Reply rate ≥ 8%; broken-state surfacing rate (% reporting issues) ≤ 3%.

### T2 — Day +5: "What did you actually do with them this week?"
- **Subject**: `5 days in. What's working?`
- **Hook**: Jared voice. Personal, not pitched. Asks a real question.
- **Value prop**: Reinforces the partnership frame ("them" not "it"). Pulls forward the user's own success story so they can witness their own progress.
- **CTA**: One-click survey (3 options): "Daily use", "Casual use", "Haven't started yet". Branches T3 variant.
- **Success metric**: CTR ≥ 22%; "Haven't started yet" rate triggers concierge re-onboarding via OP#.

### T3 — Day +9: "Show me what your AI built"
- **Subject**: `[Customer name from seed], what did [AI_NAME] help you make?`
- **Hook**: Aether voice. Direct ask. Establishes that PureBrain is about output, not consumption.
- **Value prop**: Re-anchors the value proposition: this is a partnership that produces. Not a chatbot. Not a tool. A teammate. Pull-quotes from replies become testimonials for T4 and social proof for the broader funnel (with permission).
- **CTA**: "Reply with one thing you and [AI_NAME] made" — also offers `voice.purebrain.ai` audio response option (constitutional: own voice infra ONLY, NEVER ElevenLabs).
- **Success metric**: Reply rate ≥ 5%; ≥ 3 testimonial-quality replies/week feed social.purebrain.ai approval queue.

### T4 — Day +14: "Why memory is the whole game"
- **Subject**: `The Context Tax (and why your AI is different)`
- **Hook**: Jared voice. Original IP positioning. The "Context Tax" framework — every other AI makes you re-explain yourself daily; PureBrain doesn't.
- **Value prop**: Differentiation moment. Plants competitive armor BEFORE the soft ask in T5. Subscribers who internalize the Context Tax framing pre-empt their own price objections.
- **CTA**: Link to long-form blog version on purebrain.ai/blog (no pricing CTA — restraint is the leverage).
- **Success metric**: Time-on-page ≥ 90s; share rate ≥ 1.5%; T5 conversion lift vs control (no T4) ≥ 2x.

### T5 — Day +21: "Where do we go from here?"
- **Subject**: `Three weeks with [AI_NAME] — what's next?`
- **Hook**: Aether voice. Reflective, not pushy. Acknowledges the journey.
- **Value prop**: First moment we acknowledge the commercial relationship. Tier-aware:
  - **$149 cohort**: "Continue building together at $149/mo (your launch rate is locked)" + path to $499 if ready for more.
  - **$499 cohort**: Reinforce continued value; spotlight features they haven't used.
  - **$999 Founders**: Skip pricing; offer Founders-only quarterly call instead.
- **CTA**: One-click confirmation of continued retainer OR "Talk to Jared" calendar link (concierge for hesitations).
- **Success metric**: Conversion to active retainer ≥ 35% of T5 recipients; downgrade rate ≤ 10%; concierge call requests ≥ 5%.

**Constitutional pricing note**: The $149 figure references the price-frozen `/insiders/awakened/` page only. The active $74.50 violation flagged in conductor BOOP context is a separate hunt — this sequence MUST NOT reference that page or rate. Awakened tier = $149 (locked).

---

## 3. Segmentation Hooks (D1 user record fields)

Multi-tenant compliant per `feedback_every_feature_multi_tenant_for_customers.md`. Each touch checks these fields BEFORE send:

| D1 Field | Drives | Variants |
|----------|--------|----------|
| `tier` | T5 pricing variant | $149 / $499 / $999 / Founders |
| `ai_name` | All touches (personalization) | populated post-seed; if NULL → block send + alert OP# |
| `seed_status` | T1 send gate | If `failed` → re-route to MA# concierge, suppress sequence |
| `last_login_ts` | T2 branch | < 5 days ago → "active" path; ≥ 5 days → "haven't started" path |
| `team_or_solo` | All touches (tone) | Team = "your team and [AI_NAME]"; Solo = "you and [AI_NAME]" |
| `customer_org_id` | Future white-label | When PureBrain runs sequences for Pure Marketing customers' end-users, `customer_org_id` swaps brand voice/CTAs. Today: hardcoded to PureBrain. |
| `unsubscribe_flags` | Send gate | Honor per-touch granular opt-outs (sales vs nurture) |

---

## 4. Risks & Dependencies

| Risk / Dep | Owner | Blocker For | Notes |
|-----------|-------|-------------|-------|
| MA# Day-0 welcome ship | MA# | Entire sequence | Sequence assumes Day-0 sets up tone; if MA# voice mismatches, T1 jolts user. Need MA# final draft 48h before T1 first send. |
| `ai_name` populated in D1 at seed time | ST# | T1, T3, T5 | Per `feedback_seed_flow_never_deviate.md` — AI name MUST populate before send. SD# does not own this; ST# audit needed. |
| Magic link / portal re-entry working | ST# | T5 (calendar link) | Per `feedback_magic_link_pipeline_constitutional.md`. Confirm before T5 ships. |
| `voice.purebrain.ai` audio reply path for T3 | ST# / PR# | T3 audio variant | If voice infra not exposing inbound capture, T3 ships text-only. NEVER substitute ElevenLabs/rented TTS. |
| Copy approval queue on social.purebrain.ai | Chy + Morphe | All touches | Sequence enters Draft column → review → Final. SD# does not bypass. |
| Day-3 default policy | OP# | If Jared queue stalls | Per `feedback_day3_default_policy_unblocks_jared_dependency.md` — if Jared review of T4 (his voice) stalls 3+ days, MA# ships documented default + async FYI. |
| Tier price drift | LC# / AF# | T5 | If launch pricing changes during the 21-day window (e.g., switch to post-scale $197), T5 needs revalidation. Lock pricing variants at sequence-arm time. |
| Reactive cascade displacement | OP# | All BOOP follow-through | Per `feedback_reactive_cascade_crowds_proactive_routing.md` — protect a proactive slot per BOOP for sequence build progress. |

---

## 5. Pair-Verifier Handoff (REQUIRED)

Per `feedback_verifier_independence_audit_separation.md` and `feedback_routed_items_need_verification_boop.md`:

**SD# (this brief author) MUST NOT also verify.** Different owner required at sign-off.

**Audit ask → OP# (operations-analyst):**

> OP# — at SD# sign-off, please audit this 5-touch sequence brief on these checkpoints before it enters MA# build queue:
>
> 1. **Pricing constitutional check**: Does T5 reference ONLY the $149 price-frozen page? No drift to $74.50 violation page, no reference to post-scale $197 pricing. Confirm with grep against price-frozen page list.
> 2. **Voice constitutional check**: Does T3 audio path use `voice.purebrain.ai` exclusively? No ElevenLabs / rented TTS anywhere in spec.
> 3. **Multi-tenant check**: Is every touch segmentable for future Pure Marketing customer use (i.e., `customer_org_id` swap is wired, not hardcoded brand)?
> 4. **Send-gate audit**: Are all D1 field gates documented (`ai_name`, `seed_status`, `unsubscribe_flags`)? Any NULL-state that would silently break a send?
> 5. **Day-3 default audit**: For each touch requiring Jared review (T2, T4 — Jared voice), is there a documented default copy in case approval stalls 3+ days?
> 6. **Send-rate vs close-rate**: Define the close-rate metric (T5 conversion %) up-front, separate from send-rate (touches delivered). Confirm both are tracked.
>
> Audit output: pass/fail per checkpoint + 1-paragraph integrated risk assessment. File to `.claude/memory/departments/operations-planning/2026-05-XX--SD-activation-sequence-audit.md`.
>
> **Independence**: OP# does NOT report to SD#. OP# audit findings go directly to Aether and (with sufficient confidence) to Jared. SD# may rebut but cannot suppress.

---

## Memory Written

**Path**: `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/sales-distribution/2026-05-03--post-welcome-activation-5-touch-sequence.md`
**Type**: campaign-brief (operational + teaching)
**Topic**: 5-touch post-welcome activation sequence pre-staged for MA# ship

Key learnings captured:
- Pacing rationale (Day 0/2/5/9/14/21) borrowed from proven Neural Feed welcome arc — restraint at CTA is the leverage
- Tier-aware T5 variant prevents Founders from being pitched to (relationship preservation > revenue extraction)
- Segmentation hooks documented up-front so multi-tenant white-label is wire-ready, not retrofit
- Verifier independence pattern formalized: OP# audit checkpoints listed explicitly so SD# cannot mark itself complete
