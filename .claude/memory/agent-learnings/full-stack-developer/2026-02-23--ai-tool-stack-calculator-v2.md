# AI Tool Stack Calculator V2 Build

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

Upgraded `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v2.html` from a static $299/mo comparison tool to a dynamic 4-tier PureBrain pricing calculator.

## Key Changes Made

### 1. Tool Expansion (8 categories → 13 categories, ~35 tools → 65+ tools)
- Added: AI Writing & Copywriting (Jasper, Copy.ai, Writesonic, Grammarly, Wordtune)
- Added: SEO & Marketing Intelligence (SEMrush, Ahrefs, Moz, Surfer, MarketMuse)
- Added: Social Media Management (Hootsuite, Buffer, Sprout Social, Later, SocialBee)
- Added: Project Management & Productivity AI (Notion AI, ClickUp AI, Monday, Motion, Reclaim)
- Added: Data Analysis & BI (Tableau, Power BI, Julius AI, Obviously AI)
- Extended existing categories: Grok to chatbots, Constant Contact + ConvertKit to leadgen, Elicit + Consensus to research

### 2. Dynamic Tier Recommendation Logic
Replaced fixed `PUREBRAIN_PRICE = 299` with a `TIERS` array and `getRecommendedTier()` function:
- $0–200 spend → Awakened ($79)
- $200–500 spend → Bonded ($149)
- $500–1000 spend → Partnered ($499)
- $1000+ spend → Unified ($999)

### 3. Dynamic Sidebar Panel
New `.calc-tier-panel` component:
- Shows recommended tier with "Your Best Match" badge
- Tier name, tagline, price, and feature list all update dynamically
- "Other Plans" section shows compact clickable tier cards
- User can click any tier card to compare savings at that price point
- Full 4-tier comparison table (collapsible) via `toggleCompareTable()`
- CTA button text updates: "Start Your AI Partnership — $X/mo"

### 4. Confetti Threshold Change
Was: triggered when `rawTotal > PUREBRAIN_PRICE (299)`
Now: triggered when `savings > 100` (stack minus recommended tier price > $100)

### 5. Updated Presets
New preset names and tool selections reflecting the expanded tool set:
- Solopreneur Stack (ChatGPT, Canva, Grammarly, Mailchimp, Midjourney)
- Marketing Team (ChatGPT, SEMrush, Jasper, Hootsuite, Midjourney, HubSpot, Buffer, Canva)
- Creator Studio (ChatGPT, Canva, Midjourney, Runway, Pika, InVideo, Copy.ai)
- Enterprise Stack (ChatGPT, Cursor, Copilot, SEMrush, Sprout Social, HubSpot, LinkedIn, Tableau, Botpress)
- Full Stack Founder (ChatGPT, Claude, Cursor, Lovable, Gamma, Midjourney, Jasper, Mailchimp)

## Architecture Pattern: Self-Contained Single-File HTML Calculator

For interactive calculators like this, the pattern is:
1. All CSS in `<style>` with unique class prefix (`.calc-`) for WordPress Elementor safety
2. All tool data in a JS array of category objects, each with tools array
3. State: `selectedTools = new Set()` with `toolLookup` dictionary for O(1) access
4. `updateTotals()` is the single source of truth — called after every state change
5. `animateCounter()` for smooth number transitions (easeOut cubic)

## Dynamic Tier Pattern (Reusable)

```javascript
const TIERS = [
  { id: 'tier1', price: 79, minSpend: 0, maxSpend: 200, features: [...] },
  // ...
];

function getRecommendedTier(total) {
  for (let i = TIERS.length - 1; i >= 0; i--) {
    if (total >= TIERS[i].minSpend) return TIERS[i];
  }
  return TIERS[0];
}
```

This pattern works well for any product with tiered pricing tied to customer spend.

## File Location
`/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v2.html`
2129 lines, fully self-contained, no external dependencies
