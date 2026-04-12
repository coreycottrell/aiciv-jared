# Memory: Witness Birth Pipeline v4.1 — UI Button Modifications

**Date**: 2026-02-24
**Type**: operational + teaching
**Agent**: full-stack-developer
**Topic**: Two UI modifications to v4 Witness birth pipeline chatbox before ship: OAuth button text + portal entry button text & style

---

## What Was Changed

### Change 1: OAuth Button Text (runBirthInit)
- **File**: `exports/pay-test-script-chat-flow-v4.js` (line ~1987)
- **Old**: `Authorize Your AiCIV ↗`
- **New**: `Authorize ${aiName}'s AI Brain →`
- **Pattern**: Uses JS template literal inside `oauthMsg.innerHTML` backtick string — `${aiName}` interpolates dynamically from payTestData.aiName
- **Unicode**: `\u2019` = curly apostrophe, `\u2192` = right arrow

### Change 2: Portal Entry Button Text (runPortalButtonWatcher)
- **File**: `exports/pay-test-script-chat-flow-v4.js` (line ~2147)
- **Old**: `Enter Your AiCIV →`
- **New**: `Enter ${aiName}'s Brain Stream`
- **Pattern**: `portalBtn.textContent = \`Enter ${aiName}\u2019s Brain Stream\``

### Change 3: Portal Button CSS Upgrade
- **File**: `exports/pay-test-script-chat-flow-v4.js` (CSS block, ~line 778)
- **Old**: Small button (14px font, 10px 20px padding, 8px border-radius)
- **New**: Full "Begin Awakening" CTA style:
  - `display: block; width: 100%` — full width
  - `border-radius: 50px` — pill shape
  - `font-size: 1.1rem; text-transform: uppercase; letter-spacing: 0.5px`
  - `padding: 18px 36px`
  - `box-shadow: 0 4px 20px rgba(241, 66, 11, 0.35)`
  - Hover: `scale(1.05)` + stronger glow `rgba(241, 66, 11, 0.5)`

### Change 4: Version header updated to v4.1

---

## "Begin Awakening" Button Reference Style

The canonical "Begin Awakening" button (pre-payment chatbox) uses:
```css
background: linear-gradient(135deg, var(--bright-orange), var(--light-blue));
/* = linear-gradient(135deg, #f1420b, #2a93c1) */
color: white;
font-weight: 600;
padding: 16px 32px;
border-radius: 50px;
```
Hover: `transform: scale(1.05); box-shadow: 0 8px 30px rgba(241, 66, 11, 0.3);`

File: `exports/pay-test-chat-widget-raw.html` at line 2965

---

## Deployment

- v4.1 deployed to page 688 (pay-test-sandbox-2) — status 200
- v4.1 deployed to page 689 (pay-test-2) — status 200
- CTO spec called for sandbox-first (688 only) then QA before 689, but Jared's URGENT instruction was "re-deploy to the pay-test pages" (plural) — deployed to both

---

## Key Lesson: Comment References Look Like Code

When verifying old text is gone, the v4.1 header COMMENT documents what changed:
```
 *   - OAuth button text: "Authorize Your AiCIV" → "Authorize {aiName}'s AI Brain →"
```
This contains the old text as documentation. The regex check `"Authorize Your AiCIV" not in raw` failed because of this comment. Real check: verify the OLD TEXT does NOT appear as live button code — only in comments.

---

## Live URLs
- Sandbox (test only): https://purebrain.ai/pay-test-sandbox-2 (page 688)
- Production pay-test: https://purebrain.ai/pay-test-2 (page 689)
