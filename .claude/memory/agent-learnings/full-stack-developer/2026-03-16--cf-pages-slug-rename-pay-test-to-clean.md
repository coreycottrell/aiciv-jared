# CF Pages Slug Rename: pay-test-* to clean names

**Date**: 2026-03-16
**Type**: operational
**Topic**: Renaming CF Pages directories from pay-test-* to clean production slugs

## What Was Done

Renamed 4 CF Pages directories from dev/test naming to clean production names:
- `pay-test-2` → `live`
- `pay-test-awakened` → `awakened`
- `pay-test-partnered` → `partnered`
- `pay-test-unified` → `unified`

## Directories Created

In `exports/cf-pages-deploy/`:
- `live/` (copy of pay-test-2)
- `awakened/` (copy of pay-test-awakened)
- `partnered/` (copy of pay-test-partnered)
- `unified/` (copy of pay-test-unified)
- `insiders/awakened/` (copy of insiders/pay-test-awakened)

In `purebrain-site/public/`:
- `live/` (copy of pay-test-2)

## Approach

Used a Python script (`tools/rename_slugs.py`) with regex word-boundary matching:
- Pattern `pay-test-2(?![\w-])` - safely matches `pay-test-2/` and `pay-test-2"` but NOT `pay-test-25`, `pay-test-2x`, `pay-test-2-abc`, or `pay-test-sandbox-2`
- Literal patterns for the other 3 (pay-test-awakened/partnered/unified have no ambiguous partial-match risk)

## Files Changed

### exports/cf-pages-deploy/ (29 files, 38 replacements)
Key files updated:
- invitation/index.html (all 4 slug types → 4 new slugs)
- All blog posts referencing /pay-test-2/
- live/, awakened/, partnered/, unified/ (their own self-references)
- insiders/awakened/index.html
- Homepage clones, pure-brain-agentic-ai-partner, referral pages, etc.

### purebrain-site/public/ (7 files, 10 replacements)
- index.html, invitation/index.html, live/index.html
- pay-test-2/index.html, pay-test-5/index.html (old dirs kept, updated)
- pay-test-sandbox-3/index.html, pure-brain-agentic-ai-partner/index.html

## What Was Left Alone (Correct)

- `pay-test-sandbox`, `pay-test-sandbox-2`, `pay-test-sandbox-3`, `pay-test-sandbox-5`
- `pay-test-5`
- `pay-test` (original)
- The old directories themselves (not deleted, kept as-is)

## Verification

Post-run grep confirmed zero remaining references to old slugs in files OUTSIDE their own old directories.

## Key File Paths

- Script: `/home/jared/projects/AI-CIV/aether/tools/rename_slugs.py`
- CF deploy base: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/`
- PureBrain public: `/home/jared/projects/AI-CIV/aether/purebrain-site/public/`
