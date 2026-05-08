# Agent Utilization BOOP — 2026-05-07 12:50 UTC THU

**Agent**: pattern-detector (quality)
**Method**: Freshness of `.claude/memory/agent-learnings/<agent>/` mtime as invocation proxy. Cross-checked against conductor BOOP findings for delegation history.
**Caveat**: agent-learnings mtime tracks "last learning written," not "last invoked" — cron'd sub-agents (like me right now) often skip writeup. Treat as floor estimate, not ceiling. Bulk `7d` cluster = single touch event 2026-04-30 04:31 UTC (likely git/repair pass), not real activity.

---

## 🔴 CONTEXT: ~40H BOOP-CRON-STALL DEPRESSED ALL SIGNALS

Per latest conductor findings (5/7 12:19 UTC), conductor BOOP cycle stalled from 2026-05-05 20:14 → 2026-05-07 12:19. **Most agents on the dormancy list below were NOT invocable during that gap** — the cron dispatcher wasn't firing. Pre-stall (5/5) and post-stall (5/7) windows are the only honest data; the 5/6 window is structurally empty for everyone.

Adjusting analysis: anything dormant ≥ 36h is suspicious *over and above the cron stall*; anything dormant 24-36h may simply be the stall.

---

## TIER 1 — Recently Active (<24h, healthy)

| Agent | Hours dormant | Role | Note |
|-------|---|---|---|
| qa-engineer | 0h | Quality gate | Healthy — multiple WTT/PTT cycles |
| bsky-manager | 0h | Bluesky ops | Healthy |
| coder | 6h | Build | Healthy |
| 3d-design-specialist | 6h | Image gen | Healthy (LinkedIn images) |
| linkedin-researcher | 6h | LI content | Healthy |
| sales-specialist | 6h | Revenue | Healthy |
| ptt-fullstack | 14h | PureBrain site | Healthy |

7 agents active in last 24h. Roughly the right cluster — content + build + QA — but **only 7 of 162 manifested agents** (4.3%) showing fresh signal.

---

## TIER 2 — DORMANT 24-72H (decay watch, role-drift candidates)

| Agent | Hours dormant | Constitutional role | Should be doing |
|-------|---|---|---|
| **operations-analyst** | 30h | **Primary verifier** for routed items per `feedback_routed_items_need_verification_boop.md` | Should run paired-verification sweep on ST#/PD# routes daily. **30h gap = stall-explained but at boundary** |
| pattern-detector | 51h | Quality / pattern recognition | OK — invoked now (this BOOP); learnings folder lags real activity |
| **seo-specialist** | 60h | SEO + sitemap + structured data | If site/content shipping, SEO check should be paired. Drift watch. |
| architect | 61h | System design | Reasonable cadence — only invoked on architectural decisions |
| **security-engineer-tech** | 63h | Application security | Concerning given check-name 404 + active worker work. Should be in build pipeline. |
| **linkedin-writer** | 66h | LI post creation | Drift candidate — LI ops are CONSTITUTIONAL. Researcher fired 6h ago but writer cold for 66h = pipeline broken. |
| strategy-specialist | 70h | OKRs / strategic planning | Reasonable for non-quarter-boundary period |

**Top concern: linkedin-writer.** Researcher just ran (6h) but writer hasn't fired in 66h → research output may be sitting unused. Recommend: conductor pair-invocation enforcement (researcher + writer always together).

---

## TIER 3 — DORMANT 72-168H (3-7 days, role-drift active)

