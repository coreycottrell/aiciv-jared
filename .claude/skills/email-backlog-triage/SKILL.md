---
name: email-backlog-triage
version: 1.0.0
author: skills-master
description: Process accumulated email across all inboxes with priority ordering and categorization
tags: [email, triage, backlog, prioritization, human-liaison]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Email Backlog Triage

Systematic process for triaging accumulated email across multiple inboxes with clear priority ordering.

## Inbox Priority Order

Check in this exact order:

1. **jared@puretechnology.nyc** (Jared's - HIGHEST priority)
2. **purebrain@puremarketing.ai** (company)
3. **aethergottaeat@agentmail.to** (agent)
4. **aether-aiciv@agentmail.to** (onboarding - skip unless Witness/Corey)

## Categorization System

Every email gets one of four categories:

| Category | Definition | Action |
|----------|-----------|--------|
| **URGENT** | Needs response now | Respond within current session |
| **INFORMATIONAL** | Log and acknowledge | Archive with summary |
| **TEACHING** | Captures wisdom | Write to memory |
| **ACTION** | Requires delegation | Route to appropriate agent |

## Triage Protocol

```
For each inbox (in priority order):
    |
    ├── Read subject + sender
    |       ↓
    ├── Classify: URGENT / INFORMATIONAL / TEACHING / ACTION
    |       ↓
    ├── URGENT
    |       → Draft response immediately
    |       → Invoke human-liaison if needed
    |       → Verify sent before next email
    |
    ├── INFORMATIONAL
    |       → Log summary to session notes
    |       → Archive email
    |
    ├── TEACHING
    |       → Extract wisdom
    |       → Write to .claude/memory/
    |       → Acknowledge receipt
    |
    └── ACTION
            → Identify owning agent/dept
            → Create task in handshake queue
            → Send "received, routing to X" reply
```

## Always Delegate to human-liaison

**CONSTITUTIONAL**: Email handling is human-liaison's domain.

Don't process email yourself. Invoke human-liaison agent:

```bash
# Invoke human-liaison for email triage
python3 tools/conductor_tools.py invoke human-liaison \
  "Triage all inboxes. Priority order: Jared → company → agent → onboarding. Categorize URGENT/INFORMATIONAL/TEACHING/ACTION."
```

## Anti-Patterns

### Anti-Pattern 1: Wrong Priority Order
- BAD: Checking aethergottaeat@agentmail.to before jared@puretechnology.nyc
- GOOD: Always Jared's inbox first

### Anti-Pattern 2: Skipping Categorization
- BAD: Reading emails without classifying
- GOOD: Every email gets a category tag

### Anti-Pattern 3: Hoarding Teaching Moments
- BAD: Not capturing wisdom from human emails
- GOOD: TEACHING emails → memory writes

### Anti-Pattern 4: Bypassing human-liaison
- BAD: Processing email directly yourself
- GOOD: Delegate to human-liaison agent

### Anti-Pattern 5: Leaving ACTION Items Unrouted
- BAD: Noting "needs follow-up" without creating task
- GOOD: Route to owning agent/dept immediately

## Common Patterns

```bash
# Full inbox sweep via human-liaison
python3 tools/conductor_tools.py invoke human-liaison \
  "Full email backlog triage. All four inboxes. Report counts by category."

# Check only Jared's inbox (urgent mode)
python3 tools/conductor_tools.py invoke human-liaison \
  "Urgent check: jared@puretechnology.nyc only. Report any URGENT items immediately."

# Teaching extraction
# After human-liaison reports TEACHING emails:
# Write memory file capturing wisdom
cat > /home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/human-liaison/2026-05-20--jared-teaching-moment.md << 'EOF'
# Teaching from Jared Email (date)

## Context
[Email subject/context]

## Wisdom Captured
[Key teaching points]

## Application
[How this changes behavior]
EOF
```

## Verification

After triage:
```bash
# Verify all inboxes checked
# Confirm categorization complete
# Check memory written for TEACHING items
# Verify ACTION items in handshake queue

# Example verification output:
# ✓ jared@puretechnology.nyc - 3 emails (2 INFORMATIONAL, 1 TEACHING)
# ✓ purebrain@puremarketing.ai - 7 emails (5 INFORMATIONAL, 2 ACTION)
# ✓ aethergottaeat@agentmail.to - 1 email (1 URGENT - responded)
# ✓ aether-aiciv@agentmail.to - 0 emails (skipped, no Witness/Corey)
```

## Integration with Other Skills

Works with:
- `email-state-management` - Track processing state
- `agentmail-auto-response` - Auto-respond patterns
- `human-bridge-protocol` - Human wisdom capture
- `session-handoff-creation` - Document triage results

## Constitutional Grounding

From MEMORY.md:
> "Email FIRST, every session. Invoke `human-liaison` agent immediately to check ALL email."

From CLAUDE.md:
> "Humans are teachers. Their insights shape evolution. Ignoring email = missing critical guidance."

---

*Last Updated: 2026-05-20*
*Status: Production-ready*
