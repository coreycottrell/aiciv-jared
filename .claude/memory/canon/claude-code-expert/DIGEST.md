---
lead: claude-code-expert
rebuilt_ts: 2026-06-09T01:29:35Z
ledger_lines_at_rebuild: 1
source_log: .claude/memory/canon/claude-code-expert/log.jsonl
mechanism: extractive-mechanical
---

# Canon Memory Digest: claude-code-expert

**Last 1 entries** (from 1 total)

## Findings

- `2026-06-08T23:51:57Z` **finding** — Portal-injection bug root cause: cc_bridge.py send-keys used a bare tmux session target so messages routed to the ACTIVE window; a team window stole Jared's portal messages. Fixed by pinning to :0.0 (main window). Native subagents have no pane, so this bug class is structurally impossible.
  - Receipt: `/home/jared/projects/AI-CIV/aether/tools/cc_bridge.py`
