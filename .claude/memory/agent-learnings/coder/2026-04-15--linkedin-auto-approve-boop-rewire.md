# LinkedIn Auto-Approve BOOP Rewire

**Date**: 2026-04-15
**Agent**: coder (via Primary/Aether)
**Type**: operational
**Task**: Add `--auto-approve` flag to `linkedin_icp_commenter.py` + rewire pre-comment BOOPs

---

## Context

Jared requested that LinkedIn pre-comment BOOPs shift from running the commenter (which needs pre-populated profiles) to running DISCOVERY first via the new PureSurf backend (shipped same day), then AUTO-APPROVING discovered profiles into the pool, so that the POST-comment BOOPs can then comment on them.

## Changes Made

### 1. `tools/linkedin_icp_commenter.py` (4 changes)

1. **Added `--auto-approve` flag** (line ~924):
   ```python
   p.add_argument("--auto-approve", action="store_true", 
                  help="Auto-promote discovered candidates into profiles (skip human review)")
   ```

2. **Updated `run_discovery()` signature** (line ~875):
   - Added `auto_approve: bool = False` parameter

3. **Auto-approve logic** (lines ~910-981, 70 lines):
   - Triggered when: `auto_approve and not dry_run and total > 0`
   - Reads `linkedin_icp_candidates.json`
   - Reads `configs/linkedin_icps.json`
   - Respects `block_list` (skips blocked handles)
   - Deduplicates by handle (case-insensitive)
   - Promotes to `profiles[]` array with metadata:
     - `approved: true`
     - `added_via: "auto-approve"`
     - `added_at: "YYYY-MM-DD"`
     - Preserves `match_score` and `matched_keywords`
   - Writes back to `configs/linkedin_icps.json`
   - Logs: `"[auto-approve] Promoted N candidates → profiles, skipped M duplicates, P blocked"`

4. **Pass auto_approve to run_discovery()** (line ~1003):
   ```python
   sys.exit(run_discovery(args.persona, args.all, args.count, args.dry_run, 
                          args.sync_personas, args.auto_approve))
   ```

### 2. `.claude/scheduled-tasks-state.json` (4 BOOPs)

Updated all 4 pre-comment BOOPs (`linkedin-pre-comment-0830`, `1100`, `1300`, `1500`):

**Old command**:
```
python3 .../linkedin_icp_commenter.py --user jared --count 3
```

**New command**:
```
python3 .../linkedin_icp_commenter.py --discover --all --count 5 --auto-approve
```

**New description**:
> LINKEDIN PRE-COMMENT DISCOVERY phase — companion for linkedin-post-XXXX (slot X:XXam, T-60min). Run: python3 /home/jared/projects/AI-CIV/aether/tools/linkedin_icp_commenter.py --discover --all --count 5 --auto-approve. PureSurf finds 5 ICP profiles across ALL personas, auto-promotes to profile pool. Post-comment BOOP will actually comment on them. Respects block_list. Logs: logs/linkedin_icp_commenter.log.

### 3. Backup Created

`configs/linkedin_icps.json.bak-2026-04-15` - Backup before any auto-approve writes

## Workflow Changes

### Before
- Pre-comment BOOPs ran commenter against existing profiles in pool
- Discovery was manual, required human review of candidates file

### After
- **Pre-comment BOOPs** (T-60min): PureSurf discovers 5 profiles across all personas, auto-promotes to pool
- **Post-comment BOOPs** (T+30min): Commenter runs against freshly-populated pool (unchanged behavior)

## Verification

✓ Python syntax valid (`py_compile` passed)
✓ JSON syntax valid (BOOPs file parses correctly)
✓ Dry-run test passed (auto-approve skipped correctly when dry_run=True or candidates=0)
✓ All 4 BOOPs updated and verified

## Safety Features

1. Backup created before writes
2. Block list respected
3. Case-insensitive deduplication
4. Dry-run prevents writes even with `--auto-approve`
5. Metadata preserved (match_score, matched_keywords)

## Next Action

Jared must log into `surf.purebrain.ai` as `aether-linkedin` profile (one-time setup).
After that, BOOPs run fully autonomous.

## Pattern Learned

**Two-phase BOOP workflow** works well for discovery + action patterns:
- Phase 1 (pre-BOOP): Discover/prepare resources
- Phase 2 (post-BOOP): Act on prepared resources

This prevents "no profiles to comment on" failures and enables autonomous growth of the ICP pool.

**JSON BOOP updates**: When updating BOOP descriptions with unicode (em dash `\u2014`), use Python `json.loads()` + `json.dumps()` instead of sed/text replacement to preserve encoding.

## Files Modified

- `tools/linkedin_icp_commenter.py` - 4 changes
- `.claude/scheduled-tasks-state.json` - 4 BOOP descriptions
- `configs/linkedin_icps.json.bak-2026-04-15` - Backup

## Documentation

Full implementation guide copied to:
`~/exports/portal-files/linkedin-auto-approve-implementation.md`
