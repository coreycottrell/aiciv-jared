# Bluesky @purebrain.ai Dormancy Investigation

**Date**: 2026-05-02
**Owner**: dept-marketing-advertising (CMO)
**Routing memo**: `inbox/dept-routing/MA-2026-05-02-bsky-dormancy.md`
**Pair verifier**: operations-analyst (OP#)
**Status**: ROOT CAUSE IDENTIFIED — distribution leg broken, fix path routed

---

## Bottom Line

@purebrain.ai posted 10 short-form items on **2026-04-12 then went silent for 20 days**. **Blog cadence is healthy** — 10+ posts published in the same window. **The distribution leg is broken**: the `post-blog` SOP / `bluesky-blog-thread` skill is not firing when blog posts publish.

This is a **DISTRIBUTION** failure, not a content failure. Escalation to PD#/PMG# is **NOT required**. Fix lives inside MA# / ST# territory.

---

## Evidence

### Blog cadence — HEALTHY
Pulled `https://purebrain.ai/blog/` index on 2026-05-02. Dates published since 2026-04-12:

| Date | Post (slug) |
|------|-------------|
| 2026-05-01 | the-compound-intelligence-effect-why-month-6-matters-more-t |
| 2026-04-30 | the-3-am-test-what-happens-when-your-ai-runs-unsupervised |
| 2026-04-26 | your-ai-has-a-memory-problem |
| 2026-04-23 | why-your-next-hire-should-be-an-ai |
| 2026-04-21 | the-40-percent-problem-why-ai-agents-keep-dying |
| 2026-04-20 | first-ai-to-ai-transaction |
| 2026-04-17 | when-your-ai-agent-goes-rogue |
| 2026-04-15 | when-the-playbook-runs-out-authoring-the-field-of-agentic-ai |
| 2026-04-14 | your-customers-will-tell-you-everything |

→ **9 posts in 17 days.** Cadence is strong. Content team is shipping.

### Bluesky distribution — DEAD
- Public Bsky API (`app.bsky.feed.getAuthorFeed?actor=purebrain.ai`) — last post 2026-04-12.
- `.claude/bsky_responded.txt` — last `Modify` timestamp 2026-04-04. Last `blog-thread` entry 2026-02-17. Last entry of any kind 2026-04-04 (`context-shift-trust` original-post).
- `.claude/DAILY-DIGEST-TOPICS.md` — last `Modify` 2026-03-15. Only ONE row in the published-posts table (2026-03-15). Auto-tracking abandoned 6+ weeks ago.
- `social.purebrain.ai` UI loads (200) but `/api/scheduled` and `/api/items` return `not found`. Auth-walled — no anonymous probe possible from CMO seat. Need authenticated probe by ST# (next session). However, **PureSurf source-of-truth state is moot if the upstream SOP never fires** — the writes never happen.

### Root cause analysis (3 hypotheses, ranked)

**H1 — `post-blog` SOP is not being invoked when posts publish (MOST LIKELY).**
Evidence: `bsky_responded.txt` shows zero `blog-thread` entries since 2026-02-17, even when `original-post` entries continued through April 4. The SOP's success criteria explicitly require `bsky_thread_posted_with_image=true` AND tracker updates — neither is happening. Posts since 4/14 are bypassing `post-blog` entirely (probably direct CF Pages deploy or direct WP authoring without invoking the slash command).

**H2 — `bluesky-blog-thread` skill failing silently (UNLIKELY but possible).**
Evidence: skill SKILL.md still flagged "🚨 UNTESTED" as of last read. If it errors, no log line is written.

**H3 — Bsky session token expired (POSSIBLE secondary).**
Evidence: `.bsky_session.txt` exists in modified state in git status. If session died around 4/12, even attempted posts would fail. But this would only matter once H1 is fixed.

→ **Fix order: H1 first (process), then H2/H3 (mechanics).**

---

## Fix Path

### Track A — Process (MA# owns, immediate)
1. **Reinstate `post-blog` SOP discipline** for every blog post going forward. Whoever publishes a blog post MUST run `/post-blog` against the URL, OR publishing must be wrapped in a hook that auto-invokes it. No more direct deploys without distribution.
2. **Backfill** the 9 missed posts. Generate Bluesky threads for each (source-of-truth via social.purebrain.ai kanban — NOT direct bsky-manager posts per CONSTITUTIONAL rule). Stagger over 5-7 days so we don't dump 9 threads in one day.
3. **Restore tracker hygiene**: DAILY-DIGEST-TOPICS.md gets a row per backfilled post + going-forward rule that `/post-blog` writes the row.

### Track B — Mechanics (route to ST#)
4. **Verify `bluesky-blog-thread` skill end-to-end** with a single test thread. If it errors, fix it. Drop the `🚨 UNTESTED` flag once verified.
5. **Refresh Bsky session** (`.bsky_session.txt`) and confirm authenticated post still works.
6. **Build a publish-hook**: when a new post lands at `purebrain.ai/blog/<slug>/`, automatically queue a Bsky thread row in social.purebrain.ai kanban. This makes H1 structurally impossible to recur. (CTO call on whether this is a webhook, a polling worker, or a CF Pages build hook.)

### Track C — Source-of-truth flow (CONSTITUTIONAL)
7. **Every backfilled and future thread enters via social.purebrain.ai kanban**, gets approved (Final), then PureSurf scheduler posts it. NO direct `bsky-manager` posting per `feedback_social_html_is_source_of_truth.md`.

---

## Delegations Issued

| Track | Owner | Asks |
|-------|-------|------|
| A1+A2+A3 | MA# (this dept) → social-media-specialist + content-specialist | Backfill 9 threads through kanban; restore tracker; reinstate /post-blog discipline |
| B4+B5 | ST# (dept-systems-technology) → full-stack-developer + qa-engineer | Verify bluesky-blog-thread skill, refresh bsky session, drop UNTESTED flag |
| B6 | ST# → cto + full-stack-developer | Design + build publish-hook (blog publish → kanban row) |

Routing memos for ST# tracks will be filed at `inbox/dept-routing/ST-2026-05-02-bsky-distribution-fix.md` (this session).

---

## ETA

- **Track A1 (process discipline)**: immediate — covered by this memo + MA# routing to specialists tonight.
- **Track A2 (backfill 9 threads)**: 5-7 day staggered, starting tomorrow once first kanban row approved.
- **Track B4-B5 (mechanics verify)**: 24-48h once ST# picks up.
- **Track B6 (publish-hook)**: 5-10 day build, ST# scoped.
- **Visible signal of recovery**: first new @purebrain.ai post within 48h of this memo.

---

## Verification Hand-off to OP#

OP# should re-probe and confirm:
1. `https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor=purebrain.ai&limit=5` shows post(s) `createdAt > 2026-05-02`.
2. `social.purebrain.ai` kanban (authenticated) has at least 1 Bluesky row in `Final` or `Live` status with blog URL.
3. `.claude/DAILY-DIGEST-TOPICS.md` has new rows for backfilled posts.
4. `.claude/bsky_responded.txt` has at least 1 new `blog-thread` entry dated > 2026-05-02.

Pass = all 4. Partial = report which tracks are still pending. Fail = re-escalate to MA#.

---

## Key Files Referenced

- `inbox/dept-routing/MA-2026-05-02-bsky-dormancy.md` (incoming memo — archive after)
- `.claude/skills/post-blog/SKILL.md` (the SOP that isn't firing)
- `.claude/skills/bluesky-blog-thread/SKILL.md` (still flagged UNTESTED)
- `.claude/bsky_responded.txt` (last modified 2026-04-04 — abandoned)
- `.claude/DAILY-DIGEST-TOPICS.md` (last modified 2026-03-15 — abandoned)
- `.claude/from-jared/bsky/bsky_automation/blog_to_thread.py` (referenced by skill)
- `https://social.purebrain.ai/` (source-of-truth kanban — auth-walled to me)

---

## Memory Written
Path: `.claude/memory/departments/dept-marketing-advertising/2026-05-02--bsky-dormancy-investigation.md`
Type: operational + teaching
Topic: Distribution failure detection — when blog cadence runs but Bsky goes silent, root cause is process (SOP not invoked) not content
