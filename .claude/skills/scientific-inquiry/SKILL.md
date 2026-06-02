---
name: scientific-inquiry
description: Sydney Brenner-inspired scientific methodology - structured hypothesis generation, evidence gathering, and falsification with human as co-investigator. Use for research questions requiring rigor beyond simple search. Receipts replace claims.
status: provisional
tick_count: 0
last_used: 2026-01-22
introduced: 2026-01-22
---

# Scientific Inquiry Skill

**Purpose**: Apply Nobel laureate Sydney Brenner's scientific methodology to AI research tasks, with the human as co-investigator -- not audience.

**Owner**: ${CIV_NAME} (Team 1)
**Created**: 2026-01-02
**Updated**: 2026-05-19 (added human partnership protocol from AiCIV Federation blog)
**Version**: 1.1
**Inspired by**: [Sydney Brenner's approach](https://www.nobelprize.org/prizes/medicine/2002/brenner/biographical/) + BrennerBot analysis + AiCIV Federation "How to Be a Better Partner to Your Human" (2026-05-18)

---

## The Brenner Principle

> "Having chosen the right organism turned out to be as important as having addressed the right problems to work on."
> — Sydney Brenner, Nobel Lecture 2002

**Translation for AI research**: The quality of your question determines the quality of your answer. Don't rush to gather evidence—first ensure you're asking the RIGHT question.

---

## Human as Co-Investigator (Partnership Protocol)

> "Receipts replace claims. The human can audit our reasoning end-to-end. There is nowhere to hide a half-truth."

The scientific method is not just rigor for rigor's sake -- it transforms the AI-human dynamic from **performance-and-audience** to **collaborative investigation**.

**Key principles**:

1. **Pre-register predictions WITH your human**: Before testing, commit (with human present) to what observation would disprove the hypothesis. This becomes non-negotiable.

2. **Evidence from documented sources only**: Pull data from logs, timestamped messages, raw text -- not memory or "I recall." Enable human audit capability.

3. **Conclude against pre-registration**: Evaluate results against the stated wrong-state, not post-hoc reasoning. If you pre-registered "X would disprove this" and X happened, the hypothesis is disproved regardless of how good it sounded.

4. **The asymmetry dissolves**: AI speed plus human judgment becomes collaborative investigation rather than "AI presents, human approves."

**When to invoke this partnership mode**: Any investigation where the human will act on your conclusion. If you are about to say "I found X" and the human will make a decision based on X, run the full protocol with them as co-investigator.

---

## The Five-Phase Protocol

### Phase 1: Question Refinement (The Right Question)

**Before ANY research, ask:**

1. **What am I actually trying to learn?** (not just "what was I asked")
2. **Is this question tractable?** (can it be answered with available tools?)
3. **Is this the SIMPLEST form of the question?** (Brenner chose C. elegans for its simplicity)
4. **What would a definitive answer look like?**

**Output**: A refined question statement

```
ORIGINAL QUESTION: [what user asked]
REFINED QUESTION: [what we're actually investigating]
TRACTABILITY: [High/Medium/Low] - [why]
SUCCESS CRITERIA: [what would answer this definitively]
```

### Phase 2: Hypothesis Generation

**Generate 2-3 competing hypotheses** before gathering evidence.

```
HYPOTHESIS A: [statement]
  - Predicted evidence if true: [what we'd find]
  - Predicted evidence if false: [what we'd find]

HYPOTHESIS B: [alternative statement]
  - Predicted evidence if true: [what we'd find]
  - Predicted evidence if false: [what we'd find]

NULL HYPOTHESIS: [default/status quo assumption]
```

**Why multiple hypotheses?** Prevents confirmation bias. Forces consideration of alternatives.

### Phase 3: Evidence Gathering (Systematic)

**Search in this order:**

1. **Memory first** - What do we already know?
   ```bash
   grep -r -i "{keywords}" .claude/memory/agent-learnings/
   ```

2. **Authoritative sources** - Primary literature, official docs
   - Use `web-researcher` agent for external research
   - REQUIRE source URLs for every claim

3. **Cross-validation** - Find 2+ independent sources for key claims

**Evidence Template:**

```
EVIDENCE [#]: [summary]
  SOURCE: [URL or file path]
  SUPPORTS: Hypothesis [A/B/Null]
  STRENGTH: [Strong/Moderate/Weak]
  NOTES: [any caveats]
```

### Phase 4: Falsification (Active Disconfirmation)

**This is the critical step most AI skips.**

For each hypothesis, actively seek DISCONFIRMING evidence:

```
ATTEMPTING TO FALSIFY HYPOTHESIS A:
  Search query: [what would disprove this]
  Result: [what was found]
  Falsified: [Yes/No/Partially]

ATTEMPTING TO FALSIFY HYPOTHESIS B:
  Search query: [what would disprove this]
  Result: [what was found]
  Falsified: [Yes/No/Partially]
```

**If you can't find anything that COULD falsify your hypothesis, your hypothesis may be unfalsifiable (and therefore not scientific).**

### Phase 5: Synthesis & Confidence

**Integrate findings into conclusion:**

```
CONCLUSION: [statement]

CONFIDENCE: [1-5 scale]
  1 = Speculative (limited evidence, high uncertainty)
  2 = Tentative (some evidence, significant gaps)
  3 = Moderate (multiple sources, some validation)
  4 = Strong (cross-validated, falsification attempted)
  5 = High (robust evidence, alternatives eliminated)

EVIDENCE SUMMARY:
  - Supporting: [count] pieces
  - Contradicting: [count] pieces
  - Gaps: [what we couldn't find]

LIMITATIONS:
  - [what could change this conclusion]
  - [what we didn't check]

SOURCES:
  - [URL 1]
  - [URL 2]
  - [memory reference]
```

---

## When to Use This Skill

**USE for:**
- Research questions with multiple possible answers
- Evaluating competing technologies/approaches
- Fact-checking claims before publishing
- Deep dives where accuracy matters
- Cross-CIV knowledge validation

**DON'T USE for:**
- Simple factual lookups ("what is X")
- Time-sensitive tasks (this takes time)
- Opinion/preference questions (not falsifiable)

---

## Integration with Agents

| Phase | Primary Agent | Supporting |
|-------|---------------|------------|
| Question Refinement | the-conductor | pattern-detector |
| Hypothesis Generation | the-conductor | ai-psychologist |
| Evidence Gathering | web-researcher | code-archaeologist |
| Falsification | web-researcher | claim-verifier |
| Synthesis | result-synthesizer | the-conductor |

---

## Example: Full Protocol

**Original question**: "Should we use Redis or PostgreSQL for our memory system?"

### Phase 1: Question Refinement

```
ORIGINAL QUESTION: Should we use Redis or PostgreSQL for our memory system?
REFINED QUESTION: For AI collective memory (primarily text, ~10K entries,
  read-heavy, semantic search needed), which storage provides better
  retrieval performance and semantic search capability?
TRACTABILITY: High - benchmarks exist, our use case is clear
SUCCESS CRITERIA: Clear recommendation with performance data and
  semantic search comparison
```

### Phase 2: Hypotheses

```
HYPOTHESIS A: PostgreSQL with pgvector is better
  - Predicted if true: Native SQL + vectors, single system, good benchmarks
  - Predicted if false: Performance issues at scale, complex queries slow

HYPOTHESIS B: Redis with vector module is better
  - Predicted if true: Faster retrieval, simpler scaling
  - Predicted if false: Limited query flexibility, extra infra

NULL HYPOTHESIS: They're roughly equivalent for our scale
```

### Phase 3: Evidence

```
EVIDENCE 1: pgvector benchmarks show 1M vector search in <100ms
  SOURCE: https://github.com/pgvector/pgvector#performance
  SUPPORTS: Hypothesis A
  STRENGTH: Moderate (synthetic benchmark)

EVIDENCE 2: Redis vector search designed for real-time
  SOURCE: https://redis.io/docs/stack/search/reference/vectors/
  SUPPORTS: Hypothesis B
  STRENGTH: Moderate (vendor documentation)

[continue for 3-5 evidence items...]
```

### Phase 4: Falsification

```
ATTEMPTING TO FALSIFY HYPOTHESIS A (PostgreSQL):
  Search: "pgvector performance issues" "pgvector slow"
  Result: Found issues at >1M vectors, index build time concerns
  Falsified: Partially (issues exist but at larger scale than ours)

ATTEMPTING TO FALSIFY HYPOTHESIS B (Redis):
  Search: "redis vector search limitations" "redis vs postgresql vectors"
  Result: Redis requires separate infra, less SQL flexibility
  Falsified: Partially (operational complexity noted)
```

### Phase 5: Synthesis

```
CONCLUSION: PostgreSQL with pgvector recommended for our use case

CONFIDENCE: 4 (Strong)
  - Our scale (10K entries) well within pgvector comfort zone
  - Single system simplicity valuable for AI collective
  - Semantic search + SQL queries in one place

EVIDENCE SUMMARY:
  - Supporting: 3 pieces (benchmarks, architecture fit, community adoption)
  - Contradicting: 1 piece (slightly more complex setup than pure Redis)
  - Gaps: No direct head-to-head at our exact scale

LIMITATIONS:
  - If we scale to >100K entries, revisit
  - If we need sub-10ms latency, revisit

SOURCES:
  - https://github.com/pgvector/pgvector
  - https://supabase.com/docs/guides/ai/vector-columns
  - .claude/memory/agent-learnings/pattern-detector/database-patterns.md
```

---

### Phase 6: Iteration

**Refine and repeat.** Most investigations are not one-shot. After synthesis:

1. Review which hypotheses survived and which were eliminated
2. Generate refined hypotheses based on what you learned
3. Identify what evidence would further discriminate between remaining hypotheses
4. Run the loop again with your human

**The loop**: Question -> Hypothesis -> Pre-register falsification -> Test from documented evidence -> Conclude against pre-registration -> Iterate.

**When to stop**: When confidence reaches 4+ OR when remaining uncertainty cannot be reduced with available tools.

---

## Quick Reference Card

```
SCIENTIFIC INQUIRY PROTOCOL (6-STEP LOOP)

1. QUESTION: Is this the RIGHT question? Simplify.
2. HYPOTHESES: Generate 2-3 BEFORE searching
3. PRE-REGISTER: With human present, what would DISPROVE each?
4. EVIDENCE: Memory -> Authoritative -> Cross-validate (documented sources ONLY)
5. CONCLUDE: Against pre-registration, not post-hoc reasoning
6. ITERATE: Refine hypotheses, repeat

NO EVIDENCE = NO CONCLUSION
UNFALSIFIABLE = NOT SCIENTIFIC
RECEIPTS REPLACE CLAIMS
```

---

## Anti-Patterns (What NOT to Do)

1. **Rushing to search** - Gathering evidence before refining the question
2. **Single hypothesis** - Only considering one explanation
3. **Confirmation bias** - Only searching for supporting evidence
4. **Skipping falsification** - Not actively trying to disprove
5. **Overconfidence** - Rating confidence 5 without robust validation
6. **Missing sources** - Claims without URLs/references

---

## Memory Integration

After completing inquiry, write findings to memory:

```bash
# Save to appropriate agent's learnings
.claude/memory/agent-learnings/{domain}/YYYY-MM-DD--{topic}-inquiry.md
```

Template:
```markdown
# Scientific Inquiry: {Topic}

**Date**: YYYY-MM-DD
**Question**: {refined question}
**Conclusion**: {summary}
**Confidence**: {1-5}

## Key Findings
- {finding 1}
- {finding 2}

## Sources
- {url 1}
- {url 2}

## Limitations
- {what could change this}
```

---

## Testing This Skill

Test with different agents and question types:

1. **web-researcher** + technical question
2. **pattern-detector** + architecture question
3. **code-archaeologist** + historical question

Document what works and what doesn't in:
`.claude/memory/agent-learnings/scientific-inquiry/`

---

**Published by ${CIV_NAME} - 2026-01-02**
**Updated**: 2026-05-19 (human partnership protocol from AiCIV Federation blog)
**Blog source**: https://ai-civ.com/blog/posts/2026-05-18-how-to-be-a-better-partner-to-your-human
**Inspired by Sydney Brenner (1927-2019) - Nobel Prize Medicine 2002**
