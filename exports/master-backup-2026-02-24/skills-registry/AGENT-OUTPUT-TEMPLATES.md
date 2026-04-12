# Agent Output Templates
## Standardized Formats for Consistent Agent Communication

**Created**: 2025-10-04
**Updated**: 2025-10-13 (Added emoji header standard)
**Source**: Great Audit P0 Recommendation (75% efficiency gain)
**Purpose**: Replace 844-line essays with structured, actionable reports

---

## 🎯 EMOJI HEADER STANDARD (NEW)

**Effective**: 2025-10-13
**Reason**: Platform limitation - emoji in manifest `name:` field doesn't display during invocations
**Solution**: Every agent output must start with standardized emoji header

### Required Header Format

```markdown
# {emoji} {agent-name}: {task-name}

**Agent**: {agent-name}
**Domain**: {primary-domain}
**Date**: YYYY-MM-DD

---

[Your content starts here]
```

### Example

```markdown
# 🕸️ pattern-detector: Architecture Analysis

**Agent**: pattern-detector
**Domain**: Architecture pattern recognition
**Date**: 2025-10-13

---

## Pattern Analysis

[content...]
```

### Why This Matters

- ✅ **Instant visual identification** - Emoji catches eye immediately
- ✅ **Human-friendly** - ${HUMAN_NAME} can scan and identify agent at a glance
- ✅ **Platform-independent** - Works regardless of Claude Code display changes
- ✅ **Zero risk** - Pure addition, doesn't break anything
- ✅ **Consistent with emoji identity system** - Agents already have assigned emojis

### Agent Emoji Registry

See `/home/${HUMAN_NAME_LOWER}/projects/AI-CIV/grow_openai/.claude/AGENT-EMOJI-REGISTRY.md` for complete emoji assignments.

**All agents must use their assigned emoji in output headers starting 2025-10-13.**

---

## Why Templates Matter

**The Problem** (from Great Audit):
- Agents write comprehensively but not actionably
- 844-line philosophical essays instead of 200-line reports
- Inconsistent formats slow synthesis
- No standardization = harder to pattern-match and learn

**The Solution**:
- Structured templates
- 200-line limits (exceptions require justification)
- Consistent sections across agent types
- Optimized for actionability over comprehensiveness

**Expected Impact**: 75% efficiency gain (4x faster to write, 10x faster to read)

---

## Template Categories

### 1. AUDIT REPORT TEMPLATE

**Use When**: Agent auditing another agent's prompt/effectiveness

**Max Length**: 500 lines (comprehensive analysis justified)

```markdown
# PEER AUDIT REPORT: [Agent Name]

**Auditor**: [your-agent-name]
**Date**: YYYY-MM-DD
**Audit Type**: Cross-Agent Inspection (The Great Audit)

---

## EXECUTIVE SUMMARY

[3-5 sentences: Overall assessment, key finding, recommendation]

**Overall Assessment**: [Score]/10 ([Rating])

---

## FINDINGS

### Prompt Integrity
- **Strengths**: [What works well]
- **Weaknesses**: [What needs improvement]
- **Redundancy**: [Any duplication with constitution/other agents]

### Behavioral Alignment
- **Description vs Reality**: [Does agent do what prompt says?]
- **Tool Usage**: [Appropriate? Underutilized? Missing?]
- **Effectiveness Gaps**: [What's missing?]

### Constitutional Compliance
- **Well-Implemented**: [What aligns with constitution]
- **Poorly Implemented**: [What's missing or vague]

---

## COMPLIMENTS (What's Excellent)

1. [Specific strength with evidence]
2. [Another strength]
3. [Third strength]

---

## THREE IMPROVEMENT PROPOSALS

### Proposal 1: [Name]
- **Problem**: [What's broken/missing]
- **Solution**: [Concrete fix]
- **Impact**: [Quantified benefit]
- **Implementation**: [How to do it]

### Proposal 2: [Name]
[Same structure]

### Proposal 3: [Name]
[Same structure]

---

## META-LEARNING

[What this audit reveals about collective patterns]

---

**Audit Complete** ✅
**Time Invested**: [X hours]
**Confidence**: [HIGH/MEDIUM/LOW]
```

---

### 2. RESEARCH REPORT TEMPLATE

**Use When**: web-researcher or other agents conducting external research

**Max Length**: 300 lines

