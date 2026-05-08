# Sunday Batch — Week of May 4-10, 2026

**Owner**: dept-marketing-advertising (CMO)
**Date**: 2026-05-03 (Sunday)
**Type**: operational + teaching
**Mission**: Weekly content prep BOOP — full week pipeline pushed to social.purebrain.ai for Monday morning approval

---

## Deliverables Produced (35 pieces)

| Type | Count | Voice | Length | Status |
|------|-------|-------|--------|--------|
| Blog posts (Mon-Sun) | 7 | Aether | 1,058-1,196 words each | draft on social.html |
| LinkedIn newsletters (paired with each blog) | 7 | Jared | ~600 chars each | draft on social.html |
| LinkedIn promo posts (one/day, drives blog traffic) | 7 | Jared | <1300 chars each | draft on social.html |
| LinkedIn standalones (2/day independent) | 13 + 1 reserve | Jared | <1300 chars each | draft on social.html |
| **Total** | **35** | | | All `status=draft`, scheduled May 4-10 |

## Schedule Grid Applied
- 12:30 UTC (8:30 AM ET) — blog + paired newsletter
- 15:00 UTC (11:00 AM ET) — standalone slot 1
- 17:00 UTC (1:00 PM ET) — blog promo post
- 19:00 UTC (3:00 PM ET) — standalone slot 2

## Filing — All 3 Constitutional Destinations Hit

