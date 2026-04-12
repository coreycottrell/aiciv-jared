# Calculator Pricing Audit — Proof Document
**Date**: 2026-03-03
**Agent**: dept-systems-technology
**Status**: AUDIT COMPLETE — PARTIAL MISMATCH FOUND (main site is stale, not calculator)

---

## Summary

The calculator math is correct. The calculator prices are internally consistent.
However, the MAIN SITE (page 11) is displaying an OLD pricing structure that conflicts
with both the calculator AND the invitation page. The calculator matches the invitation
page (the new structure). Page 11 needs to be updated.

---

## Step 1: Prices Found on purebrain.ai Pages

### Main Site — Page 11 (pure-brain-agentic-ai-partner) — THE HOMEPAGE
| Tier | Price Shown | Note |
|------|-------------|------|
| Awakened | $79/mo | OLD PRICE — pre-consolidation |
| Bonded | $149/mo | MOST POPULAR badge — REMOVED in new structure |
| Partnered | $499/mo | Correct |
| Unified | $999/mo | Correct |
| Enterprise | Custom | Correct |

**STATUS: STALE — This page has NOT been updated to new tier structure**

### Invitation Page — Page 987 (invitation)
| Tier | Price Shown | Strikethrough Old Price |
|------|-------------|------------------------|
| Awakened | $149/mo | ~~$197/mo~~ |
| Partnered | $499/mo | ~~$579/mo~~ |
| Unified | $999/mo | ~~$1,089/mo~~ |

**STATUS: CURRENT — 3-tier structure, correct new prices**

### Terms of Service — Page 541
| Tier | Price Shown |
|------|-------------|
| Awakened | "See purebrain.ai for current pricing" |
| Bonded | $149/month |
| Partnered | $499/month |
| Unified | $999/month |

**STATUS: MIXED — Bonded tier still listed, Awakened deferred to main site**

### Compare Page — Page 1190 (purebrain-vs-glbgpt)
- Shows: $149/mo Bonded reference in comparison table
- **STATUS: STALE** — still references Bonded tier

---

## Step 2: Calculator Prices (Page 777 - ai-tool-stack-calculator)

The calculator uses a BUNDLED pricing model: BASE PRICE + Claude Max subscription.

| Tier | Base Price | Claude Max | Display Price |
|------|-----------|-----------|---------------|
| Awakened | $149/mo | $100/mo | **$249/mo** |
| Partnered | $499/mo | $200/mo | **$699/mo** |
| Unified | $999/mo | $200/mo | **$1,199/mo** |

**TIERS array in live calculator (page 777):**
```javascript
const TIERS = [
  {
    id: 'awakened',
    name: 'Awakened',
    price: 149,
    claudeMaxCost: 100,
    get displayPrice() { return this.price + this.claudeMaxCost; }, // = 249
    minSpend: 0,
    minTools: 0,
  },
  {
    id: 'partnered',
    name: 'Partnered',
    price: 499,
    claudeMaxCost: 200,
    get displayPrice() { return this.price + this.claudeMaxCost; }, // = 699
    badge: 'Most Popular',
    minSpend: 200,
    minTools: 10,
  },
  {
    id: 'unified',
    name: 'Unified',
    price: 999,
    claudeMaxCost: 200,
    get displayPrice() { return this.price + this.claudeMaxCost; }, // = 1199
    minSpend: 400,
    minTools: 15,
  },
];
```

---

## Step 3: Match / Mismatch Report

| Source | Awakened | Partnered | Unified | Bonded | Structure |
|--------|----------|-----------|---------|--------|-----------|
| Calculator (777) | $249 (bundled) | $699 (bundled) | $1,199 (bundled) | REMOVED | 3-tier |
| Invitation Page (987) | $149 base | $499 base | $999 base | REMOVED | 3-tier |
| Main Site (11) | **$79 (OLD)** | $499 base | $999 base | **$149 (OLD)** | **4-tier (STALE)** |
| Terms of Service (541) | "see site" | $499 base | $999 base | **$149** listed | **4-tier (STALE)** |

**MATCH**: Calculator base prices ($149/$499/$999) = Invitation page prices. CONSISTENT.

**MISMATCH**: Main site page 11 shows Awakened at $79 (old price) and includes Bonded tier ($149) which has been removed from the new structure.

**ROOT CAUSE OF MISMATCH**: Page 11 (the homepage/main page) has NOT been updated when the tier structure was consolidated from 4 to 3 tiers. The calculator and invitation page were updated, but page 11 was not.

---

## Step 4: Calculator Math Verification

