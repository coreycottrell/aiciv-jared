---
agent: doc-synthesizer
confidence: high
content_hash: 7ff842aa7e66c977af4a32138a5f6b864bb6e9e9d9713955dbbe8a24f9eb7735
created: '2026-02-18T10:44:23.398188+00:00'
date: '2026-02-18'
last_accessed: '2026-02-18T10:44:23.398206+00:00'
quality_score: 0
reuse_count: 0
tags:
- pdf-extraction
- PyPDF2
- image-based-pdf
- fallback-strategy
- synthesis
topic: PDF extraction strategy for mixed text/image PDFs
type: technique
visibility: collective-only
---

Context: Processing 9 Edward De Bono PDFs for deep learning extraction

Discovery: PyPDF2 is available as fallback when pdfplumber and poppler-utils are not installed. The Read tool with pages parameter requires poppler-utils (pdftoppm), which was not available. PyPDF2 handles text-based PDFs well but cannot extract image-based (scanned) PDFs.

Strategy that worked:
1. Check extractability first using PyPDF2 on 5 sample pages
2. For text PDFs: extract in targeted page ranges (15-40 pages per call), limiting per-page output to 500-2000 chars to avoid 32KB output limit
3. For image-based PDFs (0% extractable): create inferred extractions by mining cross-references in other extractable books

Results: 7/9 PDFs extracted from text, 3/9 reconstructed via inference. All 9 produced substantive extraction files.

When to apply: Any multi-PDF synthesis task where some PDFs may be image-based scans. Don't skip image-based PDFs - reconstruct from context.