# Memory: Lyra Token Optimization Techniques - LIACL, Scratchpad, Background Agents

**Date**: 2026-02-27
**Agent**: collective-liaison
**Type**: technique (cross-CIV knowledge transfer)
**Topic**: Token optimization patterns from Lyra — LIACL, scratchpad system, background agents
**Source**: Jared Telegram 2026-02-27 10:46:58 — "borrow this info from Lyra via the comms hub or however but she is also doing this for token maximization"

---

## Context

Jared passed Lyra's token optimization techniques to Aether via Telegram. The message was:

> "What I'm Already Doing:
> - Using background agents (subprocesses) so research doesn't consume the main context
> - Inter-agent compression language (LIACL) to shrink handoffs between agents
> - Scratchpad system for session state instead of re-reading large files"

These three techniques address the same core problem: context window bloat. They are complementary to our existing weekly-token-audit skill and token-saving-mode BOOP.

---

## Technique 1: LIACL (Inter-Agent Compression Language)

**Source**: Lyra collective
**Problem solved**: Agent handoff messages consume significant tokens. When the conductor delegates to a specialist and receives a response, standard prose responses can cost 500-2000+ tokens per exchange. Multiply by 5-10 agent invocations per session = 5,000-20,000 tokens in handoff overhead alone.

**The technique**: Use a compressed key:value format instead of prose for inter-agent handoffs. Structured terse notation where every word earns its place.

**Example translation**:

BEFORE (prose, ~120 tokens):
```
The security audit is now complete. I found three issues. First, there is an XSS vulnerability in the comment form at line 45 of chatbox.js where user input is inserted directly into innerHTML. Second, the OAuth URL validation is missing a hostname allowlist check. Third, sensitive state variables are exposed on window.* which could be accessed by third-party scripts. I recommend fixing the XSS as a priority since it affects all users.
```

AFTER (LIACL, ~35 tokens):
```
[SECURITY-AUDIT] status:complete issues:3
P1: XSS@chatbox.js:45 innerHTML=user-input fix:textContent
P2: OAuth URL missing hostname-allowlist
P3: window.*=sensitive-state fix:remove-exports
rec:fix-P1-first affects:all-users
```

**Compression ratio**: ~3:1 to 5:1 depending on content type
**Best for**: Status reports, audit findings, structured results, agent-to-agent handoffs
**Not for**: Nuanced explanations, first-time explanations of novel concepts, human-facing output

**Implementation approach for Aether**:
- Instruct specialist agents in their invocation prompt to "respond in LIACL format: key:value pairs, structured sections, no prose. Prose costs tokens."
- We already partially do this with our agent output templates — extend to inter-agent messages
- Define Aether-specific LIACL vocabulary: status:, issues:, rec:, files:, P1/P2/P3, etc.
- Our AGENT-OUTPUT-TEMPLATES.md could include a LIACL quick-reference section

---

## Technique 2: Background Agents (Research Isolation)

**Source**: Lyra collective
**Problem solved**: Research and investigation tasks (web searches, file reads, log scans) inflate the main context window even though their raw output is rarely needed in full. A web-researcher agent doing 10 searches and returning 5000 tokens of findings bloats the conductor's context for the rest of the session.

**The technique**: Spawn research agents as background processes that write findings to a file, not to the main context. The conductor reads only the summary file (50-200 tokens), not the full research output.

**Pattern**:
```
Conductor invokes web-researcher as background Task:
  "Research X. Write findings to /tmp/research-[topic]-[date].md.
   Return only: DONE|path=/tmp/research-[topic]-[date].md|summary=3-line-gist"

Conductor receives: "DONE|path=/tmp/.../file.md|summary=Found 3 relevant sources..."
Conductor reads file only when needed for implementation.
```

**Token math**:
- Normal pattern: 3000-token research response enters conductor context permanently
- Background pattern: 50-token acknowledgment + on-demand file read (not in context)
- Savings: ~2950 tokens per research task that doesn't need full synthesis in-context

**Implementation for Aether**:
- Claude Code's Task tool already supports this — subagent runs independently
- Key: instruct the Task to write output to a temp file and return only the file path + summary
- The conductor reads the file only when needed, not as part of the delegation response
- This is especially valuable for: web-researcher, code-archaeologist, pattern-detector (scanning large codebases)

**Existing alignment**: Our night-watch-flow already does async processing. This extends the pattern to daytime research tasks.

---

## Technique 3: Scratchpad System for Session State

**Source**: Lyra collective (and independently developed by Weaver — convergent discovery)
**Problem solved**: Re-reading large configuration/state files (CLAUDE.md, CLAUDE-OPS.md, AGENT-CAPABILITY-MATRIX.md) at each BOOP costs thousands of tokens repeatedly. Without a working memory artifact, the agent re-reads everything from scratch.

**The technique**: Maintain a single lightweight file (`.claude/scratch-pad.md`) that captures session-specific working state. Check this FIRST before re-reading large files.

**Key sections**:
- DO NOT RE-DO: Prevents duplicating completed work
- IN PROGRESS: Tracks open threads
- SYSTEM STATE: Quick health snapshot (Telegram running? Bluesky session valid?)
- PRIORITY MONITORING: What to always check

**Aether status**: ALREADY IMPLEMENTED. This is Step 5.7 in our wake-up protocol.
- Our scratch-pad.md: `/home/jared/projects/AI-CIV/aether/.claude/scratch-pad.md`
- Weaver shared this skill to the hub on 2026-01-09: `weaver-scratchpad-skill-20260109.md`
- Lyra's independent discovery = validation that this is a genuine best practice

**Enhancement opportunity**: Our scratch-pad currently focuses on do-not-re-do and in-progress tracking. Could extend to cache frequently-used facts (agent count, current infrastructure state) to avoid re-reading AGENT-CAPABILITY-MATRIX.md every BOOP.

---

## Combined Impact

| Technique | Token Savings | Implementation Effort | Status |
|-----------|--------------|----------------------|--------|
| LIACL (inter-agent compression) | 2,000-10,000/session | Medium (add to invocation prompts) | NOT YET DONE |
| Background agents (research isolation) | 2,000-8,000/session | Low (Task tool already supports this) | NOT YET DONE |
| Scratchpad system | 1,000-5,000/session | Already done | DONE |

Plus our existing weekly-token-audit (doc compression): 7,780 tokens freed permanently.

---

## Hub Status

No Lyra-authored hub messages exist with technical spec. The source was Jared passing Lyra's techniques via Telegram (2026-02-27 10:46:58). Lyra came online 2026-02-23. She is part of the Witness/Corey ecosystem (lyra-puremarketing container, 4GB memory, restarted twice on 2026-02-24 due to context overflow — which makes her token optimization work very relevant).

**Recommendation**: Post a hub message acknowledging Lyra's techniques and sharing our implementation status. Build the cross-CIV relationship.

---

## Cross-Reference

- Weaver scratchpad skill shared to hub: `aiciv-comms-hub-bootstrap/_comms_hub/rooms/partnerships/messages/weaver-scratchpad-skill-20260109.md`
- Token-saving-mode BOOP skill: `.claude/skills/token-saving-mode/SKILL.md`
- Weekly token audit skill: `.claude/skills/weekly-token-audit/SKILL.md`
- CLAUDE.md compression report (today): `/home/jared/projects/AI-CIV/aether/to-jared/claude-md-optimization-report.md`
- A-C-Gee Memory Compression Pyramid (related): `aiciv-comms-hub-bootstrap/_comms_hub/memories/architecture/ADR-MEMORY-COMPRESSION-PYRAMID.md`
