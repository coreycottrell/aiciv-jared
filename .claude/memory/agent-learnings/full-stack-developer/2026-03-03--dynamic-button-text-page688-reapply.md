# Memory: Dynamic "Activate [AI NAME] Now" Button Text — Page 688 Re-Apply

**Date**: 2026-03-03
**Agent**: dept-systems-technology / full-stack-developer
**Type**: technique
**Topic**: Re-applying dynamic CTA button text with AI name injection on pay-test-sandbox-2 (page 688)

---

## What Was Done

Re-applied dynamic "Activate [AI NAME] Now" button text to all 3 paid tiers on page 688 (pay-test-sandbox-2). This was a targeted fix — pages 11 and 689 were NOT touched.

### Changes Applied (6 total)

1. **Awakened button HTML default text**: `CLAIM THIS SPOT` → `Activate Your AI Now`
   - Element: `<button id="proCta">`
   - Location in HTML: line ~5522

2. **Partnered button**: Added `id="partnerCta"` attribute + changed `GET STARTED` → `Activate Your AI Now`
   - Was: `<button class="pricing-card__cta pricing-card__cta--secondary" onclick="openPayPalModal('Partnered')">`
   - Now: `<button class="pricing-card__cta pricing-card__cta--secondary" id="partnerCta" onclick="openPayPalModal('Partnered')">`

3. **Unified button**: Added `id="unifiedCta"` attribute + changed `GET STARTED` → `Activate Your AI Now`
   - Same pattern as Partnered above

4. **showPricing() JS function**: Fixed broken static text + added all 3 buttons
   - Was: `document.getElementById('proCta').textContent = 'CLAIM THIS SPOT';`
   - Now:
     ```js
     document.getElementById('proCta').textContent = hasName ? `Activate ${aiName} Now` : 'Activate Your AI Now';
     document.getElementById('partnerCta').textContent = hasName ? `Activate ${aiName} Now` : 'Activate Your AI Now';
     document.getElementById('unifiedCta').textContent = hasName ? `Activate ${aiName} Now` : 'Activate Your AI Now';
     ```

5. **Feature span: "permanent home"**: Wrapped `Your AI` in `<span class="ai-name-dynamic">`
   - Was: `<span style="display:inline">Your AI has a permanent home that's always on</span>`
   - Now: `<span style="display:inline"><span class="ai-name-dynamic">Your AI</span> has a permanent home that's always on</span>`

6. **Feature span: "inherits wisdom"**: Same treatment as above

### Enterprise Button — Left Unchanged

`LET'S TALK` on the Enterprise tier was explicitly NOT changed per spec.

---

## Key File Paths

- **Backup**: `exports/backup_page_688_pre_dynamic_buttons.json` (486,762 chars, pre-change)
- **Widget ID**: `292c72a` (the HTML widget in Elementor that holds all the pricing code)
- **Page ID**: 688
- **Page URL**: https://purebrain.ai/pay-test-sandbox-2/ (password-protected)

---

## Verification Pattern

Page 688 is password-protected — the live URL check will fail. Always verify via:
```python
resp = requests.get(
    'https://purebrain.ai/wp-json/wp/v2/pages/688?context=edit',
    auth=('Aether', 'ZGuh 1W8k WpWM c9iy kqyd buPr'),
    headers={'User-Agent': 'Aether-Agent/1.0'}
)
el_data = resp.json()['meta']['_elementor_data']
```
Then parse the JSON and find the HTML widget (id=292c72a).

---

## HTML Size History

| Event | Length |
|-------|--------|
| Pre-change (backup) | 457,265 chars |
| Post-change | 457,692 chars |
| Delta | +427 chars |

---

## The showPricing() Logic

The function uses `state.aiName` which is set earlier in the chatbox flow when the user names their AI. The `hasName` check is:
```js
const hasName = aiName && aiName !== 'PURE BRAIN';
```
So if a user names their AI "Nova", all 3 buttons show "Activate Nova Now". If no name, all show "Activate Your AI Now".

---

## Tags
page-688, pay-test-sandbox-2, dynamic-buttons, ai-name, pricing, CTA, showPricing, partnerCta, unifiedCta, proCta, elementor
