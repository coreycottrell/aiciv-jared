# Reveal.js PDF Generation Behind sessionStorage Password Gate

**Date**: 2026-04-09
**Type**: teaching
**Topic**: Extracting Reveal.js slide deck as PDF when deck is behind a client-side password gate

## Problem
Previous attempt to PDF `https://purebrain.ai/pitch-v2/` produced 16 copies of the login screen
because Playwright captured the gate instead of the slides. Earlier PDF was 741KB of useless
login screenshots.

## Root Cause
The deck uses a client-side `#pitch-gate` overlay with `sessionStorage.setItem('pitch_auth','1')`.
Valid codes: `PUREBRAIN2026`, `PUREINVESTOR2026`, `PUREPITCH2026`, `PUREDECK2026`.
When Reveal's `?print-pdf` mode reloads, any sessionStorage from the UI interaction MAY be
lost depending on navigation — the gate then re-appears over the print-mode layout.

## The Winning Approach
**Pre-seed sessionStorage via Playwright `add_init_script` BEFORE first navigation.**
`add_init_script` runs on every new document in the context, so it survives `?print-pdf` reload.

```python
context.add_init_script("""
    try { sessionStorage.setItem('pitch_auth','1'); } catch(e) {}
""")
page.goto(URL + "?print-pdf&pdfSeparateFragments=false", wait_until="networkidle")
```

## Reveal.js Gotchas
- `?print-pdf` is the print mode trigger (Reveal 5.x).
- **`pdfSeparateFragments=false`** is critical — without it fragments become individual
  pages, and we got 104 pages instead of 16.
- Viewport and `page.pdf` size MUST match Reveal's configured `width`/`height`
  (here 960x700). Mismatch causes clipping.
- Reveal print mode often appends one trailing empty page — trim with PyPDF2 after.
- `document.querySelectorAll('.reveal .slides > section').length` returned 0 in print mode
  (Reveal wraps sections differently). Don't rely on that as a success check — verify via
  PyPDF2 page count + `extract_text()` on page 1.

## Verification
- PyPDF2 page count: 17 → trimmed to 16
- Page 1 text starts with "PUREBRAIN.AI ... Series A ... $2.5M RAISE" (real slide 1)
- Page 16 text contains "THE ASK ... $55M PRE-MONEY" (real final slide)
- File size: 1,206,709 bytes (vs broken 741,273)

## Deployment
- `tools/cf-deploy.py downloads/purebrain-pitch-deck.pdf` (run from repo root,
  path is RELATIVE to `exports/cf-pages-deploy/`, NOT absolute).
- Deployment ID: `d77b5881-fe58-414d-b9d5-7c13b1f9fc12`
- Live verification: `curl -sI https://purebrain.ai/downloads/purebrain-pitch-deck.pdf`
  → content-length matches local file.

## Files Touched
- `/home/jared/exports/portal-files/purebrain-pitch-deck-16slides.pdf` (replaced)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/downloads/purebrain-pitch-deck.pdf` (replaced)
- `/tmp/gen_pitch_pdf.py` (throwaway script)

## Reusable Script Path
`/tmp/gen_pitch_pdf.py` — if deck changes, just re-run this.

## Key Takeaway
**For any client-side-gated SPA you need to PDF: use `context.add_init_script` to pre-seed
the unlock flag in localStorage/sessionStorage.** It's idempotent and survives all reloads.
Never try to interact with the gate UI + hope the session persists through Reveal's reload.
