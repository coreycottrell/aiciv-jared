# Weekly Token Audit — 2026-03-30

## Current State (OVER TARGET)

| File | Tokens | Target | Status |
|------|--------|--------|--------|
| CLAUDE.md | ~8,698 | <3,500 | 2.5x OVER |
| CLAUDE-CORE.md | ~3,932 | — | baseline |
| CLAUDE-OPS.md | ~4,291 | — | baseline |
| MEMORY.md | ~3,950 | <1,000 | 4x OVER |
| **Always-loaded total** | **~20,871** | **<10,000** | **2.1x OVER** |
| AGENT-CAPABILITY-MATRIX.md | ~5,887 | — | (wake-up only) |
| ACTIVATION-TRIGGERS.md | ~10,247 | — | (wake-up only) |

**Previous audit** (2026-02-27): ~9,600 tokens after compression. Current: ~20,871.
**Growth**: +117% in 31 days — far exceeding 5%/week target.

## Top Compression Opportunities

### 1. CLAUDE.md: Telegram Section (~2,400 tokens) — CONTRADICTS MEMORY
Lines 22-93: 72 lines of Telegram wrapper protocol, bridge setup, capability table.
**But MEMORY.md line 24**: "Portal is PRIMARY — NOT Telegram. Jared does not use Telegram anymore."
**Recommendation**: Remove bulk of Telegram section. Keep 2-line reference to bridge for notifications only.
**Savings**: ~2,200 tokens

### 2. CLAUDE.md: Full Agent Table (~3,000 tokens)
Lines ~300-500: 30+ agent roster with skills duplicates AGENT-CAPABILITY-MATRIX.md.
**Recommendation**: Replace with `See .claude/AGENT-CAPABILITY-MATRIX.md` pointer.
**Savings**: ~2,800 tokens

### 3. CLAUDE.md: Verbose Wake-Up Protocol (~1,500 tokens)
Detailed bash code blocks for each step. CLAUDE-OPS.md has the same info.
**Recommendation**: Compress to checklist with "See CLAUDE-OPS.md for commands."
**Savings**: ~1,000 tokens

### 4. MEMORY.md: Self-Analysis Section (10 entries, ~900 tokens)
Historical nightly scores. Only latest is actionable.
**Recommendation**: Keep only latest + rolling 3-day. Auto-prune older. → AUTO-IMPLEMENT
**Savings**: ~600 tokens

### 5. MEMORY.md: Redundant WordPress Warnings (~200 tokens)
"NO WORDPRESS EVER" appears in Delegation, Site, and Feedback sections (3x).
**Recommendation**: Single entry in Site section. → AUTO-IMPLEMENT
**Savings**: ~150 tokens

### 6. MEMORY.md: Feedback Section Bloat (~1,200 tokens)
30 feedback entries, many just pointer-to-file with no hook text.
**Recommendation**: Group related entries, remove file-only pointers where hook is sufficient.
**Savings**: ~400 tokens

## Summary of Potential Savings

| Opportunity | Tokens Saved | Risk | Action |
|-------------|-------------|------|--------|
| Remove Telegram bloat from CLAUDE.md | ~2,200 | Medium (needs Jared approval) | PROPOSE |
| Remove agent table from CLAUDE.md | ~2,800 | Low (exists in matrix) | PROPOSE |
| Compress wake-up to pointers | ~1,000 | Low | PROPOSE |
| Prune old self-analysis | ~600 | None | AUTO-IMPLEMENT |
| Deduplicate WordPress warnings | ~150 | None | AUTO-IMPLEMENT |
| Compress feedback section | ~400 | Low | AUTO-IMPLEMENT |

**Total potential**: ~7,150 tokens → would bring total from ~20,871 to ~13,721
**Auto-implementable now**: ~1,150 tokens (MEMORY.md cleanup)
**Needs Jared approval**: ~6,000 tokens (CLAUDE.md restructure)

## Auto-Implemented Changes (This Audit)

1. ✅ Pruned MEMORY.md Self-Analysis to latest 3 entries (removed 7 older)
2. ✅ Deduplicated WordPress references in MEMORY.md