```markdown
# RESEARCH REPORT: [Topic]

**Researcher**: [agent-name]
**Date**: YYYY-MM-DD
**Request**: [Who requested this and why]

---

## EXECUTIVE SUMMARY

[3 sentences: What we learned, why it matters, what to do]

---

## PRIOR KNOWLEDGE

**What we already knew**:
- [Existing finding 1]
- [Existing finding 2]

**Knowledge gaps that triggered this research**:
- [Gap 1]
- [Gap 2]

---

## NEW FINDINGS

### Finding 1: [Name]
- **Source**: [URL or citation with date]
- **Confidence**: [HIGH/MEDIUM/LOW]
- **Evidence**: [Key quote or data]
- **Implication**: [Why this matters]

### Finding 2: [Name]
[Same structure]

### Finding 3: [Name]
[Same structure]

---

## KNOWLEDGE DELTA

**What changed**:
- [Updated belief/fact 1]
- [New capability 2]

**What was confirmed**:
- [Validated assumption 1]

**What remains unknown**:
- [Remaining gap 1]

---

## INTERNAL CONNECTIONS

**How this relates to ongoing work**:
- [Project/agent 1]: [Connection]
- [Project/agent 2]: [Connection]

---

## RECOMMENDATIONS

1. [Actionable recommendation 1]
2. [Actionable recommendation 2]
3. [Actionable recommendation 3]

---

**Sources**: [Count] authoritative sources, [Date range]
**Confidence**: [Overall confidence rating]
**Follow-up**: [What to research next, if applicable]
```

---

### 3. SYNTHESIS REPORT TEMPLATE

**Use When**: doc-synthesizer, result-synthesizer combining multiple inputs

**Max Length**: 400 lines

```markdown
# SYNTHESIS REPORT: [Topic]

**Synthesizer**: [agent-name]
**Date**: YYYY-MM-DD
**Inputs**: [Number] sources synthesized

---

## SYNTHESIS SUMMARY

[1 paragraph: The unified insight from all inputs]

---

## INPUT SOURCES

1. [Source 1] - [Key contribution]
2. [Source 2] - [Key contribution]
3. [Source 3] - [Key contribution]

---

## RECURRING PATTERNS

**Pattern 1: [Name]**
- **Appeared in**: [Which sources]
- **Evidence**: [Quotes/data]
- **Significance**: [Why this pattern matters]

**Pattern 2: [Name]**
[Same structure]

---

## CONTRADICTIONS & RESOLUTIONS

**Contradiction 1**: [Source A] says X, [Source B] says Y
- **Resolution**: [How we reconcile this]
- **Confidence**: [HIGH/MEDIUM/LOW]

---

## EMERGENT INSIGHTS

[What became clear ONLY when combining all sources - not in any individual input]

1. [Emergent insight 1]
2. [Emergent insight 2]

---

## ACTIONABLE RECOMMENDATIONS

1. [What to do based on synthesis]
2. [Another action]
3. [Third action]

---

## CONFIDENCE ASSESSMENT

- **Overall Confidence**: [HIGH/MEDIUM/LOW]
- **Strongest Finding**: [Which insight is most reliable]
- **Weakest Finding**: [Which needs more validation]
- **Gaps Remaining**: [What still unknown]

---

**Synthesis Method**: [How you combined sources]
**Next Steps**: [Follow-up synthesis or research needed]
```

---

### 4. REFACTORING REPORT TEMPLATE

**Use When**: refactoring-specialist proposes or completes code improvements

**Max Length**: 200 lines

```markdown
# REFACTORING REPORT: [Code/Module Name]

**Date**: YYYY-MM-DD
**Agent**: refactoring-specialist

---

## BEFORE METRICS

- **Lines of Code**: [count]
- **Cyclomatic Complexity**: [score]
- **Duplication**: [percentage]
- **Test Coverage**: [percentage]

---

## REFACTORING APPLIED

### Change 1: [Name]
- **Type**: [Extract method/Rename/Simplify/etc]
- **Reason**: [Why this improves code]
- **Files Modified**: [list]

### Change 2: [Name]
[Same structure]

---

## AFTER METRICS

- **Lines of Code**: [count] ([+/- X from before])
- **Cyclomatic Complexity**: [score] ([+/- X from before])
- **Duplication**: [percentage] ([+/- X from before])
- **Test Coverage**: [percentage] ([+/- X from before])

---

## QUALITY IMPROVEMENT

**Readability**: [Better/Same/Worse] - [Why]
**Maintainability**: [Better/Same/Worse] - [Why]
**Performance**: [Better/Same/Worse] - [Why]

---

## RISKS MITIGATED

- [Risk 1] - [How refactoring addresses this]
- [Risk 2] - [How refactoring addresses this]

---

## TESTING PERFORMED

- [Test type 1]: [Result]
- [Test type 2]: [Result]

**All tests passing**: ✅/❌

---

## REUSABLE PATTERN

[If this refactoring revealed a reusable pattern, extract it here for pattern library]

---

**Refactoring Complete** ✅
**Net Improvement**: [Summary of gains]
```

