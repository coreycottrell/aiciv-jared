# Learning: Orphaned Agent Management

**Date**: 2026-02-21
**Type**: operational
**Topic**: Handling stale agent completions after context compaction

## Pattern

When context compacts during heavy parallel agent work, agents launched in previous context windows continue running and report back as task-notifications in the new window. These are **orphans** - their work was already captured.

## What Happened

Session 45 saw 7 orphaned agents complete after context compaction:
- 3D sprint Days 5, 6, 7 (already in scratch pad items 170-172)
- A-C-Gee invite (already item 140)
- Intel scan (already item 173)
- P.S. additions (already item 174)
- Avatar design brief (already item 175)

## Rule

When a task-notification arrives, check the scratch pad FIRST. If the work is already recorded, acknowledge and move on. Don't re-process, don't re-send deliverables, don't update scratch pad again.

## Prevention

Before launching background agents near context limits, consider:
1. Will these survive a compaction?
2. Is the work critical enough to risk orphaning?
3. Should I wait for completion before allowing compaction?
