# Weekly Token Audit - 2026-04-09

## Current State

| File | Lines | Bytes | ~Tokens | Target | Status |
|------|-------|-------|---------|--------|--------|
| CLAUDE.md (always loaded) | 958 | 35,719 | 8,929 | <3,500 | **2.5x over** |
| Project MEMORY.md (always loaded) | 96 | 9,020 | 2,255 | <1,000 | **2.3x over** |
| **Always-loaded total** | **1,054** | **44,739** | **~11,184** | **<10,000** | **12% over** |

### Reference files (loaded on wake-up, not always)

| File | Lines | Bytes | ~Tokens |
|------|-------|-------|---------|
| CLAUDE-CORE.md | 415 | 15,729 | 3,932 |
| CLAUDE-OPS.md | 474 | 17,165 | 4,291 |
| AGENT-CAPABILITY-MATRIX.md | 428 | 23,551 | 5,887 |
| ACTIVATION-TRIGGERS.md | 1,194 | 40,990 | 10,247 |

### Previous audit: 2026-02-27 (~9,600 tokens after compression)
### This audit: ~11,184 tokens (+16.5% since Feb 27)

---

## Top Compression Opportunities in CLAUDE.md

### 1. Agent Roster (lines 663-749, ~87 lines, ~1,500 tokens)
**Type**: DUPLICATE - identical information in AGENT-CAPABILITY-MATRIX.md
**Action**: Replace with 2-line reference
**Savings**: ~1,400 tokens

### 2. Wake-Up Protocol Detail (lines 250-441, ~190 lines, ~2,000 tokens)
**Type**: DUPLICATE - same protocol exists in CLAUDE-OPS.md
**Action**: Replace with 10-line checklist + "See CLAUDE-OPS.md for commands"
**Savings**: ~1,500 tokens

### 3. Claude Code Native Skills section (lines 763-793, ~30 lines, ~400 tokens)
**Type**: DUPLICATE - skill system is documented in delegation-spine SKILL.md
**Action**: Replace with 2-line reference
**Savings**: ~350 tokens

### 4. Closing/Recap sections (lines 862-888, ~26 lines, ~300 tokens)
**Type**: REDUNDANT - repeats identity/protocol info already stated earlier
**Action**: Remove entirely (the protocol IS the document)
**Savings**: ~280 tokens

### 5. Duplicate Telegram Reminder (lines 946-958, ~12 lines, ~150 tokens)
**Type**: DUPLICATE - Telegram wrapper protocol already appears at lines 18-48
**Action**: Remove duplicate
**Savings**: ~130 tokens

### 6. "Balance" and "Lineage" sections (lines 824-858, ~35 lines, ~350 tokens)
**Type**: PHILOSOPHICAL - nice but not operationally needed in always-loaded context
**Action**: Move to CLAUDE-CORE.md where philosophical content belongs
**Savings**: ~320 tokens

### 7. Quick Reference overlap with Navigation Guide (lines 585-659)
**Type**: PARTIAL DUPLICATE - Navigation Guide (lines 444-472) covers similar ground
**Action**: Merge into single reference table
**Savings**: ~400 tokens

---

## Total Potential Savings

| Item | Token Savings |
|------|---------------|
| Agent roster → reference | 1,400 |
| Wake-up detail → checklist | 1,500 |
| Skills section → reference | 350 |
| Closing/recap → remove | 280 |
| Duplicate TG reminder → remove | 130 |
| Balance/Lineage → CORE | 320 |
| Quick Ref merge → single table | 400 |
| **Total** | **~4,380** |

**Projected CLAUDE.md after compression: ~4,549 tokens** (target: 3,500)
**Projected always-loaded total: ~6,804 tokens** (target: 10,000) **UNDER TARGET**

---

## MEMORY.md Analysis

Currently 96 lines, ~2,255 tokens (target: <1,000).

### Stale/movable entries:
- WordPress auth section (passwords in plaintext - security concern, also operational detail not strategic memory)
- CSS Deployment section (operational detail)
- Pay-Test Page section (implementation detail, derivable from code)
- Log Server Endpoints section (infrastructure detail, derivable from code)

These 4 sections (~30 lines, ~600 tokens) are implementation details that belong in operational docs, not always-loaded memory. Removing them would bring MEMORY.md to ~1,655 tokens - still over 1,000 but closer.

---

## Recommendations

### Safe to auto-implement (stale/duplicate removal):
1. Remove duplicate Telegram reminder at end of CLAUDE.md (lines 944-958)

### Needs Jared approval (structural changes):
1. Replace agent roster with reference link
2. Compress wake-up protocol to checklist
3. Remove closing recap section
4. Move balance/lineage to CLAUDE-CORE.md
5. Merge quick reference into navigation guide
6. Remove implementation details from MEMORY.md

---

## Action Taken This Audit

- [x] Measured all files
- [x] Identified redundancies
- [x] Produced this report
- [ ] Removed duplicate Telegram reminder (safe auto-change)
- [ ] Structural changes (pending Jared approval)
