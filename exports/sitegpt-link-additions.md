# SiteGPT Link Additions Report

**Date**: 2026-02-27
**Agent**: full-stack-developer
**Task**: Add PureBrain vs SiteGPT link alongside existing comparison links on purebrain.ai

---

## Summary

Added SiteGPT to the compare page (page 752) at https://purebrain.ai/compare/. No other pages required updates.

---

## Pages Audited

| Page | ID | URL | Comparison Links Found | Action |
|------|-----|-----|----------------------|--------|
| Homepage | 11 | /pure-brain-agentic-ai-partner/ | None (comparison table only, no VS links) | Skipped |
| Compare hub | 752 | /compare/ | All 8 existing VS pages | **UPDATED** |
| vs ChatGPT | 753 | /purebrain-vs-chatgpt/ | None (no cross-links to other VS pages) | Skipped |
| vs Claude | 754 | /purebrain-vs-claude/ | None | Skipped |
| vs Copilot | 755 | /purebrain-vs-copilot/ | None | Skipped |
| vs Custom GPTs | 756 | /purebrain-vs-custom-gpts/ | None | Skipped |
| vs DeepSeek | 757 | /purebrain-vs-deepseek/ | None | Skipped |
| vs Gemini | 758 | /purebrain-vs-gemini/ | None | Skipped |
| vs Jasper | 759 | /purebrain-vs-jasper/ | None | Skipped |
| vs Perplexity | 760 | /purebrain-vs-perplexity/ | None | Skipped |
| Pay-Test | 439 | /pay-test/ | None | Skipped |
| Pay-Test Sandbox | 468 | /pay-test-sandbox/ | None | Skipped |
| Pay-Test Sandbox 2 | 688 | /pay-test-sandbox-2/ | None | Skipped |
| Pay-Test 2 | 689 | /pay-test-2/ | None | Skipped |

---

## Changes Made

### Compare Page (752) — /compare/

Two additions were made:

#### 1. SiteGPT Tile in the Tool Grid (HTML)

Added after the Custom GPTs tile, before Midjourney (keeping "Deep dive" tools grouped first):

```html
<div class="tool-tile" style="--tile-color: #00B4D8" onclick="openPanel('sitegpt')">
  <div class="tile-has-page"><span>Deep dive</span></div>
  <div class="tile-icon">💬</div>
  <div class="tile-name">SiteGPT</div>
  <div class="tile-tagline">Switching from SiteGPT?</div>
  <div class="tile-cta-hint">Click to see full comparison →</div>
</div>
```

Notes:
- Color `#00B4D8` (distinct teal, not their exact brand, avoids trademark territory)
- `tile-has-page` badge added (same as ChatGPT, Claude, Copilot, etc.) since a full comparison page exists
- Positioned before Midjourney (which has no deep dive page)

#### 2. SiteGPT Data Entry in TOOLS JavaScript Object

Added after hubspot-ai entry:

```javascript
sitegpt: {
  icon: '💬', name: 'SiteGPT', color: '#00B4D8',
  good: { title: 'What SiteGPT does well', body: 'Purpose-built customer support chatbot. Excellent at instant, 24/7 support responses trained on your documentation. Fast to deploy, no-code setup. Strong at reducing repetitive support ticket volume and handling multilingual inquiries.' },
  gap: { title: 'Where it leaves you', body: 'A support tool, not a business partner. One function — customer chat — executed well. No memory of your business strategy, no content creation, no operations support, no briefings. You still need a dozen other tools for everything else you do.' },
  diff: { title: 'What PureBrain does differently', body: 'PureBrain runs 12 business functions — strategy, operations, content, research, client management, and more — with persistent memory that compounds over time. SiteGPT answers support questions. PureBrain helps you run the business.' },
  deepDive: '/purebrain-vs-sitegpt/'
}
```

---

## Verification

- [x] Page 752 updated via REST API — HTTP 200
- [x] SiteGPT tile HTML present in saved content
- [x] tile-has-page Deep dive badge present
- [x] SiteGPT JS data entry present
- [x] deepDive: '/purebrain-vs-sitegpt/' present
- [x] Color #00B4D8 set correctly
- [x] Content length: 65,040 chars (was 63,669)

---

## Why Other Pages Were Skipped

- **Homepage**: Has a feature comparison TABLE (Claude Max vs ChatGPT vs Gemini vs PureBrain columns) — not VS page links. SiteGPT is not in that table, and adding it wasn't requested.
- **Individual VS pages (753-760)**: None of them cross-link to other comparison pages. They link back to /compare/ via nav only.
- **Pay-test pages**: No comparison links anywhere in content.
- **SiteGPT page itself (1044)**: Already has a "See All Comparisons" → /compare/ nav link, which is correct.
