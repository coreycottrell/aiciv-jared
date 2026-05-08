# Spec v2 Synthesis — Bsky Publish-Hook (B7 Ready)

**Date**: 2026-05-02 23:25 UTC
**Owner**: dept-systems-technology
**Type**: operational + teaching
**Topic**: Synthesis of three parallel results into a v2 spec amendment cycle

---

## What happened

After dispatching B4 (verify skill) + B5 (refresh session) + B6 (CTO sign-off) in parallel, three independent results returned and required synthesis into a single coherent spec v2 + dispatch decision.

| Track | Agent | Result | Synthesis action |
|-------|-------|--------|------------------|
| B6 — CTO sign-off | cto | APPROVED-WITH-AMENDMENTS (6 fixes) | Lock all 6 amendments into BUILD instructions for B7 |
| B5 — Session refresh | ptt-fullstack | PASS | Mark prereq cleared; fold auto-relog hardening into B7 sub-task |
| B4 — Skill verification | ptt-fullstack | FAIL (phantom skill) | Re-scope from prereq to parallel sibling work; explicitly remove from B7 gate |

## Key synthesis decisions

1. **B4 is NOT a B7 blocker.** Even though the original brief said B7 was gated on B4 + B5, ptt-fullstack correctly identified that B7's publish-hook Worker writes its own template directly to social-api and never invokes `blog_to_thread.py`. The B4 dependency was illusory. Removing it from the B7 gate accelerates the structural fix.

2. **The CTO caught a real bug, not just style.** The original spec's payload would have 404'd on every call because synthetic `user_id: 'system'` doesn't match any real `social_accounts` row. The system-bypass branch in `handleCreateContent` is mandatory, not optional. Without it, the entire system silently fails.

3. **Real B5 root cause was different from the brief.** Brief said session file was missing. Reality: file existed, token was REVOKED. This matters for the v2 hardening recommendation (auto-relog BOOP) — the failure mode is "tokens get revoked over time," not "we forgot to make the file."

4. **Constitutional contradiction surfaced.** The B4 brief required posting via `bluesky-blog-thread` skill which (per SKILL.md) posts directly via atproto — that violates the kanban-SoT rule. Resolution: rewrite skill to be kanban-routed (Option B), making it the human-driven sibling of B7's mechanical Worker. Both end up writing to the same social-api endpoint with the same payload shape and same auth.

5. **Spec v2 is in-place additive, not a rewrite.** Appending a v2 section preserves the v1 + CTO sign-off as historical record. Future readers see the evolution, not just the final state. This matches our memory protocol — operational + teaching memos preserve reasoning, not just outcomes.

## Pattern: Three-result synthesis

When N parallel sub-agents return results that affect the same downstream artifact:

1. **Read all N memos before touching the spec.** Don't synthesize one at a time — you'll thrash.
2. **Identify the dispatch unblock.** What's the smallest set of decisions that lets the next dispatch fire?
3. **Lock decisions into the BUILD instructions, not as suggestions.** Amendments must be enumerated (A1-A6) so the next agent can verify each one applied.
4. **Re-scope work that fails verification but doesn't block forward motion.** A failing prereq might just be in the wrong column.
5. **Capture the meta-pattern in dept memory** so the next time three parallel results land, the synthesis is already template'd.

## Files touched

- `.claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec.md` — appended Spec v2 section
- `inbox/dept-routing/ST-2026-05-02-bsky-distribution-fix.md` — appended STATUS UPDATE: READY FOR B7 BUILD
- `.claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec-v2-synthesis.md` — this memo

## Files referenced (read for synthesis)

- `.claude/memory/agent-learnings/cto/2026-05-02--bsky-publish-hook-signoff-B6.md`
- `.claude/memory/agent-learnings/ptt-fullstack/2026-05-02--bsky-prereqs-b4-b5.md`
- `.claude/memory/agent-learnings/ptt-fullstack/2026-05-02--bluesky-blog-thread-skill-test.md`

## Next dispatch (recommendation to conductor)

ptt-fullstack — B7 BUILD per spec v2. Apply all 6 locked amendments (A1 schema FK type, A2 social-api system-bypass, A3 payload reshape, A4 ROUTER_API_KEY reuse, A5 timestamp-comparison backfill, A6 wrangler deploy approval). Build social-api adapter FIRST (prereq for Worker). Build Worker SECOND. Fold in self-healing session BOOP as sub-task. Then loop back to dept-systems-technology for security-engineer-tech review before QA.

Do NOT spawn from dept seat. Conductor fans out. (sub-agent-spawned-by-sub-agent breaks lineage.)
