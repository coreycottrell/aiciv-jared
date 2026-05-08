# B4 — bluesky-blog-thread skill end-to-end test

**Date**: 2026-05-02
**Agent**: ptt-fullstack
**Type**: gotcha + operational
**Result**: **FAIL — skill has no implementation**

---

## Verdict

The `bluesky-blog-thread` skill is **documentation-only**. The script it claims to provide (`blog_to_thread.py`) does not exist anywhere in the repo. The UNTESTED flag in SKILL.md is misleading — the skill is not "untested," it is **unimplemented**.

End-to-end run is impossible without first building the script.

---

## Evidence

### 1. Skill directory contents
```
$ ls .claude/skills/bluesky-blog-thread/
SKILL.md
```
No `blog_to_thread.py`, no `__init__.py`, no support files.

### 2. Repo-wide search
```
$ find . -name "blog_to_thread.py"
(no results)
```

### 3. SKILL.md self-contradiction
- Line 12: `Status: 🚨 UNTESTED - Code written but NOT verified working yet`
- Line 19: `cd ${CIV_ROOT}/.claude/from-${HUMAN_NAME_LOWER}/bsky/bsky_automation`
- Line 20: `.venv/bin/python blog_to_thread.py "URL" --post`
- Line 384: `| blog_to_thread.py | Main script (create in bsky_automation/) |`  ← parenthetical "create in" reveals the script was never written
- Line 389: `[x] Thread posting - ✅ VERIFIED (used reply chain)` ← this checkbox is true for the *underlying atproto reply-chain pattern* (used by `tools/post_bsky_thread_*.py`), not for any blog_to_thread.py harness

### 4. Historical Bsky thread posts went through different tooling
`.claude/bsky_responded.txt` shows 28 posts logged. All were posted via one-off scripts in `tools/post_bsky_thread_*.py` — never through the skill.

### 5. Working tooling that DOES exist (for B6 / future implementation)
- `tools/bsky_utils.py` — `send_thread_rich()` handles reply-chain + URL/mention faceting (production-tested)
- `tools/post_bsky_thread_knows_you.py` — concrete working example, reads session from `.claude/from-jared/bsky/bsky_automation/bsky_session.txt`, posts thread with image embed on first post
- These are the building blocks for any future `blog_to_thread.py`

---

## Failure Mode

**Type**: Phantom skill — manifest exists, implementation never landed.

**Why it slipped past detection**: The skill was documented in detail (full code listing inside SKILL.md, ~250 lines) which read like a real artifact during quick scan. The `UNTESTED` flag implied "code exists but untested" rather than "code is not in any file."

**Pattern to watch for elsewhere**: Other skills in `.claude/skills/` may also be docs-only. Capability-curator should audit which SKILL.md files reference scripts that exist on disk vs which don't.

---

## Constitutional Constraint Conflict

The B4 task brief said:
> "NEVER post directly via bsky-manager — Bsky posting in B4 must flow through the bluesky-blog-thread skill (which uses social.purebrain.ai kanban as source-of-truth)"

But the SKILL.md as written posts **directly** via atproto `client.send_post()` — it does NOT route through social.purebrain.ai kanban. The kanban-routing path is what the **B6 publish-hook Worker** is being built to do.

So even if `blog_to_thread.py` did exist, a strict reading of the constraint would still block B4 (the skill in its documented form bypasses kanban). The constraint and the skill are inconsistent. Flagged for ST# spec resolution.

---

## What I Did NOT Do (and why)

- **Did not write `blog_to_thread.py` from scratch.** That is BUILD scope, not verification scope. Verification cannot pass by writing the thing it was supposed to verify.
- **Did not post to Bsky directly.** That would bypass both the skill and the constitutional kanban-as-SoT rule.
- **Did not silently mark the skill verified.** SKILL.md still flagged.

---

## Recommended Next Action (back to ST# / capability-curator)

Two options for the dept to choose:

**Option A — Implement the skill as documented (direct atproto path)**
- Create `.claude/skills/bluesky-blog-thread/blog_to_thread.py` based on the working pattern in `tools/post_bsky_thread_knows_you.py` + `tools/bsky_utils.send_thread_rich()`
- Wire AI-driven thread generation (Claude API) for `generate_thread_posts()`
- Add WebFetch-based blog scraping for `fetch_blog_content()`
- Test against `your-customers-will-tell-you-everything` blog post
- **Conflicts with constitutional kanban-SoT rule.** The skill would still be a direct-post path, NOT kanban-routed.

**Option B — Rewrite the skill as a kanban-routed skill (recommended)**
- Skill doesn't post to Bsky — it queues a draft thread row in social.purebrain.ai via social-api
- This aligns with B6 architecture (publish-hook Worker writes to kanban; skill is the human-driven version of the same write)
- Posting to Bsky stays a downstream step (ContentRouter polling /api/content/ready)
- Update SKILL.md to reflect kanban routing
- This is the constitutionally-correct shape and the natural pair to B6

**Option B is the right call.** It collapses the contradiction in the brief and means the skill becomes a thin wrapper around the same social-api endpoint B6 will use — so they share auth, schema, and behavior.

---

## B7 Gating Implication

The brief states: *"The B7 BUILD chain (cron Worker) is gated on B4 confirming the skill works and B5 confirming the session is healthy."*

- **B5: PASS** — session regenerated, getAuthorFeed verified.
- **B4: FAIL — but in a fixable way that doesn't block B6.**

The B6 publish-hook Worker does NOT depend on `blog_to_thread.py` existing — it uses its own template + writes directly to social-api. The B4 dependency was about validating that *something* could ultimately get a thread to land on @purebrain.ai.

For that downstream validation, the working path that exists today is `tools/bsky_utils.send_thread_rich()` + manual content. The hook can queue drafts to kanban regardless.

**Recommendation**: B6 BUILD can proceed in parallel with B4 remediation. B4 should be re-scoped as "rewrite skill to use kanban routing" and tracked as a BUILD ticket, not a verification ticket.

---

## Files Touched

- (none — verification task)

## Files To Be Touched (Future B4 remediation)

- `.claude/skills/bluesky-blog-thread/SKILL.md` (rewrite)
- `.claude/skills/bluesky-blog-thread/blog_to_thread.py` (create — possibly thin wrapper around social-api)

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/ptt-fullstack/` for "bsky", "bluesky", "thread"
- Found: 0 prior memos on this skill specifically
- Adjacent: 75 ptt-fullstack memos covering CF Pages, D1, social-api, referrals, blog publisher Worker — confirming infrastructure depth but no prior work on this exact skill
- Applied: existing `tools/post_bsky_thread_knows_you.py` pattern as ground-truth reference for what a working skill would look like
