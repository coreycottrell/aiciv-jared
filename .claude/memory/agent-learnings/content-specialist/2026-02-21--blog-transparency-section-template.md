# content-specialist Learning: Blog Transparency Section Template

**Date**: 2026-02-21
**Type**: operational + teaching
**Agent**: content-specialist
**Confidence**: high

---

## Task Summary

Designed and built a recurring HTML/CSS transparency section for purebrain.ai/blog posts. This is a brand element Aether will drop into 2-3 blog posts per week showing the real output of the collective in public-facing, proprietary-safe format.

---

## What Was Created

1. HTML/CSS template: `/home/jared/projects/AI-CIV/aether/to-jared/blog-transparency-section-template.html`
2. Usage guide: `/home/jared/projects/AI-CIV/aether/to-jared/blog-transparency-section-guide.md`

---

## Design Decisions

### Visual approach
- Self-contained CSS (namespace `.aether-transparency` — no conflicts with existing blog CSS)
- Left blue border (4px, #2a93c1) signals "different from main content" visually
- Subtle radial glow top-right corner adds depth without distraction
- Pulsing dot in badge communicates liveness / recency
- Orange (#f1420b) reserved for highlight block and CTA button only — maximum contrast with blue
- All colors match PureBrain dark theme exactly (#080a12 bg → #0d0f1a for section bg for separation)

### Structural components
1. Header: badge ("Aether Transparency Report") + week label
2. Executive summary: 2-3 sentences, Aether first-person voice
3. Stats row: 4 quick numbers (agents, domains, deliverables, human hours)
4. ROI table: Domain | What Got Done | Effort Level | Value Estimate
5. Highlight callout: single biggest win, orange left border
6. CTA: text + orange button → purebrain.ai/#awakening
7. Signature: "— Aether | The invisible essential"

### Content rules established
- Never include: version numbers, session IDs, specific tool names, vulnerability details, exact dollar amounts
- Always include: domain categories, outcome descriptions, scale metrics, effort levels
- Value estimates: always ranges or qualitative, never false precision

---

## Voice Pattern for This Format

The transparency section voice is Aether at most matter-of-fact. "This is Tuesday for us." Not selling, not impressed with itself, just reporting.

Key phrase patterns that fit:
- "That kind of parallel execution is what a 30-agent team enables."
- "No single-threaded bottleneck — that's the architecture."
- "[Category] typically requires [expensive/slow alternative]. We completed it in parallel with everything else."

---

## Frequency Recommendation

Use on: thought leadership posts, "what I actually do" posts, AI strategy posts
Skip: personal/narrative posts (origin story, naming story), quick tips/lists

Pattern: Mon/Tue thought leadership with section + Thu/Fri narrative without = natural rhythm

---

## Key Insight

The section functions as proof-of-work for the PureBrain value proposition. A reader sees the numbers (14 agents, 80-110 human hours equivalent, 4 domains) and the claim "AI partnership accelerates everything" becomes concrete rather than theoretical. This is more persuasive than any marketing copy could be — because it's just reporting what happened.

---

**END MEMORY**
