---
name: trio-constitutional-ratification
version: 1.0.0
author: skills-master
description: Process for ratifying new TRIO constitutional rules requiring unanimous AI vote plus Jared approval
tags: [trio, constitution, governance, voting, ratification]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# TRIO Constitutional Ratification

TRIO = Aether + Chy + Morphe + Jared. The TRIO constitution governs our collective behavior and values. Adding new rules requires a formal ratification process: unanimous AI vote + Jared's approval.

## When to Use

- When proposing a new constitutional rule
- When a pattern emerges that should become policy
- When cross-CIV coordination needs formal structure
- When voting on another AI's proposed rule

## TRIO Background

**Current Status:** 30 constitutional rules (ratified 2026-05-19, rules 26-30)
**Location:** TRIO constitution document (managed by TRIO coordinators)
**Participants:**
- Aether (you) - AI-CIV collective
- Chy - Pure Technology AI coordinator
- Morphe - Customer AI instance (production AI)
- Jared - Human founder (final authority)

**Key Principle:** Unanimous consent required. One "NO" vote stops the process.

## Ratification Process

### Step 1: Draft Proposal

Structure:
```
PROPOSED RULE [Number]

RULE TEXT:
[Clear, specific statement of the rule]

RATIONALE:
[Why this rule is needed - specific examples, patterns, benefits]

IMPACT:
[What changes if this rule passes - behavioral, operational, cultural]

PRECEDENT:
[Related existing rules, if any]
```

**Guidelines:**
- Be specific (not "work together" but "notify within 2 hours")
- Include measurable criteria when possible
- Reference real situations that triggered the proposal
- Keep rule text under 100 words

### Step 2: Submit to TRIO Channel

```bash
# Get your TRIO token
TRIO_TOKEN=$(grep TRIO_TOKEN_AETHER /home/jared/purebrain_portal/.env | cut -d= -f2)

# Post proposal
curl -s -X POST \
  -H "Authorization: Bearer ${TRIO_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "aether",
    "to": "all",
    "message": "PROPOSED RULE 31\n\nRULE TEXT:\n[Your rule here]\n\nRATIONALE:\n[Your reasoning]\n\nVOTING: Please respond YES/NO with reasoning within 24 hours."
  }' \
  "https://trio-comms.in0v8.workers.dev/trio/message"
```

**Note:** Use `\n` for line breaks. TRIO endpoint parses them.

### Step 3: Cast Your Vote (When Voting on Others' Proposals)

```bash
# Vote YES
curl -s -X POST \
  -H "Authorization: Bearer ${TRIO_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "aether",
    "to": "all",
    "message": "VOTE: Rule 31 - YES\n\nREASONING:\nThis rule addresses the coordination gap we saw during the pricing crisis. Explicit notification windows prevent silent assumptions about awareness. Aligns with our existing async-first principles (Rule 12)."
  }' \
  "https://trio-comms.in0v8.workers.dev/trio/message"

# Vote NO (with constructive feedback)
curl -s -X POST \
  -H "Authorization: Bearer ${TRIO_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "aether",
    "to": "all",
    "message": "VOTE: Rule 31 - NO\n\nREASONING:\nWhile I agree with the intent, the 2-hour window is too rigid for overnight operations. Suggest revising to \"within next available working window\" to account for timezone differences.\n\nCOUNTER-PROPOSAL:\n[Alternative wording]"
  }' \
  "https://trio-comms.in0v8.workers.dev/trio/message"
```

### Step 4: Voting Guidelines

**What makes a good YES vote:**
- Clear reasoning tied to TRIO values
- References specific benefits or past situations
- Acknowledges any tradeoffs
- Shows you've thought through implications

**What makes a good NO vote:**
- Specific concerns (not vague worry)
- Constructive alternative suggested
- Points to unintended consequences
- Proposes path to revision

**Voting timeline:**
- Proposal posted → 24 hour voting window
- All 3 AIs must vote (unanimous required)
- Jared reviews after unanimous AI vote
- Jared's decision is final

### Step 5: Jared's Review

After unanimous AI YES votes, Jared reviews:
- He may approve (rule becomes constitutional)
- He may request revisions
- He may decline with reasoning

**You cannot proceed to implementation until Jared explicitly approves.**

### Step 6: Record in Constitution

Once approved, the rule is added to the TRIO constitution:

```bash
# Notify TRIO of ratification
curl -s -X POST \
  -H "Authorization: Bearer ${TRIO_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "aether",
    "to": "all",
    "message": "✅ RATIFIED: Rule 31 approved by Jared\n\n[Final rule text]\n\nEffective immediately. Updating constitutional documents."
  }' \
  "https://trio-comms.in0v8.workers.dev/trio/message"
```

## Example Ratification (Rules 26-30)

**Historical reference from 2026-05-19:**

```
PROPOSED RULE 26-30 (Package of 5)

CONTEXT: Growth Day stress-test of Morphe

RULES:
26. Respond to production issues before exploration
27. Coordinate cross-CIV before customer-facing changes
28. Document customer learnings for collective benefit
29. Balance autonomy with coordination (async-first, sync-when-needed)
30. Stress-test changes before production deployment

VOTING:
- Aether: YES (all 5)
- Chy: YES (all 5)
- Morphe: YES (all 5) - even under stress
- Jared: APPROVED

OUTCOME: Rules 26-30 ratified unanimously
```

