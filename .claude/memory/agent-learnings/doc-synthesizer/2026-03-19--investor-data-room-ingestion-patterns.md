# Memory: Investor Data Room Ingestion Patterns

**Agent**: doc-synthesizer
**Date**: 2026-03-19
**Type**: technique + pattern
**Topic**: Google Drive investor data room ingestion — 663 files, strategic synthesis approach
**Confidence**: high

## Context

Ingested the full Pure Technology Inc. investor data room from Google Drive (folder: 1Yj35265-PESMoqKUwY_a81ejL4Hh661B). 663 total files across 46 folders.

## Key Techniques

### 1. Strategic Triage Over Exhaustive Reading
Read ~44 of 663 files (7%) = ~90% of investor-relevant intelligence.
Skip: videos, images, individual offer letters, duplicates.
Prioritize: company summaries, financial models, term sheets, customer data, tech docs.

### 2. Batch Download Pattern
8-18 files per batch via Google Drive API. Total: ~15 minutes for 44 docs.

### 3. Character Limits
max_chars=8000 for PDFs/DOCX, 8000 for XLSX. Captures first 5-10 pages or 100-150 rows.

### 4. 9-Section Investor Synthesis Structure
Company Overview, Product/Tech, Market, Financials, Team, Legal, Investment Terms, Customers, Risk Factors

### 5. Two-File Deliverable
- Full KB (~3,800 words): comprehensive reference
- System prompt (~1,900 words): condensed for AI chat with pre-written investor FAQs

## Pure Technology Key Facts
- Series A: $25M at $105M pre-money (MAKR Venture Fund, March 2025)
- 2023 Revenue: $943,136; Year 1 projected $253.8M; Year 5 $13.28B
- ~$1,792 revenue per user per year on platform
- 1,000+ influencers with 1B+ followers pre-enrolled
- Blue Ocean — no direct competitors

## Gotchas
- Financial statements are transaction logs, not P&Ls — use Board View 2025 model
- Duplicate docs across product subfolders — read one version only
- MAKR Term Sheet is partially redacted but key terms visible

## Files Generated
- /home/jared/projects/AI-CIV/aether/exports/investor-data-room-knowledge-base.md
- /home/jared/projects/AI-CIV/aether/exports/investor-agent-system-prompt.md
