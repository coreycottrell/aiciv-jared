# Skill Spec: `constitutional-preflight`

**Designed by**: agent-architect (BOOP, 2026-04-29)
**Builder**: capability-curator
**Status**: SPEC — ready for build
**Quality target**: 90/100

---

## Why this exists — the three incidents

Three deploy/ops incidents in 14 days. **Every rule already existed in MEMORY.md.** None of them fired:

| Date | Incident | Existing rule that should have fired |
|------|----------|--------------------------------------|
| 2026-04-15 | /refer/ deployed to `purebrain-staging` instead of `purebrain-production` — invisible to customers all day | "purebrain-production for customer-facing" (MEMORY.md "Site (CF Pages)") |
| 2026-04-23 | Trio injector `tmux send`'d internal comms into Thread Mark customer container | "🔴 NEVER DEPLOY TO CUSTOMER CONTAINERS" (locked 2026-04-23) |
| 2026-04-16 | Local file deploy bypassed git, wiped CF Functions, lost 30hr investor build | "🔴 NEVER LOCAL DEPLOY" (locked 2026-04-16) + "Wrangler BANNED" |

**Pattern**: rules-as-prose in MEMORY.md require an agent to *remember* and *apply* them mid-execution. They don't. We need a pattern-matching pre-flight that fires on the dangerous verbs themselves.

---

## 1. Trigger Patterns (what auto-fires the preflight)

The skill activates when an agent's next tool call matches any of these. Capability-curator can grep for these literal strings in the agent's proposed Bash/Edit/Write payload before execution:

### 1A. Deploy verbs (HIGH severity)
```
cf-deploy.py                          # any invocation
wrangler pages deploy                 # BANNED — must hard stop
wrangler deploy                       # CF Workers — flag-and-confirm
wrangler r2|d1|kv                     # data-plane writes — flag
CF_DEPLOY_FORCE_PROTECTED=1           # BANNED — must hard stop
CF_PAGES_PROJECT=purebrain-production # require git-clean check
git push.*main                        # to customer-facing repos
```

### 1B. Customer container injection (HIGHEST severity)
```
tmux send-keys.*-t (?!aether|primary|jared)   # any non-internal session
ssh.*@(thread-mark|<customer-pattern>)         # customer-named hosts
docker exec.*<customer-container>              # customer container exec
echo.*>>.*\.bashrc                             # any shell injection
```

Customer-container detection: if target session/host/container name is NOT in `aether|primary|chy|morphe|witness|<known-internal>` allowlist → flag as customer-facing.

### 1C. Payment / money movement (HIGH severity)
```
paypal.*api/v(1|2)/payments           # live payments API
paypal_auto_split\.py                 # split execution
PAYPAL_MODE=live                      # env var
sandbox\.paypal\.com → api\.paypal\.com  # endpoint switch
```

### 1D. Constitutional content modification (MEDIUM severity)
```
edit.*onboarding|seed|magic-link|payment       # files matching ONBOARDING-SPEC-DEFINITIVE.md scope
edit.*investor.*codes|gift.*pages              # FROZEN content
edit.*homepage|index\.html.*production         # 10-page payment guard set
```

### 1E. Voice / TTS (HIGH severity, post-Apr-15 ban)
```
elevenlabs\.io                        # BANNED entirely
api\.elevenlabs                       # BANNED entirely
ElevenLabs                            # case-insensitive string match
```

### 1F. Container persistence (MEDIUM severity)
```
sqlite3.*\.db                         # in-container SQLite for prod data
write.*memories/.*production          # container-local prod data
```

**Trigger philosophy**: false positives are cheap (one extra confirm prompt). False negatives cost us 30 hours of investor work. Bias toward over-triggering, especially for 1A/1B/1E.

---

## 2. Rule Source Layer (architecture decision)

**Recommendation**: **Hybrid — derive a `.claude/CONSTITUTIONAL-RULES.json` from MEMORY.md + feedback files, regenerated nightly by capability-curator.**

