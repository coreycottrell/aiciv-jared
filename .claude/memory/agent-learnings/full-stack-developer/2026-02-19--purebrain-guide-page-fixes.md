# purebrain.ai AI Partnership Guide Page Fixes
**Date**: 2026-02-19
**Type**: operational
**Agent**: full-stack-developer
**Page**: https://purebrain.ai/ai-partnership-guide (ID: 405)

## What Was Done

Fixed three categories of issues on the AI Partnership Guide pillar page.

### Part 1: Placeholder links -> Styled buttons
Five `[LINK: ...]` placeholder anchors replaced with real URLs styled as inline-block buttons matching the dark theme.

Mappings used:
- "Most AI Agents Break" -> `/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/`
- "Why AI Memory Changes Everything" -> `/why-ai-memory-changes-everything/`
- "CEO vs Employee AI Lens" -> `/ceo-vs-employee-ai-transformation-gap/`
- "Data Governance and AI Memory" -> `/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/` (same post, covers data governance)
- "AI Partnership Readiness Self-Assessment" -> `/ai-partnership-assessment/`

Button CSS used (matches site dark theme):
```
display: inline-block; padding: 12px 24px; background: rgba(42, 147, 193, 0.15);
border: 1px solid #2a93c1; color: #2a93c1; text-decoration: none; border-radius: 8px;
font-weight: 600; transition: all 0.3s; margin: 8px 0;
```
With onmouseover/onmouseout for hover effect (blue fill).

### Part 2: CTA button links fixed
- "Meet Your AI Partner" btn--primary: was pointing to `/purebrain-4/?utm_source=...` -> fixed to `/#awakening`
- "Take the Assessment" btn--secondary: was `href="#"` -> fixed to `/ai-partnership-assessment/`
- "Subscribe Free" btn--secondary: was `href="#"` -> fixed to `/blog/`

### Part 3: FAQ section converted to accordion
- Replaced flat h3/p structure with clickable `.faq-question` divs + collapsible `.faq-answer` divs
- Added CSS with max-height transition for smooth open/close animation
- JavaScript `toggleFaq()` function collapses other items when one is opened (single-item-open behavior)
- Preserved all schema.org markup (itemscope/itemprop) for SEO
- 6 FAQ items, all working

## Technical Notes
- Page uses Elementor with a single HTML widget containing the full page HTML
- REST API endpoint: `POST https://purebrain.ai/wp-json/wp/v2/pages/405`
- Auth: `Aether:FlFr2VOtlHiHaJWjzW96OHUJ` (application password)
- Elementor data path: `meta._elementor_data` -> `[0].elements[0].elements[0].settings.html`
- Must use curl (not Python urllib) for the POST - urllib had auth issues with this site
- Content was one large monolithic HTML document, not separate Elementor blocks
- Payload written to /tmp/update_payload.json and sent via `curl -d @file`

## Verification
- 0 remaining `[LINK: ...]` placeholders
- 5 styled inline-block blog links all pointing to real URLs
- 0 remaining `href="#"` broken links
- 6 FAQ questions in accordion with JS toggle + CSS animation
- HTTP 200 response, modified timestamp 2026-02-19T13:54:09
