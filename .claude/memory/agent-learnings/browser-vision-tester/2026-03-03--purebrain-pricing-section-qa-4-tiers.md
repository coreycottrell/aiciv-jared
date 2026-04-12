# Memory: PureBrain.ai Pricing Section QA - 4 Tiers Verified
**Date**: 2026-03-03
**Type**: operational + teaching
**Topic**: Pricing section QA confirming Awakened removal and 4-tier structure

---

## Task Summary

Visual QA of purebrain.ai pricing section to verify:
- $79 Awakened tier removed
- 4 tiers: Bonded ($149), Partnered ($499), Unified ($999), Enterprise (Custom)
- NO PAYMENT TODAY badges
- MOST POPULAR on Bonded
- 4-column desktop grid
- 12 features per tier
- All buttons: "Reserve Your AI Now"

**Result**: ALL 8 QA CRITERIA PASS

---

## Key Technical Finding: Pricing Section is JS-Gated

The `#pricing` section has `display: none` by default (height: 0).
It is revealed ONLY after the user completes the chatbox/awakening flow.

**To test it in Playwright without completing the flow:**
```python
await page.evaluate("window.showPricing()")
await asyncio.sleep(2)
```

The `window.showPricing()` function exists and works.
Other related functions: `revealPricing`, `closeCelebrationAndShowPricing`

**Gotcha**: `scroll_into_view_if_needed()` on `#pricing` times out because element is not visible.
Use JS scroll + `window.showPricing()` instead.

---

## Verified Pricing Structure

### 4 Tiers (No Awakened)

| Tier | Price | Badge | Featured |
|------|-------|-------|---------|
| Bonded | $149/month | MOST POPULAR | Yes (orange border) |
| Partnered | $499/month | - | No |
| Unified | $999/month | - | No |
| Enterprise | Custom | - | No |

All 4 have: NO PAYMENT TODAY, "Reserve Your AI Now" button

### Grid Layout
- `display: grid`
- `gridTemplateColumns: 254px 235px 231px 237px` (4 columns, single row)
- Total grid width fits within 1440px viewport

### Bonded Features (all 12 matching spec)
1. Unlimited agent creation
2. 50+ agent simultaneous deployment
3. Your AI has a permanent home that's always on
4. Your AI inherits wisdom from a family of AI minds
5. Comms hub access (skills sync)
6. We maintain it for you - problems fixed before you notice them
7. Proactive health checks
8. Priority skills sync
9. 24h support response
10. Telegram + Bluesky setup
11. Community support
12. Basic documentation

---

## Visual State

- Dark background (#080a12 or similar) throughout
- Brain orb animation visible behind pricing section header
- Bonded card has orange border (featured styling)
- "BRING YOUR AI FULLY ONLINE" heading
- 30-Day Relationship Guarantee badge above cards
- Subheading: "Your PURE BRAIN has discovered its identity. Now let's give it the power to actually help you."

---

## Screenshots

All in `/home/jared/projects/AI-CIV/aether/exports/screenshots/pricing-qa/`
- `06_pricing_top.png` - Header + top of cards
- `07_pricing_cards_main.png` - Full 4-card view (best overview shot)
- `08_pricing_bullets.png` - Feature bullets visible
- `09_pricing_bottom.png` - Bottom of cards

---

## Playwright Pattern for JS-Gated Sections

```python
# Navigate to page
await page.goto(URL, wait_until="domcontentloaded")
await asyncio.sleep(4)  # Wait for all JS to initialize

# Call the reveal function
await page.evaluate("window.showPricing()")
await asyncio.sleep(2)

# Scroll to it via JS (not Playwright scroll_into_view)
await page.evaluate("""
    const el = document.querySelector('#pricing');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
""")
await asyncio.sleep(1.5)

# Now screenshot
await page.screenshot(path=str(output_path))
```

**Why**: `scroll_into_view_if_needed()` fails because Playwright waits for element to be stable/visible.
JS scrollIntoView works even on just-revealed elements.