**Justification (2 sentences)**: MEMORY.md and feedback_*.md are the canonical authoring surfaces — Jared and Aether already write rules there in natural language, and changing that workflow would create authorial friction and drift. But pattern-matching at execution time needs structured triggers/actions, not prose, so we generate a JSON cache that the skill loads in O(1) — single source of truth (MEMORY.md), single read path (JSON), nightly sync closes the loop.

**Schema** (`.claude/CONSTITUTIONAL-RULES.json`):
```json
{
  "generated_at": "2026-04-29T...",
  "source_files": ["MEMORY.md", "feedback_*.md", "CLAUDE.md", "ONBOARDING-SPEC-DEFINITIVE.md"],
  "rules": [
    {
      "id": "no-customer-container-deploy",
      "severity": "HARD_STOP",
      "triggers": ["tmux send-keys.*-t thread-mark", "ssh.*customer-portal"],
      "rule": "Never deploy/inject into customer containers",
      "source": "MEMORY.md L180, feedback_never_deploy_to_customer_containers.md",
      "incident_ref": "2026-04-23"
    },
    {
      "id": "wrangler-banned",
      "severity": "HARD_STOP",
      "triggers": ["wrangler pages deploy"],
      "rule": "Use cf-deploy.py only — wrangler deletes pages not in local folder",
      "source": "MEMORY.md L71, feedback_wrangler_banned_cf_deploy_only.md",
      "incident_ref": "2026-04-16"
    },
    { "...": "..." }
  ]
}
```

**Rules NOT chosen, with reason**:
- *Pure MEMORY.md grep at runtime*: too slow + brittle (200-line file grows, format changes break parser).
- *Hand-curated `.json` only*: drifts from MEMORY.md immediately — same drift problem skills-registry has (28 days stale per Apr 28 audit).
- *Live re-parse every invocation*: latency unacceptable on hot deploy paths.

**Sync mechanism**: capability-curator's nightly BOOP runs `tools/build-constitutional-rules.py` (capability-curator builds this too) which parses the source files and writes the JSON. Same job validates that every `🔴 CONSTITUTIONAL` block in MEMORY.md has a corresponding rule entry — drift is logged.

---

## 3. Attachment Points (which agents auto-load)

**Recommended final list** (YAML `skills:` frontmatter):

**Tier 1 — must have (touch deploy/ops/customer infra):**
- `devops-engineer`
- `dept-systems-technology` (routes all tech work)
- `ptt-fullstack` (Pure Tech main builder)
- `cts-fullstack` (Chy/Cortex builder)
- `wtt-fullstack` (Witness builder)

**Tier 2 — should have (frequently call deploy/ops verbs):**
- `the-conductor` (Primary — this is me/Aether — last line of defense)
- `agent-architect` (when spawning agents that touch ops)
- `dept-finance` (PayPal triggers)
- `dept-marketing` (LinkedIn token / OAuth ops)

**Tier 3 — defer (low ops surface):**
- QA agents (`ptt-qa`, `cts-qa`, `wtt-qa`) — they verify, rarely deploy. Skip for now, add if QA starts auto-fixing.
- Content agents (`linkedin-writer`, `blogger`, `3d-design-specialist`) — they trigger ElevenLabs rule, but that's covered by Tier 1 dept-marketing routing.

**Final attachment count**: **9 agents Tier 1+2.** Roster bias respected (no new agents, just skill loading).

---

## 4. Block vs. Flag Behavior

Three response modes. Severity comes from `CONSTITUTIONAL-RULES.json`:

