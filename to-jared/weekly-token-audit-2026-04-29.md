# Weekly Token Audit — 2026-04-29

## TL;DR — STATE UNCHANGED, GROWTH CONTINUES

**Always-loaded context: ~14,356 tokens (43% over 10K target).** Both compression proposals from last week (Apr 28) are still pending your greenlight. In the 24h since, MEMORY.md grew another **3 lines / +158 tokens** — accelerating, not stable.

The pre-drafted compressed MEMORY.md still sits at:
- `to-jared/MEMORY-compressed-proposal-2026-04-28.md` (ready to deploy on one-word "go")

---

## Current State

| File | Lines | ~Tokens | Target | Status |
|------|-------|---------|--------|--------|
| **CLAUDE.md** (always loaded) | 942 | **8,844** | <3,500 | 2.5x over (unchanged) |
| **MEMORY.md** (always loaded) | 237 | **5,512** | <1,000 | 5.5x over **+ STILL TRUNCATED** |
| **Always-loaded total** | 1,179 | **~14,356** | <10,000 | **43% over** |
| CLAUDE-CORE.md (wake-up) | 415 | 3,932 | — | OK |
| CLAUDE-OPS.md (wake-up) | 474 | 4,291 | — | OK |
| AGENT-CAPABILITY-MATRIX.md (wake-up) | 428 | 5,887 | — | OK |
| ACTIVATION-TRIGGERS.md (wake-up) | 1,194 | 10,247 | — | bloated |

### Week-over-Week Trend

| Audit Date | Always-Loaded Tokens | Δ vs Prior | Status |
|------------|---------------------|------------|--------|
| 2026-02-27 | ~9,600 | (baseline) | UNDER target |
| 2026-04-09 | ~11,184 | +16.5% | 12% over |
| 2026-04-28 | ~14,198 | +27% | 42% over |
| **2026-04-29** | **~14,356** | **+1.1% in 24h** | **43% over** |

24-hour drift = **+158 tokens** (MEMORY.md only). At this rate: +4,740 tokens/month if uncorrected.

---

## What Changed Since Last Audit (Apr 28 → Apr 29)

**MEMORY.md additions (3 lines, +158 tokens):**
1. Voice selection rules expanded — Aether default vs Chy override clarification (Voice block now ~6 lines for what could be 1 index entry)
2. aether-aiciv@agentmail.to inbox skip rule added inline (should be 1 line → topic file)
3. AgentMail address line edited

**System reminder is still firing the truncation warning** — line 200+ continues to be silently dropped from context. Critical content still absent:
- Sub-agents cannot spawn sub-agents (constitutional)
- All recent self-analysis entries (Apr 14, 15, 23, 24, 25, 26)
- References block (Drive vault folder IDs, business-reference)

---

## Status of Last Week's Recommendations

### Track 1 — MEMORY.md Compression (PROPOSAL READY)

- **Drafted:** `to-jared/MEMORY-compressed-proposal-2026-04-28.md` (11.7KB)
- **Status:** awaiting one-word "go"
- **Impact:** 237 lines → ~110, 5,512 → ~1,400 tokens (-74%)
- **Risk:** none — all detail already exists in 210 topic files
- **Bonus:** ends silent truncation, restores Apr 14–26 context

### Track 2 — CLAUDE.md Compression (CONSTITUTIONAL APPROVAL NEEDED)

- **Status:** unchanged from Apr 9 + Apr 28 audits, still pending
- **Items:** 7 compression candidates, ~4,380 tokens of duplicates
- **Projected after compression:** CLAUDE.md 8,844 → ~4,464 tokens
- **After both tracks:** total always-loaded ~8,400 tokens (UNDER 10K target)

---

## Recommendation This Week

**Same as last week, more urgent.**

The proposal is sitting in `to-jared/`. Each day without action:
- MEMORY.md grows ~150 tokens
- More recent learnings get pushed past the 200-line truncation cliff
- "Sub-agents cannot spawn sub-agents" stays out of context (already silently absent)

**Lowest-friction path:** reply "go MEMORY" to greenlight Track 1 only. Track 2 (CLAUDE.md) can wait.

---

## New This Week — Anti-Pattern to Watch

The Voice rules just expanded MEMORY.md by 6 lines (~95 tokens) instead of being filed as `feedback_voice_default_aether_chy_override.md` and indexed in 1 line. **Pattern:** rules-of-thumb keep getting embedded inline rather than topic-filed.

If next audit shows continued growth despite Track 1 cleanup, recommend a **MEMORY.md write-discipline rule:** any new entry > 150 chars MUST be a topic file + 1-line pointer. Aether (me) and any agent writing memories must enforce this.

---

## Next Audit

**Target:** 2026-05-06 (weekly cadence). If Track 1 greenlit before then, expect MEMORY.md restored to <1,500 tokens. If unchanged, this report becomes copy-paste of itself with bigger numbers.

---

**Audited by:** doc-synthesizer (scheduled BOOP)
**Skill:** `.claude/skills/weekly-token-audit/SKILL.md`
**Pre-drafted compression:** `to-jared/MEMORY-compressed-proposal-2026-04-28.md`
