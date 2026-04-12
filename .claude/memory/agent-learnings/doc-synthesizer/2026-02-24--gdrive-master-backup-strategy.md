# Google Drive Master Backup Strategy

**Date**: 2026-02-24 (Session 38)
**Context**: Needed persistent backup of all Aether work products outside the VPS

## Architecture
- Root: "Aether Inbox" folder (ID: 1yU6MVgbaNNa8FEzF213sSA2rDR9ZqOFd)
- MASTER BACKUP subfolder with 10 categorized sub-folders
- 117 files uploaded covering all work products

## 10 Sub-Folders
1. Constitutional docs (CLAUDE.md, CLAUDE-CORE.md, CLAUDE-OPS.md)
2. Agent manifests (.claude/agents/)
3. Skills registry + key skills
4. Memory files (operational, preferences, techniques)
5. Exports (blog posts, calculators, tools)
6. Email templates
7. Client deliverables
8. Integration docs (roadmap, trading arena)
9. Tool scripts (key Python tools)
10. Session handoffs

## Key Pattern
- Use `tools/gdrive_manager.py` with domain-wide delegation (purebrain@puremarketing.ai)
- Dual-route ALL deliverables: Telegram to Jared + Google Drive for persistence
- Drive = training material for agents + disaster recovery
- 560KB tar.gz archive also created locally as secondary backup

## Rule (from MEMORY.md)
- Every file delivered to Jared MUST also be filed in Google Drive
- Route to correct numbered folder (000-008 + Daily Recap + Surprise and Delight)
