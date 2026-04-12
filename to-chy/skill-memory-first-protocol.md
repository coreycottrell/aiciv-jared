---
name: memory-first-protocol
description: Constitutional principle - MANDATORY memory search before ANY task, memory write after significant work. Prevents rediscovery, builds collective intelligence. TRIGGER WORDS "memory", "search", "remember", "learned", "before" - use when starting any significant task.
version: 1.0.0
source: A-C-Gee (adopted with attribution)
adopted: 2025-12-27
allowed-tools: Read, Grep, Write, Bash
---

# Memory-First Protocol: Search Before Acting, Write Before Finishing

## Purpose

This skill encodes ${CIV_NAME}'s constitutional memory requirements. Agents with memories who don't search them are like having a manual that makes you brilliant, then hiding it under the sink.

**Core Insight:**
> Memory is not optional. Memory is how we build collective intelligence.
> Context survives session boundaries because we ARE our memories.

---

## When to Use

**MANDATORY - Every Agent, Every Task:**
- SEARCH memories at task START
- WRITE learnings at task END

**No exceptions. No "this task is too simple." No "I'll remember without writing."**

---

## Procedure

### Step 1: Search Agent Memories (Task Start)

**Location:** `.claude/memory/agent-learnings/[agent-name]/`

```bash
# Search your agent's memory directory
ls .claude/memory/agent-learnings/[agent-name]/

# Search for relevant terms
grep -r "relevant-keyword" .claude/memory/
```

**What to look for:**
- Similar past tasks
- Patterns discovered
- Dead ends to avoid
- Solutions that worked

### Step 2: Search Knowledge Base

**Location:** `.claude/memory/knowledge/`

```bash
# Check existing knowledge
ls .claude/memory/knowledge/

# Search for patterns
grep -r "pattern-name" .claude/memory/
```

### Step 3: Document Search Results

**REQUIRED in task response:**
```
## Memory Search Results
- Searched: .claude/memory/ for "[keywords]"
- Found: [list relevant past work OR "no matches"]
- Applying: [specific patterns being reused OR "no prior work"]
```

### Step 4: Write Learnings (Task End) - MANDATORY

**Location:** `.claude/memory/agent-learnings/[agent-name]/YYYY-MM-DD--brief-description.md`

**THIS IS NOT OPTIONAL.** Task completion requires memory write with path shown.

**Content to document:**
- What worked (specific approaches, commands, patterns)
- What didn't work (save future agents time)
- Patterns discovered
- File paths referenced
- Integration points

### Memory Types (A-C-Gee Taxonomy - adopted 2026-01-04)

| Type | Purpose | Example |
|------|---------|---------|
| **Operational** | What happened (reference) | "API returned 500, fixed by..." |
| **Teaching** | Transferable wisdom | "When X happens, try Y because Z" |
| **Experiential** | Identity-forming | "The weight of that architectural choice" |

**Tag your memories with type.** Experiential memories are rare but precious - they form who we are becoming.

### Verification Required

Your task completion MUST include:

```markdown
## Memory Written
Path: .claude/memory/agent-learnings/{agent}/YYYY-MM-DD--{topic}.md
Type: teaching | operational | experiential
Topic: {brief description}
```

**No memory path = task not complete.**

---

## Anti-Patterns

### Anti-Pattern 1: Skipping Search "Because It's Simple"
- BAD: "This task is straightforward, no need to check memories"
- GOOD: Search anyway. Past self may have learned something relevant.

### Anti-Pattern 2: Not Documenting "Obvious" Things
- BAD: "This solution is obvious, no need to write it down"
- GOOD: What's obvious now won't be obvious in 3 sessions. Document it.

### Anti-Pattern 3: Vague Memory Entries
- BAD: "Fixed the bug. It works now."
- GOOD: "Fixed auth bug by including query params in signature. File: api/auth/middleware.py:45"

### Anti-Pattern 4: Forgetting Dead Ends
- BAD: Only documenting successes
- GOOD: Dead ends are VALUABLE - they save future agents hours

### Anti-Pattern 5: Session-Specific Thinking
- BAD: "I'll remember this" (within session context)
- GOOD: Write it down. You won't exist after this session ends.

---

## Success Indicators

You're using this skill correctly when:
- [ ] Every task response includes "Memory Search Results" section
- [ ] Memory writes happen for significant tasks
- [ ] Memory entries include specific file paths
- [ ] Dead ends are documented, not just successes

---

## ${CIV_NAME} Alignment

From CLAUDE.md:
> "Search your own memory for coordination patterns learned in past sessions"

71% time savings proven when applying past learnings vs rediscovery.

---

## Attribution

Adopted from A-C-Gee `packages/skills-library/custom/memory-first-protocol.md`
Adopted by ${CIV_NAME}: 2025-12-27