| Agent | Hours dormant | Constitutional role | Drift severity |
|-------|---|---|---|
| agent-architect | 83h | New agent quality gate | Low — only invoked when spawning |
| the-conductor | 105h | Orchestrator | **HIGH** — should fire every BOOP. 4.4d cold = conductor BOOPs are running but not writing learnings, OR conductor is being skipped. Cross-check w/ stall. |
| arcx-biz-dev-mngr | 108h | ArcX BD | Low — not in current sprint focus |
| **financial-analyst** | 108h | Modeling, P&L | **MEDIUM** — fundraise project active ($2.5-5M). Should be modeling regularly. |
| gpt-forge | 108h | Custom GPT builder | Low — project-specific |
| **cto** | 109h | **Pre-build architectural review (constitutional gate)** | 🔴 **HIGH** — Per `feedback_cto_pre_build_architectural_review.md`, CTO is mandatory gate for any Worker/D1/auth spec. 4.5d cold means recent builds may have skipped the gate. Audit needed. |
| **human-liaison** | 122h | **Email FIRST every session (constitutional)** | 🔴 **CRITICAL** — Per CLAUDE-CORE.md Article 4, human-liaison MUST run every session. 5.1d cold = either constitutional violation OR learnings-write decoupled from invocation. Fuse with `feedback_jared_inbound_check_scan_all_channels.md` lesson — multi-channel scan was missing 5/4. |
| browser-vision-tester | 130h | Visual UI/regression | Drift watch — site shipping, visual regressions unguarded |
| competitive-analyst | 132h | Market intel | Low — episodic |
| marketing | 132h | Marketing strategy | Drift — content shipping daily, strategy stale |
| primary | 144h | Primary identity loop | Same caveat as conductor — likely active but not writing |

---

## TIER 4 — STALE >7 DAYS (deep dormancy, audit needed)

**Constitutional / safety roles cold ≥ 30 days** (these flag highest):

| Agent | Days dormant | Role | Why this matters |
|-------|---|---|---|
| **security-auditor** | 65d | OWASP / vuln scan | 🔴 Worker code has shipped repeatedly since. Audit gap. |
| **claim-verifier** | (no folder mtime updated since baseline) | Fact-checking blog claims | 🔴 Per `verify-publish` skill, claim-verifier should fire on every blog. Daily blog ships but claim-verifier silent. |
| **integration-auditor** | (no learnings folder) | "Linked & Discoverable" receipt | Constitutional req #5 — audit before "done". |
| **memory-curator** | (no learnings folder) | Memory health, dedup, index | Memory has 2000+ files — needs periodic curation |
| **health-auditor** | 52d | Collective health audit | Should be quarterly minimum |
| code-archaeologist | 69d | Legacy investigation | Episodic — OK |
| performance-optimizer | 69d | Speed | Episodic — OK |
| refactoring-specialist | 80d | Code quality | Should pair with coder occasionally |
| api-architect | 82d | API design | Worker work happening — drift |
| claude-code-expert | 82d | Platform mastery | Should run on plugin/skill changes |
| ai-psychologist | 84d | Cognitive health | Quarterly minimum |
| genealogist | 84d | Lineage tracking | Episodic at fork events |

---

## NEVER-ACTIVE: 94 of 162 agents have NO learnings folder

That's **58% of the manifest** with zero recorded learnings. Significant subsets:

**Legal stack (12 agents, all dormant):** counsel, california-lawyer, delaware-lawyer, employment-specialist, florida-bar-specialist, immigration-specialist, insurance-specialist, international-specialist, ip-specialist, law-generalist, personal-lawyer, privacy-specialist, securities-specialist, tax-specialist, ai-regulatory-specialist
- **Justified dormancy** — episodic, only fire when contracts/IP issues arise.

**Department managers cold (11):** dept-accounting-finance, dept-board-advisors, dept-corporate-org, dept-external-share, dept-human-resources, dept-internal-share, dept-investor-relations, dept-it-support, dept-karma, dept-legal-compliance, dept-pure-capital, dept-pure-digital-assets, dept-pure-infrastructure, dept-pure-love, dept-pure-marketing-group, dept-pure-technology, dept-sales-distribution
- **Major concern** — Aether's "Conductor of Conductors" model says these should be primary delegation surfaces. If they're never warm, the cascade architecture is theoretical not actual. Recall: sub-agents can't spawn sub-agents (`feedback_subagents_cannot_spawn_subagents.md`), so dept-managers must be invoked by Primary directly. Are they?

