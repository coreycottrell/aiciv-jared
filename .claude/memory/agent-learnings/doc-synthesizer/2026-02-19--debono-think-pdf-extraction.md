# Memory: de Bono "Think!" PDF Extraction - 2026-02-19

**Agent**: doc-synthesizer
**Type**: technique
**Topic**: PDF extraction and thinking model synthesis from de Bono "Think!"
**Confidence**: high

## Context

Extracted all thinking models, frameworks, and techniques from Edward de Bono's "Think! Before It's Too Late" (2009, 205 pages). Goal was a practical AI prompting reference for Jared.

## Discovery: PDF Extraction Method

The Read tool requires `poppler-utils` for PDF rendering, which wasn't installed. But pdfplumber works as a Python library:

```bash
venv/bin/pip install pdfplumber
venv/bin/python3 -c "
import pdfplumber
with pdfplumber.open('/path/to/file.pdf') as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text and text.strip():
            all_text.append(f'--- PAGE {i+1} ---\n{text}')
"
```

This PDF had 205 pages, 203 extractable, ~300K characters. First 10 pages were front matter (no text or table of contents).

## Discovery: Synthesis Structure for Thinking Models

Best structure for a thinking model reference document:
1. Quick Reference Table first (name, category, purpose, prompting shortcut)
2. Group by type (Creative / Exploratory / Perceptual / Design / Values / Meta)
3. For each model: what it is, how to use it, real example from the book, prompting application in quotes
4. Combination templates section at end
5. Key principles summary at end

## Models Found (39 total sections)

Core frameworks extracted:
- Lateral Thinking (umbrella concept)
- 7 lateral thinking tools: Random Word, Challenge, Provocation (Po), Movement, Concept Extraction, Concept Fan, Focus
- Septine (NEW in this book - first publication)
- Six Thinking Hats (Blue/White/Red/Black/Yellow/Green + Parallel Thinking)
- 7 CoRT perceptual tools: PMI, CAF, C&S, AGO, FIP, APC, OPV
- Flowscape (Water Logic visual mapping)
- Design Thinking + Court of Design + Operacy
- Six Value Medals (Gold/Silver/Steel/Glass/Wood/Brass)
- Proto-truth, Confliction/De-confliction, Directed Attention

## Key Insight Worth Remembering

The ASYMMETRY principle is the core logic for ALL of de Bono's creative tools:
- Brain forms asymmetric patterns
- An ant on a leaf reaches the trunk 100% of the time
- An ant on the trunk reaches a specific leaf only 1:8,000 times
- Therefore: ideas that are OBVIOUS IN HINDSIGHT are NOT REACHABLE BY FORWARD LOGIC
- This is why you need lateral tools - to arrive from the periphery, not the center

## Prompting Pattern That Works

The most powerful pattern for AI prompting from this book:
```
"Po: [impossible/absurd statement]. Now use movement:
1. Extract the concept
2. Focus on the difference from normal
3. Find positive aspects
4. Imagine it moment-to-moment
5. Find special circumstances where it applies"
```

## Output File

/home/jared/projects/AI-CIV/aether/to-jared/de-bono-think-models.md
- 780 lines, 43KB
- 39 framework sections
- Quick reference table for all 37 models
- Combination templates for complex AI prompting sessions
