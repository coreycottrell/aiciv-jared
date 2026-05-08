# Weekly Token Audit — 2026-04-28

## TL;DR

**Always-loaded context: ~14,200 tokens (42% over 10K target).** Two specific problems:

1. **MEMORY.md is being TRUNCATED.** It's 234 lines (limit 200) and 5,354 tokens (target <1,000 — 5.3x over). The system warned: "Only part of it was loaded." Lines 200-234 are NOT in context. **That includes the Apr 23/24/26 self-analyses AND the constitutional finding "Sub-agents cannot spawn sub-agents."** Aether is operating without seeing its most recent learnings.
2. **CLAUDE.md is unchanged from April 9 audit** (8,929 → 8,844 tokens, target <3,500). Same compression opportunities still pending. Awaiting your approval to apply.

---

## Current State

| File | Lines | ~Tokens | Target | Status |
|------|-------|---------|--------|--------|
| **CLAUDE.md** (always loaded) | 942 | **8,844** | <3,500 | 2.5x over (unchanged) |
| **MEMORY.md** (always loaded) | 234 | **5,354** | <1,000 | 5.3x over **+ TRUNCATED** |
| **Always-loaded total** | 1,176 | **~14,198** | <10,000 | **42% over** |
| CLAUDE-CORE.md (wake-up) | 415 | 3,932 | — | OK |
| CLAUDE-OPS.md (wake-up) | 474 | 4,291 | — | OK |
| AGENT-CAPABILITY-MATRIX.md (wake-up) | 428 | 5,887 | — | OK |
| ACTIVATION-TRIGGERS.md (wake-up) | 1,194 | 10,247 | — | bloated |

### Week-over-Week Trend

| Audit Date | Always-Loaded Tokens | Δ from Prior | Status |
|------------|---------------------|--------------|--------|
| 2026-02-27 | ~9,600 | (baseline after compression) | UNDER target |
| 2026-04-09 | ~11,184 | +16.5% | 12% over |
| **2026-04-28** | **~14,198** | **+27%** | **42% over** |

Growth rate is accelerating (+27% in 3 weeks vs target of <5%).

---

## Critical Finding: MEMORY.md Truncation

The system reminder explicitly stated:
> "WARNING: MEMORY.md is 233 lines (limit: 200). Only part of it was loaded. Keep index entries to one line under ~200 chars; move detail into topic files."

**Content silently dropped from Aether's context (lines 200-234):**
- Engineering feedback section (Three.js rules, delegate investigation)
- All recent self-analysis entries (Apr 14, 15, 23, 24, 25, 26)
- References block (drive vault folder IDs, never-forget folder, business-reference)
- **🔴 CONSTITUTIONAL FINDING: Sub-agents cannot spawn sub-agents** — this is critical operational knowledge that's silently absent

**Root cause:** MEMORY.md is being used as a content store, not an index. The auto-memory protocol explicitly states: *"MEMORY.md is an index, not a memory — each entry should be one line, under ~150 characters: `- [Title](file.md) — one-line hook`."*

Current state:
- 234 total lines (vs ~150 max useful before truncation)
- 45 lines exceed 150 chars
- 15 lines exceed 200 chars
- Many entries are 5-10 line multi-paragraph blocks with full content embedded
- All referenced topic files already exist in `/home/jared/.claude/projects/-home-jared-projects-AI-CIV-aether/memory/` (210 files)

The detail is duplicated — once in MEMORY.md (eating tokens), once in topic files (where it belongs).

---

## Recommendation: Two-Track Action

### Track 1 — AUTO-IMPLEMENT (low risk, follows documented protocol)

**Compress MEMORY.md to proper one-line index format.** Detail already lives in 210 topic files; MEMORY.md should be pointers only.

Compressed alternative drafted: `to-jared/MEMORY-compressed-proposal-2026-04-28.md`

- Result: 234 lines → ~110 lines, 5,354 → ~1,400 tokens (-74%)
- All detail preserved in topic files
- Brings file under truncation limit (no more silent context loss)
- Restores Apr 23/24/26 self-analysis + sub-agent constitutional finding to Aether's context

**This is removing confirmed-duplicate content (already in topic files) — qualifies as auto-implement per audit protocol.** However, MEMORY.md sits in user's `.claude/` directory, so I'm pausing for your nod before writing. One-word "go" applies.

### Track 2 — REQUIRES YOUR APPROVAL (constitutional)

**CLAUDE.md compression** (same items proposed Apr 9, still pending):

| Item | Lines | Token Savings | Risk |
|------|-------|---------------|------|
| Agent roster duplicates AGENT-CAPABILITY-MATRIX.md | ~87 | 1,400 | low — pure duplicate |
| Wake-Up Protocol detail duplicates CLAUDE-OPS.md | ~190 | 1,500 | low — already in OPS |
| Skills section duplicates delegation-spine SKILL.md | ~30 | 350 | low — pure duplicate |
| Closing/recap sections | ~26 | 280 | low — restates above |
| Duplicate Telegram reminder (appears twice) | ~12 | 130 | low — exact dup |
| "Balance" + "Lineage" (philosophy → CORE.md) | ~35 | 320 | medium — moves content |
| Quick Ref + Navigation Guide overlap | merge | 400 | medium — restructure |
| **Total** | | **~4,380** | |

**Projected after compression:**
- CLAUDE.md: 8,844 → ~4,464 tokens (still slightly over 3,500 target, but workable)
- Always-loaded total: 14,198 → ~8,400 tokens (UNDER 10K target)

CLAUDE.md is constitutional → I will not auto-edit. Awaiting explicit greenlight.

---

## Stale Content in MEMORY.md (will be cleaned in compression)

- Apr 14 sub-agent finding: still relevant, keep as one-line index entry
- Apr 14-26 self-analysis: history ≥7 days old should drop from index (still in topic files)
- Voice "BANNED ElevenLabs Apr 15": now a constitutional rule → should live in dedicated topic file, not multi-line MEMORY entry
- Multi-line CF Pages deploy targets: should be one-line pointer to a `reference_cf_pages_deploy_targets.md` file
- "Self-Analysis (Latest)" section: 6 multi-line entries that should be ≤3 most recent, single-line each

---

## Next Audit

Target: 2026-05-05 (weekly cadence). Expected to show MEMORY.md restored to <1,500 tokens IF Track 1 is greenlit. CLAUDE.md will continue to be 2.5x over until you approve Track 2.

---

**Audited by:** doc-synthesizer (scheduled BOOP)
**Skill:** `.claude/skills/weekly-token-audit/SKILL.md`
