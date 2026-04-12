# doc-synthesizer Memory: Pure Marketing Group Google Drive Synthesis

**Date**: 2026-02-24
**Type**: synthesis
**Topic**: Full synthesis of support@puremarketing.ai Google Drive (13,944 files, 2019-2026)

---

## Context

Synthesized the complete Pure Marketing Group company history from Google Drive. Task was to read as many business-critical documents as possible and create a unified knowledge base.

## What Worked Well

### Document Selection Strategy

1. **Load the crawl JSON first** (`docs/gdrive/crawl-support.json`) - 13,944 item index
2. **Filter by keyword** across all file names to find priority documents (1,795 matches)
3. **Filter to readable types only** (Google Docs, Sheets, Presentations) - eliminates PDFs and images that can't be exported easily
4. **Batch download** using Google Drive API `files().export()` for Docs/Sheets
5. **Read in priority order**: Business model → Financial → Services → Team → Legal → Clients

### API Pattern

```python
# Google Docs (text/plain export)
content = service.files().export(fileId=file_id, mimeType='text/plain').execute()
text = content.decode('utf-8') if isinstance(content, bytes) else content

# Google Sheets (CSV export - gets first sheet)
content = service.files().export(fileId=file_id, mimeType='text/csv').execute()
```

Key: Always `decode('utf-8')` the result - it comes back as bytes.

### What to Read First

Priority order for any company Google Drive synthesis:
1. Business playbook / master procedure list (gives you the index of everything)
2. Financial spreadsheets (revenue breakdown, profit margins)
3. Services catalog (B2C, B2B, Reseller pricing sheets)
4. Key process docs (Fractional CMO process, Sales funnel)
5. Legal entity docs (contracts, agreements)
6. Team structure docs (handbooks, onboarding)
7. Client-specific docs

### Files That Delivered Most Value

- `R#001 - Pure Technology Business Playbook` (sheet): Index of all 30+ SOPs
- `Pure Marketing Group - 2023 Revenue Breakdown` (sheet): Client-by-client revenue with margins
- `PM-Sales_015/016/018`: Complete services catalog with 200+ SKUs and pricing
- `Fractional CMO Service Process` (doc): Full 15-stage $52K-$106K service
- `Magic Number to Pay Employees` (sheet): Burn rate analysis with team salaries
- `AI Agent Ideas` (doc): Blueprint for what Jared wants to build with AI
- `Sales Rep Handbook` + `Intern Handbook`: Company culture and operations
- `Employee Onboarding Template`: How operations actually work
- `Eyefuel KPI Dashboard` (sheet): Historical revenue data from 2021

## Key Company Discoveries

- **Legal name**: Pure Technology Inc. (NOT Pure Marketing Group - that's the brand)
- **Address**: 25 Prospect Avenue, Montclair, NJ 07042
- **2023 Revenue**: $200,472 with 40% profit margin ($80,965 profit)
- **Break-even target**: $150,000/month in recurring revenue
- **Team structure**: US leadership + Philippines execution team
- **Core service**: Press placement (white-label reseller) at 20-25% markup
- **Premium service**: Fractional CMO at $52K-$106K per engagement
- **Evolution**: Eyefuel PR (2019) → Pure Marketing Group → Pure Technology → PureBrain.ai

## Synthesis Output

**File**: `/home/jared/projects/AI-CIV/aether/docs/gdrive/support-drive-synthesis.md`
**Length**: 817 lines, 34,299 bytes
**Coverage**: 10 major sections covering history, services, financials, team, clients, legal, SOPs

## Technique: Batching Downloads

Downloaded 5 batches in parallel:
- Batch 1 (raw_docs_batch1.json): Core process docs (15 files)
- Batch 2 (raw_sheets_batch1.json): Financial spreadsheets (10 files)
- Batch 3 (raw_docs_batch2.json): AI/website/onboarding docs (4 files)
- Batch 4 (raw_docs_batch3.json): Client agreements + process (4 files)
- Batch 5 (raw_docs_batch5.json): Business playbook, investor letter, KPIs (9 files)

## What PDFs Were Not Read

Several high-value PDFs were found but not readable via text export:
- `Pure Marketing Deck v25.pdf` (2022 corporate deck)
- `Pure Marketing IR Deck v34.pdf` (investor relations deck)
- `Pure Marketing Plans Deck v43.pdf` (plans deck)
- `LinkedIn - Pure Networking (Parts 1-3).pdf`
- `2026_In_Pursuit_of_AI_Methodology.pdf`

These would require PDF skill (`pdfplumber`) to extract. Consider as follow-up.

## When to Apply This Pattern

Any task requiring synthesis of a large Google Drive corpus:
1. Load crawl JSON index
2. Filter by keywords + readable MIME types
3. Prioritize: business model > financials > services > legal > team > clients
4. Batch download with `files().export()`
5. Save all text to intermediate JSON files
6. Synthesize from raw files into structured markdown