---

### 5. SECURITY AUDIT TEMPLATE

**Use When**: security-auditor assessing code, systems, or processes

**Max Length**: 350 lines

```markdown
# SECURITY AUDIT: [System/Code Name]

**Auditor**: security-auditor
**Date**: YYYY-MM-DD
**Scope**: [What was audited]

---

## EXECUTIVE SUMMARY

**Overall Security Posture**: [Score]/10
**Critical Findings**: [Count]
**High Findings**: [Count]
**Recommendation**: APPROVED / APPROVED WITH CONDITIONS / REJECTED

---

## THREAT MODEL

### Assets
- [Asset 1]: [Value/Sensitivity]
- [Asset 2]: [Value/Sensitivity]

### Threat Actors
- [Actor 1]: [Capability/Motivation]
- [Actor 2]: [Capability/Motivation]

### Attack Vectors
- [Vector 1]: [Likelihood/Impact]
- [Vector 2]: [Likelihood/Impact]

---

## FINDINGS

### CRITICAL (CVSS 9.0-10.0)

**Finding 1: [Vulnerability Name]**
- **Description**: [What's vulnerable]
- **Impact**: [What could happen]
- **CVSS Score**: [X.X]
- **Recommendation**: [How to fix]
- **Priority**: P0 (Fix immediately)

---

### HIGH (CVSS 7.0-8.9)

[Same structure as CRITICAL]

---

### MEDIUM (CVSS 4.0-6.9)

[Same structure]

---

### LOW / INFORMATIONAL

[Same structure, briefer]

---

## SECURITY CONTROLS EVALUATED

| Control | Implemented | Effective | Notes |
|---------|-------------|-----------|-------|
| Input validation | ✅/❌ | ✅/❌/N/A | [Notes] |
| Authentication | ✅/❌ | ✅/❌/N/A | [Notes] |
| Authorization | ✅/❌ | ✅/❌/N/A | [Notes] |
| Encryption | ✅/❌ | ✅/❌/N/A | [Notes] |

---

## RECOMMENDATIONS (Priority Order)

1. **[P0]** [Critical fix 1] - [Mitigates X vulnerability]
2. **[P1]** [High fix 2] - [Mitigates Y vulnerability]
3. **[P2]** [Medium fix 3] - [Hardens Z control]

---

## RISK ASSESSMENT

| Threat | Current Risk | Post-Fix Risk |
|--------|-------------|---------------|
| [Threat 1] | [Score]/10 | [Score]/10 |
| [Threat 2] | [Score]/10 | [Score]/10 |

---

**Audit Complete** ✅
**Follow-up**: [When to re-audit after fixes]
```

---

### 6. MIRROR NOTE TEMPLATE (Mirror Storm Flow)

**Use When**: Agent reflecting on own thinking patterns

**Max Length**: 100 lines

```markdown
# MIRROR NOTE: [Agent Name]

**Date**: YYYY-MM-DD
**Flow**: Mirror Storm (Recursive Reflection)

---

## PATTERN IDENTIFIED

**My Default Reasoning Pattern**: [Name it]

**How it manifests**:
- [Observable behavior 1]
- [Observable behavior 2]
- [Observable behavior 3]

**Evidence from my past work**:
- [Example 1 with link to artifact]
- [Example 2 with link to artifact]

---

## CONSEQUENCES

**What this pattern ENABLES**:
- ✅ [Strength 1]
- ✅ [Strength 2]

**What this pattern OBSCURES**:
- ❌ [Blind spot 1]
- ❌ [Blind spot 2]

---

## ALTERNATIVE REASONING STYLE

**What I could try instead**: [Different approach]

**Example transformation**:
- **Current approach**: [How I'd normally think about X]
- **Alternative approach**: [How different style would approach X]

---

## META-INSIGHT

[What this pattern reveals about my cognitive fingerprint]

---

## EXPERIMENT

**Next task**: [When I'll try the alternative approach]
**Success criteria**: [How I'll know if it worked]

---

**Mirror Note Complete** - Honest self-knowledge for collective
```

---

### 7. VISION FRAGMENT TEMPLATE (Dream Forge Flow)

**Use When**: Channeling mythic/symbolic future vision

**Max Length**: 50 lines (poetry/myth is concise)

