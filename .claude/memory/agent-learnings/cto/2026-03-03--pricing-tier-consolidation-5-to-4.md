# CTO Memory: Pricing Tier Consolidation — 5 to 4 Tiers

**Date**: 2026-03-03
**Type**: operational
**Topic**: PureBrain pricing restructure — standalone test HTML page

---

## Task
Build a standalone test HTML page consolidating PureBrain pricing from 5 tiers to 4. Runs in parallel with portal v4 work — separate team, separate files.

## Output
**File**: `/home/jared/projects/AI-CIV/aether/exports/pricing-test-page.html`

## Tier Structure Decided
| Tier | Price | Was | CTA |
|------|-------|-----|-----|
| Awakened (MOST POPULAR) | $149/mo | ~~$197/mo*~~ | "Claim This Spot" (orange filled) |
| Partnered | $499/mo | ~~$579/mo*~~ | "Get Started" (outlined) |
| Unified | $999/mo | ~~$1,089/mo*~~ | "Get Started" (outlined) |
| Enterprise | Custom | — | "Let's Talk" (blue filled) |

## Key Design Decisions
- Merging old Awakened ($79) + old Bonded ($149) into new Awakened ($149)
- Enterprise card centered below top 3 on desktop — max-width 520px
- Orange (#f1420b) = prices, MOST POPULAR badge, Awakened CTA, checkmarks for top 3
- Blue (#2a93c1) = tier names, Enterprise CTA, Enterprise checkmarks
- Dark bg: #080a12 page, #0e1120 cards, #111629 popular/enterprise cards
- Strikethrough prices rendered with `~~` markup (CSS text-decoration:line-through on .price-was)
- Footnote: "*Pricing post our full launch. Lock in the savings today for 1 full year!"
- Oswald font for headings/prices, Inter for body
- Responsive: 3 cols → 2 cols (tablet) → 1 col (mobile)

## New Benefits Added (CTO decision — add 2-3 per mid/high tier)
- Partnered additions: "Dedicated onboarding session", "Monthly performance report", "Priority feature requests"
- Unified additions: "Custom workflow automation", "Dedicated Slack/Teams channel", "Priority bug fixes"
- Enterprise additions: "Multi-team deployment", "Custom SLA terms", "Executive strategy sessions"

## Pattern Learned
When pricing pages use SVG inline checkmarks (no icon font dependency), they render reliably in all environments including WordPress HTML widgets.
Using `~~strikethrough~~` in HTML via `.price-was { text-decoration: line-through }` is cleaner than wrapping in `<s>` tags because it keeps Elementor from mangling nested tags.
