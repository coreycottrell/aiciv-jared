# Calculator V3: Tier Pricing, Social Share Modal, Tool Expansion

**Date**: 2026-02-23
**Type**: operational
**File**: `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`

## What Was Done

### Change 1: Tier Thresholds + Partnered Price
- Partnered price changed from $499 to $599 (Jared's screenshot instruction)
- Updated minSpend/maxSpend to match new thresholds:
  - Awakened: $0-$179 (minSpend:0, maxSpend:179)
  - Bonded: $180-$549 (minSpend:180, maxSpend:549)
  - Partnered: $550-$999 (minSpend:550, maxSpend:1000)
  - Unified: $1000+ (minSpend:1000, maxSpend:Infinity)
- getTier() uses minSpend iterating from highest→lowest, so threshold values directly control logic

### Change 2: Social Share Modal
- Replaced clipboard-only share button with full social share popup
- Added `.calc-share-overlay` + `.calc-share-modal` HTML and CSS
- Modal placed just before `<!-- Mobile bottom bar -->`
- CSS added just before closing `</style>` tag
- New functions: `buildShareText()`, `handleShare()`, `closeShareModal()`, `handleShareCopy()`
- `buildShareText()` extracted into separate function (reused by both the preview and copy)
- Social platforms: Twitter/X, LinkedIn, Facebook, Email, Copy to Clipboard
- LinkedIn shares URL only (platform limitation - no text in URL sharing)
- Facebook shares URL + quote param
- Twitter/Email get full encoded text
- Modal closes on: X button, click outside, Escape key
- Body scroll locked while modal open

### Change 3: Tool Expansion
- Previous: 110 tools, 25 categories
- After: 138 tools, 31 categories
- 6 new categories added: voice_ai, ai_music, ai_3d, ai_agents, notetaking, ai_search
- New tools added to existing categories: reclaim, clockwise, motion (meetings), paradox, phenom (hr), harvey_ai, cocounsel (legal), thoughtspot (data), ramp, stampli (finance), tray_io (automation)
- Hero stats updated: 130+ → 140+, 25 → 31 categories
- globalToolCount display updated to "0 of 140+"

## Patterns / Gotchas

### JS Brace Balance
The file has 0 brace diff ({=336, }=336) - always verify after editing JS
Use: `python3 -c "content=open('file.html').read(); js=content[content.find('<script>'):]; print(js.count('{'), js.count('}'))"`

### Self-Contained File Rule
File has zero external dependencies. All CSS uses `calc-` prefix for WordPress safety.
No CDN imports allowed. Icons done via emoji (not icon fonts).

### Tier Logic
TIERS array is ordered Awakened→Unified. getTier() iterates REVERSE (highest first).
When adding a tier or changing prices, update both: `price:` field AND `minSpend:`/`maxSpend:` range.

### Tool Count
Always re-count after adding tools:
`grep "{ id:" file.html | grep "price:" | wc -l`
