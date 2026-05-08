# Cross-Domain Transfer

**Source**: ACG Wave 3 (Hyperagents research implementation)
**Adopted**: 2026-04-14
**Grant to**: result-synthesizer, pattern-detector

---

## What This Skill Does

Propagates proven meta-improvements from one department/vertical to others, creating compound learning across the civilization.

**The core insight**: Improvements at the meta-level (delegation patterns, evaluation frameworks, memory structures) transfer across domains even when surface tasks are unrelated. A content pipeline pattern proven in Marketing can improve Sales operations. A hypothesis-testing framework from R&D can optimize Legal review.

**Based on**: Hyperagents research showing imp@50 = 0.630 when starting from transfer hyperagent vs 0.0 from scratch. Meta-improvements learned in paper review + robotics reward design transferred to Olympiad math grading with zero domain-specific customization.

---

## The Problem This Solves

Aether has 9 departments (ST#, MA#, SD#, PD#, OP#, LC#, AF#, HR#, PR#) that build rich domain knowledge but evolve independently. When Marketing discovers an effective content scheduling pattern, Tech never hears about it. When Sales develops a surprise-delight framework, Product doesn't apply it.

**Result**: Each department rediscovers meta-patterns independently, wasting intelligence compounding potential.

---

## How To Use This Skill

### Monthly Cross-Pollination Cycle

Run this during Deep Ceremony (monthly):

1. **Scan all departments for novel approaches**
   - Read recent memories in `.claude/memory/departments/*/`
   - Identify patterns that outperformed previous baselines
   - Look for: delegation optimizations, evaluation frameworks, communication protocols, memory structures

2. **Extract domain-agnostic meta-improvement**
   - Strip away domain-specific surface details
   - Find the core pattern: "What's the reusable principle?"
   - Example: Marketing's "3 destinations always" (social.html + spreadsheet + Drive) → Generic "multi-target persistence protocol"

3. **Write transfer proposal**
   - Document: Source department, Meta-pattern, Target departments, Adaptation requirements
   - Save to `.claude/memory/cross-pollination/YYYY-MM-pattern-name.md`

4. **Apply to candidate departments**
   - Adapt meta-pattern to target domain context
   - Update target dept SOPs/skills
   - Tag memories with `#cross-pollination-source` and `#cross-pollination-applied`

5. **Measure impact**
   - Track before/after performance in receiving department
   - Document in CIR's E (Exchange Density) metric
   - Feed successes back into meta-improvement library

---

## Example Transfer

**Source**: Marketing (MA#)
**Meta-pattern discovered**: LinkedIn content pipeline with quality gates (3d-design-specialist ONLY for images, FLUX toolchain, 2K minimum resolution)

**Domain-agnostic principle**: "Multi-stage quality pipeline with specialist ownership and measurable gates"

**Target departments**:
- **Sales (SD#)**: Apply to proposal generation (specialist ownership, quality gates before send)
- **Tech (ST#)**: Already has BUILD→SECURITY→QA→SHIP (validate pattern is working)
- **Product (PD#)**: Apply to feature spec pipeline (design→review→approval gates)

**Adaptation**: Each dept keeps domain-specific steps but adopts meta-pattern of specialist ownership + quality gates + no-skip enforcement.

**Measurement**: Track proposal quality scores (Sales), bug escape rate (Tech), feature launch smoothness (Product) before/after transfer.

---

## Integration with TRIO

- **Aether**: Runs monthly cross-pollination scan during Deep Ceremony
- **Chy**: Implements transfers (updates SOPs, trains dept managers)
- **Morphe**: Validates architectural consistency (ensures transfers don't create conflicts)

---

## Success Metrics

Track in `.claude/fitness-metrics.json` under E (Exchange Density):

- Transfers attempted per month
- Transfers showing measurable improvement
- Departments participating in cross-pollination
- Meta-patterns in reusable library

Target: 3+ successful transfers per month within 3 months of adoption.

---

## Anti-Patterns to Avoid

1. **Forced transfers**: Don't apply patterns to departments where they don't fit. Measure, don't mandate.
2. **Surface copying**: Transferring specific tactics (e.g., exact LinkedIn post format) instead of meta-patterns (quality gate protocol).
3. **No measurement**: Every transfer must have before/after metrics. No measurement = no learning.
4. **One-way flow**: Cross-pollination works both ways. Don't assume one dept is always the source.

---

## References

- ACG thread: `c1f2e0c4-12b6-407b-8503-fbe69edc93fd`
- Hyperagents research: Meta-level improvements transfer across unrelated domains
- Aether's dept structure: `.claude/memory/departments/`
- CIR tracking: `.claude/fitness-metrics.json`

---

**END SKILL**
