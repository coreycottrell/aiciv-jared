# Memory: Google Drive Layer Architecture for AI Civilization

**Date**: 2026-04-06
**Type**: teaching
**Agent**: architect
**Task**: Design Google Drive folder structure for Pure Technology AI civilization

---

## Pattern Discovered

When an operation has two conflicting consumption patterns — AI agents filing by function, humans navigating by department — the correct architecture is a two-layer system:

- **Layer 1 (Content Vault)**: Function-based folders where files actually live. Gives AI deterministic filing rules. One file per location, no judgment calls about "which department owns this."
- **Layer 2 (Department Views)**: Google Drive shortcuts pointing into the Vault. Zero copies — just pointers. Humans get their departmental view; AI maintains ground truth.

This resolves the classic "cross-cutting concerns" problem (a blog post touches Marketing + Design + SEO — which folder owns it?). Answer: the Content Vault owns it (01-Content/Blog/), and every department that cares about it has a shortcut.

## Key Decisions

1. **Monthly subfolders (YYYY-MM/) are mandatory** for any folder receiving daily AI output. At 50+ files/day, a flat folder becomes unusable in under a week.

2. **Naming convention**: YYYY-MM-DD--[descriptor].[ext] ensures chronological sort in any folder view without opening files.

3. **Never file directly in Department View folders** — shortcuts only. Files saved there are invisible to the Vault and get lost.

4. **Cross-platform content** (blog + LinkedIn + Bluesky simultaneously) gets its own folder (Cross-Platform/) rather than splitting across channel folders.

5. **Team-scoped views** for specific human team members (Nathan/Lyra, Phil/Clarity, Nate/Anchor) are curated shortcut collections, not separate folder trees. This avoids permission management complexity.

## Scaling Threshold

At >100 files/day in a given folder category, add daily subfolders inside monthly ones. The upgrade path is additive — no restructuring needed.

## What Layer Architecture Does NOT Solve

- Approval workflow (who approves before publishing) — that's a portal/tracking sheet problem
- Automatic agent filing — filing rules must be in agent prompts/SOPs
- Cross-type client search — Drive keyword search handles that; folder structure doesn't optimize for it

## Files Produced

- `/home/jared/exports/portal-files/drive-architecture-proposal.md` — full proposal with Vault tree, filing rules table, migration plan, and trade-off rationale

## Context

- Pure Technology: 23 department agents, 6 locked folders (preserve their IDs), 50+ files/day projected
- Existing Drive uses numbered prefix convention (e.g., "004. Social Media Strategist...") — preserve as subfolders in 04-Training/Agent-Training/ during migration
- Team members: Nathan/Lyra, Phil/Clarity, Nate/Anchor need segmented views
