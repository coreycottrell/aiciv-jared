# Investor Intelligence Page 1205 Update
**Date**: 2026-03-05
**Task**: Apply J. Paris feedback to WP page 1205, build investor brief

## Key Learnings

### Page 1205 Architecture
- Template: `elementor_canvas` — content in `post_content`, NOT Elementor data
- All HTML is one self-contained `<!-- wp:html -->` block (73KB)
- REST API edit context required to get `raw` content: `?context=edit`
- Credentials: `Aether` / `ZGuh 1W8k WpWM c9iy kqyd buPr`

### Section Reorder Pattern (Safe)
1. Extract full content as line array
2. Find section boundaries via `<!-- ══` comment dividers
3. Find `</section>` closing tags to get exact block ranges
4. Reassemble blocks in new order
5. Update nav dots and JS `sections[]` array to match

### Changes Applied
1. Section padding: 100px → 60px (also hero, responsive)
2. Section title font: `clamp(32px, 4.5vw, 54px)` → `clamp(36px, 5.2vw, 62px)`
3. Hero "18 Months" headline: `<p>` → `<h2>` with font-size clamp(22px,3.5vw,42px) + bold styling
4. METR flowchart removed: `<!-- METR Autonomy Timeline -->` block + metr-source line
5. Capital Signal section moved from position 5 → position 3 (after Market Opportunity)

### Verification (All 11 PASS)
- Always verify section ORDER via `html.index()` position comparison
- Check flowchart removal via exact `<div class="metr-display">` string (CSS references OK)
- Confirm font size strings exist in live HTML via `curl + python`

### Investor Brief HTML
- File: `exports/investor-brief/investor-brief.html`
- Email gate with Brevo API integration
- Brevo list ID 3, notification to jared@puretechnology.nyc
- Print-to-PDF download pattern (gate hidden via @media print)
- Contact fallback to localStorage if Brevo fails
