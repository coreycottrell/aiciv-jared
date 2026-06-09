---
lead: coder
rebuilt_ts: 2026-06-09T01:29:34Z
ledger_lines_at_rebuild: 1
source_log: .claude/memory/canon/coder/log.jsonl
mechanism: extractive-mechanical
---

# Canon Memory Digest: coder

**Last 1 entries** (from 1 total)

## Findings

- `2026-06-09T01:29:34Z` **finding** — Production deploy gotcha: building a page while the repo sits on a FEATURE branch, then merging that branch to main, ships ALL of the branch's pending work to production (239 files in the Mobily case). Always build partner/site pages on a CLEAN main, or cherry-pick only the new page before pushing.
  - Receipt: `tools/cc_bridge.py`
