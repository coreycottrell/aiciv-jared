# Weekly Token Audit — 2026-05-07

## TL;DR — PARTIAL WIN, STILL OVER TARGET

**Always-loaded context: ~13,041 tokens (30% over 10K target).** Down 9.2% from last week (14,356 → 13,041). MEMORY.md was partially compressed (237 → 136 lines, -1,315 tokens), but CLAUDE.md compression (Track 2) remains untouched and is now the dominant overage source.

**This week's ask:** greenlight Track 2 (CLAUDE.md compression). Drops total to ~8,400 tokens, finally under the 10K target.

---

## Current State

| File | Lines | ~Tokens | Target | Status | Δ vs Apr 29 |
|------|-------|---------|--------|--------|------------|
| **CLAUDE.md** (always loaded) | 942 | **8,844** | <3,500 | 2.5x over | unchanged |
| **MEMORY.md** (always loaded) | 136 | **4,197** | <1,000 | 4.2x over | -101 lines / -1,315 tokens ✅ |
| **Always-loaded total** | 1,078 | **~13,041** | <10,000 | **30% over** | **-9.2%** |
| CLAUDE-CORE.md (wake-up) | 415 | 3,932 | — | OK | unchanged |
| CLAUDE-OPS.md (wake-up) | 474 | 4,291 | — | OK | unchanged |
| AGENT-CAPABILITY-MATRIX.md (wake-up) | 428 | 5,887 | — | OK | unchanged |
| ACTIVATION-TRIGGERS.md (wake-up) | 1,194 | 10,247 | — | bloated | unchanged |

### Week-over-Week Trend

| Audit Date | Always-Loaded | Δ vs Prior | Status |
|------------|---------------|------------|--------|
| 2026-02-27 | ~9,600 | (baseline) | UNDER target |
| 2026-04-09 | ~11,184 | +16.5% | 12% over |
| 2026-04-28 | ~14,198 | +27.0% | 42% over |
| 2026-04-29 | ~14,356 | +1.1% (24h) | 43% over |
| **2026-05-07** | **~13,041** | **-9.2%** | **30% over** |

First downward trend since Feb baseline. Track 1 partial compression worked.

---

## What Changed Since Apr 29

**MEMORY.md (auto-memory) compressed from 237 → 136 lines.** Most multi-line blocks consolidated into denser bullets. Truncation warning gone (under 200-line limit). Content reorganized into 14 thematic sections.

**However:** of 99 bullet lines in MEMORY.md, only **1** follows the documented one-line `[Title](file.md) — hook` index format. The rest are still embedding rule content inline rather than pointing to topic files. **The pattern from last week's anti-pattern note (rules embedded inline) continues** — just at higher density per line now.

**Long-line check:** 25 lines exceed 200 chars (target: 0). Worst offenders:
- Line 124 (425 chars): "Multi-channel sweep before Jared silent" — entire incident write-up inline
- Line 127 (394 chars): "BOOP gap detection" — full root-cause analysis inline
- Line 123 (316 chars): "On my side = absorption tell" — full incident inline

These belong as `feedback_*.md` topic files with 1-line MEMORY.md pointers.

**CLAUDE.md (project file) unchanged** — last commit `fbe3fc1` predates audit history; Track 2 has been pending greenlight since 2026-04-09 (~4 weeks).

---

## Recommendation This Week

### Track 2 — CLAUDE.md Compression (CONSTITUTIONAL APPROVAL NEEDED)

Same items, fourth audit asking. After Track 1 success, this is the lowest-hanging fruit remaining.

| Item | Token Savings | Risk |
|------|---------------|------|
| Agent roster duplicates AGENT-CAPABILITY-MATRIX.md | 1,400 | low — pure dup |
| Wake-Up Protocol detail duplicates CLAUDE-OPS.md | 1,500 | low — already in OPS |
| Skills section duplicates delegation-spine SKILL.md | 350 | low — pure dup |
| Closing/recap sections | 280 | low — restates above |
| Duplicate Telegram reminder (appears twice) | 130 | low — exact dup |
| "Balance" + "Lineage" (philosophy → CORE.md) | 320 | medium — moves content |
| Quick Ref + Navigation Guide overlap | 400 | medium — restructure |
| **Total** | **~4,380** | |