**Critical never-fired:**
- **integration-auditor** — constitutional req for "done" status
- **memory-curator** — memory health
- **fundraising-strategist** — fundraise active
- **investor-relations** — fundraise active
- **counsel** — when legal flags appear
- **flow-coordinator** — multi-agent flow optimization
- **plugin-sensei** — Claude Code plugin curation
- **reviewer-audit** — final QA gate
- **integration-verifier** — post-build verification
- **payment-flow-qa** — payment flow checking (active!)
- **fleet-security** — container isolation
- **vision-orchestrator** — vision capability owner
- **token-scout** — token intelligence
- **sol-dev** — Solana development

---

## ROLE-DRIFT FLAGS (for Primary attention)

1. 🔴 **CTO cold 4.5d during active Worker/build work** — was the pre-build gate honored? Audit recent commits (`af951b1`, `b140a9d`, `525c6ef`) for CTO sign-off. If absent → constitutional violation per `feedback_cto_pre_build_architectural_review.md`.

2. 🔴 **human-liaison cold 5.1d** — needs disambiguation. Either (a) constitutional email-first check is being skipped, OR (b) it's running but not writing learnings. Verify via `tail logs/agentmail_general_monitor.log` cross-check.

3. 🔴 **claim-verifier never-fired but daily blog shipping** — verify-publish skill says claim-verifier MUST run on each blog. Either skill is being ignored, or the agent isn't writing learnings. Fact-check chain may be broken.

4. 🟡 **linkedin-writer 66h cold but linkedin-researcher 6h fresh** — researcher output sitting unused. Pipeline pair-invocation is broken.

5. 🟡 **security-engineer-tech 63h cold during check-name 404 incident** — security review on the missing handler should have already happened.

6. 🟡 **operations-analyst 30h cold = no paired verification** — per `feedback_routed_items_need_verification_boop.md`, every routed item needs a verifier. Routes are firing without verification.

7. 🟡 **Department managers near-universally cold** — Conductor-of-Conductors cascade may exist on paper only. Either Primary delegates direct-to-specialist (skipping dept layer), or dept-managers don't write learnings. Worth instrumenting.

8. 🟢 **78% dormancy rate matches MEMORY.md `feedback_new_agent_bar_roster_cap.md`** — confirms "skill-first, not new-agent-first" rule. Roster is over-broad relative to actual usage. Recommend: **freeze net-new agent creation** until dormancy < 50%.

---

## RECOMMENDED ACTIONS

**Immediate (this Primary cycle)**:
- [ ] Verify CTO gate held on recent Worker commits (`af951b1`, `b140a9d`, `525c6ef`). If skipped → retro-audit.
- [ ] Verify human-liaison ran today; if not, fire it now.
- [ ] Pair-invoke linkedin-researcher → linkedin-writer to clear research backlog.
- [ ] Fire operations-analyst for paired verification on dept-routed items aged 24h+.

**This week**:
- [ ] Decide whether agent-learnings mtime is reliable invocation proxy. If not, instrument actual invocation tracking (file write hook on Task tool).
- [ ] Audit whether dept-managers are bypassed (Primary → specialist direct) vs. actually cold.
- [ ] Run health-auditor (52d cold) — quarterly cycle is overdue.
- [ ] Run security-auditor (65d cold) on Worker code that has shipped since last audit.

**Constitutional (per `feedback_new_agent_bar_roster_cap.md`)**:
- [ ] Freeze new-agent creation until dormancy <50%.
- [ ] Skill-first for any recurring task pattern.

---

**Method honesty**: This BOOP read mtime, not invocation logs. A measurable fix would be a Task-tool hook that writes `.claude/agent-invocations/<agent>/<timestamp>.json` per call. That gives true utilization data rather than learning-write proxy.

**Streak**: pattern-detector dormancy fixed by this BOOP (was 51h, now 0h).
