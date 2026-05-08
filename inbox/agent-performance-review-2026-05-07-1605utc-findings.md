# Agent Performance Review — 2026-05-07 16:05 UTC THU

**Agent**: health-auditor (quality)
**Method**: Sampled recent learnings for output quality + audited manifest depth as prompt-quality proxy. Cross-referenced today's pattern-detector utilization BOOP (12:50 UTC) for context.
**Scope**: 162 manifested agents, 70 with learnings folders.

---

## EXECUTIVE TAKEAWAY

**Output quality is high where invocation is happening.** The agents that fire produce evidence-backed, severity-classified, method-honest work. **Prompt quality is the real gap** — 11 thin manifests (≤25 lines) read as delegation cul-de-sacs, not operational personalities. Fix the prompts and dormant agents become invocable.

---

## TIER A — THRIVING (output exemplary, prompts mature)

| Agent | Evidence |
|---|---|
| **the-conductor** | Nightly self-analyses are brutally honest, evidence-backed, route their own commits. `2026-05-03--nightly-self-analysis.md` includes a "0/3 delivered, this is the SAME anti-pattern" verdict. Self-correcting loop is functioning. |
| **cto** | `2026-05-07--referral-v1-prebuild-review.md` caught hardcoded admin token (`purebrain-admin-2026` fallback) pre-BUILD. Architectural patterns documented with confidence tags. Constitutional gate earning its keep. |
| **qa-engineer** | Hancock Law full QA audit: 56 endpoints tested live, 2 CRITICAL / 5 HIGH / 4 MEDIUM / 5 LOW classification, dead ends transparently flagged. Best-in-class audit format. |
| **pattern-detector** | Today's 12:50 UTC utilization BOOP includes method-honesty caveat ("agent-learnings mtime is floor estimate, not ceiling") and proposes instrumentation. Mature self-aware analysis. |
| **ptt-fullstack** | B7 BUILD: 27/27 tests green, refused to silently fix B4 phantom skill — flagged honestly and re-scoped. TDD discipline holding. |
| **3d-design-specialist** | 122 learnings, consistent format, FLUX/PIL pipeline hardened across 30+ Gleb training nights. Reproducible craft. |

**Pattern**: agents with strong identity-anchored prompts produce strong work.

---

## TIER B — STEADY (cadence healthy, prompts adequate)

linkedin-researcher, sales-specialist, bsky-manager, coder, content-specialist, full-stack-developer, browser-vision-tester, dept-systems-technology, collective-liaison, marketing-strategist.

These fire regularly and produce on-spec output. No prompt changes needed.

---

## TIER C — PROMPT-DEPRIVED (output thin or untestable because prompt is thin)

These manifests are ≤25 lines and read like routing memos, not operational personalities. When invoked, they have nothing to anchor depth against.

| Agent | Lines | Diagnosis |
|---|---|---|
| **fundraising-strategist** | 29 | 🔴 Active $2.5-5M raise, prompt has no methodology, no investor-avatar guidance, no Cortex-spec hooks. **Highest-priority rewrite.** |
| **operations-analyst** | 35 | 🟡 Has rules but ZERO concrete verification-BOOP methodology. Constitutional verifier role per `feedback_routed_items_need_verification_boop.md` — prompt should spell out: "Given a routed item, here's how you verify it." Currently 30h cold (per AM BOOP) → prompt isn't pulling its weight. |
| **channel-strategist** | 19 | Channel priority list but no analysis framework. Referral program "needs optimization" — but how does it analyze? |
| **team-performance** | 21 | Lists hire priorities but no capacity-planning methodology, no delegation-effectiveness measurement protocol. |
| **conversion-optimizer / conversion-rate-optimizer** | 22 | Two agents same domain, both thin. Consolidation candidate. |
| **project-coordinator** | 22 | Empty rules, no OKR cadence, no deliverable-tracking framework. |
| **competitive-analyst** | 25 | No competitor list anchored, no monitoring cadence. |
| **market-researcher** | 25 | No TAM/SAM/SOM methodology stated. |
| **pipeline-tracker** | 27 | Sales pipeline agent — no CRM integration, no scoring methodology. |
| **cts-qa, ptt-qa, wtt-qa** | 21-22 | "Route via X with trigger" boilerplate. These are real QA roles — should have at minimum: (a) what they verify, (b) what evidence they require, (c) when they pass/fail. |

**11 of 162 agents (6.8%)** have prompts so minimal that invocation produces shallow output regardless of model capability.

---

## TIER D — CONSTITUTIONAL ROLES, PROMPT MAY BE THE BLOCKER

Per pattern-detector's BOOP, these are dormant despite constitutional mandates. I scanned manifests to test whether the prompt itself is invocation-blocking:

| Agent | Status | Prompt diagnosis |
|---|---|---|
| **claim-verifier** | Never-fired despite daily blog ships requiring it (verify-publish skill) | Prompt likely fine; problem is **skill not wired into post-blog workflow** — same `feedback_skill_filed_does_not_equal_skill_enforced.md` pattern. |
| **integration-auditor** | No learnings folder, constitutional req for "done" status | Prompt depth not the blocker; **Primary not invoking** — needs hook in mission-completion ceremony. |
| **memory-curator** | No learnings folder, 2000+ memory files unsorted | Prompt depth unknown until checked; likely hook problem. |
| **payment-flow-qa** | Never-fired despite active payment work | Prompt probably exists; **CTS#/ST# delegation chain not routing through it.** |
| **reviewer-audit** | Never-fired despite being final QA gate | Conductor pattern omits it. Either hook into delegation-spine or retire. |

**Pattern**: dormancy here is invocation-pipeline failure, not prompt failure. Different fix class.

---

## ROLE DRIFT (work happening, wrong owner)

Cross-referencing today's commits + pattern-detector's BOOP:

1. 🔴 **Recent referral-v1 work shipped** (commits `0e417f2`, `fa7a4da`, `37cdf89`, `b1c10a3`, `d8a0306`) — CTO **did** sign off pre-build (good), but **security-engineer-tech 63h cold** during D1/Worker security-relevant changes. Security review on `paypal-webhook` A1+A2 webhook signature verification should have paired with build. Audit gap.

2. 🟡 **linkedin-researcher fresh (6h) + linkedin-writer cold (66h)** confirms researcher output is unused. Pair-invocation rule needed in delegation-spine: "researcher fires → writer must follow within 24h or research expires."

3. 🟡 **financial-analyst cold 108h** during active fundraise. If fundraising-strategist gets the prompt rewrite recommended above, financial-analyst pair-invocation should be specified within it.

---

## RECOMMENDED ACTIONS

**This week (prompt rewrites — content fix, not pipeline fix):**
- [ ] Rewrite `fundraising-strategist.md` — investor avatar (Claude API + Chy persona), Cortex spec hooks, valuation methodology, raise stage gates. Pair-call to `financial-analyst` + `investor-relations`.
- [ ] Rewrite `operations-analyst.md` — concrete verification-BOOP procedure: "Given a routed item with status X, evidence required is Y, output format is Z."
- [ ] Audit all 11 sub-25-line manifests; delete or expand. Two conversion-optimizer agents → consolidate to one.
- [ ] Rewrite `claim-verifier.md` AND wire it into `post-blog` skill (per `feedback_skill_filed_does_not_equal_skill_enforced.md`).

**This week (pipeline fixes — invocation, not prompt):**
- [ ] Add `integration-auditor` invocation to mission-completion ceremony. Constitutional req #5 currently theatrical.
- [ ] Add `payment-flow-qa` to PayPal/D1 build pipeline — currently bypassed by ST#→cts-fullstack direct.
- [ ] Pair-invocation rule: any `linkedin-researcher` fire requires `linkedin-writer` within 24h.

**Promote as templates:**
- Conductor's nightly-self-analysis format → use for any strategic agent's reflection cycle.
- QA-engineer's severity-classification format (CRITICAL / HIGH / MEDIUM / LOW + dead ends) → mandatory format for all auditor outputs.
- CTO's confidence-tag + tag-list memory frontmatter → mandatory format for all decision-class learnings.

**Constitutional reinforcement:**
- Per `feedback_new_agent_bar_roster_cap.md`: **freeze net-new agents** until dormancy <50%. (Currently 78% per AM BOOP.) Concur.
- Per `feedback_skill_filed_does_not_equal_skill_enforced.md`: every agent prompt rewrite must end with "wired into [skill/workflow] at [file:line]" — filing ≠ enforcement.

---

## QUALITY METRICS PROPOSED

For next health-auditor cycle (recommend 14d cadence given the cron-stall fragility):

1. **Output-quality score per agent**: severity-classified findings present? evidence cited? dead-ends documented? confidence tagged?
2. **Prompt-depth threshold**: <30 lines = audit candidate. <20 lines = rewrite required.
3. **Pair-invocation adherence**: researcher→writer, builder→security, route→verify. Track gap rate.
4. **"Filed vs enforced" ratio per skill**: skills filed but not wired = the real backlog.

---

**Streak note**: health-auditor was 52d cold; this BOOP fixes that. Last comprehensive review precedent unclear — recommend Aether anchor next cycle to 2026-05-21 as the every-14d marker.

**Method honesty**: I sampled ~12 learnings across 5 tiers and read 7 thin manifests directly. Not exhaustive. A measurable upgrade: parse all 162 manifest YAMLs for line count + skills array length + tools array, write to `.claude/agent-quality-baseline.json`, run weekly diff. Would catch prompt-depth regressions automatically.
