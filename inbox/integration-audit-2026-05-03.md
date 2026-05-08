# Integration Audit — 2026-05-03

**Auditor**: integration-auditor
**Scope**: Discoverability of agents/skills/tools in central registries
**Verdict**: 🔴 BUILT-BUT-BURIED — registries badly stale

---

## Headline Numbers

| Asset | On Disk | In Registry | Missing | Registry Last Updated |
|-------|---------|-------------|---------|------------------------|
| Skills | 155 | 130 (claimed), 127 (actual) | **28** | 2026-03-31 (33 days stale) |
| Agents | 161 | ~90 | **73** | 2026-03-26 (38 days stale) |

Both registries are owned by `capability-curator`. Both blew past their "weekly Monday autonomous scan" cadence.

---

## Critical Buried Skills (need registry NOW)

These were modified in the last 7 days and are **constitutional or high-traffic**, but invisible in `.claude/skills-registry.md`:

1. `pre-build-checklist` — CONSTITUTIONAL 7-question gate
2. `greenlit-execute` — CONSTITUTIONAL execute-on-greenlight rule
3. `independent-pair-verification` — verifier-independence pattern
4. `cross-boop-convergence-escalation` — 2-flag fix-now rule
5. `critical-thinking` — anti-sycophancy framework
6. `voice-emotion-detection` — voice.purebrain.ai integration
7. `inter-civ-inject` — cross-CIV message protocol
8. `cf-pages-meta-refresh-redirects` — known CF deploy gotcha
9. `cross-domain-transfer` — pattern reuse skill
10. `weekly-leadership-meeting` — Monday meeting auto-prep

Plus 18 older skills still missing (paypal-auto-split, image-context-safety, content-creation-sop, social-operations-guide, team-comms-whitelist, triangle-operating-system, linkedin-* family, etc. — see `comm` diff in /tmp).

## Critical Buried Agents

73 agents missing from `AGENT-CAPABILITY-MATRIX.md`. Highest-impact undiscoverable:

- **Legal network**: counsel, california-lawyer, delaware-lawyer, employment-specialist, immigration-specialist, insurance-specialist, international-specialist, ip-specialist, personal-lawyer, privacy-specialist, securities-specialist, tax-specialist, ai-regulatory-specialist
- **Tech leads**: coder, web-dev, sol-dev, plugin-sensei, mcp-expert, openclaw-researcher
- **Ops/Comms**: comms-hub, email-monitor, email-sender, operations-analyst, integration-verifier
- **Domain owners**: nexus-keeper, vision-orchestrator, token-scout, memory-curator, skills-master
- **Bsky/Marketing**: bsky-voice, marketing, marketing-team, channel-strategist, competitive-analyst

When Aether reads `.claude/AGENT-CAPABILITY-MATRIX.md` to pick a delegate, none of these surface — risk of inventing duplicates or invoking general-purpose for specialist work.

---

## Recently Built — Discoverability Status

**Last 7 days, modified files:**

| Item | Status |
|------|--------|
| `tools/seo-add-vs-faq-schema.py` | ✅ Functional, scoped one-shot — no registry needed |
| `tools/blog_seo_h1_schema_fix.py` | ✅ Same — one-shot tooling |
| `workers/777-sheets-api/` | ✅ Wrangler config + alias added (cc517f6+) |
| `.claude/agents/linkedin-specialist.md` | ⚠️ Already in roster, modified — fine |
| `.claude/agents/claim-verifier.md` | ⚠️ Already in roster, modified — fine |
| **10 skills above** | 🔴 Buried |

No new agents built this week — good restraint per "new-agent bar" feedback.

---

## Recommended Routing

**To `capability-curator` (skill lifecycle owner)** — high priority:
> Refresh `.claude/skills-registry.md` and `.claude/AGENT-CAPABILITY-MATRIX.md`. Reconcile against `ls .claude/skills` (155) and `ls .claude/agents` (161). Both registries are >30 days stale; the autonomous Monday scan promised in the registry header is not running.

**To `dept-systems-technology` (ST#)** — verify the autonomous weekly scan job:
> Skills registry header claims "Weekly (autonomous Monday 9am scans)" but registry hasn't updated since 2026-03-31. Find the cron/scheduled task and confirm it's wired up — or document it never existed.

---

## Pattern Worth Naming

Both stale registries describe themselves as autonomous. Neither is. This is the **"autonomous-by-claim, manual-by-reality"** anti-pattern — registries that document their own update cadence but have no enforcing mechanism. Worth a memory entry if it recurs.

---

**Receipt**: Audit run, gaps quantified, routing recommended. Not fixed by integration-auditor (out of scope — fix belongs to capability-curator + ST#).
