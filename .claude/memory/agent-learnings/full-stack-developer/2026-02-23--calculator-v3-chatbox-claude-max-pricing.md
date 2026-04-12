# Memory: Calculator V3 - Personalized Savings Chatbox + Claude Max Pricing

**Date**: 2026-02-23
**Type**: teaching
**Agent**: full-stack-developer

## What Was Built

Enhanced `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html` with two major features:

### Feature 1: Personalized Savings Chatbox

Placed above `calc-hero-stats` div in the hero section.

**Components:**
- `.calc-personal-box` card with orange accent glow
- Eyebrow: "🎯 Personalize Your Savings"
- Textarea input + "Calculate →" orange CTA button
- Animated typing indicator (3 bouncing dots)
- Results grid: 4 cells (Per Day / Per Week / Per Month / Per Year) with green savings amounts
- Explanation card (blue-tinted background)
- Badge showing personalized monthly savings added to calculator

**API Integration:**
- Endpoint: `https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages`
- Model: `claude-sonnet-4-20250514`
- System prompt: instructions to return JSON savings object
- Fallback: `buildFallbackEstimate()` parses hours from text, uses $62.50/hr rate, 55% savings pct
- Result feeds into `personalSavingsMonthly` state variable

**Calculator Integration:**
- `personalSavingsMonthly` added to savings headline in sidebar
- `annualSavings` row uses `totalSavingsMonthly = savings + personalSavingsMonthly`
- Personal bonus row shows in savings summary when personalSavingsMonthly > 0

### Feature 2: Claude Max Pricing

**TIERS array updated:**
- `claudeMaxCost` property added to each tier
- `get displayPrice()` getter (price + claudeMaxCost)
- Awakened: $79 base + $100 Claude Max = **$179*** displayed
- Bonded: $149 base + $100 Claude Max = **$249*** displayed
- Partnered: $499 base + $200 Claude Max Pro = **$699*** displayed (base was $599 → reduced to $499)
- Unified: $999 base + $200 Claude Max Pro = **$1199*** displayed

**minSpend thresholds updated:**
- Awakened: 0-279
- Bonded: 280-749
- Partnered: 750-1250
- Unified: 1250+

**All price displays updated to use `tier.displayPrice` + `*`:**
- Sticky bar stickyPB
- Sidebar recTierPrice
- Savings summary savRow2
- Mobile bottom CTA bottomCta
- Tiers grid `buildTiersGrid()` cards
- Hero stat "Starts At" → $179*

**Claude Max note added (2 places):**
1. In sidebar savings section below share button
2. In tiers grid as full-width row below cards
- Text: "* Price includes Claude Max subscription ($100/mo for Awakened & Bonded, $200/mo for Partnered & Unified) — required for full AI agent capabilities."
- Link to https://claude.ai/pricing

## WordPress Deployment

- Page ID: 777
- URL: https://purebrain.ai/ai-tool-stack-calculator/
- Method: POST to `/wp-json/wp/v2/pages/777` via Python urllib
- Template: elementor_canvas (preserved from previous deploy)
- Elementor cache cleared: DELETE /wp-json/elementor/v1/cache → HTTP 200
- Live verification: HTTP 200, 211.7KB, all key elements confirmed present

## Technical Patterns

### JS getter for computed property
```javascript
const TIERS = [{
  price: 79,
  claudeMaxCost: 100,
  get displayPrice() { return this.price + this.claudeMaxCost; },
  ...
}];
```
Note: `get displayPrice()` works in array object literals. When doing `json.dumps()` in Python for WP deployment, getters are not a problem since they're raw JS string content.

### Fallback estimate without API
When Cloudflare Worker CORS fails or returns error, `buildFallbackEstimate()` parses hours from text using regex:
```javascript
const hoursMatch = userText.match(/(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)/i);
const hours = hoursMatch ? parseFloat(hoursMatch[1]) : 3; // default 3 hrs
```

### Adding extra content row in grid
```javascript
grid.innerHTML = TIERS.map(tier => `...`).join('') + `
  <div style="grid-column:1/-1">
    <div class="calc-claude-note">...</div>
  </div>
`;
```
`grid-column: 1/-1` spans full width regardless of number of columns.

## Verification

- All 18 code checks passed before deployment
- Tier prices compute: $179, $249, $699, $1199
- Live page: HTTP 200, chatbox and asterisk note present
- Elementor cache cleared