### getTier() Logic
```javascript
function getTier(spend, toolCount) {
  for (let i = TIERS.length - 1; i >= 0; i--) {
    if (spend >= TIERS[i].minSpend ||
        (toolCount != null && toolCount >= TIERS[i].minTools && TIERS[i].minTools > 0)) {
      return TIERS[i];
    }
  }
  return TIERS[0];
}
```

**Logic**: Iterates from highest tier down. Returns first tier where spend OR tool count meets threshold.

### Test Results

| Test Case | Stack Total | Tool Count | Expected Tier | Actual Tier | PASS? |
|-----------|-------------|-----------|---------------|-------------|-------|
| No tools | $0 | 0 | Awakened | Awakened ($249) | PASS |
| 4 basic tools (~$83) | $83 | 4 | Awakened | Awakened ($249) | PASS |
| 8 tools, $250 spend | $250 | 8 | Partnered (spend>=$200) | Partnered ($699) | PASS |
| 10 tools, $150 spend | $150 | 10 | Partnered (tools>=10) | Partnered ($699) | PASS |
| 9 tools, $200 spend | $200 | 9 | Partnered (spend>=$200) | Partnered ($699) | PASS |
| 9 tools, $199 spend | $199 | 9 | Awakened (under both) | Awakened ($249) | PASS |
| 12 tools, $500 spend | $500 | 12 | Unified (spend>=$400) | Unified ($1199) | PASS |
| 15 tools, $300 spend | $300 | 15 | Unified (tools>=15) | Unified ($1199) | PASS |
| 14 tools, $400 spend | $400 | 14 | Unified (spend>=$400) | Unified ($1199) | PASS |
| 14 tools, $399 spend | $399 | 14 | Partnered (spend>=$200) | Partnered ($699) | PASS |
| 20 tools, $600 spend | $600 | 20 | Unified (both) | Unified ($1199) | PASS |

**ALL 11 MATH TESTS: PASS**

### Tier Escalation Thresholds
- **Awakened**: Default tier (no threshold) — shown when spend < $200 AND tools < 10
- **Partnered**: Triggers when spend >= $200 OR tool count >= 10
- **Unified**: Triggers when spend >= $400 OR tool count >= 15

### Savings Calculation
The calculator computes savings as: `stack_total - tier.displayPrice`

This means when tool stack costs LESS than PureBrain, the number is negative.
The calculator handles this correctly — it only shows "savings" when the value is positive
(i.e., user's current tools cost more than the PureBrain tier they'd need).

---

## Step 5: Fixes Required

### ISSUE 1 — REQUIRES ACTION: Main Site Page 11 Shows Stale Pricing
**Severity**: High — Users landing on homepage see $79 Awakened + Bonded tier which no longer exist
**Fix needed**: Update page 11 pricing section to match new 3-tier structure:
  - Remove Awakened at $79 and Bonded at $149
  - Add Awakened at $149 (Most Popular)
  - Keep Partnered at $499, Unified at $999, Enterprise Custom

### ISSUE 2 — MINOR: Terms of Service Still Lists Bonded
**Severity**: Low — Legal page still references Bonded tier at $149
**Fix needed**: Update TOS pricing table to reflect 3-tier structure

### ISSUE 3 — NOT AN ISSUE (INFORMATIONAL): Calculator Shows Bundled Prices
The calculator displays $249/$699/$1,199 (base + Claude Max bundled).
This is INTENTIONAL — the calculator shows users their TRUE total cost including
the required Claude Max subscription. The footnote "* Includes required Claude Max subscription" explains this.
This is NOT a mismatch — it is a deliberate UX choice.

---

## Verification Evidence

### Calculator (Page 777) TIERS Array Verified
- Fetched live from WP API: `GET /wp/v2/pages/777?context=edit`
- Response: 166,393 chars of content
- TIERS array extracted and confirmed: 3 tiers, correct prices
- All tier name/price/minSpend/minTools values confirmed

### Math Tests Executed
- Python simulation of exact JS getTier() logic
- 11 test cases covering all edge conditions
- Result: 11/11 PASS

### Page Audit
- Page 11: Checked via WP REST API, confirmed stale $79 Awakened + Bonded
- Page 987: Confirmed new 3-tier structure with $149/$499/$999
- Page 777: Confirmed calculator uses $149/$499/$999 base (matching invitation page)

---

## Final Verdict

| Claim | Status |
|-------|--------|
| Calculator math works correctly | CONFIRMED |
| Calculator tier prices internally consistent | CONFIRMED |
| Calculator prices match invitation page (new structure) | CONFIRMED |
| Calculator prices match main site page 11 | MISMATCH — page 11 is stale |
| All escalation thresholds work correctly | CONFIRMED |
| Savings calculation is correct | CONFIRMED |

**ACTION REQUIRED**: Update main site page 11 to new 3-tier pricing structure.
The calculator is correct. Page 11 is the stale page.
