# Memory: Master Handoff Synthesis Patterns

**Date**: 2026-02-24
**Agent**: doc-synthesizer
**Type**: teaching
**Topic**: Creating comprehensive master handoff documents from scattered sources

---

## Context

Created a 1,392-line, 60KB master handoff document for Aether session continuity. This was a "CRITICAL" synthesis task requested at session end to give the next iteration with more compute power a complete reference.

---

## Source Files Used (and Their Priority)

### Highest signal sources (read these first):
1. **`.claude/scratch-pad.md`** - Primary session log with numbered tasks, BOOP-by-BOOP history, DO NOT RE-DO lists. This is the richest source. Read in chunks (200 lines per pass) due to size.
2. **`MEMORY.md`** - Auto-memory with locked-in rules. This is the source of truth for NON-NEGOTIABLE behaviors.
3. **`.claude/setup-status.json`** - Identity config, credential status, setup completion date.
4. **`to-jared/HANDOFF-*.md`** - Recent individual session handoffs provide clean summaries.

### Important secondary sources:
5. **`.claude/CONTACTS.md`** - All email addresses and contact info
6. **`.claude/memory/pure-technology-knowledge-base.md`** - Business context
7. **`docs/gdrive/purebrain-drive-synthesis.md`** and **`docs/gdrive/support-drive-synthesis.md`** - Drive knowledge
8. **`outbox/witness-phase1-reply.md`** - Active integration plans
9. **`/tmp/witness-aether-comms/from-witness.txt`** - Cross-CIV latest comms
10. **`.env`** (structure only, never values) - Credential location reference

---

## Document Structure That Works for Master Handoffs

The 12-section structure used:

1. **Identity and Constitutional Framework** - Who they are, the delegation principle, agent roster, human relationships
2. **Business Context** - Company history, products, philosophies, key KB files
3. **Infrastructure Status** - Every tool with verify commands, paths, configs
4. **Active Integrations** - In-progress work with full API/flow details
5. **Website and Content Status** - Page map with IDs, URLs, status
6. **Scheduled Tasks** - What runs autonomously (nightly, weekly, BOOP cycles)
7. **Memory Files Index** - Categorized list of where agent learnings live
8. **Credentials** (location only, never values) - Where to find auth
9. **Locked-In Rules** - Every NON-NEGOTIABLE rule with source attribution
10. **Immediate Priorities** - What to do next session, ordered by urgency
11. **All Files Delivered** - Complete deliverable log with locations
12. **Drive Structure** - Reference for Google Drive navigation

**Plus**: Session history summary for context on recent accomplishments.

---

## Key Discovery: Scratch-pad is the Single Richest Source

The scratch-pad.md file for a heavy session is 37,000+ tokens. It cannot be read at once. Strategy:
- Read first 200 lines for current session
- Read next 200-300 lines for recent history
- Pattern: BOOP number + UTC time + numbered task + status emoji
- DO NOT RE-DO sections are critical for preventing duplicate work
- KEY LEARNINGS sections capture technical discoveries

---

## Efficiency Note

This master handoff was created in a single pass by:
1. Reading all source files in parallel (6-8 simultaneous reads where possible)
2. Holding context from each source and synthesizing into unified sections
3. Using the scratch-pad to extract precise task numbers and completion status
4. Cross-referencing MEMORY.md against scratch-pad to confirm locked-in rules

**Total synthesis time**: ~10 minutes with parallel reads.

---

## When to Create a Master Handoff vs Regular Handoff

**Regular handoff** (`HANDOFF-YYYY-MM-DD-topic.md`):
- End of individual session
- 1-4 pages
- Focus on what changed THIS session + immediate next steps

**Master handoff** (`MASTER-HANDOFF-YYYY-MM-DD.md`):
- Session ending with compute power limitation
- Handing off to new iteration
- 1,000+ lines
- Covers everything: identity, infrastructure, all active work, all rules
- Acts as a complete "brain dump" for the next agent

---

## Files Referenced

- `/home/jared/projects/AI-CIV/aether/to-jared/MASTER-HANDOFF-2026-02-24.md` (output)
- `/home/jared/projects/AI-CIV/aether/.claude/scratch-pad.md` (primary source)
- `/home/jared/projects/AI-CIV/aether/MEMORY.md` (rules source)
- All other files listed in the Source Files section above
