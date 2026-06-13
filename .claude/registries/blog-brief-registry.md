# Blog Brief Registry

**Purpose**: Tracks content briefs from creation → draft → published. Closes the unowned
blog-draft step (bsky-drought failure shape: briefs written, never drafted, drought discovered
weeks later). Any BOOP/agent producing a content brief MUST add a row here. The drafting
check reads this registry — a brief sitting in `pending` 3+ days is a stall flag.

**Created**: 2026-06-13 by agent-architect capability-gap BOOP (action item 5 of 06-12 digest).

**Status values**: `pending` (brief exists, no draft) · `drafted` (draft exists, awaiting approval)
· `published` (live, distribution fired) · `dropped` (Jared declined — note why).

| Date filed | Brief path | Status | Owner | Notes |
|------------|-----------|--------|-------|-------|
| 2026-06-11 | exports/content-briefs/2026-06-11-receipts-beat-memory-brief.md | pending | the-conductor | Seeded at registry creation; verify not already drafted before drafting |
| 2026-06-12 | ~/exports/voice-beat-2026-06-12/BRIEF.md | drafted | the-conductor | blog-draft.md + social-extracts.md exist in same dir; holds for overnight bundle per 06-13 ground |