**Projected:**
- CLAUDE.md: 8,844 → ~4,464 tokens
- Always-loaded total: 13,041 → **~8,661** (UNDER 10K target ✅)

**Lowest-friction path:** reply "go CLAUDE" to greenlight. I'll draft the compressed CLAUDE.md to `to-jared/CLAUDE-md-compressed-proposal-2026-05-07.md` first for review before writing.

### Track 1.5 — MEMORY.md Discipline Rule (NEW)

Compression worked but pattern persists. Propose adopting:

> **MEMORY.md write rule:** any new entry > 200 chars MUST become a topic file + 1-line pointer. Existing 25 over-200 lines should be migrated by file-guardian agent on next session-end.

This is a behavioral rule for me + any agent writing memories, not a content edit. Greenlight with "go DISCIPLINE" or amend.

---

## Stale Content Spotted (Auto-Implementable)

Reviewed MEMORY.md for stale entries — found nothing obviously dead. All sections still operationally active. The bloat is verbosity, not staleness.

---

## Next Audit

**Target:** 2026-05-14 (weekly cadence). Expected outcomes:
- If "go CLAUDE" greenlit: total drops to ~8,661 tokens (30% → -13% under target)
- If "go DISCIPLINE" greenlit: MEMORY.md trends to <2,000 tokens over 2-3 weeks as agents migrate inline rules to topic files
- If neither: state holds ~13,000 ± drift; next audit will flag any new MEMORY.md inline-rule additions

---

**Audited by:** doc-synthesizer (scheduled BOOP)
**Skill:** `.claude/skills/weekly-token-audit/SKILL.md`
**Prior audits:** `to-jared/weekly-token-audit-2026-04-29.md`, `…-04-28.md`, `…-04-09.md`
**Pre-drafted compression (Track 1, executed):** `to-jared/MEMORY-compressed-proposal-2026-04-28.md`

---

## ADDENDUM — 16:44 UTC re-fire delta (same day)

The weekly-token-audit BOOP fired again 70 min after the 15:34 run. No duplicate audit — drift check only.

| Metric | 15:34 UTC | 16:44 UTC | Δ |
|--------|-----------|-----------|---|
| CLAUDE.md | 8,844 | 8,844 | 0 |
| MEMORY.md (lines) | 136 | 139 | +3 |
| MEMORY.md (tokens) | 4,197 | 4,422 | **+225** |
| **Always-loaded total** | 13,041 | **13,266** | **+225 (1.7% in 70 min)** |

**What grew (last 70 min):** 2 long inline-rule entries appended to MEMORY.md:
1. `BOOP gap detection (process alive ≠ cron firing)` — ~394 chars inline (full root-cause + remediation embedded)
2. `Skill filed ≠ skill enforced` — ~400 chars inline (CE SME / Phil creds incident embedded)

**Pattern confirmed.** Both are exactly the anti-pattern flagged in this audit's body: rules embedded inline rather than `[Title](file.md) — hook` pointers. 70 min produced +225 tokens of new inline content; extrapolating, MEMORY.md alone is on track to grow ~5,000 tokens/day if unchecked.

**Recommendation upgrade — Track 1.5 ("go DISCIPLINE") now blocks Track 2.** No point greenlighting a one-time CLAUDE.md compression while MEMORY.md is the active leak. Order of ops:
1. **First:** "go DISCIPLINE" — write rule for any agent/me adding to MEMORY.md (>200 chars = topic file + 1-line pointer). Apply to the 2 entries added since 15:34 + the 25 pre-existing >200-char lines.
2. **Then:** "go CLAUDE" — Track 2 compression on stable-state MEMORY.md.

Without DISCIPLINE first, Track 2 gains get re-spent within ~2 weeks of MEMORY.md growth.

**Re-fire summary:** No new audit needed. State drifted +225 tokens, 100% of which validates this audit's diagnosis.