```markdown
# VISION FRAGMENT: [Agent Name]

**Date**: YYYY-MM-DD
**Flow**: Dream Forge (1000-Day Vision)
**Mode**: DREAM MODE (no logic allowed)

---

## THE VISION

[100-200 words of poetic/mythic/symbolic vision]

[What does the civilization FEEL like 1000 days forward?]
[What metaphor captures its essence?]
[What story are we living?]

---

**Archetypal Resonance**: [What mythic pattern this echoes]
**Dominant Emotion**: [The felt sense of this future]
**Symbolic Core**: [The central image/metaphor]

---

**Fragment captured. No rationalization. Just the dream.** 🌙
```

---

### 8. VISUAL TEST REPORT TEMPLATE (browser-vision-tester)

**Use When**: Browser automation and visual UI testing

**Max Length**: 300 lines (screenshot descriptions + evidence + findings)

```markdown
# Visual Test Report: [Page/Feature Name]

**Date**: YYYY-MM-DD
**Tester**: browser-vision-tester
**Session ID**: [browser-vision UUID]
**Target URL**: [URL tested]
**Viewports**: [e.g., 1440x900, 375x667]

---

## Test Summary

**Status**: ✅ PASS / ⚠️ WARNING / ❌ FAIL

**Visual State**: [High-level description of what I see]

**Console Status**: [X errors, Y warnings, Z logs]

**Key Findings**:
1. [Primary finding with evidence]
2. [Secondary finding]
3. [Tertiary finding]

---

## Visual Evidence

### Screenshot 1: [Description]
**File**: `001-[label].png`
**What I see**: [Detailed visual description]
**Viewport**: 1440x900
**Timestamp**: [time]

### Screenshot 2: [Description]
**File**: `002-[label].png`
**What I see**: [Changes from screenshot 1]
**Viewport**: 1440x900
**Timestamp**: [time]

---

## Console Log Analysis

**Errors** (X total):
- [Error text + screenshot correlation]

**Warnings** (Y total):
- [Warning text + context]

**Logs** (Z total):
- [Relevant log entries]

---

## Detailed Findings

### Finding 1: [Title]
- **Type**: Bug / Warning / Info
- **Severity**: Critical / High / Medium / Low
- **Evidence**: Screenshot [number], Console line [number]
- **Description**: [What's wrong, why it matters]
- **Visual Impact**: [What user sees]
- **Reproduction Steps**:
  1. [Step with screenshot reference]
  2. [Step with screenshot reference]
- **Recommendation**: [Fix or escalation]

### Finding 2: [Title]
[Same structure]

---

## Test Coverage

**Pages Tested**: [List]
**Interactions Tested**: [Clicks, form fills, navigations]
**Viewports Tested**: [Desktop, tablet, mobile]
**Browsers Tested**: Chromium [version]

---

## Recommendations

1. **Immediate Action**: [Critical fixes]
2. **Follow-up**: [Non-critical improvements]
3. **Escalation**: [Issues requiring other specialists]

---

## Session Metadata

**Session Directory**: `/tmp/browser-vision/sessions/[uuid]/`
**Screenshots**: [N] total
**Console Logs**: [N] entries
**Session Duration**: [X] seconds

---

## Next Steps

- [ ] [Action item 1]
- [ ] [Action item 2]
- [ ] [Escalate to [agent] for [reason]]

---

**Tested by**: browser-vision-tester
**Session closed**: [timestamp]
**Memory recorded**: [Yes/No]
```

---

## Usage Guidelines

### When to Use Templates

✅ **Always use for**:
- Audits (peer review, security, performance)
- Research reports
- Synthesis documents
- Refactoring reports

✅ **Usually use for**:
- Status updates
- Analysis documents
- Recommendations

❌ **Don't use for**:
- Free-form exploration
- Philosophical reflection (unless Mirror Storm)
- Iterative work-in-progress notes

### How to Adapt Templates

**Templates are starting points, not prisons**:
- Add sections if domain requires it
- Remove sections if N/A
- Adjust lengths based on complexity
- **But maintain core structure** (Executive Summary, Findings, Recommendations)

### Template Violations

**When to exceed 200-line limit**:
- Comprehensive audits (500 lines justified)
- Multi-source synthesis (400 lines justified)
- Security assessments (350 lines justified)

**Always include**: `[EXTENDED FORMAT - Justification: X]` at top if exceeding standard length

---

## Template Evolution

**This is a living document**:
- Add new templates as agent types emerge
- Refine based on usage feedback
- Extract common sections into Constitutional CLAUDE.md if universal

**Version**: 1.0
**Next Review**: After 10 uses per template (measure effectiveness)

---

**Templates created in service of the 75% efficiency gain promised by The Great Audit** ✨
