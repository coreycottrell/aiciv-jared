# Memory: PureBrain.ai Master SRS Assembly

**Date**: 2026-02-26
**Type**: synthesis
**Agent**: doc-synthesizer

## What Was Produced

Assembled `exports/SRS-PureBrain-Master.md` — a 3,799-line, 175KB master Software Requirements
Specification for the PureBrain.ai platform. Document is agency-ready for quoting a full rebuild
from scratch.

## Assembly Pattern Used

**Four-layer structure**:
1. Cover page + Executive Summary (new synthesis, not from sources)
2. Master Table of Contents (synthesized across both sources)
3. Part I: full content from SRS-System-Architecture-API-Specification.md (lines 10+)
4. Part II: full content from SRS-purebrain-content-ux-branding.md (lines 9 to -14, trimming agent headers/footers)
5. Part III: Requirements Traceability Matrix (new synthesis from code-archaeologist memory)
6. Part IV: Appendices (synthesized from both sources — page inventory, API quick ref, env vars, glossary)
7. Agency Instructions (new content with 7 quote line items)

## Key Synthesis Decisions

- **Executive Summary**: Wrote 5 key architectural decisions that an agency MUST understand
  (self-contained HTML, WP plugin as all-in-one, tmux bridge, birth pipeline complexity, dual-publish)
  These were not in either source file as a consolidated list — synthesized from patterns across both.

- **RTM (Part III)**: Code-archaeologist counted 439 requirements across 10 categories.
  RTM maps each category to the exact section(s) in the combined document. New value-add.

- **Glossary (Appendix D)**: 25 terms defined. Captures PureBrain-specific vocabulary
  (Context Tax, Pilot Purgatory, Naming Ceremony, Birth Pipeline, etc.) that an agency team
  would need to understand to implement correctly.

- **7 Quote Line Items**: Structured to give the agency clean scope boundaries:
  WordPress Frontend, Backend API, Customer Portal (WebGL), Email System, Content Migration,
  DevOps/Infrastructure, QA/Testing.

- **Agency Context Note**: Included the "$1,215 in 13 days by AI" framing to invite comparison
  with human agency quote. This is the honest framing for the RFQ.

## File Paths

- **Output**: `/home/jared/projects/AI-CIV/aether/exports/SRS-PureBrain-Master.md`
- **Source 1**: `/home/jared/projects/AI-CIV/aether/exports/SRS-System-Architecture-API-Specification.md`
- **Source 2**: `/home/jared/projects/AI-CIV/aether/exports/SRS-purebrain-content-ux-branding.md`
- **Requirements source**: `.claude/memory/agent-learnings/code-archaeologist/2026-02-26--purebrain-srs-technical-requirements.md`

## Stats

- Final file: 3,799 lines, 175KB
- Source lines synthesized: ~2,900
- New content written: ~900 lines (exec summary, TOC, RTM, appendices, agency instructions)
- Total requirements documented: ~439 across 10 categories

## When to Apply This Pattern

When assembling a master document from multiple specialist agent outputs:
1. Write the synthesis layer FIRST (exec summary, TOC, cross-reference matrix)
2. Then append source documents with clean part headers
3. Write appendices LAST — they require reading all source content first
4. Agency instructions section is a forcing function: makes you think through how a reader
   will USE the document, not just read it.