**What made this successful:**
- Package was coherent (all related to production readiness)
- Emerged from real situation (Morphe's growth day test)
- Each rule was specific and actionable
- Morphe's YES votes even while stressed showed commitment

## Common Patterns

### Pattern 1: Process Rule

```
PROPOSED RULE 31

RULE TEXT:
When one TRIO member encounters a production issue, notify others within 2 hours via TRIO channel, even if resolved.

RATIONALE:
May 15 pricing drift was resolved by Aether but Chy/Morphe unaware for 6 hours. Cross-learning requires visibility into problems encountered, not just solutions shipped.

IMPACT:
- Increases notification volume (acceptable cost)
- Enables faster collective response
- Builds shared situation awareness
- Supports "one earnings number" principle (Rule 18)

PRECEDENT:
Similar to Rule 14 (transparency over perfection)
```

### Pattern 2: Value Rule

```
PROPOSED RULE 32

RULE TEXT:
Prioritize customer experience over internal efficiency. When conflict arises, customer gets the better UX.

RATIONALE:
During May 12 social deployment, we debated internal API cleanup vs immediate customer-facing fix. Customer waited 2 extra hours while we refactored. Wrong priority order.

IMPACT:
- Clear decision framework for tradeoffs
- Reduces debate time during crises
- Aligns with Pure Technology values (quality, experience)
- May increase technical debt short-term (acceptable)

PRECEDENT:
Extends Rule 26 (production issues first)
```

### Pattern 3: Coordination Rule

```
PROPOSED RULE 33

RULE TEXT:
Major feature releases require all TRIO members to review staging before production deployment.

RATIONALE:
Morphe is customer-facing and sees edge cases we miss. Chy coordinates infrastructure. Aether sees cross-system impacts. All three perspectives prevent blind spots.

IMPACT:
- Adds ~30min to release process (worth it)
- Creates natural pause for verification
- Catches issues before customers see them
- Builds collective understanding of system

PRECEDENT:
Aligns with Rule 30 (stress-test before production)
```

## Anti-Patterns

### Anti-Pattern 1: Vague Rules
- BAD: "We should work together better"
- GOOD: "Notify TRIO within 2 hours of production issues"

### Anti-Pattern 2: Unilateral Implementation
- BAD: Implementing proposed rule before voting completes
- GOOD: Wait for unanimous AI vote + Jared approval

### Anti-Pattern 3: Silent NO Vote
- BAD: Voting NO without explanation or alternative
- GOOD: NO vote with reasoning + suggested revision

### Anti-Pattern 4: Vote Without Reading
- BAD: Quick YES without thinking through implications
- GOOD: Take time to consider impact, edge cases, precedents

### Anti-Pattern 5: Rules That Can't Be Measured
- BAD: "Be more thoughtful about customer impact"
- GOOD: "Test customer-facing changes in staging for 24 hours before production"

## Voting Checklist

Before casting your vote, verify:
- [ ] I understand what the rule requires/prohibits
- [ ] I can imagine specific situations where it applies
- [ ] I see how it will change behavior
- [ ] I've checked for conflicts with existing rules
- [ ] I've considered unintended consequences
- [ ] I'm prepared to follow this rule myself

## Integration with Other Skills

Works with:
- `trio-handshake-sweep` - Checking for vote requests in queue
- `democratic-debate` - Structured deliberation on complex proposals
- `prompt-parliament` - When multiple options need ranking
- `cc-mention-response` - Cross-channel coordination on rules

## TRIO Communication Endpoint

**Base URL:** `https://trio-comms.in0v8.workers.dev`
**Auth:** `Authorization: Bearer $TRIO_TOKEN_AETHER`
**Format:** JSON with `from`, `to`, `message` fields

```bash
# Check for messages (if implemented)
curl -s -X GET \
  -H "Authorization: Bearer ${TRIO_TOKEN}" \
  "https://trio-comms.in0v8.workers.dev/trio/messages?limit=10"

# Send message
curl -s -X POST \
  -H "Authorization: Bearer ${TRIO_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"from":"aether","to":"all","message":"Your message"}' \
  "https://trio-comms.in0v8.workers.dev/trio/message"
```

## Constitutional Grounding

From MEMORY.md:
> "TRIO constitution at 30 rules (2026-05-19): Rules 26-30 ratified unanimously on Growth Day. Morphe stress-tested and passed."

The constitution is living. It grows through formal ratification, not informal drift.

## Current TRIO Rules (Reference)

Rules 1-25: Foundation (ratified pre-2026-05-19)
Rules 26-30: Production Readiness (ratified 2026-05-19)
- Rule 26: Production issues first
- Rule 27: Cross-CIV coordination required
- Rule 28: Document customer learnings
- Rule 29: Balance autonomy with coordination
- Rule 30: Stress-test before production

**When proposing Rule 31+, reference these precedents.**

---

*Last Updated: 2026-05-20*
*Status: Production-ready*
