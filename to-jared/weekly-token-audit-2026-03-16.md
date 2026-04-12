# Weekly Token Audit — 2026-03-16

## Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| MEMORY.md (total) | 25,108 bytes / ~6,277 tokens | 4,260 bytes / ~1,065 tokens | **-83%** |
| MEMORY.md (visible) | 13,491 bytes / ~3,372 tokens | 4,260 bytes / ~1,065 tokens | **-68%** |
| CLAUDE.md | 33,562 bytes / ~8,390 tokens | unchanged | — |
| **Total always-loaded** | **~11,763 tokens** | **~9,455 tokens** | **-20%** |
| MEMORY.md lines | 379 (truncated at 200) | 72 (fully visible) | **-81%** |

**Target: <10,000 tokens — NOW MET** (was 18% over)

## Critical Fix: MEMORY.md Truncation

MEMORY.md had 379 lines but only 200 were loaded (system limit). This meant **179 lines / ~30 entries were completely invisible** — including:
- Telegram response rules
- Background agent update rules
- Portal UX rules (5-point spec)
- Auto seed forwarding
- Portal file delivery rules
- CIV recovery skill
- Governance flow
- Email SMTP rules
- Pricing updates
- Multiple operational rules

All of these were silently lost every session.

## What Changed

**Created 5 topic files** (detailed content moved out of index):
- `google-drive-routing.md` — all folder IDs and filing rules
- `portal-rules.md` — UX rules, file delivery, restart protocol
- `telegram-rules.md` — bridge, markers, bg agent updates
- `wordpress-rules.md` — templates, Elementor, credentials, security plugin
- `business-reference.md` — pricing, emails, timezone, governance, log server

**Compressed MEMORY.md** from verbose inline content to 1-2 line index entries with topic file references.

**Removed duplicates**:
- "Elementor Deployment" appeared twice
- Telegram rules spread across 4 entries → 1 section + topic file
- Portal rules spread across 5 entries → 1 section + topic file
- Google Drive across 5 entries → 1 section + topic file

## Next Steps (for future audits)

CLAUDE.md at ~8,390 tokens is still 2.4x over the 3,500 target. Compressing it would require restructuring the agent roster table (largest section, ~2,000 tokens) and wake-up protocol. This needs Jared's input as it changes constitutional documents.
