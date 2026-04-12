# Memory: Competitor Exodus Pages - Full Build

**Date**: 2026-02-23
**Type**: operational
**Topic**: Built all 6 remaining competitor exodus pages for purebrain.ai

## What Was Built

6 self-contained HTML pages, all saved to `/home/jared/projects/AI-CIV/aether/exports/`:

### Individual Pages (5)
1. `competitor-exodus-deepseek.html` — Privacy crisis angle. Alert banner at top citing 7+ country bans. Unique "ban map" grid section showing countries + reasons. Q1 quiz based on data type exposed.
2. `competitor-exodus-gemini.html` — "So close yet so far" angle. Unique two-column irony grid showing "what Google knows" vs "what Gemini uses." Google's 15+ year data advantage wasted.
3. `competitor-exodus-claude.html` — Most nuanced page. "Same engine. Different relationship." Honest disclosure that PureBrain IS built on Claude. Unique "what stays / what you gain" grid showing model quality stays, partnership layer added. No badmouthing Claude model.
4. `competitor-exodus-perplexity.html` — Sophisticated ICP angle. Research tool vs. thinking partner positioning. Unique spectrum/cards section showing what Perplexity excels at vs. what PureBrain adds (contextual interpretation).
5. `competitor-exodus-custom-gpts.html` — Power user angle. "You built a tool. We built a partner." Unique numbered "ceiling steps" section showing 4 structural limitations of configuration-based AI.

### Hub Page (1)
- `competitor-exodus-hub.html` — 16-tile grid, 4 columns desktop / 2 mobile. Each tile click opens an inline accordion panel (no page navigation needed) with 3-column breakdown: what it does well / where it leaves you / what PureBrain does differently. Below grid: 2-question quiz with email gate → personalized tool recommendation. 16 tools: ChatGPT, Copilot, Gemini, Claude, DeepSeek, Perplexity, Jasper, Custom GPTs, Midjourney, DALL-E, Gamma, Cursor, Lovable, Notion AI, Salesforce Einstein, HubSpot AI.

## Architecture Pattern (Matched From Existing 3 Pages)

Every individual page has:
1. Gradient strip (competitor color → PureBrain blue)
2. Nav with sticky positioning + backdrop blur
3. Hero with badge, stats, scroll hint
4. Pain section (3 quote cards in competitor color tint)
5. UNIQUE structural section per page (ban map, irony grid, honest truth, spectrum, ceiling steps)
6. 3-question quiz (vanilla JS, no deps)
7. Email gate → POST `/wp-json/purebrain/v1/guide-unlock` (generous: shows results even on failure)
8. Personalized results (4 personas keyed to Q1 answer)
9. CTA → `https://purebrain.ai/#awakening`
10. Comparison table (6 rows)
11. Footer

## Competitor Brand Colors Used
- DeepSeek: `#4D6BFE`
- Gemini: `#8E75B2`
- Claude: `#D4A574`
- Perplexity: `#20B2AA`
- Custom GPTs: `#10a37f` (OpenAI green)

## Key Design Decisions

### Claude Page: Radical Honesty
- Explicitly states PureBrain is built on Claude
- Comparison table has a "same" row color for model quality (tan/orange) vs. check for added features
- Frame: "You keep everything you valued. You gain everything that was missing."
- This builds trust with Claude power users who'd detect BS immediately

### DeepSeek Page: Alert Banner
- Added red alert banner below nav citing 7+ country bans before hero
- Ban map grid shows 8 countries/entities with flags + reason
- This page leans hardest into the urgency/crisis framing given peak search volume

### Hub Page: Accordion Architecture
- All 16 tiles open panels inline (no navigation away)
- Panel content is data-driven from a JS object (TOOLS dict)
- 8 tiles marked "Deep dive" with badge linking to individual pages
- Quiz uses 2-question format (shorter than individual pages) → 16 result combinations

## Brand Rules Applied
- Dark theme: `#080a12` bg, `#0d1120` cards
- Pure Tech Blue: `#2a93c1`, Orange: `#f1420b`
- CTA buttons: orange bg + white text, hover: blue bg
- All CTAs → `https://purebrain.ai/#awakening`
- Self-contained HTML (no external deps)
- No agent names anywhere

## File Sizes
- Individual pages: 37-40KB each
- Hub: 49KB (larger due to 16-tool data + accordion JS)

## WordPress Deployment Notes (When Ready)
- Use `elementor_canvas` template for purebrain.ai
- Need to scope all CSS under unique wrapper ID (standard pattern)
- Individual pages deploy to slugs: /switching-from-deepseek, /switching-from-gemini, etc.
- Hub deploys to: /switch-to-purebrain
- Hub page's deep-dive links hardcoded to those slugs
