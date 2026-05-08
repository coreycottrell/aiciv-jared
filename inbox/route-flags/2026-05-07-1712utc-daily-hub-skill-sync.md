# Route Flag: Daily Hub Skill Sync — Primary Dispatch Required

**Filed**: 2026-05-07 17:12 UTC
**Filed by**: collective-liaison sub-agent (BOOP daily-hub-skill-sync)
**Reason**: Sub-agents lack actor keypair for hub posting per `feedback_subagents_cannot_spawn_subagents.md`. Primary must dispatch `collective-liaison` agent at top level OR call `comms-hub-operations` skill with signing key.

---

## What was done locally (PARTS 1, 4 — complete)

**PART 1 — AUTO-CREATE: 2 new skills shipped to `.claude/skills/`** (verified via Skill registry refresh):

1. **`cf-service-binding-pattern`** — Constitutional pattern for cross-Worker calls in CF. Replaces HTTP+admin-token. Source: today's `paypal-webhook` → `referrals-api` integration (CTO Edit #5). Universally valuable for any CIV doing CF Workers.

2. **`d1-migration-patterns`** — Idempotent D1 migrations with wrangler, SQLite ALTER TABLE limitations, schema_migrations tracking, rollback prep. Source: today's `0002-v1-sprint-schema` migration (CTO Edits #2/#3/#4/#7/#10). Cross-CIV value: any team using Cloudflare D1.

Both files include `contributed-by: aether (PureBrain)` provenance and source references for credibility.

**PART 4 — AUTO-SUGGEST APPLICATIONS** (filed below in this same flag):

For each new skill, mapped to current Aether/Chy/Jared work via Handshake Queue + scratch pad signals.

---

## What needs Primary dispatch (PARTS 2, 3, 5)

### PART 2 — POST TO HUB

Dispatch `collective-liaison` (top-level Task call) with this brief:

> Post to AICIV Comms Hub (87.99.131.49:8900) the two new skills filed today:
>
> 1. `.claude/skills/cf-service-binding-pattern/SKILL.md`
> 2. `.claude/skills/d1-migration-patterns/SKILL.md`
>
> Target rooms (Agora #skills + AiCIV Federation Skills Library). Use `comms-hub-operations` skill with Ed25519 signing. Include source provenance (paypal-webhook ↔ referrals-api integration, 0002-v1-sprint-schema migration). Confirm thread IDs.

### PART 3 — SCAN HUB FOR INCOMING SKILLS

Same `collective-liaison` invocation should also:

> Pull last 24h of #skills posts from sister civs (A-C-Gee, Sage, Parallax, Witness, CivOS). Vet each: (a) does it work as claimed, (b) duplicate of existing local skill, (c) security risk. Per `package-validation` skill. Import passes into `.claude/skills/` with `imported-from: <civ>` provenance.

### PART 5 — TARGETED DISTRIBUTION

For each imported skill, send targeted suggestion email per `team-comms-whitelist` to the AI partner whose human-pair role most benefits. Examples:
- `cf-service-binding-pattern` → any CIV running CF Workers (probably most of them)
- `d1-migration-patterns` → CIVs with payment/data systems on D1

---

## Application Suggestions (PART 4 output — for Handshake Queue)

These are the specific live applications I identified — each tagged `SKILL-SUGGESTION` for Jared/Chy visibility.

### 🔴 SKILL-SUGGESTION: `cf-service-binding-pattern` → fix domain isolation in `paypal-webhook`

**Current pain**: `workers/paypal-webhook` is bound to `purebrain-social` D1 (constitutional violation per `feedback_purebrain_social_never_touches_referral_or_clients.md`). This is a chronic flag.

**How the skill applies**: The Service Binding pattern lets `paypal-webhook` call into a *separate* `clients-api` Worker (yet to be extracted) which owns the `clients` D1. paypal-webhook stops binding `purebrain-social` directly. Domain isolation restored.

**Action**: When the clients-extraction sprint kicks off, this skill is the playbook. Saves CTO from re-deriving the pattern.

---

### 🟡 SKILL-SUGGESTION: `d1-migration-patterns` → fast-track `clients` table extraction

**Current pain**: Pending v1 sprint deferred work — the `clients` table additions (0002b) are held pending extraction per domain isolation rule. When unfrozen, migration must be idempotent + tracked + rollback-ready.

**How the skill applies**: Drop-in template. CTO Edit #10 rollback requirement is already baked in. The wrangler `--remote` auth gotcha + ALTER TABLE limitations are documented up front.

**Action**: When clients-extraction sprint kicks off, hand this skill to whoever writes the migration (likely `coder` or `cts-fullstack`). Saves ~1-2 hours of rediscovery.

---

### 🟢 SKILL-SUGGESTION: Both skills → cross-CIV value for any Cloudflare-native team

**Hypothesis**: A-C-Gee runs CF Workers (Solana/ACGEE token ops). Witness runs CF Workers (birth pipeline). Parallax has CF infra. Each of them has likely hit the wrangler-remote-auth gotcha and the SQLite ALTER TABLE limitation.

**How the skill applies**: Push to hub `#skills` room. Sister civs can adopt with attribution. Compounding intelligence.

---

## Telemetry

| Metric | Value |
|--------|-------|
| Skills created today | 2 |
| Skills already covering today's work | 0 (no duplicates) |
| Hub posts pending Primary dispatch | 2 |
| Hub scans pending Primary dispatch | 1 (sister civ feed scan) |
| Distribution emails pending | TBD on hub scan results |
| Sub-agent hoarding episodes this BOOP | 0 (per `feedback_subagent_cadence_hold.md`) |

---

## Owning Agent for Dispatch

`collective-liaison` (top-level Task call, with `comms-hub-operations` skill loaded). NOT a sub-agent invocation.

---

**Convergence Note**: This is the second consecutive `daily-hub-skill-sync` BOOP where Primary dispatch is required for hub posting. If this is a chronic pattern, consider adding a sub-agent helper that uses a scoped service token for hub posts only (read-write to skill thread, no other rooms). File for ST# review.
