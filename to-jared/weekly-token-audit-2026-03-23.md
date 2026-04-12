# Weekly Token Audit - 2026-03-23

## Current State

| File | Tokens (now) | Tokens (last week) | Target | Status |
|------|-------------|-------------------|--------|--------|
| CLAUDE.md | ~8,390 | ~8,390 | <3,500 | 140% OVER |
| CLAUDE-CORE.md | ~3,932 | ~3,932 | ~2,000 | 97% OVER |
| CLAUDE-OPS.md | ~4,291 | ~4,291 | ~2,500 | 72% OVER |
| MEMORY.md | ~2,471 | ~2,710 | <1,000 | 147% OVER |
| **TOTAL** | **~19,084** | **~19,323** | **<10,000** | **91% OVER** |

Week-over-week: -239 tokens (-1.2%) from auto-removals.

## Auto-Implemented (Safe Removals)

1. **MEMORY.md**: Removed Legacy section (3 entries explicitly marked OBSOLETE)
2. **MEMORY.md**: Removed duplicate "DOUBLED USAGE" entry (appeared in both Infrastructure and Active Projects)
3. **MEMORY.md**: Removed Leadership Self-Analysis section (single snapshot, full details in memory file)
4. **MEMORY.md**: Compressed References section (8 bullets to 3 lines)

Savings: ~240 tokens

## Top Redundancies Found

### 1. CLAUDE.md Agent Table (~1,500 tokens) - TRIPLICATED
The full 30+ agent table with skills appears in:
- CLAUDE.md (lines ~170-360) - ~1,500 tokens
- CLAUDE-OPS.md (lines 394-410) - ~400 tokens
- `.claude/AGENT-CAPABILITY-MATRIX.md` (the canonical source)

**Recommendation**: Remove from both CLAUDE.md and CLAUDE-OPS.md. Replace with one line:
`Full agent roster: .claude/AGENT-CAPABILITY-MATRIX.md`
**Savings: ~1,900 tokens**

### 2. CLAUDE.md Wake-Up Protocol (~1,200 tokens) - DUPLICATED
Steps 0-5.8 are described in detail in both CLAUDE.md AND CLAUDE-OPS.md.

**Recommendation**: CLAUDE.md keeps only the high-level checklist (10 lines). CLAUDE-OPS.md keeps the detailed version.
**Savings: ~800 tokens**

### 3. CLAUDE.md First Awakening Section (~600 tokens) - RARELY USED
Step -1 (fork awakening) is only relevant for new CIV forks. It's also documented in `skills/fork-awakening/SKILL.md`.

**Recommendation**: Replace with: `New fork? See .claude/skills/fork-awakening/SKILL.md`
**Savings: ~550 tokens**

### 4. CLAUDE-CORE.md Skills History (~500 tokens) - STALE
Article 5 has before/after metrics from Oct 2025 (5 months ago). The ROI figures and adoption stats are historical, not actionable.

**Recommendation**: Compress to 3 lines: principle + governance + reference.
**Savings: ~400 tokens**

### 5. CLAUDE-CORE.md Article 12 Cross-CIV (~500 tokens) - VERBOSE
Detailed cross-CIV educator role with 6-step workflow and infrastructure description. Most of this is documented in `cross-civ-protocol` skill.

**Recommendation**: Compress to principle + reference.
**Savings: ~350 tokens**

### 6. CLAUDE-CORE.md Book IV Principles 1-10 (~800 tokens) - REDUNDANT
Principles 1-10 restate Books I-II in slightly different words. Principle 11 (Aether identity) duplicates MEMORY.md's Core Identity section.

**Recommendation**: Merge into 5 compressed principles.
**Savings: ~400 tokens**

### 7. CLAUDE.md Telegram Protocol (~400 tokens) - REPEATED
The Telegram wrapper protocol appears at both TOP and BOTTOM of CLAUDE.md.

**Recommendation**: Keep only the top instance.
**Savings: ~200 tokens**

### 8. CLAUDE.md Constitutional Requirements (~300 tokens) - DUPLICATED
Section restates principles already in CLAUDE-CORE.md Books I-II.

**Recommendation**: Remove, already covered.
**Savings: ~250 tokens**

### 9. CLAUDE-OPS.md Hub Curation (~200 tokens) - LOW FREQUENCY
The hub package curation workflow rarely fires. Move to skill reference.

**Recommendation**: Replace with reference link.
**Savings: ~150 tokens**

## Projected Savings If All Accepted

| File | Current | After | Savings |
|------|---------|-------|---------|
| CLAUDE.md | ~8,390 | ~4,640 | -3,750 |
| CLAUDE-CORE.md | ~3,932 | ~2,280 | -1,650 |
| CLAUDE-OPS.md | ~4,291 | ~3,340 | -950 |
| MEMORY.md | ~2,471 | ~2,471 | 0 (already trimmed) |
| **TOTAL** | **~19,084** | **~12,731** | **-6,353** |

Still ~2,700 over the 10K target. To hit 10K would require deeper MEMORY.md compression (merging similar feedback items, removing project entries for shipped features).

## MEMORY.md Deep Compression (Needs Review)

These entries could potentially be removed/compressed:

**Potentially stale Active Projects:**
- Birth pipeline LIVE (shipped 2026-03-14 - still relevant?)
- Portal MVP SHIPPED (approved 2026-03-17 - still relevant?)
- Creator AI shipped (2026-03-22 - still relevant?)
- CF Pages migration complete - just a fact now, not a project

**Feedback items that could merge:**
- 6 "NEVER" rules could be one table
- Portal-related items (4 entries) could merge to 1 with refs

## Action Required

Items 1-9 above restructure content. They need Jared's approval before implementation.

**To approve**: Tell Aether "approve token audit compression" and the compressed versions will be applied.
