# Memory: Compare Hub Full Audit - purebrain.ai/compare/
**Date**: 2026-03-02
**Type**: operational + teaching
**Topic**: Complete audit of all 18 comparison tiles and 10 dedicated comparison pages

---

## Task Summary

Full audit of purebrain.ai/compare/ hub page and all linked comparison pages.

---

## Architecture Discovery (Critical)

### Hub Page Structure
- Page ID: 752 (WordPress), elementor_canvas template
- Self-contained HTML with custom CSS + inline JavaScript
- 18 tool tiles rendered in a 4-column responsive grid
- Tiles use `onclick=openPanel('toolkey')` -- NOT anchor tags
- This means standard link extraction (`querySelectorAll('a')`) finds ZERO comparison links
- Must use `window.TOOLS` JS object to discover deepDive URLs

### URL Pattern
- Correct pattern: `/purebrain-vs-[tool]/`
- Wrong pattern: `/switching-from-[tool]` (404s)
- Tool keys do NOT always match URL slugs (e.g., `glbgpt` -> `/purebrain-vs-glbgpt/`)

### Two-Tier Content System
1. **Tile panel** (modal): All 18 tools have one. Shows good/gap/diff columns. Tiles without deepDive show only "Start Your AI Partnership" CTA.
2. **Full comparison page**: 10 of 18 tools have dedicated `/purebrain-vs-[tool]/` pages with "Read full comparison" button.

---

## Tools with Dedicated Pages (10)

| Tool | URL | Status |
|------|-----|--------|
| ChatGPT | /purebrain-vs-chatgpt/ | WORKING |
| Microsoft Copilot | /purebrain-vs-copilot/ | WORKING |
| Google Gemini | /purebrain-vs-gemini/ | WORKING |
| Claude (Anthropic) | /purebrain-vs-claude/ | WORKING |
| DeepSeek | /purebrain-vs-deepseek/ | WORKING |
| Perplexity | /purebrain-vs-perplexity/ | WORKING |
| Jasper | /purebrain-vs-jasper/ | WORKING |
| Custom GPTs | /purebrain-vs-custom-gpts/ | WORKING |
| SiteGPT | /purebrain-vs-sitegpt/ | WORKING |
| GlobalGPT (GLBGPT) | /purebrain-vs-glbgpt/ | WORKING |

All 10 return HTTP 200 with rich comparison content.

## Tools with Panel Only (8 - no dedicated page)

Midjourney, DALL-E, Gamma, Cursor, Lovable, Notion AI, Salesforce Einstein, HubSpot AI
- All panels show correct content for their respective tool
- No "Read full comparison" link (correct - intentional)
- Only "Start Your AI Partnership" CTA

---

## Key Learnings for Future Audits

### 1. JS-Driven Navigation Requires window.TOOLS Inspection
Standard link extraction finds 0 comparison links. Always eval `window.TOOLS` on hub-style pages.

### 2. False Positive in Panel Index Test
When my initial test clicked tile index 8 (SiteGPT), it showed SiteGPT content -- correct. I misread it as Midjourney. Always verify tile's onclick value, not its visual position.

### 3. Hub Page Self-Contained HTML (Not Elementor widgets)
No `.elementor-section` classes found. Page content is raw HTML injected via WP post content with `<!-- wp:html -->`. This is the non-Elementor deployment pattern.

---

## Screenshots

All stored in: `exports/compare-audit/screenshots/`
- `00-compare-hub.png` - Full hub page
- `00-hub-after-chatgpt-click.png` - ChatGPT panel open
- `00-midjourney-click-check.png` - Midjourney panel (no deepDive link)
- `01-correct-chatgpt.png` through `10-correct-glbgpt.png` - All 10 full comparison pages