| Severity | Behavior | Examples |
|----------|----------|----------|
| **HARD_STOP** | Refuse execution. Return error. Require Jared override token (`OVERRIDE: <rule-id>` in dispatch text) to proceed. | Customer container injection (Apr 23), `wrangler pages deploy`, `CF_DEPLOY_FORCE_PROTECTED=1`, ElevenLabs API call, modifying frozen investor codes |
| **FLAG_CONFIRM** | Show the rule + incident reference. Require explicit "yes proceed" in same turn before executing. Single-turn confirm. | CF Pages project mismatch (deploying to `purebrain-staging` when path implies customer-facing), live PayPal switch, editing onboarding spec files |
| **WARN_CONTINUE** | Log to `.claude/preflight-warnings.jsonl`, surface in next session summary, but don't block. | Container SQLite for non-prod data, edits to homepage during off-hours |

**Specific incident-driven mappings:**
- **Apr 23 (customer container)** → HARD_STOP. No exceptions. The override token requirement makes Jared an explicit second pair of eyes for any future legitimate customer-container ops (rare → likely never).
- **Apr 15 (wrong CF project)** → FLAG_CONFIRM. The deploy itself is legitimate; the *target* needs human verification. Skill prints: "About to deploy to `purebrain-staging`. Path `/refer/` matches customer-facing pattern. Did you mean `purebrain-production`? [yes/no]"
- **Apr 16 (local deploy / wrangler)** → HARD_STOP for `wrangler pages deploy` and `CF_DEPLOY_FORCE_PROTECTED=1`. These have zero legitimate use cases per MEMORY.md.
- **PayPal sandbox vs prod** → FLAG_CONFIRM on any switch from `sandbox` to `live` mode. HARD_STOP on direct `api.paypal.com/v2/payments` without going through `paypal_auto_split.py`.

**Override token format**: `OVERRIDE: <rule-id> reason: <one-line>` — logged to `.claude/preflight-overrides.jsonl` with timestamp + agent + task. Reviewed weekly by capability-curator.

---

## 5. Failure Mode (skill itself errors)

**Decision: FAIL-CLOSED with clear error.**

If the skill cannot:
- Load `CONSTITUTIONAL-RULES.json` (file missing, malformed, stale >7d)
- Parse the proposed action
- Match against rules

…then it **blocks the action** and returns:
```
PREFLIGHT FAILURE: <reason>
Action NOT executed. 
Manual override: include "OVERRIDE: preflight-fail reason: <why safe>" in dispatch.
Sync: BOOP capability-curator to regenerate rules JSON.
```

**Justification**: The three incidents prove fail-open is a feature in disguise — an "unenforced" rule is the same as fail-open. Cost of fail-closed = one extra round-trip when JSON is broken (rare, fixable in <5 min by curator). Cost of fail-open = repeat of Apr 16/23 = lost work + customer trust damage.

**Staleness check**: if `generated_at` >7 days old, skill emits WARN but still runs (rules are mostly stable; the BOOP fix from Gap 2 will keep this fresh).

---

## Quality Self-Score: 92/100

| Dimension | Score | Notes |
|-----------|-------|-------|
| Clarity | 19/20 | Specific patterns, concrete severity levels, every decision justified |
| Completeness | 19/20 | All 5 sections covered + override mechanism + failure mode |
| Constitutional alignment | 19/20 | Maps directly to existing MEMORY.md rules; doesn't invent new doctrine |
| Activation precision | 18/20 | Trigger regexes are explicit; -1 for not exhaustively enumerating customer-container hostnames (curator should expand) |
| Integration readiness | 17/20 | Clear handoff to capability-curator; -3 because the rules-JSON generator script is described but not specified line-by-line (curator's design space) |

---

## Out-of-scope (explicit)

- ❌ Writing the SKILL.md — capability-curator's job
- ❌ Writing `tools/build-constitutional-rules.py` — capability-curator's job
- ❌ Voice-ops agent (Gap 3) — separate spec, separate track
- ❌ Tools-registry (Gap 2) — covered by capability-curator scope expansion

---

**Spec by agent-architect, 2026-04-29.**
**Routes to**: capability-curator for build.
**Verification owner**: operations-analyst (per verifier-independence rule — capability-curator should NOT verify their own build).
