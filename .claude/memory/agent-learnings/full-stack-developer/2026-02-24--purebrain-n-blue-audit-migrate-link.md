# PUREBRAIN 'N' Blue Audit + Migrate Footer Link

**Date**: 2026-02-24
**Type**: operational
**Agent**: full-stack-developer
**Plugin Version**: 5.5.0

---

## Task

Audit ALL pages on purebrain.ai to ensure "N" in PUREBRAIN is always blue.

Rule: PUREBR(#2a93c1 blue) + AI(#f1420b orange) + N(#2a93c1 blue) + .ai(white)

Also: Add "Migrate" link to plugin footer bar.

---

## Audit Results

**Total pages scanned**: 42 published pages on purebrain.ai

**Pages with CORRECT PUREBR/AI/N pattern** (already fixed):
- 794 /why-purebrain/
- 800 /migrate/
- 620 /ai-partnership-audit/
- 577 /ai-adoption-review/
- 752-760 (compare + all competitor pages)
- 405 /ai-partnership-guide/
- 284 /ai-partnership-assessment/
- 777 /ai-tool-stack-calculator/
- 816 /ai-website-analysis/
- 860 /ai-website-execution/
- 855 /website-execution/
- 700 /blog-neural-feed-memories/
- 309 /thank-you/

**Pages with BAD pattern PURE(blue)+BRAIN(orange)**: Only page 929
- Fixed 2 occurrences in page 929 /mission-vision-values/
  1. Nav logo: `<span class="blue">PURE</span><span class="orange">BRAIN</span>` → `<span class="blue">PUREBR</span><span class="orange">AI</span><span class="blue">N</span>`
  2. Footer logo: same fix applied

**Pages with plain PUREBRAIN text** (CSS comments, not visible): 403, 11 — no fix needed

**Plugin footer bar**: Shows "PureBrain.ai" (title case link, not all-caps PUREBRAIN) — no fix needed

---

## Fix Applied

### Page 929 (/mission-vision-values/)
- Used WP REST API to get raw content, fix in-place, POST back
- Two occurrences fixed (nav-logo + footer-logo)
- Used `.blue` CSS class (already defined in page CSS) for "N" span
- Deployed: `curl POST /wp-json/wp/v2/pages/929`

### Plugin v5.5.0 Changes
- Added `pb-footer-migrate` CSS class (same pill style as why/mission)
- Added Migrate link to footer HTML: `<a href="/migrate/" class="pb-footer-migrate">Migrate</a>`
- Hidden on mobile (<600px) same as other pill links
- Deploy script: `tools/security/deploy_plugin_v550_purebrain.py`

---

## Deployment

- Plugin deployed via Playwright (CodeMirror editor)
- All 14 validation checks: OK
- All 13 live verification checks: OK
- Elementor cache 403 is normal (endpoint auth quirk, not a failure)

---

## Key Pattern

When a self-contained HTML page has the old PURE/BRAIN split:
1. `curl GET /wp-json/wp/v2/pages/{id}?context=edit` → get `content.raw`
2. Fix the span pattern
3. `curl POST /wp-json/wp/v2/pages/{id}` with `{"content": fixed_content, "status": "publish"}`

The `.blue` class is always defined in these pages' scoped CSS, so reusing it for the N span works cleanly.