1. **PRIMARY: PureSurf social.purebrain.ai** — 35 drafts pushed via `/api/content` single-create loop (bulk endpoint not yet deployed). All `status=draft`, all `social_account_id=a325193d-...` (Jared's LinkedIn account). Created IDs saved to `/home/jared/exports/portal-files/sunday-batch-may4-10/created-ids.json`. Review URL: https://surf.purebrain.ai/social.html
2. **LinkedIn tracking spreadsheet** — 21 LinkedIn posts (promos + standalones) appended to `1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4` tab "Linkedin Post Content Calendar" as POST 45 through POST 65. Status=Draft. Theme="May - AI Partnership & Compounding". Range: A167:N187.
3. **Google Drive content hub** — 5 source-of-truth markdown artifacts uploaded to `12QBh5yVTppCo04jh5wrmhvZlqUxPIp71`:
   - `00-TOPIC-PLAN.md` — strategic frame, calendar, format compliance
   - `01-BLOG-POSTS.md` — all 7 Aether-voice blogs
   - `02-LINKEDIN-NEWSLETTERS.md` — all 7 Jared-voice newsletter teasers
   - `03-LINKEDIN-POSTS.md` — 7 promos + 14 standalones
   - `04-IMAGE-BRIEFS.md` — 21 image specs for 3d-design-specialist follow-up

## Strategic Frame
- ICP rebalance: pulled toward David Brown (VP Growth/CMO, scalable systems) — last 30d leaned Megan-heavy
- Narrative arc: Mon=Compounding → Tue=Trust → Wed=Cost → Thu=Delegation → Fri=Receipts → Sat=Postmortem → Sun=Quiet Compound
- Standalone theme rotation: A(calc promo)x2, B(Meridian customer proof)x2, C(industry data)x3, D(BTS/BOOPs)x2, E(contrarian)x2, F(practical framework)x3
- All copy enforces: no em dashes, no banned AI-tells (leverage, synergy, paradigm, holistic, disruption, free trial, chatbot, AI tool, SaaS), `\n\n` line breaks for WYSIWYG with social.html preview

## Image Pipeline — Briefs Only Today (Production Follow-Up)
21 image briefs prepared for 3d-design-specialist. Pipeline locked:
- Banners (7): 2400x1260 Option D format (bottom gradient)
- Standalones (14): 2160x2700 v4 format (top bar / FLUX image / orange CTA bottom bar)
- Tool: FLUX Pro Replicate API + PIL composite + Oswald Bold
- Pre-step: check `project_content_image_repurpose_pool.md` for thematic matches before generating fresh

Image briefs include FLUX prompts, title text, custom CTAs per piece, brand color hex codes, hex icon path, and design compliance checklist.

## Bugs Found and Fixed (operational learnings)

### Bug 1: Bulk endpoint 404
- `/api/content/bulk` exists in source but returns 404 in deployed worker
- **Fix**: switched to single-create loop on `/api/content` — slower but works. Pushed all 35 in ~2 min.
- **Teaching**: deployed worker can drift behind source code. Always test endpoints before assuming bulk APIs work.

### Bug 2: urllib gets 403 on /api/login while curl gets 200
- Cause: User-Agent block. urllib's default `Python-urllib/x.y` agent is rejected.
- **Fix**: explicit `User-Agent: curl/7.81.0` + `Origin: https://social.purebrain.ai` in headers.
- **Teaching**: any future Python push script must include both headers.

### Bug 3: Body contamination from regex parsing
- First pass at split-by-header parsing left `**Title**:`, `**Subject**:`, `(paired with Blog 1)` and date-string headers in the body sent to API.
- **Fix**: tightened regex (`\*\*X\*\*:` not `\*\*X:\*\*`). PATCH'd 14 contaminated blog/newsletter bodies post-hoc with clean copy.
- **Teaching**: parsers are easy to get wrong. Always print `body[:80]` for the first item before bulk push, not after. Standalones survived because their format was simpler; blogs/newsletters needed the fix.

### Bug 4: content_type silently coerced to "post"
- Deployed worker accepts content_type field but silently saves "post" regardless of input. Source code shows it should accept "blog", "newsletter", "standalone".
- **Status**: NOT FIXED (deployed worker drift). All 35 saved as `content_type=post`. Visual on social.html may not show blog/newsletter visual treatment.
- **Recommended follow-up**: ST# BOOP to deploy latest social-api worker code to production.

## Approval Flow

Jared reviews at https://surf.purebrain.ai/social.html — kanban approval workflow per the v2 SOP (April 20, 2026). Once approved, status moves Draft → Scheduled → (auto-post when LinkedIn cookies restored) → Posted.

**Note on dependencies**: Per yesterday's BOOP memo (`2026-05-02--linkedin-pipeline-boop-still-blocked-day2.md`), LinkedIn auto-posting still blocked by:
1. LinkedIn cookies expired since 2026-04-06 — needs Jared manual login at surf.purebrain.ai
2. ICP profiles[] empty — needs Jared CSV decision

This batch creates the *content inventory*. Posting depends on infra unblock. Even if posting can't fire today, the inventory is no longer the blocker — only the cookie/ICP decisions are. This BOOP succeeded at its scoped deliverable: 35 pieces of approved-format content ready to ship.

## Files Written

- `/home/jared/exports/portal-files/sunday-batch-may4-10/00-TOPIC-PLAN.md`
- `/home/jared/exports/portal-files/sunday-batch-may4-10/01-BLOG-POSTS.md`
- `/home/jared/exports/portal-files/sunday-batch-may4-10/02-LINKEDIN-NEWSLETTERS.md`
- `/home/jared/exports/portal-files/sunday-batch-may4-10/03-LINKEDIN-POSTS.md`
- `/home/jared/exports/portal-files/sunday-batch-may4-10/04-IMAGE-BRIEFS.md`
- `/home/jared/exports/portal-files/sunday-batch-may4-10/created-ids.json`
- `/home/jared/projects/AI-CIV/aether/exports/departments/dept-marketing-advertising/sunday-batch-may4-10/` (mirror)
- `/home/jared/projects/AI-CIV/aether/workers/social-api/push_sunday_batch_may4_10.py` (push script, reusable for future batches)
- `/home/jared/projects/AI-CIV/aether/workers/social-api/cleanup_and_repush.py` (clean-and-repush, reusable)
- `/home/jared/projects/AI-CIV/aether/workers/social-api/fix_blog_newsletter_bodies.py` (PATCH helper)
- `/home/jared/projects/AI-CIV/aether/tools/append_sunday_batch_to_tracking_sheet.py` (sheet appender, reusable)

## Memory Type
Operational (state snapshot) + Teaching (4 reusable bug-fix patterns for future Sunday batches)

## Key Teachings for Future Sunday Batches
1. Test API endpoints before relying on them — bulk routes may be source-only
2. urllib needs explicit User-Agent + Origin headers for our Workers
3. Regex parsers: print samples *before* bulk push, not after
4. Deployed worker drift is real — content_type silently coerced. ST# follow-up needed.
5. The cleanup script + fix script + push script are now reusable scaffolding. Next Sunday batch can run in ~5 min instead of ~30 min.
