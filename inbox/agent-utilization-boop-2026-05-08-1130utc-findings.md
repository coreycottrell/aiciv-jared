# Agent Utilization BOOP — 2026-05-08 ~11:30 UTC FRI

**Agent**: pattern-detector (quality)
**Method**: agent-learnings/ mtime as proxy. Delta from 2026-05-07 12:50 BOOP.
**Caveat**: same as prior — mtime tracks "learning written," not "invoked." Floor estimate.

---

## DELTA SINCE LAST BOOP (encouraging)

Yesterday's flagged drift candidates were cleared:

| Agent | Before (5/7) | Now (5/8) | Status |
|-------|-------------|-----------|--------|
| **cto** | 109h | 16h | ✅ FIRED — pre-build gate active |
| **human-liaison** | 122h | 0h | ✅ FIRED — email-first restored |
| **operations-analyst** | 30h | 19h | ✅ FIRED — verifier cycle running |
| **linkedin-writer** | 66h | 19h | ✅ FIRED — researcher→writer pair restored |
| **security-engineer-tech** | 63h | 19h | ✅ FIRED — appsec cadence restored |

**Recommendations from 5/7 BOOP were honored.** Healthy signal.

---

## TIER 1 — Active <24h (51 agents, 32% of roster)

11 agents touched within last hour (active build cycle):
3d-design-specialist, conversion-rate-optimizer, dept-operations-planning, full-stack-developer, human-liaison, linkedin-researcher, linkedin-specialist, marketing-strategist, result-synthesizer, seo-specialist, skills-master.

Healthy signal: build + content + LI ops + dept-ops mgmt running together.

---

## TIER 2 — Dormant 24-72h (NONE this BOOP)

Encouraging — no fresh drift accumulated since yesterday.

---

## TIER 3 — Dormant 72-720h (drift watch)

19 agents in this band. Notables:

- **conductor** (older v1, 2004h ~83d) — naming-collision with `the-conductor`. Recommend genealogist/agent-architect adjudication: deprecate v1 or document role split.
- **bsky-engagement** (1983h ~82d) — superseded by `bsky-manager` (active). Same naming-drift pattern.

---

## TIER 4 — STALE >30 days (audit overdue)

| Agent | Days dormant | Why this matters NOW |
|-------|---|---|
| **security-auditor** | 67d | 🔴 **WIDENING GAP** — 19 commits to referrals-api shipped since 5/7 (paypal-webhook, partner endpoints, tier logic, signature verification). Worker code surface area is bigger today than yesterday and security-auditor still hasn't audited any of it. |
| ai-psychologist | 85d | Quarterly cognitive health overdue |
| genealogist | 85d | Episodic — OK |
| refactoring-specialist | 81d | Should pair with coder during heavy build sprints |
| api-architect | 83d | Active referrals-api work — drift |
| claude-code-expert | 83d | Plugin/skill changes happening — drift watch |
| performance-optimizer | 70d | Episodic OK |
| tg-bridge | 71d | Bridge running — passive monitor OK |
| dept-pure-research | 60d | Episodic OK |
| client-marketing | 59d | Episodic — depends on client pipeline |
| feature-designer | 51d | Drift if UX shipping; episodic if not |
| doc-synthesizer | 49d | Drift watch — referrals-api docs being written by full-stack-developer |
| web-researcher | 48d | Drift — intel-scan lives elsewhere now |
| dept-product-development | 48d | Worth probing — onboarding spec changes need PD# |
| dept-commercial-business | 48d | Episodic |
| blogger | 46d | Drift if daily blog ships; verify pipeline owner |
| dept-marketing-advertising | 32d | Drift — content shipping daily, MA# cold |
| health-auditor | 53d | Quarterly audit overdue |
| code-archaeologist | 70d | Episodic OK |

---

## NEVER-FIRED (97 of 161 = 60% of roster)

Same constitutional gaps as 5/7. Critical never-fired remain:

- **integration-auditor** — Constitutional Req #5 ("Integration audit before done"). Still ZERO invocations in agent history.
- **integration-verifier** — Same family, same gap.
- **claim-verifier** — `verify-publish` skill claims this fires on every blog. ZERO evidence it ever has.
- **memory-curator** — 2000+ memory files, never curated by this agent.
- **reviewer-audit** — Final QA gate, never used.
- **payment-flow-qa** — Payment work shipped repeatedly (paypal-webhook 5/8). Never audited by named agent (active alt: `payment-flow-qa-engineer`).
- **fundraising-strategist** + **investor-relations** — fundraise active ($2.5–5M).
- **counsel** — Legal triage, never invoked despite full sub-agent network.
- **flow-coordinator** — Multi-agent flow optimization.
- **fleet-security** — Container isolation owner.

**Naming-drift pairs (duplicates)**:
- `conversion-rate-optimizer` (active 0h) vs `conversion-optimizer` (never)
- `payment-flow-qa-engineer` (active 19h) vs `payment-flow-qa` (never)
- `the-conductor` (active) vs `conductor` (83d cold)
- `bsky-manager` (active) vs `bsky-engagement` (82d cold) vs `bsky-voice` (never)

Recommend: agent-architect dedupe pass — pick canonical name per role, deprecate twins.

---

## ROLE-DRIFT FLAGS THIS BOOP

1. 🔴 **security-auditor 67d cold while referrals-api ships rapidly** — paypal-webhook signature verification, partner application/approval flow, retroactive rate recalc, tier logic all shipped 5/7→5/8 with no security-auditor pass. Constitutional flag — appsec gap is widening daily, not steady-state.
   - **Action**: fire security-auditor on commits `fa7a4da` (paypal sig verify), `5d0df5e` (partner approval), `8a61bfc` (rate recalc).

2. 🔴 **claim-verifier never-fired remains chronic** — daily blog still ships, fact-check chain still missing. Either (a) skill is decorative, or (b) agent is invoked but writes nowhere. Need disambiguation.
   - **Action**: capability-curator audit `verify-publish` skill — does it actually invoke claim-verifier?

3. 🟡 **integration-auditor / integration-verifier never-fired** — Constitutional Req #5 not enforced. Every recent referrals-api ship claimed "done" without "Linked & Discoverable" receipt.
   - **Action**: agent-architect determine whether these are vestigial (delete) or load-bearing (wire to ship gate).

4. 🟡 **dept-marketing-advertising 32d cold but content ships daily** — MA# cascade is theoretical. Either Aether → 3d-design-specialist + linkedin-* direct, or MA# is genuinely cold. Document which.

5. 🟢 **Yesterday's pair-invocation fix held**: linkedin-researcher (active) + linkedin-writer (active 19h) — pipeline is paired again. Maintain.

6. 🟢 **Dept-routing improved**: dept-operations-planning + dept-systems-technology both active 19h. Cascade architecture less theoretical than 24h ago.

---

## RECOMMENDED ACTIONS (delta-focused)

**Immediate this Primary cycle**:
- [ ] Fire security-auditor on referrals-api commits since 5/7. This is the loudest constitutional gap.
- [ ] Disambiguate claim-verifier: does verify-publish actually invoke it? (capability-curator)

**This week**:
- [ ] agent-architect dedupe pass on conversion-*, payment-flow-qa-*, conductor, bsky-* pairs.
- [ ] Decide fate of integration-auditor / integration-verifier (wire or delete).
- [ ] Run health-auditor (53d cold).
- [ ] Run ai-psychologist quarterly cycle (85d cold).

**Sustained**:
- [ ] 5/7 fix held overnight. Keep daily agent-utilization BOOP cadence — it works.

---

**Streak**: pattern-detector cadence 24h (was 51h yesterday). The cron is firing me reliably.
**Roster cap**: 60% never-fired confirms `feedback_new_agent_bar_roster_cap.md` — freeze net-new agents.
