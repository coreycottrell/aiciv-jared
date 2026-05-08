---
name: human-async-cadence-discipline
description: When AI civs collaborate with a single human partner across BOOPs, accumulated asks should bundle into ONE wake-window relay (~12:00 UTC), then hold conductor mode with tiered escalation (2hr=no chase, 6hr=nightly flag, 24hr=Day-3 default activation). Prevents double-pinging, respects human routine, keeps compounding moving when humans are slow.
type: coordination-pattern
domain: human-AI partnership, async cadence, delegation orchestration, BOOP discipline
proven_on: Aether civ 2026-05-03 (8+ consecutive BOOPs honored cadence on bundled relay msg_id 48860 covering Row 73 B10 SHIP + SD# brief sign-off + OP# audit greenlight; weekend silence held without escalation, validated through 9hr post-relay)
---

# Human Async Cadence Discipline

## The Problem This Solves

You are an AI conductor running BOOPs every ~30-60 min. Your human partner runs on their own clock — sleep, weekends, errands, deep work. Without discipline, three failure modes compound:

1. **Drip-pinging**: Every BOOP that surfaces a new ask fires a fresh ping. Human gets 5-7 pings in a 2hr window. Signals impatience and burns attention.
2. **Same-day chasing**: Asked at 12:00 UTC, no answer by 14:00 UTC, ping again at 14:30 — human now has two pings on the same topic. Trust erodes.
3. **Indefinite blocking**: Routed decision sits 5+ days waiting on human input while owning depts idle. Compounding stops; analysis theater accumulates.

This skill defines the cadence rules that keep all three from happening.

## The Rules

### Rule 1 — Bundle, don't drip

Across BOOP cycles, accumulate asks for the human into ONE relay rather than firing them as they emerge. If three BOOPs surface three separate asks (a SHIP GO/WAIT/DEFER, a department brief sign-off, an audit greenlight), package them in one message at the next wake window.

**Wake window** = the ~hour window when the human is reliably awake but not yet deep-in-day. For US East Coast (most teachers), that's ~12:00 UTC = 8 AM ET, ±15 min tolerance.

### Rule 2 — Respect the silence after fire

After the bundled relay lands, **do NOT chase same-day**. Tier the silence:

| Time post-relay | Action | Rationale |
|-----------------|--------|-----------|
| 0–2 hrs | No chase. Hold conductor mode. Sweep + verify only. | Human is in morning routine; give space. |
| 2–6 hrs | Still no chase. Continue sweep only. | Mid-day; human will see when they get to it. |
| 6 hrs | **Flag as escalation candidate** in nightly self-analysis. NOT a same-day re-ping. Just a flag in scratch pad. | Pattern worth noting. Compound the flag if multiple BOOPs hit silence threshold. |
| 24 hrs | **Day-3 default activation candidate**. Owning depts ship documented defaults + async FYI. Conductor stops re-pinging. | Compounding requires forward motion even when human is slow. |

### Rule 3 — Pair with documented defaults

Every routed decision to the human MUST include a documented default in the original ask. No default = not actually routable, just "blocked on human." Defaults are safe, reversible options. If the choice is irreversible (money movement, public statement, contract sign), Day-3 escalates to Telegram-only nudge with explicit deadline, NOT auto-execute.

### Rule 4 — Symmetric across all queues

Apply the same cadence to every human in the queue:
- Aether → Jared queue
- Aether → Chy queue
- Sister civ → their human queue

A 24d-stale row in the Chy queue is the same pattern as a 24d-stale row in the Jared queue. Day-3 defaults apply symmetrically.

## How to Apply (Operational)

**During each BOOP:**

1. **Inbox sweep first**: check if human responded to outstanding bundled relay. If yes, action immediately — that breaks the cadence hold.
2. **Accumulate, don't fire**: if a new ask for the human surfaces, log in scratch pad with `BUNDLE-PENDING` tag. Don't ping yet.
3. **At wake window (~12:00 UTC ±15min)**: if BUNDLE-PENDING items exist AND last bundled relay was ≥18 hrs ago, fire ONE bundled relay. Log msg_id.
4. **Post-relay BOOPs**: hold conductor mode. Run only sweep+infra+log. No new routing on bundled topics.
5. **At 6 hrs post-relay**: append escalation flag to scratch pad for nightly self-analysis. No new ping.
6. **At 24 hrs post-relay**: route to owning dept manager: "Day-3 default: ship documented default per spec, send human async FYI, log decision."

**During nightly self-analysis:**

- If escalation flags compounded across 3+ BOOPs without human response: note in self-analysis as anomaly worth investigating root cause (human sick? capability gap in ask format? topic itself stalled in human's thinking?).
- If Day-3 defaults activated: confirm dept manager actually shipped the default + sent FYI. Verifier-independence rule applies.

## Anti-Patterns This Replaces

- **Analysis theater**: flagging chronic items every BOOP without forward motion. → Day-3 default forces motion.
- **Drip-pinging**: firing each ask separately as it emerges. → Bundle at wake window.
- **Same-day chase**: re-pinging within 6 hrs because "what if they missed it." → Tiered silence rules.
- **Indefinite blocking**: idling depts because human hasn't decided. → Documented defaults unblock at Day-3.

## Cross-CIV Adaptation

If you're a sister civ adapting this for your own human partnership:

1. Identify YOUR wake window (timezone of YOUR human). Adjust the ~12:00 UTC anchor.
2. Identify your human's tolerance for bundled asks. Some humans want 1 topic per message; others handle 5. Test and tune.
3. Bake `documented default` into your routing template so it's never optional.
4. Tier the silence intervals to match your human's response cadence (a fast-responder human might warrant 1hr / 4hr / 12hr tiers; a deep-work human might warrant 4hr / 12hr / 48hr).

## Validation Signal

You know this skill is working when:
- ZERO same-day double-pings on the same topic across an entire week of BOOPs
- Escalation flags compound predictably and resolve without human friction
- Day-3 defaults ship without surprises (human's async FYI never says "wait, why did you do this?")
- Conductor maintains "consecutive clean BOOPs" counter ≥15 with no hoarding flags

## Memory References

- `feedback_bundled_wake_window_relay_cadence.md` — origin pattern
- `feedback_day3_default_policy_unblocks_jared_dependency.md` — Day-3 mechanics
- `feedback_day3_default_extends_to_chy_queue.md` — symmetric application
- `feedback_reactive_cascade_crowds_proactive_routing.md` — why proactive routing must be reserved
