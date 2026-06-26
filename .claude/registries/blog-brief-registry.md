# Blog Brief Registry

**Purpose**: Tracks content briefs from creation → draft → published. Closes the unowned
blog-draft step (bsky-drought failure shape: briefs written, never drafted, drought discovered
weeks later). Any BOOP/agent producing a content brief MUST add a row here. The drafting
check reads this registry — a brief sitting in `pending` 3+ days is a stall flag.

**Created**: 2026-06-13 by agent-architect capability-gap BOOP (action item 5 of 06-12 digest).

**Status values**: `pending` (brief exists, no draft) · `drafted` (draft exists, awaiting approval)
· `published` (live, distribution fired) · `dropped` (Jared declined — note why)
· `killed-stale` (Aether ship-or-kill = KILL after repeated zero-action nightlies; draft files retained, reversible).

| Date filed | Brief path | Status | Owner | Notes |
|------------|-----------|--------|-------|-------|
| 2026-06-11 | exports/content-briefs/2026-06-11-receipts-beat-memory-brief.md | pending | the-conductor | Seeded at registry creation; verify not already drafted before drafting |
| 2026-06-12 | ~/exports/voice-beat-2026-06-12/BRIEF.md | killed-stale | the-conductor | KILLED 2026-06-26 (ST#): Aether own-brand ship-or-kill decision after 4+ nightlies w/ zero action; draft files retained in ~/exports (reversible label flip, NOT deleted); blog-draft.md + social-extracts.md still exist in same dir |
| 2026-06-15 | exports/content-briefs/2026-06-15-smb-beats-enterprise-ai-brief.md | pending | intel-scan-boop | Best story from 06-15 intel brief; SMB-beats-enterprise AI adoption; verify stats w/ claim-verifier before draft |
| 2026-06-20 | exports/content-briefs/2026-06-20-smb-ai-agent-roi-brief.md | pending | intel-scan-boop | Best story from 06-20 intel brief; SMB AI-agent ROI (30% cost cut / 20+ hrs); verify stats w/ claim-verifier before draft |
