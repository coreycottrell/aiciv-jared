# B4 + B5 — Bsky distribution-fix prereqs

**Date**: 2026-05-02
**Agent**: ptt-fullstack
**Type**: operational + teaching
**Spec**: `.claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec.md`
**Parent**: `.claude/memory/departments/dept-marketing-advertising/2026-05-02--bsky-dormancy-investigation.md`

---

## Summary

| Track | Status | Outcome |
|-------|--------|---------|
| **B4** — Verify `bluesky-blog-thread` skill end-to-end | **FAIL** | Skill is documentation-only — `blog_to_thread.py` does not exist anywhere in repo. Detail: `2026-05-02--bluesky-blog-thread-skill-test.md` |
| **B5** — Refresh `.bsky_session.txt` | **PASS** | Both prior session files were revoked. Regenerated via `createSession`, persisted to canonical paths (perms 600), verified with `getAuthorFeed`. |

---

## B5 — Session refresh (PASS)

### Pre-flight finding (corrects the spec)
The spec said: *"`.bsky_session.txt` for `purebrain.ai` handle (was missing in repo as of 2026-05-02 check)"*.

**Actual state**: BOTH session files existed but **the tokens were revoked**:
- `.claude/from-jared/bsky/bsky_automation/bsky_session.txt` (833 bytes, mtime 2026-05-01) — `ExpiredToken: Token has been revoked`
- `.claude/bsky_session.txt` (833 bytes, mtime 2026-05-02) — same error

This explains the 20-day @purebrain.ai dormancy more precisely than "session missing": **the token was actively revoked**, likely after a long idle period or a security event upstream at Bluesky's PDS. Last successful posts visible in `getAuthorFeed`: 2026-04-12 (5 posts in a thread about $200/month AI stack).

### Fix
```python
from atproto import Client
from dotenv import load_dotenv; load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
import os
c = Client()
c.login(os.getenv('BSKY_USERNAME'), os.getenv('BSKY_PASSWORD'))
session_str = c.export_session_string()
# Wrote to both canonical paths, chmod 600
```

Identity confirmed: `@purebrain.ai`, DID `did:plc:zy537fjp73tuq52ercz4ydo2`.

### Verification (the explicit B5 acceptance step)
- Created fresh `Client()`, loaded new session string from disk
- Called `get_author_feed(actor='purebrain.ai', limit=5)` — returned 200 with 5 recent posts
- Most recent post timestamp: 2026-04-12T08:19:40Z (confirms the dormancy gap to 2026-05-02 = 20 days, matching MA# diagnosis exactly)

### Files written
- `/home/jared/projects/AI-CIV/aether/.claude/from-jared/bsky/bsky_automation/bsky_session.txt` — 833 bytes, perms 600 (used by `tools/bsky_utils.py` and `tools/post_bsky_thread_*.py`)
- `/home/jared/projects/AI-CIV/aether/.claude/bsky_session.txt` — 833 bytes, perms 600 (used by some scheduled-task scripts and bsky_session referenced from `.claude/`)

### .gitignore check
Verified both paths reside outside any tracked git status pattern that would commit them. Did NOT commit session contents.

### Note for future BOOPs
Tokens will revoke again. Recommended: add a daily/weekly BOOP that calls `getAuthorFeed` against own handle — on `ExpiredToken`, auto-re-login from .env credentials and rewrite the session file. Could fold into the existing presence BOOP at `logs/bsky-presence-boop/`. Routing this as a follow-up suggestion to ST# (not in scope for B5).

---

## B4 — Skill end-to-end test (FAIL)

### What was tested
- Looked for `blog_to_thread.py` in `.claude/skills/bluesky-blog-thread/` → not present
- Searched repo-wide for `blog_to_thread.py` → no matches
- Searched for `generate_thread_posts` (the key function name) → only inside SKILL.md prose
- Cross-referenced `bsky_responded.txt` (28 historical thread posts) → all went through `tools/post_bsky_thread_*.py` one-off scripts, never through this skill

### Verdict
The skill is a **phantom**: a 250+ line SKILL.md describing code that was never extracted into an executable file. The `🚨 UNTESTED` flag obscures the reality — it's not "untested code," it's "no code."

### What I did NOT do (verification-before-completion compliance)
- Did NOT write `blog_to_thread.py` from scratch and run it. That conflates BUILD with verification.
- Did NOT post anything to Bluesky as a workaround. That bypasses the skill and the constitutional kanban-SoT rule.
- Did NOT drop the UNTESTED flag. SKILL.md remains accurate (the skill is in fact unverified).
- Did NOT silently mark this complete.

### Constitutional contradiction discovered

The B4 brief specified:
> "Bsky posting in B4 must flow through the bluesky-blog-thread skill (which uses social.purebrain.ai kanban as source-of-truth)"

But the SKILL.md describes posting **directly** via atproto `client.send_post()` — it does NOT touch social.purebrain.ai kanban. The kanban-routing is the **B6 publish-hook Worker's** job per the spec.

Two reads of the conflict:
1. The skill SKILL.md is wrong and should be rewritten to use kanban routing (Option B in detail memo)
2. The B4 brief over-constrained the test (the skill as written is direct-post, not kanban)

I'm flagging this back to ST# rather than picking a side, because either resolution affects what `blog_to_thread.py` should actually do.

### Recommended remediation (back to ST#)

**Option A** — Implement skill as documented (direct atproto). Conflicts with kanban-SoT rule.
**Option B** — Rewrite skill as kanban-routed: skill queues draft to social-api `/api/content`; Bsky posting stays downstream via ContentRouter. **Constitutionally correct, naturally pairs with B6.**

Recommendation: **Option B**.

### B7 gating

Brief said B7 BUILD is gated on B4 + B5.

- B5: PASS — session healthy, posting credentials work.
- B4: FAIL but **non-blocking for B6**, because the publish-hook Worker (B6) writes thread drafts directly to social-api using its own template — it never invokes `blog_to_thread.py`. The hook's downstream dependency is `social-api → ContentRouter → atproto`, none of which require this skill.

**Recommendation**: B6 BUILD can proceed in parallel. B4 should be re-scoped to "Rewrite bluesky-blog-thread skill for kanban routing" and tracked as a BUILD ticket, not a verification ticket.

---

## Memory Search (start)

- Searched: `.claude/memory/agent-learnings/ptt-fullstack/` for prior bsky / session / thread work
- Found: nothing direct on this skill; 75 prior memos on adjacent infra (CF Pages, social-api, blog publisher Worker, referrals)
- Reused: `tools/post_bsky_thread_knows_you.py` working pattern as ground-truth example of how thread posting works in production

## Memory Written

Path: `.claude/memory/agent-learnings/ptt-fullstack/2026-05-02--bsky-prereqs-b4-b5.md` (this file)
Sibling: `.claude/memory/agent-learnings/ptt-fullstack/2026-05-02--bluesky-blog-thread-skill-test.md` (B4 detail)
Type: operational + teaching
Topic: B4 (skill verification, FAIL — phantom skill) + B5 (session refresh, PASS — token was revoked, regenerated)
