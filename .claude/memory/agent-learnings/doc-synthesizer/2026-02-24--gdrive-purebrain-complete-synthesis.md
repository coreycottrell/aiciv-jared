# doc-synthesizer: Google Drive PureBrain Complete Synthesis

**Agent**: doc-synthesizer
**Date**: 2026-02-24
**Type**: synthesis
**Topic**: Complete Google Drive knowledge base synthesis for Pure Technology / PureBrain

---

## Context

Synthesized 40+ documents from purebrain@puremarketing.ai Google Drive across all 8 priority training folders.

**Output file**: `/home/jared/projects/AI-CIV/aether/docs/gdrive/purebrain-drive-synthesis.md` (875 lines)

## Documents Read and Synthesized

### Source of Truth PDFs (000 folder)
- PT Handbook v7 (4.6MB) - employee handbook, culture, values
- Identity Statement (404KB) - vision, mission, 7 pillars, 7 objectives, USP, competition philosophy
- Company Culture PDF (439KB)
- Why What How PDF (304KB) - core business rationale
- PMG Mission Vision PDF (142KB) - PMG positioning
- PMG Crystal Clear Focus PDF (261KB) - PMG as proof-to-product engine
- Category Design PDF (348KB) - competitive differentiation
- Actualizing Brilliance PDF (65KB) - consumer hierarchy framework
- Crystalized Thoughts PDF (86KB) - insight methodology

### Training Materials
- CEO Training.docx - 6 CEO storytelling frameworks
- Sales & Money Making Training.docx - first $1000 system
- Strategic Planning.docx - Ohtani 9x9 matrix framework
- Marketing Automation Training.docx - signal playbook
- Content Creation Training.docx - AI tools for content
- More Profile Audit.docx - LinkedIn profile scoring

### Pure Lead Gen System (complete 7-step system)
- Blueprint + Steps 1-6 + Experiential Giveaway Engine + 1-pager

### Platform Docs (007 folder)
- PURE-BRAIN-REFERENCE.md - technical reference
- Pure Brain Platform Plain English (Google Doc)
- Pure Brain Platform Build.docx (5-phase MVP plan)
- README-purebrain-post-payment-flow.md (46KB)

### Operational
- DEPARTMENT-ROUTING-GUIDE.md - 23 departments with trigger prefixes
- Shorthand Commands - D/R/B/F/P/S/!/!! system
- pure-tech-team-dossier-v2.md - 49-person org chart

### Marketing Analysis (from Drive)
- Distribution strategy (45KB)
- LinkedIn strategy (33KB)
- Blog analysis (34KB)
- Lead gen system (28KB)

## Key Discoveries / Patterns

### 1. "Engineer Resonance, Not Chase Attention" is the Operating Philosophy
Appears across ALL documents: PMG positioning, PureBrain differentiation, lead gen approach, content strategy. Not just a tagline - it dictates HOW every system is built.

### 2. The Proof-to-Product Pipeline is the Entire PT Strategy
PMG (manual services) → proves thesis → Pure Influence (automation) → Key Phone (data layer) → PureBrain (AI relationship layer). Each piece feeds the next. PMG is not permanent - it's the runway to product.

### 3. 7 Pillars of Value Define All Decisions
Integrity, Accountability, Transparency, Growth, Innovation, Persistence, Love. These appear in employee handbook AND marketing docs AND product design. Apply them to evaluate any decision.

### 4. The Lead Gen System is a Complete Engine
6 steps: Hook (1-pager "ENGINE") → LinkedIn Profile as Landing Page → Fit Check Qualification → Weekly LinkedIn Execution → DM Scripts → Automation. All 6 steps documented with copy-paste ready templates. Fit Check link: https://forms.gle/FYE75HLWV58DBhqE8

### 5. PureBrain Has Technical Architecture Documented
Claude API (claude-sonnet-4-20250514) via api.puremarketing.ai proxy, name detection regex, [SHOW_PRICING] trigger, 5 pricing tiers ($49-custom), affiliate 5% perpetual, Google Forms waitlist integration (8 fields).

## Synthesis Technique Learnings

**What worked well for this complex synthesis**:
1. Start with folder structure (Python script to parse crawl JSON) before downloading anything
2. Download all PDFs and DOCXs in parallel batches before reading
3. Install pdfplumber + python-docx once, then batch-process all files
4. For large PDFs (PT Handbook 4.6MB), read only priority pages (1-15 for core identity)
5. For each domain, identify the "canonical" document vs supporting docs
6. Write synthesis organized by USE CASE (what Aether needs to know to act) not by source document

**Gotcha**: pdfplumber not available in system python - must `pip install pdfplumber --break-system-packages`. Takes 30 seconds.

**Gotcha**: Large PDFs (4.6MB) can be read from page 1-30 for core content without hitting limits.

**Document priority for future synthesis**:
- Google Docs (Google Slides exported as text) = most readable
- Markdown files = cleanest, most agent-ready
- Small PDFs (<500KB) = good with pdfplumber
- Large DOCXs (>1MB) often contain training material collections (LinkedIn posts, etc.) not original content

## When to Apply These Learnings

- Any time someone asks "what does Jared's company actually do?"
- Any time an agent needs context on PT's philosophy for a decision
- When building content that must align with brand voice
- When routing a request to the right department (use routing guide)
- When building features for PureBrain (use technical reference)

## Confidence

High - directly from source documents Jared curated as training material.
