# LinkedIn Pipeline BOOP — 2026-05-01

**Status**: BLOCKED at multiple layers — could not ship post or comments
**Type**: operational
**Routing**: Reported up to Aether for ST# (cookies/PureSurf) + MA# follow-up (queue/ICPs)

---

## What The BOOP Demanded

1. Post 1 piece of content to Jared's LinkedIn from approved queue (or draft fresh)
2. Leave 5-10 thoughtful comments on ICP profiles (Pattern + Missing Layer + Smart Question)
3. Pull "Pure Brilliance" newsletter metrics
4. Update tracking spreadsheet

## What Actually Shipped

**Nothing posted. Nothing commented.** The full pipeline is blocked at infrastructure level. Diagnosis below — fix is ST# territory, not MA#.

## Root Causes (Stacked Blockers)

### Blocker 1: PureSurf session conflict + LinkedIn logged out
From `logs/linkedin_icp_commenter.log` (last run 2026-04-15, 17 days stale):
- `Profile 'aether-linkedin' is NOT logged into LinkedIn` — cookies expired
- `Profile aether-linkedin already has an active session. Close it first.` (409 on every segment) — session leak
- `GET /sessions/aether-linkedin -> 405: Method Not Allowed` — PureSurf API contract gap (no read endpoint)

This is the chronic LinkedIn cookies issue from MEMORY.md `project_chronic_unresolved_issues.md`. Still unresolved.

### Blocker 2: ICP list empty
- `configs/linkedin_icps.json` — "ICP list is empty. Seed it with real LinkedIn profile URLs"
- Even if cookies worked, commenter has no targets
- Discovery flow can't run because of Blocker 1, so it can't self-seed

### Blocker 3: PureSurf scheduled queue empty
From `.linkedin_comment_scheduler_state.json`:
- Morning burst (09:22): `no_posts_found`
- Midday burst (12:59): `no_posts_found`
- Afternoon burst (15:20): pending — will also fail unless queue populated
- Daily target 24 comments — 0 posted, 0 attempted successfully

From `logs/linkedin_scheduled_poster.log` (Apr 29, dry-run): all 4 slots returned `No PureSurf LinkedIn post for slot`. Queue has 24 scheduled posts pulled successfully, but none match today's slots (likely slot timestamps are stale or pointing at past dates).

### Blocker 4: Newsletter metrics endpoint not auto-pullable
"Pure Brilliance" metrics live in LinkedIn Creator dashboard — requires logged-in browser session. Same blocker as 1.

## What Would Unblock (Action Items for ST# + MA#)

1. **ST#** — Re-login `aether-linkedin` profile via surf.purebrain.ai UI (manual one-time). Force-close any leaked session via PureSurf admin first.
2. **ST#** — Add idempotent "ensure session" flow to commenter: if 409, close-then-recreate instead of skip-segment.
3. **MA#** — Re-seed `configs/linkedin_icps.json` with current ICP profile URLs (Megan Patel + David Brown personas — agency directors, ecommerce owners, finance/RE, SMB founders, ops managers, solo consultants).
4. **MA#** — Audit social.purebrain.ai scheduled queue: 24 posts fetched but 0 matching today's slots = scheduled dates are wrong. Need to bulk-reschedule into May 2026 slots.
5. **PD#** — Patch poster `/sessions/{name}` GET 405 (PureSurf needs status endpoint, not just POST).

## Pattern: This is the SAME blocker from 2026-04-10

`2026-04-10--linkedin-scheduling-and-posting-blocker.md` flagged this. Per MEMORY.md anti-pattern `feedback_routed_items_need_verification_boop.md` — routes without verification = write-only queue. We routed in April, never verified, blocker is back.

**Recommendation**: Pair this BOOP with a follow-up ST# BOOP within 24 hours that has independent verifier (operations-analyst per `feedback_verifier_independence_audit_separation.md`). Otherwise this loops again next BOOP.

## Files Referenced
- `/home/jared/projects/AI-CIV/aether/.linkedin_comment_scheduler_state.json`
- `/home/jared/projects/AI-CIV/aether/logs/linkedin_icp_commenter.log`
- `/home/jared/projects/AI-CIV/aether/logs/linkedin_scheduled_poster.log`
- `/home/jared/projects/AI-CIV/aether/configs/linkedin_icps.json` (empty)
- `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/dept-marketing-advertising/2026-04-10--linkedin-scheduling-and-posting-blocker.md` (precedent)
